"""
Agente de ingesta de precios desde imagenes (flyers de estados y grupos de WhatsApp).

Flujo:
  1. POST /api/v1/ingesta/imagenes   -> sube la imagen, la lee con un modelo de vision
                                        y guarda PROPUESTAS en ingesta_propuestas.
  2. GET  /api/v1/ingesta/propuestas -> cola de revision (admin).
  3. POST /api/v1/ingesta/propuestas/{id}/aprobar  -> recien aca se escribe en
                                        producto / historial_precios / ofertas.
  4. POST /api/v1/ingesta/propuestas/{id}/rechazar

Nada se carga en la app sin aprobacion de un admin.

Variables de entorno (Render y .env local):
  INGESTA_PROVEEDOR   gemini | claude          (default: gemini)
  GEMINI_API_KEY      clave de Google AI Studio (si proveedor = gemini)
  ANTHROPIC_API_KEY   clave de console.anthropic.com (si proveedor = claude)
  INGESTA_MODELO      opcional: id del modelo (default segun proveedor)
"""

import base64
import json
import os
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import List, Optional

import requests
from fastapi import APIRouter, Body, File, Form, Header, HTTPException, Query, UploadFile
from pydantic import BaseModel

from database_manager import DatabaseManager

router = APIRouter(prefix="/api/v1/ingesta", tags=["Ingesta"])

BUCKET = "product-images"
MAX_IMAGENES_POR_ENVIO = 6
LADO_MAX_IMAGEN = 1600          # mas grande que las fotos de producto: los flyers tienen letra chica
UMBRAL_COMERCIO = 0.6           # similitud minima para asignar comercio solo
MARGEN_COMERCIO = 0.3           # y diferencia minima con el segundo candidato
UMBRAL_PRODUCTO = 0.6           # similitud minima para proponer "actualizar" en vez de "crear"
RANGO_PRECIO = (0.5, 1.6)       # precio leido / precio actual: fuera de este rango no se asocia solo
DIAS_OFERTA_DEFAULT = 7

UNIDADES_VALIDAS = ["Kilogramo", "Gramos", "Litro", "Mililitro", "Unidad", "Docena", "Paquete", "Caja"]

# Variantes que puede devolver el modelo -> vocabulario de cate_medida
_MAPA_UNIDADES = {
    "kg": "Kilogramo", "kgs": "Kilogramo", "kilo": "Kilogramo", "kilos": "Kilogramo", "kilogramo": "Kilogramo",
    "kilogramos": "Kilogramo",
    "g": "Gramos", "gr": "Gramos", "grs": "Gramos", "gramo": "Gramos", "gramos": "Gramos",
    "l": "Litro", "lt": "Litro", "lts": "Litro", "litro": "Litro", "litros": "Litro",
    "ml": "Mililitro", "cc": "Mililitro", "cm3": "Mililitro", "mililitro": "Mililitro", "mililitros": "Mililitro",
    "u": "Unidad", "un": "Unidad", "unidad": "Unidad", "unidades": "Unidad", "c/u": "Unidad",
    "docena": "Docena", "doc": "Docena", "docenas": "Docena",
    "paquete": "Paquete", "pack": "Paquete", "paquetes": "Paquete",
    "caja": "Caja", "cajas": "Caja",
}

_ABREV = {"Kilogramo": "kg", "Gramos": "g", "Litro": "L", "Mililitro": "ml",
          "Unidad": "u", "Docena": "doc", "Paquete": "paq", "Caja": "caja"}

