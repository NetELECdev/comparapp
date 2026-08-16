#!/usr/bin/env python3
"""
CARGA DE IMÁGENES DESDE UN CATÁLOGO CON URLs (fuente con permiso).

Este script NO busca imágenes en internet. Toma un CSV que YA trae la URL de la
imagen de cada producto — por ejemplo, el catálogo de un distribuidor/mayorista
que te autorizó a usar sus imágenes, o un listado propio tuyo — y las integra a
ComparApp: las descarga, las optimiza, las sube a tu bucket de Supabase y actualiza
la columna imagen_prod de los productos que coincidan.

El cruce con tus productos se hace por:
  1) EAN (columna ean_prod) si el catálogo trae código de barras — preciso.
  2) Nombre exacto (case-insensitive) si no hay EAN — coincidencia por texto.

Uso típico:
    # 1) Revisar qué coincidiría, SIN tocar nada (recomendado primero):
    python cargar_imagenes_catalogo.py --csv catalogo.csv --dry-run

    # 2) Ejecutar de verdad (descarga, optimiza, sube, actualiza imagen_prod):
    python cargar_imagenes_catalogo.py --csv catalogo.csv --aplicar

Formato esperado del CSV (con encabezados). Indicá qué columna es cuál con los flags:
    --col-ean       nombre de la columna con el EAN        (opcional)
    --col-nombre    nombre de la columna con el nombre     (opcional)
    --col-imagen    nombre de la columna con la URL imagen (REQUERIDO)
    --delimitador   ; o ,  (default ,)
    --encoding      utf-8 o latin-1 (default utf-8)

Al menos uno de --col-ean o --col-nombre debe estar presente para poder cruzar.

Requisitos:
    pip install requests python-dotenv pillow
.env (en la carpeta desde donde se ejecuta):
    SUPABASE_URL=https://TU-PROYECTO.supabase.co
    SUPABASE_SERVICE_KEY=tu_service_role_key
    SUPABASE_BUCKET=product-images
"""

import argparse
import csv
import os
import re
import sys
import time
import uuid
from io import BytesIO
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "product-images")

MAX_W, MAX_H = 800, 800
JPEG_QUALITY = 82

# Archivo donde se guarda el progreso (para reanudar si el script se corta)
PROGRESO_FILE = ".progreso_catalogo.json"


def cargar_progreso() -> set:
    """Devuelve el set de claves (ean o nombre) ya procesadas en corridas previas."""
    import json
    try:
        with open(PROGRESO_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, ValueError):
        return set()


def guardar_progreso(procesados: set):
    """Persiste el set de claves procesadas."""
    import json
    try:
        with open(PROGRESO_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(procesados), f, ensure_ascii=False, indent=0)
    except Exception as e:
        print(f"    ⚠️ No se pudo guardar el progreso: {e}")


def faltan_credenciales() -> bool:
    return not SUPABASE_URL or not SUPABASE_SERVICE_KEY


def ean_valido(code: str) -> bool:
    """Valida EAN-8 / EAN-13 con dígito verificador."""
    s = (code or "").strip()
    if not s.isdigit() or len(s) not in (8, 13):
        return False
    digits = [int(c) for c in s]
    check = digits.pop()
    empieza_en_3 = len(s) == 8
    suma = 0
    for i, d in enumerate(digits):
        peso = (3 if empieza_en_3 else 1) if i % 2 == 0 else (1 if empieza_en_3 else 3)
        suma += d * peso
    return (10 - (suma % 10)) % 10 == check


