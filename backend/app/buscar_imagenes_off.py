#!/usr/bin/env python3
"""
Busca imágenes de productos en OPEN FOOD FACTS y las sube a Supabase Storage.
Diseñado para ComparApp (FastAPI + Supabase + Nuxt).

Fuente: Open Food Facts (https://world.openfoodfacts.org)
  - Base abierta de alimentos empaquetados, con imágenes bajo licencia libre
    (Creative Commons), pensada para reutilizar.
  - Búsqueda en cascada: primero por EAN (código de barras, preciso),
    si no hay, por nombre (mayor cobertura, menor precisión).

IMPORTANTE sobre cobertura:
  - OFF cubre ALIMENTOS EMPAQUETADOS DE MARCA.
  - NO cubre frescos (carne, verdura, pollo al peso) ni productos locales/artesanales.
  - Para una carnicería la cobertura será BAJA: es esperable, no es un error.

Uso:
    # Solo buscar y descargar (sin tocar Supabase), para medir cobertura:
    python buscar_imagenes_off.py --csv listado.csv --output resultados.json

    # Buscar, descargar y subir al bucket (NO toca la tabla producto):
    python buscar_imagenes_off.py --csv listado.csv --output resultados.json --upload

Requisitos:
    pip install requests python-dotenv

Variables de entorno (.env):
    SUPABASE_URL=https://tu-proyecto.supabase.co
    SUPABASE_SERVICE_KEY=tu_service_role_key
    SUPABASE_BUCKET=product-images
"""

import argparse
import csv
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# ─── Configuración ───────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "product-images")

OFF_BASE = "https://world.openfoodfacts.org"

# Open Food Facts pide identificar la app en el User-Agent (buena práctica y obligatorio).
OFF_USER_AGENT = "ComparApp/1.0 (comparapp.home@gmail.com) - imagenes productos"

# Mapeo de columnas del CSV del POS (mismo formato que ya usás)
HEADERS_CSV = {
    "code": 0,
    "description": 2,
    "brand": 6,
    "price": 9,
    "ean": 13,   # columna EAN si el CSV la trae; si no existe, se ignora
}

SKIP_ROWS = 5  # Filas de encabezado al inicio del CSV


def parse_csv(csv_path: str) -> list[dict]:
    """Parsea el CSV del comercio y devuelve lista de productos."""
    products = []
    with open(csv_path, "r", encoding="latin-1") as f:
        reader = csv.reader(f, delimiter=";")
        for idx, row in enumerate(reader):
            if idx < SKIP_ROWS:
                continue
            if len(row) < 10:
                continue
            code = row[HEADERS_CSV["code"]].strip()
            desc = row[HEADERS_CSV["description"]].strip()
            brand = row[HEADERS_CSV["brand"]].strip()
            price = row[HEADERS_CSV["price"]].strip()
            # EAN es opcional: solo si la columna existe en el CSV
            ean = ""
            if len(row) > HEADERS_CSV["ean"]:
                ean = row[HEADERS_CSV["ean"]].strip()
            if code and desc and code != "Código":
                products.append({
                    "code": code,
                    "description": desc,
                    "brand": brand,
                    "price": price,
                    "ean": ean,
                    "search_query": f"{desc} {brand}".strip(),
                })
    return products


def ean_valido(code: str) -> bool:
    """Valida EAN-8 / EAN-13 con dígito verificador (mismo criterio que el frontend)."""
    s = (code or "").strip()
    if not s.isdigit() or len(s) not in (8, 13):
        return False
    digits = [int(c) for c in s]
    check = digits.pop()
    empieza_en_3 = len(s) == 8
    suma = 0
    for i, d in enumerate(digits):
        if i % 2 == 0:
            peso = 3 if empieza_en_3 else 1
        else:
            peso = 1 if empieza_en_3 else 3
        suma += d * peso
    return (10 - (suma % 10)) % 10 == check


def _mejor_imagen(product: dict) -> Optional[str]:
    """Extrae la mejor URL de imagen de un objeto product de OFF."""
    # OFF ofrece varias resoluciones; preferimos la grande, luego la de display.
    for key in ("image_url", "image_front_url", "image_front_small_url"):
        url = product.get(key)
        if url:
            return url
    # Fallback: dentro de 'selected_images'
    sel = product.get("selected_images", {})
    front = sel.get("front", {})
    display = front.get("display", {})
    if display:
        # toma cualquier idioma disponible
        return next(iter(display.values()), None)
    return None


def search_off_by_ean(ean: str) -> Optional[str]:
    """Busca imagen en OFF por código de barras (preciso). Devuelve URL o None."""
    url = f"{OFF_BASE}/api/v2/product/{ean}.json"
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": OFF_USER_AGENT},
            params={"fields": "image_url,image_front_url,image_front_small_url,selected_images"},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get("status") == 1 and data.get("product"):
            return _mejor_imagen(data["product"])
        return None
    except Exception as e:
        print(f"  ⚠️ Error OFF por EAN '{ean}': {e}")
        return None