PROMPT_EXTRACCION = """Sos un extractor de precios de flyers de comercios de barrio de General Alvear (Mendoza, Argentina).
Recibis UNA imagen (flyer, estado de WhatsApp o lista de precios) y devolves SOLO un JSON, sin texto extra, con esta forma:

{
  "comercio": "nombre del comercio tal como aparece en la imagen, o null si no aparece",
  "productos": [
    {
      "nombre": "nombre generico y corto en Title Case, sin marca ni cantidad (ej: Mandarina, Asado, Leche Entera)",
      "marca": "marca si aparece, o null",
      "cantidad": numero,
      "unidad": "Kilogramo | Gramos | Litro | Mililitro | Unidad | Docena | Paquete | Caja",
      "precio_total": numero,
      "precio_anterior": numero o null,
      "tipo": "precio | promo_cantidad | oferta",
      "texto_original": "el texto del flyer de donde sale este precio",
      "confianza": "alta | media | baja"
    }
  ]
}

Reglas:
- Formato de numeros argentino: el punto separa miles y la coma decimales. "$3.500" = 3500. "$1.250,50" = 1250.5.
- cantidad y unidad describen a que corresponde precio_total: "2 kilos de mandarina $3.500" -> cantidad 2, unidad Kilogramo, precio_total 3500. "Asado $8.500 el kg" -> cantidad 1, Kilogramo, 8500. "Yerba 500 g $2.100" -> cantidad 500, Gramos. "3 x $1.000" -> cantidad 3, Unidad, 1000. Si no se indica, cantidad 1 y unidad Unidad.
- Tamano: si el contenido (500 g, 1,5 L, 900 cc) se lee en el texto o en la etiqueta del envase, usalo. Si no se ve, NO lo supongas: cantidad 1 y unidad Unidad.
- Pack vs promo: "x3", "x 3", "x12" pegado al nombre o impreso en el envase es la PRESENTACION (un pack que se vende entero): cantidad 1, unidad Paquete, y agrega "x3" al final del nombre. Ej: "La Providencia x3 $1.590" -> nombre "Galletitas x3", marca "La Providencia", cantidad 1, Paquete, 1590. Solo es promo_cantidad si el texto dice que hay que llevar varios: "3 x $...", "3 por $...", "llevando 3", "2x1".
- Imagenes repetidas: si el producto aparece en 2 o mas fotos iguales pero ningun texto indica cantidad, es decoracion: el precio es por 1 unidad, confianza "media" y agrega al final de texto_original "(se ven N unidades en la imagen)".
- Unidades: kg/kilo -> Kilogramo; g/gr/grs -> Gramos; L/lt -> Litro; ml/cc -> Mililitro; c/u -> Unidad; doc -> Docena; pack -> Paquete.
- tipo: "promo_cantidad" si el precio es por llevar una cantidad mayor a 1 (2 kg x $..., 3 x $..., llevando 2...). "oferta" si dice oferta/promo/descuento/precio especial (en el producto o como titulo del flyer). "precio" en cualquier otro caso.
- precio_anterior: solo si hay un precio tachado o "antes $...". Si no, null.
- comercio: sale del logo o del nombre impreso en el flyer. En capturas de estados de WhatsApp, el nombre que aparece arriba junto a la foto de perfil es el contacto, NO el comercio.
- Una entrada por cada producto con precio. Ignora productos sin precio, telefonos, direcciones y horarios.
- No inventes nada. Si un precio o nombre no se lee con claridad, igual incluilo pero con confianza "baja".
- Si la imagen no tiene precios, devolve "productos": [].
"""


# ---------------------------------------------------------------------------
# Autenticacion (solo admin)
# ---------------------------------------------------------------------------

from supabase import create_client

_SB_SERVICIO = None


def _sb_servicio():
    """Cliente Supabase propio del router, SIEMPRE con service role.
    No usa DatabaseManager._shared_supabase: si otro endpoint inicia sesion
    de un usuario en ese cliente compartido, storage y tablas pasan a usar
    el JWT del usuario y RLS rechaza (403 'violates row-level security')."""
    global _SB_SERVICIO
    if _SB_SERVICIO is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise HTTPException(status_code=500, detail="Faltan SUPABASE_URL / SUPABASE_SERVICE_KEY")
        _SB_SERVICIO = create_client(url, key)
    return _SB_SERVICIO