def leer_catalogo(path, col_ean, col_nombre, col_imagen, delim, enc):
    filas = []
    with open(path, "r", encoding=enc, newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        if col_imagen not in (reader.fieldnames or []):
            print(f"❌ La columna de imagen '{col_imagen}' no está en el CSV.")
            print(f"   Columnas disponibles: {reader.fieldnames}")
            sys.exit(1)
        for row in reader:
            img = (row.get(col_imagen) or "").strip()
            if not img:
                continue
            filas.append({
                "ean": (row.get(col_ean) or "").strip() if col_ean else "",
                "nombre": (row.get(col_nombre) or "").strip() if col_nombre else "",
                "imagen": img,
            })
    return filas


def buscar_productos(item) -> list:
    """Busca en la base los productos que coinciden con este item del catálogo.
    Devuelve lista de filas de 'producto' (id_prod, nombre_prod, ean_prod, imagen_prod)."""
    base = f"{SUPABASE_URL}/rest/v1/producto"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }
    select = "select=id_prod,nombre_prod,ean_prod,imagen_prod,comercio_prod&activo_prod=eq.true"

    # 1) Por EAN válido
    ean = item["ean"]
    if ean and ean_valido(ean):
        url = f"{base}?{select}&ean_prod=eq.{ean}"
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200 and r.json():
            return r.json()

    # 2) Por nombre exacto (case-insensitive)
    nombre = item["nombre"]
    if nombre:
        # ilike sin comodines = igualdad case-insensitive; escapamos comas/paréntesis
        safe = nombre.replace(",", "").replace("(", "").replace(")", "")
        url = f"{base}?{select}&nombre_prod=ilike.{requests.utils.quote(safe)}"
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200 and r.json():
            return r.json()

    return []


def descargar_y_optimizar(url: str) -> Optional[bytes]:
    """Descarga la imagen de la URL del catálogo y la optimiza a JPEG liviano."""
    try:
        req_headers = {"User-Agent": "ComparApp/1.0 carga-catalogo"}
        resp = requests.get(url, headers=req_headers, timeout=30)
        if resp.status_code != 200:
            print(f"    ⚠️ La URL respondió {resp.status_code}")
            return None
        raw = resp.content
    except Exception as e:
        print(f"    ⚠️ No se pudo descargar: {e}")
        return None

    try:
        from PIL import Image, ImageOps
        img = Image.open(BytesIO(raw))
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P", "LA"):
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            fondo.paste(rgba, mask=rgba.split()[-1])
            img = fondo
        else:
            img = img.convert("RGB")
        img.thumbnail((MAX_W, MAX_H), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        return buf.getvalue()
    except Exception as e:
        print(f"    ⚠️ No se pudo optimizar, se sube el original: {e}")
        return raw


def subir_a_bucket(data: bytes) -> Optional[str]:
    nombre = f"productos/{uuid.uuid4()}.jpg"
    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{nombre}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=60)
        if r.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{nombre}"
        print(f"    ⚠️ Error subiendo al bucket {r.status_code}: {r.text[:150]}")
        return None
    except Exception as e:
        print(f"    ⚠️ Error subiendo al bucket: {e}")
        return None


def actualizar_imagen(ids: list, url_publica: str) -> int:
    """Actualiza imagen_prod en todos los productos coincidentes (por id_prod)."""
    base = f"{SUPABASE_URL}/rest/v1/producto"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    lista = ",".join(ids)
    url = f"{base}?id_prod=in.({lista})"
    r = requests.patch(url, headers=headers, json={"imagen_prod": url_publica}, timeout=30)
    return len(ids) if r.status_code in (200, 204) else 0