def search_off_by_name(query: str) -> Optional[str]:
    """Busca imagen en OFF por nombre (más cobertura, menos precisión)."""
    url = f"{OFF_BASE}/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5,
        "fields": "product_name,brands,image_url,image_front_url,image_front_small_url,selected_images",
    }
    try:
        resp = requests.get(url, headers={"User-Agent": OFF_USER_AGENT},
                            params=params, timeout=30)
        if resp.status_code != 200:
            return None
        data = resp.json()
        for product in data.get("products", []):
            img = _mejor_imagen(product)
            if img:
                return img
        return None
    except Exception as e:
        print(f"  ⚠️ Error OFF por nombre '{query}': {e}")
        return None


def download_image(url: str, dest_path: Path) -> bool:
    """Descarga una imagen a disco."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": OFF_USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as response:
            dest_path.write_bytes(response.read())
        return True
    except Exception as e:
        print(f"  ⚠️ Error descargando imagen: {e}")
        return False


def upload_to_supabase(local_path: Path, remote_name: str) -> Optional[str]:
    """Sube una imagen a Supabase Storage. Devuelve la public URL o None."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError("Faltan credenciales de Supabase")

    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{remote_name}"
    # OFF sirve imágenes jpg/png; usamos content-type genérico de imagen.
    ext = local_path.suffix.lower()
    content_type = "image/png" if ext == ".png" else "image/jpeg"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    try:
        with open(local_path, "rb") as f:
            resp = requests.post(url, headers=headers, data=f, timeout=60)
        if resp.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{remote_name}"
        print(f"  ⚠️ Supabase upload error {resp.status_code}: {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  ⚠️ Error subiendo a Supabase: {e}")
        return None


def process_products(products, output_json, download_dir="./imagenes_off",
                     limit=None, delay=1.0, upload=False):
    """Busca imagen (EAN→nombre), descarga y opcionalmente sube. Deja JSON para revisar."""
    download_path = Path(download_dir)
    download_path.mkdir(parents=True, exist_ok=True)

    results = []
    total = len(products) if limit is None else min(limit, len(products))
    n_ean, n_nombre, n_sin = 0, 0, 0

    for i, prod in enumerate(products[:total], 1):
        print(f"[{i}/{total}] {prod['description']} ({prod['brand']})")

        img_url = None
        fuente = None

        # 1) Cascada: EAN primero (si es válido), luego nombre
        ean = prod.get("ean", "")
        if ean and ean_valido(ean):
            img_url = search_off_by_ean(ean)
            if img_url:
                fuente = "ean"
                n_ean += 1
        if not img_url:
            img_url = search_off_by_name(prod["search_query"])
            if img_url:
                fuente = "nombre"
                n_nombre += 1

        if not img_url:
            n_sin += 1
            print("  ∅ Sin imagen en Open Food Facts")
            results.append({**prod, "fuente": None, "image_url": None,
                            "local_path": None, "supabase_url": None})
            time.sleep(delay)
            continue

        print(f"  ✅ Encontrada por {fuente}")

        # 2) Descargar
        safe_brand = (prod["brand"] or "sinmarca").replace(" ", "_").lower()
        safe_name = f"off_{prod['code']}_{safe_brand}.jpg"
        local_file = download_path / safe_name
        if not download_image(img_url, local_file):
            local_file = None

        # 3) Subir al bucket (opcional). NO toca la tabla producto.
        supabase_url = None
        if upload and local_file:
            supabase_url = upload_to_supabase(local_file, safe_name)
            if supabase_url:
                print(f"  ☁️ Subida: {supabase_url}")

        results.append({
            **prod,
            "fuente": fuente,
            "image_url": img_url,
            "local_path": str(local_file) if local_file else None,
            "supabase_url": supabase_url,
        })
        time.sleep(delay)  # cortesía con la API de OFF

    # Guardar JSON de revisión
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    con_img = sum(1 for r in results if r["image_url"])
    print(f"\n🎉 Listo. Resultados en {output_json}")
    print(f"   Productos procesados : {len(results)}")
    print(f"   Con imagen (total)   : {con_img}  ({con_img*100//max(len(results),1)}%)")
    print(f"     · por EAN          : {n_ean}")
    print(f"     · por nombre       : {n_nombre}")
    print(f"   Sin imagen           : {n_sin}")
    if upload:
        print(f"   Subidas al bucket    : {sum(1 for r in results if r['supabase_url'])}")
    print("\n👉 Revisá el JSON y las imágenes descargadas ANTES de asignarlas a productos.")


def main():
    parser = argparse.ArgumentParser(description="Busca imágenes en Open Food Facts para productos de un CSV")
    parser.add_argument("--csv", required=True, help="Ruta al CSV de productos")
    parser.add_argument("--output", default="resultados_off.json", help="JSON de salida")
    parser.add_argument("--download-dir", default="./imagenes_off", help="Carpeta de descarga")
    parser.add_argument("--limit", type=int, default=None, help="Limitar cantidad (para probar)")
    parser.add_argument("--delay", type=float, default=1.0, help="Segundos entre búsquedas")
    parser.add_argument("--upload", action="store_true", help="Subir imágenes al bucket de Supabase")
    args = parser.parse_args()

    print("📖 Leyendo CSV...")
    products = parse_csv(args.csv)
    print(f"   {len(products)} productos encontrados\n")

    process_products(
        products,
        output_json=args.output,
        download_dir=args.download_dir,
        limit=args.limit,
        delay=args.delay,
        upload=args.upload,
    )


if __name__ == "__main__":
    main()