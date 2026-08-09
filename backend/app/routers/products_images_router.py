"""
Router de imagenes de productos con fallback Pillow.
Ruta: backend/app/routers/products_images_router.py
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from typing import Optional
from io import BytesIO
import uuid
import requests
import re

from database_manager import DatabaseManager
from supabase_config import SupabaseConfig

router = APIRouter()


# ---------------------------------------------------
# Dependencias (autonomas para evitar import circular)
# ---------------------------------------------------

def get_db() -> DatabaseManager:
    return DatabaseManager()


def set_user_from_token(db: DatabaseManager, authorization: Optional[str]):
    """Extrae el token Bearer y establece el usuario actual en db."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            user = db.supabase.auth.get_user(token)
            if user and user.user:
                user_data = {
                    "id": user.user.id,
                    "user_metadata": user.user.user_metadata or {}
                }
                try:
                    user_res = db.supabase.table("users")\
                        .select("id_user, rol_user, id_comer, es_comercio_user, comercio_verificado_user, activo_user")\
                        .eq("id_user", user.user.id)\
                        .execute()
                    if not user_res.data and user.user.email:
                        user_res = db.supabase.table("users")\
                            .select("id_user, rol_user, id_comer, es_comercio_user, comercio_verificado_user, activo_user")\
                            .eq("email_user", user.user.email)\
                            .execute()
                    if user_res.data and len(user_res.data) > 0:
                        row = user_res.data[0]
                        if row.get("activo_user") is False:
                            return
                        user_data["id"] = row.get("id_user", user.user.id)
                        user_data["rol_user"] = row.get("rol_user", "usuario")
                        user_data["id_comer"] = row.get("id_comer")
                        user_data["es_comercio_user"] = row.get("es_comercio_user", False)
                        user_data["comercio_verificado_user"] = row.get("comercio_verificado_user", False)
                except Exception:
                    pass
                db.set_current_user(user_data)
        except Exception:
            pass


# ---------------------------------------------------
# Optimizacion de imagen con fallback ImportError
# ---------------------------------------------------

def _optimize_image(file_bytes: bytes) -> bytes:
    """
    Optimiza: EXIF transpose, aplana transparencia, thumbnail 800x800, JPEG 82%.
    Si Pillow no esta instalado (tu maquina local sin espacio), sube tal cual.
    """
    try:
        from PIL import Image, ImageOps
        img = Image.open(BytesIO(file_bytes))
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P", "LA"):
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            fondo.paste(rgba, mask=rgba.split()[-1])
            img = fondo
        else:
            img = img.convert("RGB")
        img.thumbnail((800, 800), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=82, optimize=True)
        return buf.getvalue()
    except ImportError:
        # Pillow no esta instalado (desarrollo local) — sube tal cual
        return file_bytes
    except Exception as e:
        print(f"⚠️ No se pudo optimizar la imagen, se sube el original: {e}")
        return file_bytes


# ---------------------------------------------------
# Endpoints
# ---------------------------------------------------

@router.post("/api/v1/products/{product_id}/imagen")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Sube imagen para un producto. Optimiza con Pillow si esta disponible.
    Guarda en Storage y propaga la URL a productos con mismo EAN/nombre.
    """
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    rol = db.get_user_role()
    if rol not in ("admin", "comercio"):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    if rol == "comercio" and not db.current_user.get("comercio_verificado_user"):
        raise HTTPException(status_code=403, detail="Tu comercio todavia no esta verificado")

    ext = (file.filename or "").split(".")[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        raise HTTPException(status_code=400, detail="Formato no soportado (usar jpg, png o webp)")

    try:
        contenido = await file.read()
        contenido_optimizado = _optimize_image(contenido)

        # Si se optimizo, siempre queda como JPEG
        if contenido_optimizado is not contenido:
            nombre_archivo = f"productos/{uuid.uuid4()}.jpg"
            content_type = "image/jpeg"
        else:
            nombre_archivo = f"productos/{uuid.uuid4()}.{ext}"
            content_type = file.content_type or "image/jpeg"

        db.supabase.storage.from_("product-images").upload(
            nombre_archivo,
            contenido_optimizado,
            {"content-type": content_type}
        )
        url_publica = db.supabase.storage.from_("product-images").get_public_url(nombre_archivo)

        # Propagar a productos con mismo EAN o nombre
        base = db.supabase.table("producto")\
            .select("id_prod, nombre_prod, ean_prod")\
            .eq("id_prod", product_id).limit(1).execute()
        if not base.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        prod = base.data[0]
        ean = (prod.get("ean_prod") or "").strip()
        nombre = prod.get("nombre_prod") or ""

        if ean and re.fullmatch(r"\d{12,13}", ean):
            db.supabase.table("producto").update({"imagen_prod": url_publica})\
                .eq("ean_prod", ean).eq("activo_prod", True).execute()
        else:
            db.supabase.table("producto").update({"imagen_prod": url_publica})\
                .ilike("nombre_prod", nombre).eq("activo_prod", True).execute()

        return {
            "message": "Imagen subida correctamente",
            "url": url_publica,
            "optimizada": contenido_optimizado is not contenido
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")


@router.delete("/api/v1/products/{product_id}/imagen")
def delete_product_image(
    product_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Limpia imagen_prod del producto (no borra el archivo de Storage)."""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    rol = db.get_user_role()
    if rol not in ("admin", "comercio"):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    if rol == "comercio" and not db.current_user.get("comercio_verificado_user"):
        raise HTTPException(status_code=403, detail="Tu comercio todavia no esta verificado")

    try:
        db.supabase.table("producto").update({"imagen_prod": None})\
            .eq("id_prod", product_id).execute()
        return {"message": "Imagen eliminada del producto"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/products/{product_id}/imagen/openfoodfacts")
def get_openfoodfacts_image(
    product_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Busca imagen del producto en Open Food Facts por EAN."""
    try:
        prod = db.supabase.table("producto")\
            .select("ean_prod, nombre_prod")\
            .eq("id_prod", product_id).limit(1).execute()
        if not prod.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        ean = (prod.data[0].get("ean_prod") or "").strip()
        if not ean or not re.fullmatch(r"\d{12,13}", ean):
            return {"encontrada": False, "motivo": "EAN no valido o no disponible"}

        url = f"https://world.openfoodfacts.org/api/v0/product/{ean}.json"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if data.get("status") != 1:
            return {"encontrada": False, "motivo": "Producto no encontrado en OFF"}

        image_url = data.get("product", {}).get("image_url") or data.get("product", {}).get("image_front_url")
        if not image_url:
            return {"encontrada": False, "motivo": "El producto existe pero no tiene imagen"}

        return {
            "encontrada": True,
            "ean": ean,
            "nombre": data.get("product", {}).get("product_name"),
            "image_url": image_url
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/products/{product_id}/imagen/status")
def get_image_status(
    product_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Devuelve si el producto tiene imagen y su URL."""
    try:
        prod = db.supabase.table("producto")\
            .select("imagen_prod, nombre_prod, ean_prod")\
            .eq("id_prod", product_id).limit(1).execute()
        if not prod.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        data = prod.data[0]
        return {
            "tiene_imagen": bool(data.get("imagen_prod")),
            "imagen_prod": data.get("imagen_prod"),
            "nombre_prod": data.get("nombre_prod"),
            "ean_prod": data.get("ean_prod")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))