def main():
    ap = argparse.ArgumentParser(description="Carga imágenes a ComparApp desde un CSV con URLs (fuente con permiso)")
    ap.add_argument("--csv", required=True, help="CSV del catálogo con URLs de imagen")
    ap.add_argument("--col-imagen", required=True, help="Nombre de la columna con la URL de la imagen")
    ap.add_argument("--col-ean", default=None, help="Nombre de la columna con el EAN")
    ap.add_argument("--col-nombre", default=None, help="Nombre de la columna con el nombre del producto")
    ap.add_argument("--delimitador", default=",", help="Delimitador del CSV (, o ;)")
    ap.add_argument("--encoding", default="utf-8", help="Encoding del CSV (utf-8 o latin-1)")
    ap.add_argument("--limit", type=int, default=None, help="Procesar solo N filas (para probar)")
    ap.add_argument("--delay", type=float, default=0.5, help="Segundos entre productos")
    ap.add_argument("--solo-sin-foto", action="store_true", help="Saltar productos que YA tienen imagen")
    ap.add_argument("--dry-run", action="store_true", help="Solo mostrar qué haría, sin escribir nada")
    ap.add_argument("--aplicar", action="store_true", help="Ejecutar de verdad (descarga, sube, actualiza)")
    args = ap.parse_args()

    if not args.col_ean and not args.col_nombre:
        print("❌ Indicá al menos --col-ean o --col-nombre para poder cruzar con tus productos.")
        sys.exit(1)

    modo_real = args.aplicar and not args.dry_run
    if modo_real and faltan_credenciales():
        print("❌ Faltan SUPABASE_URL / SUPABASE_SERVICE_KEY en el .env (necesarias para --aplicar).")
        sys.exit(1)
    if not args.aplicar and not args.dry_run:
        print("ℹ️  No indicaste --dry-run ni --aplicar. Corriendo en DRY-RUN por seguridad.\n")
        args.dry_run = True

    print("📖 Leyendo catálogo...")
    filas = leer_catalogo(args.csv, args.col_ean, args.col_nombre, args.col_imagen,
                          args.delimitador, args.encoding)
    print(f"   {len(filas)} filas con URL de imagen\n")

    total = len(filas) if args.limit is None else min(args.limit, len(filas))
    n_match, n_sin_match, n_subidas, n_saltados = 0, 0, 0, 0

    # Reanudación: en modo real, saltear lo ya procesado en corridas anteriores.
    # (En dry-run no se usa, porque no se escribe nada.)
    procesados = set() if args.dry_run else cargar_progreso()
    n_reanudados = 0
    if procesados:
        print(f"↻ Reanudando: {len(procesados)} productos ya procesados en corridas previas se saltearán.\n")

    for i, item in enumerate(filas[:total], 1):
        etiqueta = item["ean"] or item["nombre"] or "(sin id)"
        clave = (item["ean"] or item["nombre"] or "").strip().lower()

        # Saltar si ya se procesó antes (solo en modo real)
        if not args.dry_run and clave and clave in procesados:
            n_reanudados += 1
            continue

        print(f"[{i}/{total}] {etiqueta}")

        prods = buscar_productos(item)
        if not prods:
            n_sin_match += 1
            print("    ∅ Sin coincidencia en tu base")
            time.sleep(args.delay)
            continue

        # Filtrar los que ya tienen foto, si se pidió
        objetivo = prods
        if args.solo_sin_foto:
            objetivo = [p for p in prods if not p.get("imagen_prod")]
            if not objetivo:
                n_saltados += 1
                print(f"    ↷ Los {len(prods)} coincidentes ya tienen foto, salto")
                time.sleep(args.delay)
                continue

        n_match += 1
        comercios = sorted({p.get("comercio_prod", "?") for p in objetivo})
        print(f"    ✓ Coincide en {len(objetivo)} producto(s) — {', '.join(comercios)}")

        if args.dry_run:
            print(f"      (dry-run) subiría {item['imagen'][:60]}... y actualizaría {len(objetivo)} filas")
            time.sleep(args.delay)
            continue

        # Real: descargar → optimizar → subir → actualizar
        data = descargar_y_optimizar(item["imagen"])
        if not data:
            time.sleep(args.delay)
            continue
        url_publica = subir_a_bucket(data)
        if not url_publica:
            time.sleep(args.delay)
            continue
        ids = [p["id_prod"] for p in objetivo]
        actualizados = actualizar_imagen(ids, url_publica)
        n_subidas += 1
        print(f"      ☁️ Subida y aplicada a {actualizados} producto(s) ({len(data)//1024} KB)")

        # Marcar como procesado y persistir (para poder reanudar si se corta)
        if clave:
            procesados.add(clave)
            guardar_progreso(procesados)
        time.sleep(args.delay)

    print("\n🎉 Listo.")
    print(f"   Filas procesadas     : {total}")
    if not args.dry_run and n_reanudados:
        print(f"   Saltados (ya hechos) : {n_reanudados}")
    print(f"   Con coincidencia     : {n_match}")
    print(f"   Sin coincidencia     : {n_sin_match}")
    if args.solo_sin_foto:
        print(f"   Saltados (ya tenían) : {n_saltados}")
    if not args.dry_run:
        print(f"   Imágenes aplicadas   : {n_subidas}")
        print(f"\n   Progreso guardado en {PROGRESO_FILE} — si se corta, volvé a correr y sigue donde quedó.")
        print(f"   (Para reprocesar todo desde cero, borrá ese archivo.)")
    else:
        print("\n   (DRY-RUN: no se escribió nada. Si el cruce se ve bien, corré con --aplicar)")


if __name__ == "__main__":
    main()