def _db_admin(authorization: Optional[str]) -> DatabaseManager:
    """Valida el token Bearer y exige rol admin. Devuelve un DatabaseManager con current_user admin."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    db = DatabaseManager()
    db.supabase = _sb_servicio()  # cliente limpio con service role (ver _sb_servicio)
    token = authorization[len("Bearer "):]
    try:
        auth = db.supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")
    if not auth or not auth.user:
        raise HTTPException(status_code=401, detail="Token invalido")

    campos = "id_user, rol_user, activo_user"
    res = db.supabase.table("users").select(campos).eq("id_user", auth.user.id).limit(1).execute()
    if not res.data and auth.user.email:
        res = db.supabase.table("users").select(campos).eq("email_user", auth.user.email).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=403, detail="Usuario sin registro")
    fila = res.data[0]
    if fila.get("activo_user") is False or fila.get("rol_user") != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")

    db.set_current_user({"id": fila["id_user"], "rol_user": "admin"})
    return db


# ---------------------------------------------------------------------------
# Imagen
# ---------------------------------------------------------------------------

def _optimizar_imagen(contenido: bytes) -> bytes:
    """Rota segun EXIF, aplana transparencia y reduce a LADO_MAX_IMAGEN en JPEG."""
    from PIL import Image, ImageOps
    img = Image.open(BytesIO(contenido))
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "P", "LA"):
        rgba = img.convert("RGBA")
        fondo = Image.new("RGB", rgba.size, (255, 255, 255))
        fondo.paste(rgba, mask=rgba.split()[-1])
        img = fondo
    else:
        img = img.convert("RGB")
    img.thumbnail((LADO_MAX_IMAGEN, LADO_MAX_IMAGEN), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Modelo de vision (aislado: cambiar de proveedor = cambiar una variable de entorno)
# ---------------------------------------------------------------------------

def _extraer_json(texto: str) -> dict:
    """Saca el primer objeto JSON del texto (tolera ```json ... ``` alrededor)."""
    texto = (texto or "").strip()
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto)
    ini, fin = texto.find("{"), texto.rfind("}")
    if ini == -1 or fin == -1:
        raise ValueError("El modelo no devolvio JSON")
    return json.loads(texto[ini:fin + 1])


def _leer_imagen_con_modelo(jpeg: bytes) -> dict:
    proveedor = os.getenv("INGESTA_PROVEEDOR", "gemini").strip().lower()
    b64 = base64.b64encode(jpeg).decode("ascii")

    if proveedor == "claude":
        clave = os.getenv("ANTHROPIC_API_KEY")
        if not clave:
            raise RuntimeError("Falta ANTHROPIC_API_KEY")
        modelo = os.getenv("INGESTA_MODELO") or "claude-haiku-5-5"
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": clave, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={
                "model": modelo,
                "max_tokens": 3000,
                "temperature": 0,
                "system": PROMPT_EXTRACCION,
                "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                    {"type": "text", "text": "Extrae los productos y precios de esta imagen. Responde solo con el JSON."},
                ]}],
            },
            timeout=90,
        )
        if r.status_code != 200:
            raise RuntimeError(f"Claude {r.status_code}: {r.text[:300]}")
        bloques = r.json().get("content", [])
        return _extraer_json("".join(b.get("text", "") for b in bloques if b.get("type") == "text"))

    if proveedor == "gemini":
        clave = os.getenv("GEMINI_API_KEY")
        if not clave:
            raise RuntimeError("Falta GEMINI_API_KEY")
        # INGESTA_MODELO acepta varios separados por coma: se prueban en orden
        modelos = [m.strip() for m in (os.getenv("INGESTA_MODELO") or "gemini-3.6-flash").split(",") if m.strip()]
        cuerpo = {
            "contents": [{"parts": [
                {"text": PROMPT_EXTRACCION},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
            ]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
        }
        errores = []
        for modelo in modelos:
            for espera in (0, 5, 15):          # 3 intentos por modelo ante saturacion
                if espera:
                    time.sleep(espera)
                try:
                    r = requests.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
                        headers={"x-goog-api-key": clave, "content-type": "application/json"},
                        json=cuerpo,
                        timeout=60,
                    )
                except requests.exceptions.RequestException as e:
                    errores.append(f"{modelo}: {type(e).__name__}")
                    break                       # timeout / red: pasar al siguiente modelo
                if r.status_code == 200:
                    partes = (r.json().get("candidates") or [{}])[0].get("content", {}).get("parts", [])
                    return _extraer_json("".join(p.get("text", "") for p in partes if not p.get("thought")))
                errores.append(f"{modelo} {r.status_code}")
                if r.status_code not in (429, 500, 503):
                    break                       # 404 u otro error: no tiene sentido reintentar ese modelo
        raise RuntimeError("Gemini sin respuesta: " + "; ".join(errores))

    raise RuntimeError(f"INGESTA_PROVEEDOR desconocido: {proveedor}")


# ---------------------------------------------------------------------------
# Normalizacion (funciones puras, sin base de datos)
# ---------------------------------------------------------------------------

def _num(valor) -> Optional[float]:
    """Acepta 3500, "3500", "$3.500", "1.250,50"."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    s = re.sub(r"[^\d,.\-]", "", str(valor))
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def _normalizar_unidad(u: Optional[str]) -> str:
    if not u:
        return "Unidad"
    u = str(u).strip()
    if u in UNIDADES_VALIDAS:
        return u
    return _MAPA_UNIDADES.get(u.lower().rstrip("."), "Unidad")


def _fmt_ar(n: float) -> str:
    """3500 -> '3.500'; 1250.5 -> '1.250,50'."""
    if abs(n - round(n)) < 0.005:
        return f"{int(round(n)):,}".replace(",", ".")
    return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _precio_unitario(precio_total: float, cantidad: float, unidad: str) -> float:
    """Precio por kg, por L o por unidad, para comparar entre comercios."""
    if unidad in ("Gramos", "Mililitro"):
        return round(precio_total / (cantidad / 1000), 2)
    return round(precio_total / cantidad, 2)


def _campos_producto(cantidad: float, unidad: str, precio_total: float, tipo: str) -> dict:
    """
    Convierte lo leido del flyer en cantidad_prod (smallint), unidad_prod y precio_prod.
    - Promo por cantidad en kg/L/u/docena: se guarda por 1 unidad ("2 kg x $3.500" -> 1 kg $1.750).
    - Cantidades fraccionarias: kg -> g y L -> ml (1,5 kg -> 1500 g).
    """
    if tipo == "promo_cantidad" and unidad in ("Kilogramo", "Litro", "Unidad", "Docena") and cantidad != 1:
        return {"cantidad_prod": 1, "unidad_prod": unidad, "precio_prod": round(precio_total / cantidad, 2)}
    if abs(cantidad - round(cantidad)) > 1e-9:
        if unidad == "Kilogramo":
            unidad, cantidad = "Gramos", cantidad * 1000
        elif unidad == "Litro":
            unidad, cantidad = "Mililitro", cantidad * 1000
    cant = int(round(cantidad))
    cant = max(1, min(cant, 32767))
    return {"cantidad_prod": cant, "unidad_prod": unidad, "precio_prod": round(precio_total, 2)}


def _normalizar_item(item: dict) -> Optional[dict]:
    """Limpia un producto devuelto por el modelo. None si no sirve (sin nombre o sin precio)."""
    nombre = (item.get("nombre") or "").strip()
    precio = _num(item.get("precio_total"))
    if not nombre or not precio or precio <= 0:
        return None
    cantidad = _num(item.get("cantidad")) or 1.0
    if cantidad <= 0:
        cantidad = 1.0
    unidad = _normalizar_unidad(item.get("unidad"))
    tipo = item.get("tipo") if item.get("tipo") in ("precio", "promo_cantidad", "oferta") else "precio"
    if tipo == "promo_cantidad" and cantidad == 1:
        tipo = "oferta"
    confianza = item.get("confianza") if item.get("confianza") in ("alta", "media", "baja") else "media"
    condicion = None
    if tipo == "promo_cantidad":
        condicion = f"{_fmt_ar(cantidad)} {_ABREV[unidad]} x ${_fmt_ar(precio)}"
    return {
        "nombre_leido": nombre[:120],
        "marca_leida": (item.get("marca") or None),
        "cantidad": cantidad,
        "unidad": unidad,
        "precio_total": precio,
        "precio_unitario": _precio_unitario(precio, cantidad, unidad),
        "precio_anterior_leido": _num(item.get("precio_anterior")),
        "tipo": tipo,
        "condicion_oferta": condicion,
        "texto_original": (item.get("texto_original") or None),
        "confianza": confianza,
    }


# ---------------------------------------------------------------------------
# Emparejamiento (funciones SQL buscar_comercio_similar / buscar_producto_similar)
# ---------------------------------------------------------------------------

def _resolver_comercio(db: DatabaseManager, comercio_leido: Optional[str]) -> Optional[dict]:
    if not comercio_leido:
        return None
    res = db.supabase.rpc("buscar_comercio_similar", {"p_texto": comercio_leido}).execute()
    cands = res.data or []
    if not cands:
        return None
    mejor = cands[0]
    segundo = cands[1]["similitud"] if len(cands) > 1 else 0
    if mejor["similitud"] >= UMBRAL_COMERCIO and mejor["similitud"] - segundo >= MARGEN_COMERCIO:
        return mejor
    return None


def _comercio_por_id(db: DatabaseManager, id_comer: str) -> Optional[dict]:
    res = db.supabase.table("comercio").select("id_comer, nombre_comer").eq("id_comer", id_comer).limit(1).execute()
    return res.data[0] if res.data else None


def _precio_compatible(precio_actual, precio_nuevo) -> bool:
    """Evita asociar productos distintos (ej. lavandina comun vs gel 700cc) por un nombre parecido."""
    try:
        a, n = float(precio_actual or 0), float(precio_nuevo or 0)
    except (TypeError, ValueError):
        return False
    if a <= 0 or n <= 0:
        return False
    return RANGO_PRECIO[0] <= n / a <= RANGO_PRECIO[1]


def _candidatos_producto(db: DatabaseManager, nombre_comer: str, nombre: str) -> list:
    res = db.supabase.rpc("buscar_producto_similar",
                          {"p_comercio": nombre_comer, "p_texto": nombre, "p_limite": 3}).execute()
    return [{
        "id_prod": c["id_prod"], "nombre_prod": c["nombre_prod"], "marca_prod": c.get("marca_prod"),
        "unidad_prod": c.get("unidad_prod"), "cantidad_prod": c.get("cantidad_prod"),
        "precio_prod": c.get("precio_prod"), "similitud": round(float(c["similitud"]), 3),
    } for c in (res.data or [])]


# ---------------------------------------------------------------------------
# 1. Subir imagenes -> propuestas
# ---------------------------------------------------------------------------

@router.post("/imagenes")
async def ingestar_imagenes(
    files: List[UploadFile] = File(...),
    origen: str = Form("compartir"),
    id_comer: Optional[str] = Form(None),   # opcional: si ya sabes de que comercio es (ej. su estado)
    authorization: Optional[str] = Header(None),
):
    db = _db_admin(authorization)
    if len(files) > MAX_IMAGENES_POR_ENVIO:
        raise HTTPException(status_code=400, detail=f"Maximo {MAX_IMAGENES_POR_ENVIO} imagenes por envio")
    if origen not in ("compartir", "estado", "grupo", "bot"):
        origen = "compartir"

    comercio_fijo = None
    if id_comer:
        comercio_fijo = _comercio_por_id(db, id_comer)
        if not comercio_fijo:
            raise HTTPException(status_code=400, detail="id_comer no existe")

    resultados = []
    for f in files:
        lote_id = str(uuid.uuid4())
        try:
            jpeg = _optimizar_imagen(await f.read())
        except Exception as e:
            resultados.append({"archivo": f.filename, "ok": False, "error": f"Imagen invalida: {e}"})
            continue

        ruta = f"ingesta/{lote_id}.jpg"
        try:
            db.supabase.storage.from_(BUCKET).upload(ruta, jpeg, {"content-type": "image/jpeg"})
            imagen_url = db.supabase.storage.from_(BUCKET).get_public_url(ruta)
        except Exception as e:
            resultados.append({"archivo": f.filename, "ok": False, "error": f"No se pudo subir: {e}"})
            continue

        try:
            leido = _leer_imagen_con_modelo(jpeg)
        except Exception as e:
            resultados.append({"archivo": f.filename, "ok": False, "imagen_url": imagen_url,
                               "error": f"Lectura fallida: {e}"})
            continue

        comercio_leido = (leido.get("comercio") or None)
        comercio = comercio_fijo or _resolver_comercio(db, comercio_leido)

        filas = []
        for item in leido.get("productos") or []:
            norm = _normalizar_item(item)
            if not norm:
                continue
            fila = {
                "lote_id": lote_id, "imagen_url": imagen_url, "origen": origen,
                "comercio_leido": comercio_leido,
                "id_comer": comercio["id_comer"] if comercio else None,
                **norm,
            }
            if norm["tipo"] != "precio":
                fila["fecha_fin_oferta"] = (datetime.now(timezone.utc) + timedelta(days=DIAS_OFERTA_DEFAULT)).isoformat()

            if comercio:
                cands = _candidatos_producto(db, comercio["nombre_comer"], norm["nombre_leido"])
                fila["candidatos"] = cands
                if (cands and cands[0]["similitud"] >= UMBRAL_PRODUCTO
                        and _precio_compatible(cands[0].get("precio_prod"), norm["precio_total"])):
                    fila["accion"] = "actualizar"
                    fila["id_prod_sugerido"] = cands[0]["id_prod"]
                else:
                    fila["accion"] = "crear"
            else:
                fila["candidatos"] = []
                fila["accion"] = "crear_comercio" if comercio_leido else "crear"
            filas.append(fila)

        if filas:
            db.supabase.table("ingesta_propuestas").insert(filas).execute()

        resultados.append({
            "archivo": f.filename, "ok": True, "lote_id": lote_id, "imagen_url": imagen_url,
            "comercio_leido": comercio_leido,
            "comercio_asignado": comercio["nombre_comer"] if comercio else None,
            "propuestas": len(filas),
        })

    return {"resultados": resultados}


# ---------------------------------------------------------------------------
# 2. Cola de revision
# ---------------------------------------------------------------------------

@router.get("/propuestas")
def listar_propuestas(
    estado: str = Query("pendiente"),
    limit: int = Query(200, le=500),
    authorization: Optional[str] = Header(None),
):
    db = _db_admin(authorization)
    res = db.supabase.table("ingesta_propuestas").select("*")\
        .eq("estado", estado).order("creado_en", desc=True).limit(limit).execute()
    return {"propuestas": res.data or []}


# ---------------------------------------------------------------------------
# 3. Aprobar (unico punto que escribe en producto / historial / ofertas)
# ---------------------------------------------------------------------------

class AprobarBody(BaseModel):
    accion: Optional[str] = None          # actualizar | crear (pisa la sugerida)
    id_prod: Optional[str] = None         # para actualizar
    id_comer: Optional[str] = None        # obligatorio si la propuesta no tiene comercio
    nombre: Optional[str] = None
    marca: Optional[str] = None
    cantidad: Optional[float] = None
    unidad: Optional[str] = None
    precio_total: Optional[float] = None
    tipo: Optional[str] = None            # precio | promo_cantidad | oferta
    dias_oferta: int = DIAS_OFERTA_DEFAULT


def _cargar_propuesta(db: DatabaseManager, propuesta_id: str) -> dict:
    res = db.supabase.table("ingesta_propuestas").select("*").eq("id", propuesta_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    prop = res.data[0]
    if prop["estado"] != "pendiente":
        raise HTTPException(status_code=409, detail=f"La propuesta ya esta {prop['estado']}")
    return prop


def _crear_oferta(db: DatabaseManager, id_prod: str, precio_normal: float, precio_oferta: float,
                  dias: int, condicion: Optional[str]) -> None:
    ahora = datetime.now(timezone.utc)
    db.supabase.table("ofertas").insert({
        "id_prod": id_prod,
        "precio_normal": float(precio_normal),
        "precio_oferta": float(precio_oferta),
        "fecha_inicio": ahora.isoformat(),
        "fecha_fin": (ahora + timedelta(days=max(1, dias))).isoformat(),
        "activa": True,
        "creada_por": db.current_user.get("id"),
        "condicion_oferta": condicion,
    }).execute()


@router.post("/propuestas/{propuesta_id}/aprobar")
def aprobar_propuesta(
    propuesta_id: str,
    body: AprobarBody = Body(default_factory=AprobarBody),
    authorization: Optional[str] = Header(None),
):
    db = _db_admin(authorization)
    prop = _cargar_propuesta(db, propuesta_id)

    # Correcciones del admin sobre lo que leyo el modelo
    nombre = (body.nombre or prop["nombre_leido"]).strip()
    marca = body.marca if body.marca is not None else prop.get("marca_leida")
    cantidad = body.cantidad or float(prop.get("cantidad") or 1)
    unidad = _normalizar_unidad(body.unidad or prop.get("unidad"))
    precio_total = body.precio_total or float(prop["precio_total"])
    tipo = body.tipo or prop["tipo"]
    accion = body.accion or prop.get("accion")
    id_comer = body.id_comer or prop.get("id_comer")

    if accion not in ("actualizar", "crear"):
        raise HTTPException(status_code=400, detail="Elegi accion 'actualizar' o 'crear' (y el comercio si falta)")
    if not id_comer:
        raise HTTPException(status_code=400, detail="Falta el comercio (id_comer)")
    comercio = _comercio_por_id(db, id_comer)
    if not comercio:
        raise HTTPException(status_code=400, detail="id_comer no existe")
    nombre_comer = comercio["nombre_comer"]

    campos = _campos_producto(cantidad, unidad, precio_total, tipo)
    precio_nuevo = campos["precio_prod"]
    condicion = None
    if tipo == "promo_cantidad":
        condicion = f"{_fmt_ar(cantidad)} {_ABREV[unidad]} x ${_fmt_ar(precio_total)}"
    es_promo = tipo in ("promo_cantidad", "oferta")
    detalle = []

    if accion == "actualizar":
        id_prod = body.id_prod or prop.get("id_prod_sugerido")
        if not id_prod:
            raise HTTPException(status_code=400, detail="Falta id_prod a actualizar")
        res = db.supabase.table("producto").select("id_prod, comercio_prod, precio_prod")\
            .eq("id_prod", id_prod).limit(1).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        actual = res.data[0]
        if actual["comercio_prod"] != nombre_comer:
            raise HTTPException(status_code=400, detail="El producto no pertenece a ese comercio")
        precio_actual = float(actual["precio_prod"] or 0)

        if es_promo and precio_actual > precio_nuevo:
            # Promo vigente: NO se pisa el precio normal; se crea la oferta (vence sola).
            _crear_oferta(db, id_prod, precio_actual, precio_nuevo, body.dias_oferta, condicion)
            detalle.append(f"Oferta creada: ${_fmt_ar(precio_actual)} -> ${_fmt_ar(precio_nuevo)}")
        else:
            ok, msg = db.update_product(id_prod, {"precio_prod": precio_nuevo})
            if not ok:
                raise HTTPException(status_code=400, detail=msg)
            if abs(precio_actual - precio_nuevo) < 0.005:
                detalle.append(f"Precio confirmado: ${_fmt_ar(precio_nuevo)} (se actualiza la fecha)")
            else:
                detalle.append(f"Precio actualizado: ${_fmt_ar(precio_actual)} -> ${_fmt_ar(precio_nuevo)}")

    else:  # crear
        anterior = prop.get("precio_anterior_leido")
        precio_base = float(anterior) if (es_promo and anterior and float(anterior) > precio_nuevo) else precio_nuevo
        datos = {
            "nombre_prod": nombre, "marca_prod": marca, "comercio_prod": nombre_comer,
            "precio_prod": precio_base, "cantidad_prod": campos["cantidad_prod"],
            "unidad_prod": campos["unidad_prod"], "activo_prod": True,
        }
        if prop.get("imagen_url"):
            datos["describe_prod"] = f"Cargado desde flyer ({prop['origen']})"
        ok, msg = db.create_product(datos)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        # create_product no devuelve el id: se busca el recien creado
        res = db.supabase.table("producto").select("id_prod")\
            .eq("comercio_prod", nombre_comer).eq("nombre_prod", nombre)\
            .order("fecha_prod", desc=True).limit(1).execute()
        id_prod = res.data[0]["id_prod"] if res.data else None
        detalle.append(f"Producto creado: {nombre} ${_fmt_ar(precio_base)}")
        if id_prod and precio_base > precio_nuevo:
            _crear_oferta(db, id_prod, precio_base, precio_nuevo, body.dias_oferta, condicion)
            detalle.append(f"Oferta creada: ${_fmt_ar(precio_base)} -> ${_fmt_ar(precio_nuevo)}")

    db.supabase.table("ingesta_propuestas").update({
        "estado": "aprobada",
        "accion": accion,
        "id_comer": id_comer,
        "id_prod_sugerido": id_prod,
        "revisado_por": db.current_user.get("id"),
        "revisado_en": datetime.now(timezone.utc).isoformat(),
    }).eq("id", propuesta_id).execute()

    return {"ok": True, "id_prod": id_prod, "detalle": detalle}


@router.post("/propuestas/{propuesta_id}/rechazar")
def rechazar_propuesta(propuesta_id: str, authorization: Optional[str] = Header(None)):
    db = _db_admin(authorization)
    _cargar_propuesta(db, propuesta_id)
    db.supabase.table("ingesta_propuestas").update({
        "estado": "rechazada",
        "revisado_por": db.current_user.get("id"),
        "revisado_en": datetime.now(timezone.utc).isoformat(),
    }).eq("id", propuesta_id).execute()
    return {"ok": True}
