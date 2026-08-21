"""
ComparApp - API Backend
Autor: Fernando Silva
Version: 1.1
Descripcion:
    API FastAPI que conecta con Supabase usando los modulos
    supabase_config.py y database_manager.py
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Header, Body, UploadFile, File, Form, Request
import uuid
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta
import time
from collections import defaultdict
import os

# Cargar variables del .env local (si existe).
# En producción (Render) no hay .env — las variables vienen del panel de Render.
# python-dotenv no sobreescribe variables que ya existen en el entorno del SO,
# así que esto es seguro de dejar siempre activo.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv no está instalado — no es crítico en producción

# Importar los modulos locales
from database_manager import DatabaseManager, LIMITE_PRODUCTOS_PLAN_FREE
from supabase_config import SupabaseConfig


# ---------------------------------------------------
# Modelos Pydantic
# ---------------------------------------------------

class ProductCreate(BaseModel):
    nombre_prod: str
    precio_prod: float
    cate_prod: Optional[str] = None
    describe_prod: Optional[str] = None
    unidad_prod: Optional[str] = None
    cantidad_prod: Optional[int] = None
    comercio_prod: Optional[str] = None
    marca_prod: Optional[str] = None
    imagen_prod: Optional[str] = None
    activo_prod: Optional[bool] = True
    cate_id: Optional[str] = None

class ProductResponse(BaseModel):
    success: bool
    message: str


# ---------------------------------------------------
# Inicializacion general
# ---------------------------------------------------

# En desarrollo (ENVIRONMENT=development en .env local), /docs y /redoc
# quedan accesibles para explorar la API con comodidad.
# En producción (Render no tiene esa variable), se deshabilitan — dejar
# el mapa completo de la API público es un riesgo de seguridad innecesario.
_env = os.getenv("ENVIRONMENT", "production").lower()
_is_dev = _env == "development"

app = FastAPI(
    title="ComparApp API",
    version="1.1.0",
    description="API de comparacion de precios conectada a Supabase",
    docs_url="/docs" if _is_dev else None,
    redoc_url="/redoc" if _is_dev else None,
    openapi_url="/openapi.json" if _is_dev else None,
)

# ---------------------------------------------------
# CORS — solo los orígenes reales del proyecto
# ---------------------------------------------------
# allow_origins=["*"] era demasiado permisivo: cualquier sitio web del
# mundo podía hacer peticiones a la API usando credenciales reales de
# un usuario. Ahora solo se aceptan los orígenes conocidos.
# Para no hardcodear la URL de Netlify (puede cambiar de plan/dominio),
# se usa validación dinámica: cualquier subdominio de netlify.app que
# contenga "compar" se considera legítimo (cubre deploy previews también).

_ALLOWED_ORIGINS_EXACT = {
    "https://compar-app.netlify.app",   # producción
    "http://localhost:3000",            # dev frontend local
    "http://localhost:8000",            # dev backend local (por si acaso)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
}

def _is_origin_allowed(origin: str) -> bool:
    if origin in _ALLOWED_ORIGINS_EXACT:
        return True
    # Cubre deploy previews de Netlify:
    # https://deploy-preview-123--compar-app.netlify.app
    if origin.endswith(".netlify.app") and "compar" in origin:
        return True
    # En desarrollo local, permitir cualquier localhost con cualquier puerto
    if _is_dev and (origin.startswith("http://localhost:") or origin.startswith("http://127.0.0.1:")):
        return True
    return False

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_ALLOWED_ORIGINS_EXACT),
    allow_origin_regex=r"https://[a-z0-9\-]+--compar-app\.netlify\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# ---------------------------------------------------
# Routers
# ---------------------------------------------------
from routers.products_images_router import router as images_router
app.include_router(images_router)


# Instancia usada solo para tareas de arranque/apagado del servidor
# (ver shutdown_event más abajo). NO se usa para atender requests —
# cada request recibe su propia instancia vía get_db(), justamente
# para que current_user nunca se comparta entre personas distintas.
db = DatabaseManager()

# ---------------------------------------------------
# Middleware de registro de peticiones
# ---------------------------------------------------

from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    print(f"🛰️  {request.method} {request.url.path}?{request.url.query} -> {response.status_code} ({process_time:.2f}ms)")
    return response

# ---------------------------------------------------
# Utilidades / dependencias
# ---------------------------------------------------

def get_db() -> DatabaseManager:
    # Una instancia NUEVA por request: cada una tiene su propio current_user,
    # así que dos personas usando la app al mismo tiempo nunca se pisan entre
    # sí. La conexión real a Supabase de abajo se sigue compartiendo (ver
    # DatabaseManager._shared_supabase), así que esto es liviano — no se
    # abre una conexión HTTP nueva en cada llamada.
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
                # Leer rol y datos de comercio desde tabla users
                try:
                    user_res = db.supabase.table("users")\
                        .select("id_user, rol_user, id_comer, es_comercio_user, comercio_verificado_user, activo_user")\
                        .eq("id_user", user.user.id)\
                        .execute()
                    # Fallback: si esta identidad de Auth (ej. Google) no tiene fila propia,
                    # puede que la persona ya tenga cuenta con otra identidad (ej. email/password)
                    # para el mismo email. Sin esto, cada login con un método distinto generaría
                    # un usuario "fantasma" o, peor, un error de email duplicado al intentar crearlo.
                    if not user_res.data and user.user.email:
                        user_res = db.supabase.table("users")\
                            .select("id_user, rol_user, id_comer, es_comercio_user, comercio_verificado_user, activo_user")\
                            .eq("email_user", user.user.email)\
                            .execute()
                    if user_res.data and len(user_res.data) > 0:
                        row = user_res.data[0]
                        # Cuenta desactivada por un admin → no se establece current_user.
                        # Todo endpoint que chequea "if not db.current_user: 401" lo bloquea acá,
                        # sin esto desactivar a alguien era puramente cosmético.
                        if row.get("activo_user") is False:
                            return
                        # Normalizar el id al de la fila real en 'users', no al de esta identidad de Auth
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
# Endpoint raiz
# ---------------------------------------------------

@app.get("/", tags=["General"])
def home():
    return {
        "status": "ok",
        "app": "ComparApp API",
        "version": "1.1.0",
        "supabase_url": SupabaseConfig.get_url(),
        "database_connected": db._test_connection_simple()
    }

# ---------------------------------------------------
# Endpoints de autenticacion
# ---------------------------------------------------

@app.post("/api/v1/forgot-password", tags=["Auth"])
def forgot_password(
    email: str = Body(...),
    db: DatabaseManager = Depends(get_db)
):
    db.reset_password_email(email)
    return {"message": "Si el email existe, recibiras un link para resetear tu contrasena."}


@app.post("/api/v1/change-password", tags=["Auth"])
async def change_password(
    password_actual: str = Body(...),
    password_nueva: str = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    if len(password_nueva) < 6:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres")
    if password_actual == password_nueva:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe ser distinta a la actual")

    try:
        # Obtener el email directamente del token (no de current_user, que no lo guarda)
        token = authorization.replace("Bearer ", "") if authorization else ""
        auth_user = db.supabase.auth.get_user(token)
        if not auth_user or not auth_user.user:
            raise HTTPException(status_code=401, detail="Token inválido. Cerrá sesión y volvé a entrar.")
        email_user = auth_user.user.email
        if not email_user:
            raise HTTPException(status_code=400, detail="Esta cuenta no tiene contraseña — usá Google para entrar.")

        # Verificar la contraseña actual con un sign_in real
        try:
            verificacion = db.supabase.auth.sign_in_with_password({
                "email": email_user,
                "password": password_actual
            })
            if not verificacion.user:
                raise HTTPException(status_code=401, detail="La contraseña actual es incorrecta")
        except Exception as e:
            err = str(e).lower()
            if "invalid" in err or "credentials" in err or "password" in err:
                raise HTTPException(status_code=401, detail="La contraseña actual es incorrecta")
            raise HTTPException(status_code=401, detail="No se pudo verificar tu contraseña actual")

        # Cambiar la contraseña — usamos el cliente con el token activo del usuario
        db.supabase.auth._headers = {**db.supabase.auth._headers, "Authorization": f"Bearer {token}"}
        db.supabase.auth.update_user({"password": password_nueva})

        return {"message": "Contraseña actualizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="No se pudo cambiar la contraseña. Intentá de nuevo.")



@app.post("/api/v1/register", tags=["Auth"])
async def register_user(
    email: str = Form(...),
    password: str = Form(...),
    nombre_completo: str = Form(...),
    telefono: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    db: DatabaseManager = Depends(get_db)
):
    avatar_bytes = None
    avatar_ext = None
    if avatar is not None and avatar.filename:
        avatar_ext = avatar.filename.split(".")[-1].lower()
        if avatar_ext not in ("jpg", "jpeg", "png", "webp"):
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado (usar jpg, png o webp)")
        avatar_bytes = await avatar.read()

    success, msg, user_data = db.register_user(email, password, nombre_completo, telefono, avatar_bytes, avatar_ext)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "user": user_data}

# ---------------------------------------------------
# Rate limiting para /login
# ---------------------------------------------------
# Estructura: { ip: [(timestamp, exitoso), ...] }
# Solo contamos intentos FALLIDOS. Un login exitoso no consume el límite.
# Máximo: 5 intentos fallidos por IP en una ventana de 15 minutos.
# Si se supera, el siguiente intento devuelve 429 con cuántos segundos faltan.

_login_attempts: dict = defaultdict(list)
_LOGIN_MAX_INTENTOS = 5
_LOGIN_VENTANA_SEG = 15 * 60  # 15 minutos


def _get_client_ip(request: Request) -> str:
    """IP real del cliente, considerando proxies de Render/Netlify."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(ip: str) -> tuple[bool, int]:
    """
    Devuelve (está_bloqueada, segundos_restantes).
    Limpia intentos viejos fuera de la ventana antes de evaluar.
    """
    ahora = time.time()
    # Limpiar intentos fuera de la ventana
    _login_attempts[ip] = [
        t for t in _login_attempts[ip]
        if ahora - t < _LOGIN_VENTANA_SEG
    ]
    fallidos = len(_login_attempts[ip])
    if fallidos >= _LOGIN_MAX_INTENTOS:
        mas_viejo = min(_login_attempts[ip])
        segundos_restantes = int(_LOGIN_VENTANA_SEG - (ahora - mas_viejo))
        return True, max(0, segundos_restantes)
    return False, 0


@app.post("/api/v1/login", tags=["Auth"])
def login_user(
    email: str = Body(...),
    password: str = Body(...),
    request: Request = None,
    db: DatabaseManager = Depends(get_db)
):
    ip = _get_client_ip(request) if request else "unknown"

    # Chequear si esta IP está bloqueada antes de tocar Supabase
    bloqueada, segundos = _check_rate_limit(ip)
    if bloqueada:
        minutos = segundos // 60
        raise HTTPException(
            status_code=429,
            detail=f"Demasiados intentos fallidos. Esperá {minutos} minuto{'s' if minutos != 1 else ''} antes de intentar de nuevo.",
            headers={"Retry-After": str(segundos)}
        )

    success, msg, user_data = db.login_user(email, password)

    if not success:
        # Registrar el intento fallido para esta IP
        _login_attempts[ip].append(time.time())
        fallidos_ahora = len(_login_attempts[ip])
        restantes = _LOGIN_MAX_INTENTOS - fallidos_ahora
        if restantes > 0:
            raise HTTPException(
                status_code=401,
                detail=f"{msg} Te quedan {restantes} intento{'s' if restantes != 1 else ''} antes de un bloqueo temporal."
            )
        else:
            raise HTTPException(
                status_code=429,
                detail=f"Cuenta bloqueada temporalmente por demasiados intentos fallidos. Intentá de nuevo en {_LOGIN_VENTANA_SEG // 60} minutos.",
                headers={"Retry-After": str(_LOGIN_VENTANA_SEG)}
            )

    # Login exitoso: limpiar intentos fallidos de esta IP
    _login_attempts.pop(ip, None)
    return {"message": msg, "user": user_data}

@app.post("/api/v1/logout", tags=["Auth"])
def logout_user(db: DatabaseManager = Depends(get_db)):
    db.logout_user()
    return {"message": "Sesion cerrada correctamente."}


@app.post("/api/v1/auth/google/callback", tags=["Auth"])
def google_oauth_callback(
    data: dict = Body(...),
    db: DatabaseManager = Depends(get_db)
):
    """
    Recibe el token de Supabase tras el OAuth de Google.
    Crea o actualiza el usuario en la tabla users y devuelve los datos del usuario.
    """
    try:
        access_token = data.get("access_token")
        email = data.get("email", "")
        nombre_completo = data.get("nombre_completo", "")

        if not access_token:
            raise HTTPException(status_code=400, detail="Token requerido")

        # Verificar el token con Supabase
        try:
            user_resp = db.supabase.auth.get_user(access_token)
            supabase_user_id = user_resp.user.id
            user_email = user_resp.user.email or email
            meta = user_resp.user.user_metadata or {}
            user_nombre = meta.get("full_name") or meta.get("name") or nombre_completo or user_email
        except Exception as token_err:
            print(f"⚠️ Token verify failed: {token_err} — usando datos del body")
            # Si falla la verificación, usar los datos que mandó el frontend
            if not email:
                raise HTTPException(status_code=401, detail="Token inválido y sin datos de respaldo")
            supabase_user_id = None
            user_email = email
            user_nombre = nombre_completo or email

        # Buscar si ya existe en nuestra tabla users
        existing = None
        if supabase_user_id:
            res = db.supabase.table("users")                .select("*")                .eq("id_user", supabase_user_id)                .execute()
            existing = res if res.data else None
        
        if not existing:
            res = db.supabase.table("users")                .select("*")                .eq("email_user", user_email)                .execute()
            existing = res if res.data else None

        if existing and existing.data:
            # Cuenta desactivada por un admin — no se sincroniza ni se deja pasar
            if existing.data[0].get("activo_user") is False:
                raise HTTPException(status_code=403, detail="Tu cuenta fue desactivada. Contactá al administrador.")
            # Ya existe — mantenemos el nombre que ya tenía en la BD,
            # no lo pisamos con el que mande Google en este login
            user_data = existing.data[0]
            nombre_final = user_data.get("nombre_completo_user") or user_data.get("nombre_completo") or user_nombre
        else:
            # Crear nuevo usuario en tabla users
            new_user = {
                "id_user": supabase_user_id,
                "email_user": user_email,
                "nombre_completo_user": user_nombre,
                "rol_user": "usuario"
            }
            result = db.supabase.table("users").insert(new_user).execute()
            user_data = result.data[0] if result.data else new_user
            nombre_final = user_nombre

        return {
            "message": "Login con Google exitoso",
            "user": {
                "id": user_data.get("id_user") or supabase_user_id,
                "id_user": user_data.get("id_user") or supabase_user_id,
                "email": user_email,
                "email_user": user_email,
                "nombre_completo": nombre_final,
                "nombre_completo_user": nombre_final,
                "rol": user_data.get("rol_user", "usuario"),
                "rol_user": user_data.get("rol_user", "usuario"),
                "avatar_url_user": user_data.get("avatar_url_user"),
                "es_comercio_user": user_data.get("es_comercio_user", False),
                "comercio_verificado_user": user_data.get("comercio_verificado_user", False),
                "id_comer": user_data.get("id_comer"),
                "activo_user": user_data.get("activo_user", True),
                "access_token": access_token
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error Google callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# Endpoints de CATEGORIAS
# ---------------------------------------------------

@app.get("/api/v1/categorias", tags=["Categorias"])
def get_categorias(db: DatabaseManager = Depends(get_db)):
    """
    Obtiene todas las categorias de productos desde la tabla cate_producto.
    Agrega icono y color por defecto segun el nombre de la categoria.
    """
    try:
        response = db.supabase.table("cate_producto").select("*").execute()

        if not response.data:
            return []

        # Mapeo de iconos (imagen) y colores por nombre de categoria
        SUPA_IMG = "https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images"
        icon_map = {
            "almacen": f"{SUPA_IMG}/almacen1.jpg",
            "bebidas": f"{SUPA_IMG}/bebidas.jpg",
            "carniceria": f"{SUPA_IMG}/carniceria.jpg",
            "limpieza": f"{SUPA_IMG}/limpieza.jpg",
            "verduleria": f"{SUPA_IMG}/verduleria.jpg",
            "ferreteria": f"{SUPA_IMG}/ferreteria.jpg",
            "lacteos": f"{SUPA_IMG}/lacteos.jpg",
            "servicios": f"{SUPA_IMG}/servicios1.jpg",
            "higiene personal": f"{SUPA_IMG}/higiene-personal.jpg",
            "otros": f"{SUPA_IMG}/almacen1.jpg",
        }

        color_map = {
            "almacen": "#fbbf24",
            "bebidas": "#60a5fa",
            "carniceria": "#f87171",
            "limpieza": "#34d399",
            "verduleria": "#4ade80",
            "ferreteria": "#a78bfa",
            "lacteos": "#93c5fd",
            "servicios": "#fb923c",
            "higiene personal": "#f472b6",
            "otros": "#94a3b8",
        }

        categorias = []
        for cat in response.data:
            nombre_key = cat.get("nombre", "").lower().strip()
            categorias.append({
                "id_cate": str(cat.get("id", "")),
                "nombre_cate": cat.get("nombre", ""),
                "icono_cate": icon_map.get(nombre_key, f"{SUPA_IMG}/almacen1.jpg"),
                "color": color_map.get(nombre_key, "#e8c4a0"),
                "cantidad_prod": 0
            })

        return categorias

    except Exception as e:
        print(f"❌ Error obteniendo categorias: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo categorias: {str(e)}")

@app.get("/api/v1/medidas", tags=["Categorias"])
def get_medidas(db: DatabaseManager = Depends(get_db)):
    """Obtiene todas las unidades de medida desde cate_medida."""
    try:
        response = db.supabase.table("cate_medida").select("*").order("id").execute()
        return [{"id": r["id"], "nombre": r["nombre_medida"]} for r in (response.data or [])]
    except Exception as e:
        print(f"❌ Error obteniendo medidas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# ═══════════════════════════════════════════════════
# ENDPOINTS DE PRODUCTOS - ORDEN CRITICO EN FASTAPI
# Rutas estaticas SIN parametros primero,
# rutas dinamicas CON {param} DESPUES.
# ═══════════════════════════════════════════════════
# ---------------------------------------------------

# 1. POST /api/v1/products — Crear (estatico, sin parametros)
@app.post("/api/v1/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    user = db.get_current_user()
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado. Inicia sesion nuevamente.")

    print(f"DEBUG create_product: usuario={user.get('email_user', 'N/A')}, rol={db.get_user_role()}")

    success, message = db.create_product(product.dict())
    if not success:
        if "Permisos" in message:
            raise HTTPException(status_code=403, detail=message)
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}

# 2. GET /api/v1/products/search — BÚSQUEDA CON COMPARACIÓN (estatico)
@app.get("/api/v1/products/search", tags=["Productos"])
def search_products_comparison(
    q: str = Query(..., min_length=1, description="Termino de busqueda"),
    limit: int = Query(50, ge=1, le=500),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Busca productos y devuelve datos enriquecidos con comparacion de precios
    entre productos del mismo nombre (distintos comercios).
    """
    set_user_from_token(db, authorization)
    try:
        import requests
        import traceback

        rest_url = f"{SupabaseConfig.get_url()}/rest/v1"
        service_key = os.getenv('SUPABASE_SERVICE_KEY', SupabaseConfig.get_anon_key())

        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json"
        }

        # Buscar productos que coincidan
        url = f"{rest_url}/producto"
        params = {
            "select": "*",
            "activo_prod": "eq.true",
            "or": f"(nombre_prod.ilike.*{q}*,marca_prod.ilike.*{q}*,cate_prod.ilike.*{q}*)",
            "limit": limit
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Supabase error: {response.text[:500]}")

        productos = response.json()

        # Agrupar por nombre para calcular comparaciones
        por_nombre = defaultdict(list)
        for p in productos:
            por_nombre[p['nombre_prod']].append(p)

        # Enriquecer cada producto con datos de comparacion
        for p in productos:
            grupo = por_nombre[p['nombre_prod']]
            if len(grupo) > 1:
                precios = [float(x['precio_prod']) for x in grupo]
                min_precio = min(precios)
                max_precio = max(precios)
                precio_actual = float(p['precio_prod'])

                # % mas caro que el mas barato
                if min_precio > 0 and precio_actual > min_precio:
                    p['pct_vs_min'] = round(((precio_actual - min_precio) / min_precio) * 100, 1)
                else:
                    p['pct_vs_min'] = 0

                p['es_mas_barato'] = abs(precio_actual - min_precio) < 0.01
                p['es_mas_caro'] = abs(precio_actual - max_precio) < 0.01
                p['total_competidores'] = len(grupo)
                p['precio_min_grupo'] = min_precio
                p['precio_max_grupo'] = max_precio
            else:
                p['pct_vs_min'] = 0
                p['es_mas_barato'] = True
                p['es_mas_caro'] = True
                p['total_competidores'] = 1
                p['precio_min_grupo'] = float(p['precio_prod'])
                p['precio_max_grupo'] = float(p['precio_prod'])

        db.save_search_history(
            search_term=q,
            search_type='general',
            results_count=len(productos)
        )

        return {
            "count": len(productos),
            "query": q,
            "results": productos
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en busqueda: {str(e)}")


# 2.5 GET /api/v1/products/destacados — Debe ir ANTES de /products/{product_id}
# para que FastAPI no la capture como un product_id literal "destacados".
@app.get("/api/v1/products/destacados", tags=["Productos"])
def get_productos_destacados(
    limit: int = Query(10, ge=1, le=30),
    db: DatabaseManager = Depends(get_db)
):
    """
    Productos 'destacados' — proxy de más buscados mientras no haya
    tracking real acumulado (ver get_productos_destacados en database_manager).
    """
    try:
        resultados = db.get_productos_destacados(limit=limit)
        return {"count": len(resultados), "results": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo destacados: {str(e)}")


# 3. GET /api/v1/products — Listar todos (estatico, query params)
@app.get("/api/v1/products", tags=["Productos"])
def get_all_products(
    q: Optional[str] = Query(""),
    comercio: Optional[str] = Query(None, description="Filtra por comercio_prod exacto (no es búsqueda difusa)"),
    limit: Optional[int] = Query(None),
    db: DatabaseManager = Depends(get_db)
):
    try:
        import requests
        import traceback

        rest_url = f"{SupabaseConfig.get_url()}/rest/v1"
        service_key = os.getenv('SUPABASE_SERVICE_KEY', SupabaseConfig.get_anon_key())

        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json"
        }

        url = f"{rest_url}/producto"
        params = {
            "select": "*",
            "activo_prod": "eq.true",
            "limit": limit or 5000
        }

        if q and q.strip():
            params["nombre_prod"] = f"ilike.%{q}%"

        if comercio and comercio.strip():
            params["comercio_prod"] = f"ilike.{comercio.strip()}"

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {"count": len(data), "results": data}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Supabase error: {response.text[:500]}")

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


# 2.6 GET /api/v1/products/images-by-name — Imágenes disponibles para un nombre de producto
# Debe ir ANTES de /products/{product_id} para no ser capturada como product_id literal.
@app.get("/api/v1/products/images-by-name", tags=["Productos"])
def get_images_by_name(
    nombre: str = Query(..., min_length=1, description="Nombre exacto del producto (case-insensitive)"),
    exclude_id: Optional[str] = Query(None, description="id_prod a excluir del resultado (el que se está editando)"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Busca productos con el mismo nombre (match exacto, sin distinguir mayúsculas)
    en cualquier comercio que ya tengan imagen cargada. Sirve para reutilizar
    la foto de un producto entre comercios distintos sin repetir la carga.
    """
    try:
        import requests

        rest_url = f"{SupabaseConfig.get_url()}/rest/v1"
        service_key = os.getenv('SUPABASE_SERVICE_KEY', SupabaseConfig.get_anon_key())
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json"
        }

        url = f"{rest_url}/producto"
        params = {
            "select": "id_prod,comercio_prod,imagen_prod,marca_prod",
            "nombre_prod": f"ilike.{nombre.strip()}",
            "activo_prod": "eq.true",
            "imagen_prod": "not.is.null"
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Supabase error: {response.text[:500]}")

        productos = response.json()
        if exclude_id:
            productos = [p for p in productos if p.get('id_prod') != exclude_id]

        # Deduplicar por comercio+imagen (puede haber más de un producto igual en el mismo comercio)
        vistos = set()
        opciones = []
        for p in productos:
            if not p.get('imagen_prod'):
                continue
            clave = (p.get('comercio_prod'), p.get('imagen_prod'))
            if clave in vistos:
                continue
            vistos.add(clave)
            opciones.append(p)

        return {"count": len(opciones), "results": opciones}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando imágenes: {str(e)}")



@app.get("/api/v1/products/{product_id}/same-name", tags=["Productos"])
def get_same_name_products(
    product_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """
    Devuelve todos los productos con el mismo nombre que el producto dado.
    Util para comparar precios entre comercios.
    """
    try:
        # Obtener el producto para saber su nombre
        product = db.supabase.table('producto')            .select('nombre_prod, precio_prod, comercio_prod, fecha_prod')            .eq('id_prod', product_id)            .eq('activo_prod', True)            .limit(1)            .execute()

        if not product.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        nombre = product.data[0]['nombre_prod']

        # Buscar todos los productos con ese nombre
        result = db.supabase.table('producto')            .select('*')            .ilike('nombre_prod', nombre)            .eq('activo_prod', True)            .order('precio_prod', desc=False)            .execute()

        productos = result.data or []

        # Calcular stats y enriquecer
        if len(productos) > 0:
            precios = [float(p['precio_prod']) for p in productos]
            min_p = min(precios)
            max_p = max(precios)
            avg_p = sum(precios) / len(precios)

            for p in productos:
                precio = float(p['precio_prod'])
                p['es_mejor_precio'] = abs(precio - min_p) < 0.01
                p['es_peor_precio'] = abs(precio - max_p) < 0.01
                if min_p > 0 and precio > min_p:
                    p['pct_vs_min'] = round(((precio - min_p) / min_p) * 100, 1)
                else:
                    p['pct_vs_min'] = 0
        else:
            min_p = max_p = avg_p = 0

        return {
            "nombre": nombre,
            "count": len(productos),
            "stats": {
                "min": min_p,
                "max": max_p,
                "avg": round(avg_p, 2),
                "diff_max_min": round(max_p - min_p, 2) if len(productos) > 1 else 0,
                "diff_pct": round(((max_p - min_p) / min_p) * 100, 1) if min_p > 0 and len(productos) > 1 else 0
            },
            "results": productos
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# 5. GET /api/v1/products/{product_id} — Obtener uno (dinamico, AL FINAL)
@app.get("/api/v1/products/{product_id}", tags=["Productos"])
def get_product_by_id(
    product_id: str,
    db: DatabaseManager = Depends(get_db)
):
    try:
        response = db.supabase.table('producto').select('*').eq('id_prod', product_id).eq('activo_prod', True).limit(1).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")

# 6. PUT /api/v1/products/{product_id} — Actualizar
@app.put("/api/v1/products/{product_id}", tags=["Productos"])
def update_product(
    product_id: str,
    product_data: dict = Body(..., description="Datos a actualizar"),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Actualiza un producto. Si cambia el precio, guarda el precio anterior en
    historial_precios (esto lo hace db.update_product — no se duplica acá).
    """
    set_user_from_token(db, authorization)

    success, msg = db.update_product(product_id, product_data)
    if not success:
        status = 403 if "Permisos" in msg else 400
        raise HTTPException(status_code=status, detail=msg)
    return {"message": msg}

# 7. DELETE /api/v1/products/{product_id} — Eliminar
@app.delete("/api/v1/products/{product_id}", tags=["Productos"])
def delete_product(
    product_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    success, msg = db.delete_product(product_id)
    if not success:
        status = 403 if "Permisos" in msg else 400
        raise HTTPException(status_code=status, detail=msg)
    return {"message": msg}


@app.put("/api/v1/products/{product_id}/imagen", tags=["Productos"])
def set_imagen_producto(
    product_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Setea imagen_prod y la PROPAGA a todos los productos que sean el mismo:
    por EAN válido si lo tiene, si no por nombre exacto (case-insensitive),
    en TODOS los comercios. La foto es del producto, no del comercio.
    Permitido a admin o comercio verificado.
    """
    import re
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    rol = db.get_user_role()
    if rol not in ("admin", "comercio"):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    if rol == "comercio" and not db.current_user.get("comercio_verificado_user"):
        raise HTTPException(status_code=403, detail="Tu comercio todavía no está verificado")

    imagen_url = (data.get("imagen_prod") or "").strip()
    if not imagen_url:
        raise HTTPException(status_code=400, detail="Falta la URL de la imagen (imagen_prod)")

    base = db.supabase.table("producto")\
        .select("id_prod, nombre_prod, ean_prod")\
        .eq("id_prod", product_id).limit(1).execute()
    if not base.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    prod = base.data[0]
    ean = (prod.get("ean_prod") or "").strip()
    nombre = prod.get("nombre_prod") or ""

    try:
        if ean and re.fullmatch(r"\d{12,13}", ean):
            res = db.supabase.table("producto").update({"imagen_prod": imagen_url})\
                .eq("ean_prod", ean).eq("activo_prod", True).execute()
        else:
            res = db.supabase.table("producto").update({"imagen_prod": imagen_url})\
                .ilike("nombre_prod", nombre).eq("activo_prod", True).execute()
        return {
            "message": "Imagen aplicada",
            "productos_actualizados": len(res.data or []),
            "imagen_prod": imagen_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error aplicando imagen: {str(e)}")
# ---------------------------------------------------
# NUEVOS ENDPOINTS: HISTORIAL DE PRECIOS
# ---------------------------------------------------

@app.get("/api/v1/products/{product_id}/price-history", tags=["Productos"])
def get_price_history(
    product_id: str,
    dias: Optional[int] = Query(30, description="Dias hacia atras"),
    todos_comercios: Optional[bool] = Query(False, description="Incluir historial de todos los comercios del mismo producto"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Obtiene historial de precios de un producto para el gráfico.
    Si todos_comercios=true, agrega el historial de todos los competidores
    (mismo nombre de producto) para mostrar la curva unificada del mercado.
    El último punto siempre es el precio actual del producto solicitado.
    """
    try:
        desde = datetime.now() - timedelta(days=dias)

        # 1. Historial del producto solicitado
        response = db.supabase.table("historial_precios")            .select("precio, fecha_registro")            .eq("id_prod", product_id)            .gte("fecha_registro", desde.isoformat())            .order("fecha_registro", desc=False)            .execute()

        serie = list(response.data or [])

        # 2. Si se pide historial unificado, agregar historial de competidores
        if todos_comercios:
            # Obtener nombre del producto actual
            prod_res = db.supabase.table("producto")                .select("nombre_prod, precio_prod")                .eq("id_prod", product_id)                .limit(1).execute()

            if prod_res.data:
                nombre = prod_res.data[0]["nombre_prod"]
                precio_actual = prod_res.data[0]["precio_prod"]

                # Buscar competidores con mismo nombre
                comp_res = db.supabase.table("producto")                    .select("id_prod")                    .ilike("nombre_prod", nombre)                    .eq("activo_prod", True)                    .neq("id_prod", product_id)                    .execute()

                competidor_ids = [c["id_prod"] for c in (comp_res.data or [])]

                # Obtener historial de cada competidor
                for comp_id in competidor_ids:
                    comp_hist = db.supabase.table("historial_precios")                        .select("precio, fecha_registro")                        .eq("id_prod", comp_id)                        .gte("fecha_registro", desde.isoformat())                        .order("fecha_registro", desc=False)                        .execute()
                    serie.extend(comp_hist.data or [])

                # Ordenar toda la serie por fecha
                serie.sort(key=lambda x: x.get("fecha_registro", ""))

                # Agregar precio actual como último punto
                serie.append({
                    "precio": precio_actual,
                    "fecha_registro": datetime.now().isoformat()
                })

        # Mapear al formato que espera el frontend
        series_mapped = [
            {"precio": r["precio"], "fecha": r["fecha_registro"]}
            for r in serie
        ]

        return {
            "product_id": product_id,
            "dias_consultados": dias,
            "todos_comercios": todos_comercios,
            "count": len(series_mapped),
            "series": series_mapped,
            "history": serie  # compatibilidad con código anterior
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")


# ---------------------------------------------------
# REEMPLAZAR el endpoint price-stats existente en main.py
# ---------------------------------------------------

@app.get("/api/v1/products/{product_id}/price-stats", tags=["Productos"])
def get_price_stats(
    product_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Precio actual vs hace 7 y 30 dias con variacion porcentual"""
    try:
        # Precio actual
        prod = db.supabase.table("producto").select("precio_prod, nombre_prod").eq("id_prod", product_id).execute()
        if not prod.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        actual = float(prod.data[0].get("precio_prod") or 0)
        nombre = prod.data[0].get("nombre_prod", "")

        def get_historical_price(dias: int):
            fecha_limite = datetime.now() - timedelta(days=dias)

            result = db.supabase.table("historial_precios")                .select("precio, fecha_registro")                .eq("id_prod", product_id)                .lte("fecha_registro", fecha_limite.isoformat())                .order("fecha_registro", desc=True)                .limit(1)                .execute()

            if result.data and len(result.data) > 0:
                try:
                    precio = result.data[0].get("precio")
                    if precio is not None and precio != "":
                        return float(precio), result.data[0].get("fecha_registro")
                except (TypeError, ValueError):
                    pass
            return actual, None

        precio_7, fecha_7 = get_historical_price(7)
        precio_30, fecha_30 = get_historical_price(30)

        def pct_diff(actual, anterior):
            if anterior == 0 or anterior is None: return 0
            return round(((actual - anterior) / anterior) * 100, 2)

        return {
            "producto": nombre,
            "precio_actual": actual,
            "precio_7_dias": precio_7,
            "variacion_7_dias_pct": pct_diff(actual, precio_7),
            "fecha_7_dias": fecha_7,
            "precio_30_dias": precio_30,
            "variacion_30_dias_pct": pct_diff(actual, precio_30),
            "fecha_30_dias": fecha_30,
            "tendencia": "subiendo" if actual > precio_7 else "bajando" if actual < precio_7 else "estable"
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR price-stats producto {product_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

# ---------------------------------------------------
# PRECIOS price-full
# ---------------------------------------------------

@app.get("/api/v1/products/{product_id}/price-full", tags=["Productos"])
def get_product_price_full(
    product_id: str,
    dias: Optional[int] = Query(90, description="Dias hacia atras"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Devuelve stats + serie completa de precios en una sola request.
    Formato: { product, stats, series }
    """
    try:
        # 1. Producto
        prod = db.supabase.table("producto")            .select("precio_prod, nombre_prod, cate_prod")            .eq("id_prod", product_id)            .execute()

        if not prod.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        actual = float(prod.data[0].get("precio_prod") or 0)
        nombre = prod.data[0].get("nombre_prod", "")
        categoria = prod.data[0].get("cate_prod", "")

        # 2. Historial completo
        desde = datetime.now() - timedelta(days=dias)
        hist_response = db.supabase.table("historial_precios")            .select("precio, fecha_registro")            .eq("id_prod", product_id)            .gte("fecha_registro", desde.isoformat())            .order("fecha_registro", desc=False)            .execute()

        serie_raw = hist_response.data or []

        # 3. Construir serie: historial + precio actual
        series = []
        for h in serie_raw:
            series.append({
                "fecha": h["fecha_registro"],
                "precio": float(h["precio"])
            })

        # Siempre agregar precio actual al final (si no esta ya)
        if not series or series[-1]["precio"] != actual:
            series.append({
                "fecha": datetime.now().isoformat(),
                "precio": actual
            })

        # 4. Stats
        todos_precios = [p["precio"] for p in series]
        precio_min = min(todos_precios) if todos_precios else actual
        precio_max = max(todos_precios) if todos_precios else actual
        avg_price = round(sum(todos_precios) / len(todos_precios), 2) if todos_precios else actual

        # Variacion desde el primer registro
        first_price = todos_precios[0] if todos_precios else actual
        price_change = round(((actual - first_price) / first_price) * 100, 2) if first_price != 0 else 0.0

        return {
            "product": {
                "id": product_id,
                "nombre": nombre,
                "categoria": categoria
            },
            "stats": {
                "current_price": actual,
                "min_price": precio_min,
                "max_price": precio_max,
                "avg_price": avg_price,
                "price_change": price_change,
                "total_records": len(series)
            },
            "series": series
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR price-full producto {product_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial completo: {str(e)}")


# ---------------------------------------------------
# Endpoints de HISTORIAL (desde historial_endpoints.py)
# ---------------------------------------------------

@app.get("/api/v1/historial/{product_id}", tags=["Historial"])
def get_historial_producto(
    product_id: str,
    dias: Optional[int] = Query(90, description="Dias de historial a traer (default 90)"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Devuelve el historial de precios de un producto con estadisticas.
    """
    try:
        # Fecha limite segun parametro
        fecha_desde = (datetime.now() - timedelta(days=dias)).isoformat()

        # Historial ordenado por fecha ASC (para el grafico)
        historial_res = db.supabase.table('historial_precios')            .select('precio, fecha_registro')            .eq('id_prod', product_id)            .gte('fecha_registro', fecha_desde)            .order('fecha_registro', desc=False)            .execute()

        registros = historial_res.data or []

        # Precio actual del producto
        prod_res = db.supabase.table('producto')            .select('precio_prod')            .eq('id_prod', product_id)            .eq('activo_prod', True)            .limit(1)            .execute()

        if not prod_res.data or len(prod_res.data) == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        precio_actual = prod_res.data[0]['precio_prod']

        # Calcular referencias historicas
        ahora = datetime.now()

        def precio_hace(dias_atras: int):
            """Busca el precio mas cercano a N dias atras."""
            limite = ahora - timedelta(days=dias_atras)
            candidatos = [
                r for r in registros
                if datetime.fromisoformat(str(r['fecha_registro']).replace('Z', '+00:00').replace('+00:00', '')) <= limite
            ]
            if candidatos:
                return candidatos[-1]['precio']
            return None

        precio_7d  = precio_hace(7)
        precio_30d = precio_hace(30)

        # % variacion respecto a 30d
        variacion_30d = None
        if precio_actual and precio_30d and precio_30d > 0:
            variacion_30d = round((precio_actual - precio_30d) / precio_30d * 100, 1)

        # % variacion respecto a 7d
        variacion_7d = None
        if precio_actual and precio_7d and precio_7d > 0:
            variacion_7d = round((precio_actual - precio_7d) / precio_7d * 100, 1)

        # Min / max historico
        precios_lista = [r['precio'] for r in registros]
        precios_lista.append(precio_actual)

        # Incluir precios actuales de todos los comercios con el mismo producto
        # para que el min/max sea real entre todos los competidores
        try:
            nombre_res = db.supabase.table('producto') \
                .select('nombre_prod') \
                .eq('id_prod', product_id) \
                .limit(1).execute()
            if nombre_res.data:
                nombre_prod = nombre_res.data[0]['nombre_prod']
                otros_res = db.supabase.table('producto') \
                    .select('precio_prod') \
                    .ilike('nombre_prod', nombre_prod) \
                    .eq('activo_prod', True) \
                    .execute()
                for otro in (otros_res.data or []):
                    if otro['precio_prod']:
                        precios_lista.append(float(otro['precio_prod']))
        except Exception:
            pass  # no crítico

        precio_minimo = min(precios_lista) if precios_lista else None
        precio_maximo = max(precios_lista) if precios_lista else None

        # Serie para el grafico (incluye precio actual al final)
        serie = [{"precio": r['precio'], "fecha": r['fecha_registro']} for r in registros]
        serie.append({"precio": precio_actual, "fecha": ahora.isoformat()})

        return {
            "id_prod":       product_id,
            "precio_actual": precio_actual,
            "precio_7d":     precio_7d,
            "precio_30d":    precio_30d,
            "variacion_7d":  variacion_7d,
            "variacion_30d": variacion_30d,
            "precio_minimo": precio_minimo,
            "precio_maximo": precio_maximo,
            "total_cambios": len(registros),
            "serie":         serie
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error historial {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/historial/{product_id}", tags=["Historial"])
def registrar_precio_manual(
    product_id: str,
    precio: float = Body(..., embed=True),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Registra manualmente un precio en el historial (solo admin).
    Util para cargar precios historicos iniciales.
    """
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")
    try:
        res = db.supabase.table('historial_precios').insert({
            "id_prod":        product_id,
            "precio":         precio,
            "fecha_registro": datetime.now().isoformat()
        }).execute()
        if res.data:
            return {"message": "Precio registrado", "data": res.data[0]}
        raise HTTPException(status_code=400, detail="Error al registrar")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Endpoints de comercios
# ---------------------------------------------------

@app.get("/api/v1/comercios", tags=["Comercios"])
def search_comercios(
    search: Optional[str] = Query("", description="Texto a buscar (nombre o representante)"),
    sort_by: Optional[str] = Query("nombre", description="Campo de ordenamiento"),
    db: DatabaseManager = Depends(get_db)
):
    comercios, error = db.search_comercios(search, sort_by)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"count": len(comercios), "results": comercios}

@app.get("/api/v1/comercios/{comercio_id}", tags=["Comercios"])
def get_comercio_by_id(comercio_id: str, db: DatabaseManager = Depends(get_db)):
    comercio, error = db.get_comercio_by_id(comercio_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return comercio

@app.post("/api/v1/comercios", tags=["Comercios"])
def create_comerdor(
    comercio_data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear comercios")

    comercio, error = db.insert_comercio(comercio_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Comercio agregado correctamente", "data": comercio}

@app.put("/api/v1/comercios/{comercio_id}", tags=["Comercios"])
def update_comerdor(
    comercio_id: str,
    update_data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden editar comercios")

    comercio, error = db.update_comerdor(comercio_id, update_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Comercio actualizado", "data": comercio}

@app.delete("/api/v1/comercios/{comercio_id}", tags=["Comercios"])
def delete_comerdor(
    comercio_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar comercios")

    success, msg = db.delete_comerdor(comercio_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# ---------------------------------------------------
# Endpoints de busqueda avanzada
# ---------------------------------------------------

@app.get("/api/v1/search/price", tags=["Busqueda avanzada"])
def search_by_price(
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    term: Optional[str] = Query("", description="Termino de busqueda"),
    db: DatabaseManager = Depends(get_db)
):
    results = db.search_productos_by_precio(min_price, max_price, term)
    return {"count": len(results), "results": results}

@app.get("/api/v1/search/date", tags=["Busqueda avanzada"])
def search_by_date(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    term: Optional[str] = Query(""),
    db: DatabaseManager = Depends(get_db)
):
    results = db.search_productos_by_fecha(fecha_desde, fecha_hasta, term)
    return {"count": len(results), "results": results}

@app.get("/api/v1/search-history", tags=["Busqueda avanzada"])
def get_my_search_history(
    limit: int = Query(10, ge=1, le=50),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Historial de búsquedas del usuario autenticado (vacío si no hay sesión)."""
    set_user_from_token(db, authorization)
    historial = db.get_search_history(limit=limit)
    return {"count": len(historial), "results": historial}

# ---------------------------------------------------
# Apagado y limpieza
# ---------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():
    db.close_connections()
    print("💤 Servidor detenido correctamente.")

# ---------------------------------------------------
# Endpoints de OFERTAS
# ---------------------------------------------------

@app.get("/api/v1/ofertas", tags=["Ofertas"])
def get_ofertas_vigentes(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    comercio: Optional[str] = Query(None, description="Filtrar por comercio"),
    limit: Optional[int] = Query(50, description="Limite de resultados"),
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene todas las ofertas vigentes (activas y dentro de fecha)"""
    try:
        # Intentar con la vista, si no existe usar la tabla directa
        # Tabla ofertas con join a producto
        try:
            query = db.supabase.table('ofertas')                .select('*, producto(nombre_prod, cate_prod, imagen_prod, comercio_prod)')                .eq('activa', True)                .gte('fecha_fin', datetime.now().isoformat())
            response = query.limit(limit).order('descuento_pct', desc=True).execute()
        except Exception as join_err:
            print(f"⚠️ Join falló ({join_err}), intentando sin join")
            query = db.supabase.table('ofertas')                .select('*')                .eq('activa', True)
            response = query.limit(limit).execute()

        if response.data:
            return {"count": len(response.data), "results": response.data}
        return {"count": 0, "results": []}

    except Exception as e:
        print(f"❌ Error obteniendo ofertas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ofertas/{oferta_id}", tags=["Ofertas"])
def get_oferta_by_id(
    oferta_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene una oferta especifica por ID"""
    try:
        response = db.supabase.table('ofertas_vigentes').select('*').eq('id', oferta_id).limit(1).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Oferta no encontrada o vencida")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ofertas", tags=["Ofertas"])
def create_oferta(
    oferta_data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Crea una nueva oferta (solo admin)"""
    set_user_from_token(db, authorization)

    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear ofertas")

    try:
        # Validaciones basicas
        required = ['id_prod', 'precio_normal', 'precio_oferta', 'fecha_fin']
        for field in required:
            if field not in oferta_data or not oferta_data[field]:
                raise HTTPException(status_code=400, detail=f"Campo requerido: {field}")

        # Calcular descuento si no viene
        if 'descuento_pct' not in oferta_data:
            precio_normal = float(oferta_data['precio_normal'])
            precio_oferta = float(oferta_data['precio_oferta'])
            if precio_normal > 0:
                oferta_data['descuento_pct'] = round((precio_normal - precio_oferta) / precio_normal * 100)

        # Campos según estructura real de la tabla ofertas
        # descuento_pct es columna generada — Supabase la calcula automáticamente
        insert_data = {
            'id_prod':       oferta_data['id_prod'],
            'precio_normal': float(oferta_data['precio_normal']),
            'precio_oferta': float(oferta_data['precio_oferta']),
            'fecha_inicio':  oferta_data.get('fecha_inicio', datetime.now().isoformat()),
            'fecha_fin':     oferta_data['fecha_fin'],
            'activa':        True,
            'creada_por':    db.current_user.get('id') if db.current_user else None
        }

        response = db.supabase.table('ofertas').insert(insert_data).execute()

        if response.data:
            return {"message": "Oferta creada correctamente", "data": response.data[0]}
        raise HTTPException(status_code=500, detail="Error al crear oferta")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando oferta: {str(e)}")


@app.put("/api/v1/ofertas/{oferta_id}", tags=["Ofertas"])
def update_oferta(
    oferta_id: str,
    oferta_data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Actualiza una oferta existente (solo admin)"""
    set_user_from_token(db, authorization)

    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden actualizar ofertas")

    try:
        # descuento_pct es una columna generada: la base la calcula sola a partir
        # de precio_normal y precio_oferta. Si la mandamos en el update, Postgres
        # rechaza con "can only be updated to DEFAULT". Por eso la quitamos del payload.
        oferta_data.pop('descuento_pct', None)

        response = db.supabase.table('ofertas').update(oferta_data).eq('id', oferta_id).execute()

        if response.data and len(response.data) > 0:
            return {"message": "Oferta actualizada", "data": response.data[0]}
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando oferta: {str(e)}")


@app.delete("/api/v1/ofertas/{oferta_id}", tags=["Ofertas"])
def delete_oferta(
    oferta_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Elimina (desactiva) una oferta (solo admin)"""
    set_user_from_token(db, authorization)

    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar ofertas")

    try:
        response = db.supabase.table('ofertas').update({'activa': False}).eq('id', oferta_id).execute()

        if response.data:
            return {"message": "Oferta desactivada correctamente"}
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando oferta: {str(e)}")


# ---------------------------------------------------
# Endpoints de USUARIOS
# ---------------------------------------------------

@app.get("/api/v1/users/me", tags=["Usuarios"])
def get_current_user_info(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene la informacion del usuario autenticado"""
    set_user_from_token(db, authorization)

    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    return {
        "id": db.current_user.get("id"),
        "rol": db.current_user.get("rol_user", "usuario"),
        "metadata": db.current_user.get("user_metadata", {})
    }


@app.get("/api/v1/users", tags=["Usuarios"])
def list_users(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Lista todos los usuarios (solo admin)"""
    set_user_from_token(db, authorization)

    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden listar usuarios")

    try:
        response = db.supabase.table('users').select('*').execute()
        return {"count": len(response.data), "results": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/users/{user_id}/role", tags=["Usuarios"])
def update_user_role(
    user_id: str,
    rol: str = Body(..., embed=True),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Actualiza el rol de un usuario (solo admin)"""
    set_user_from_token(db, authorization)

    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores pueden cambiar roles")

    try:
        response = db.supabase.table('users').update({'rol_user': rol}).eq('id_user', user_id).execute()
        if response.data:
            return {"message": "Rol actualizado", "data": response.data[0]}
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Endpoints de ESTADISTICAS / DASHBOARD
# ---------------------------------------------------

@app.get("/api/v1/stats/dashboard", tags=["Estadisticas"])
def get_dashboard_stats(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene estadisticas del dashboard"""
    set_user_from_token(db, authorization)

    try:
        # Total productos activos
        prod_response = db.supabase.table('producto').select('*', count='exact').eq('activo_prod', True).execute()
        total_productos = prod_response.count if hasattr(prod_response, 'count') else len(prod_response.data)

        # Total comercios
        prov_response = db.supabase.table('comercio').select('*', count='exact').eq('activo_comer', True).execute()
        total_comercios = prov_response.count if hasattr(prov_response, 'count') else len(prov_response.data)

        # Total ofertas vigentes
        ofertas_response = db.supabase.table('ofertas').select('*', count='exact').eq('activa', True).execute()
        total_ofertas = ofertas_response.count if hasattr(ofertas_response, 'count') else len(ofertas_response.data)

        # Total usuarios
        users_response = db.supabase.table('users').select('*', count='exact').execute()
        total_usuarios = users_response.count if hasattr(users_response, 'count') else len(users_response.data)

        return {
            "total_productos": total_productos,
            "total_comercios": total_comercios,
            "total_ofertas": total_ofertas,
            "total_usuarios": total_usuarios
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadisticas: {str(e)}")


@app.get("/api/v1/stats/products-by-category", tags=["Estadisticas"])
def get_products_by_category(
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene cantidad de productos por categoria"""
    try:
        response = db.supabase.table('producto').select('id_cate, cate_producto(nombre)').eq('activo_prod', True).execute()

        counts = {}
        for item in response.data:
            cat_name = item.get('cate_producto', {}).get('nombre', 'Sin categoria')
            counts[cat_name] = counts.get(cat_name, 0) + 1

        return {"results": [{"categoria": k, "cantidad": v} for k, v in counts.items()]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# SUBIDA DE IMAGENES A BUCKET (herramienta admin / extension Chrome)
# ---------------------------------------------------

class UploadBucketBody(BaseModel):
    imagen_base64: str
    nombre: str
    bucket: Optional[str] = "product-images"
    carpeta: Optional[str] = ""
    optimizar: Optional[bool] = True
    content_type: Optional[str] = "image/jpeg"

@app.post("/api/v1/admin/upload-a-bucket", tags=["Admin"])
def upload_a_bucket(
    body: UploadBucketBody,
    x_api_key: Optional[str] = Header(None),
):
    """
    Sube una imagen (base64) a un bucket de Supabase Storage.
    Auth por clave propia (UPLOAD_API_KEY) para la extension de admin.
    Devuelve la URL publica del archivo.
    """
    import re
    import base64
    import requests

    # 1. Auth por clave secreta
    api_key_esperada = os.getenv("UPLOAD_API_KEY")
    if not api_key_esperada:
        raise HTTPException(status_code=503, detail="UPLOAD_API_KEY no configurada en el servidor")
    if not x_api_key or x_api_key != api_key_esperada:
        raise HTTPException(status_code=401, detail="Clave de API invalida")

    # 2. Decodificar (acepta data-URI o base64 puro)
    raw = body.imagen_base64.strip()
    content_type = body.content_type or "image/jpeg"
    if raw.startswith("data:"):
        try:
            cabecera, raw = raw.split(",", 1)
            m = re.search(r"data:([^;]+);", cabecera)
            if m:
                content_type = m.group(1)
        except ValueError:
            pass
    try:
        image_bytes = base64.b64decode(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="imagen_base64 invalida")
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Imagen vacia")

    # 3. Optimizacion opcional (Pillow: 800x800, JPEG q82)
    if body.optimizar:
        try:
            import io
            from PIL import Image, ImageOps
            img = Image.open(io.BytesIO(image_bytes))
            img = ImageOps.exif_transpose(img)
            if img.mode in ("RGBA", "LA", "P"):
                fondo = Image.new("RGB", img.size, (255, 255, 255))
                img = img.convert("RGBA")
                fondo.paste(img, mask=img.split()[-1])
                img = fondo
            else:
                img = img.convert("RGB")
            img.thumbnail((800, 800), Image.LANCZOS)
            out = io.BytesIO()
            img.save(out, format="JPEG", quality=82, optimize=True)
            image_bytes = out.getvalue()
            content_type = "image/jpeg"
        except Exception as e:
            print(f"⚠️ Optimizacion fallo, se sube original: {e}")

    # 4. Path seguro + extension coherente
    ext_por_mime = {
        "image/jpeg": "jpg", "image/jpg": "jpg", "image/png": "png",
        "image/webp": "webp", "image/gif": "gif",
    }
    ext = ext_por_mime.get(content_type, "jpg")
    nombre = re.sub(r"[^a-zA-Z0-9._-]", "-", (body.nombre or "imagen").strip()).strip("-.") or "imagen"
    nombre = re.sub(r"\.(jpg|jpeg|png|webp|gif)$", "", nombre, flags=re.I)
    nombre = f"{nombre}.{ext}"

    carpeta = re.sub(r"[^a-zA-Z0-9._/-]", "-", (body.carpeta or "").strip().strip("/"))
    path = f"{carpeta}/{nombre}" if carpeta else nombre
    bucket = (body.bucket or "product-images").strip().strip("/")

    # 5. Subir via REST con service role
    service_key = SupabaseConfig.get_service_key()
    base_url = SupabaseConfig.get_url()
    upload_url = f"{base_url}/storage/v1/object/{bucket}/{path}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    try:
        resp = requests.post(upload_url, headers=headers, data=image_bytes, timeout=30)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error de red al subir: {e}")
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Storage rechazo la subida ({resp.status_code}): {resp.text}")

    public_url = f"{base_url}/storage/v1/object/public/{bucket}/{path}"
    return {
        "success": True,
        "bucket": bucket,
        "path": path,
        "content_type": content_type,
        "bytes": len(image_bytes),
        "public_url": public_url,
    }

# ---------------------------------------------------
# Health Check
# ---------------------------------------------------

@app.get("/health", tags=["General"])
def health_check():
    """Endpoint de health check para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db._test_connection_simple()
    }

# ---------------------------------------------------
# OPTIMIZADOR DE LISTAS DE COMPRA
# ---------------------------------------------------

@app.get("/api/v1/listas/{lista_id}/optimize", tags=["Listas"])
def optimize_lista(
    lista_id: str,
    user_lat: Optional[float] = Query(None, description="Latitud del usuario para calcular distancias"),
    user_lng: Optional[float] = Query(None, description="Longitud del usuario para calcular distancias"),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Calcula el costo total de la lista por cada comercio.
    Incluye: productos por comercio, faltantes, distancia al usuario,
    alternativa completa, y sugerencia de división óptima.
    """
    set_user_from_token(db, authorization)

    import math
    from collections import defaultdict

    def haversine(lat1, lng1, lat2, lng2):
        """Distancia en km entre dos coordenadas."""
        if None in (lat1, lng1, lat2, lng2):
            return None
        R = 6371
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng/2)**2
        return round(R * 2 * math.asin(math.sqrt(a)), 1)

    try:
        # 1. Obtener items de la lista
        lista_res = db.supabase.table('lista_compra')\
            .select('*, lista_item(*)')\
            .eq('id_lista', lista_id)\
            .eq('activa', True)\
            .limit(1)\
            .execute()

        if not lista_res.data:
            raise HTTPException(status_code=404, detail="Lista no encontrada")

        items = lista_res.data[0].get('lista_item', [])
        if not items:
            return {"lista_id": lista_id, "items_count": 0, "message": "La lista está vacía",
                    "comercios": [], "mejor_opcion": None, "division_sugerida": None}

        # 2. Cargar coordenadas de todos los comercios activos
        prov_res = db.supabase.table('comercio')\
            .select('nombre_comer, ubicacion_comer, direccion_comer')\
            .eq('activo_comer', True)\
            .execute()

        coords_por_comercio = {}
        for prov in (prov_res.data or []):
            nombre = prov.get('nombre_comer', '')
            coords = db._parse_wkb_point(prov.get('ubicacion_comer') or '')
            distancia = haversine(user_lat, user_lng, coords.get('lat'), coords.get('lng'))
            coords_por_comercio[nombre] = {
                'lat': coords.get('lat'),
                'lng': coords.get('lng'),
                'distancia_km': distancia,
                'direccion': prov.get('direccion_comer', '')
            }

        # 3. Para cada item, buscar productos coincidentes
        productos_por_item = {}
        items_sin_precio = []   # productos que no tienen ningún precio en la BD
        todos_comercios = set()
        HACE_7_DIAS = (datetime.now() - timedelta(days=7)).isoformat()

        for item in items:
            nombre_item = item.get('nombre_item', '').strip()
            if not nombre_item:
                continue
            prod_res = db.supabase.table('producto')\
                .select('id_prod, nombre_prod, precio_prod, comercio_prod, marca_prod, unidad_prod, cantidad_prod, fecha_prod')\
                .eq('activo_prod', True)\
                .ilike('nombre_prod', f'%{nombre_item}%')\
                .execute()
            productos = prod_res.data or []

            # Separar frescos (≤7 días) de antiguos (>7 días)
            frescos = [p for p in productos if p.get('fecha_prod') and p['fecha_prod'] >= HACE_7_DIAS]
            antiguos = [p for p in productos if p not in frescos]

            # Usar frescos si los hay; si no, usar antiguos marcándolos
            usar = frescos if frescos else antiguos
            for p in usar:
                p['_precio_viejo'] = p not in frescos

            if not usar:
                items_sin_precio.append(nombre_item)

            productos_por_item[item['id_item']] = usar
            for p in usar:
                todos_comercios.add(p.get('comercio_prod', 'Desconocido'))

        # 4. Calcular costo por comercio con detalle de productos
        comercios_data = {}
        for comercio in todos_comercios:
            total = 0
            items_encontrados = 0
            items_faltantes = []
            detalle_productos = []  # productos que SÍ tiene este comercio

            for item in items:
                item_id = item['id_item']
                cantidad = item.get('cantidad', 1)
                productos = productos_por_item.get(item_id, [])

                producto_comercio = None
                for p in productos:
                    if p.get('comercio_prod') == comercio:
                        if not producto_comercio or float(p['precio_prod']) < float(producto_comercio['precio_prod']):
                            producto_comercio = p

                if producto_comercio:
                    precio = float(producto_comercio['precio_prod'])
                    total += precio * cantidad
                    items_encontrados += 1
                    detalle_productos.append({
                        "nombre": item['nombre_item'],
                        "cantidad": cantidad,
                        "precio_unitario": precio,
                        "subtotal": round(precio * cantidad, 2),
                        "precio_viejo": bool(producto_comercio.get('_precio_viejo'))
                    })
                else:
                    items_faltantes.append(item['nombre_item'])

            info_coords = coords_por_comercio.get(comercio, {})
            comercios_data[comercio] = {
                "comercio": comercio,
                "total": round(total, 2),
                "items_encontrados": items_encontrados,
                "items_faltantes": items_faltantes,
                "completo": len(items_faltantes) == 0,
                "detalle_productos": detalle_productos,
                "distancia_km": info_coords.get('distancia_km'),
                "direccion": info_coords.get('direccion', '')
            }

        # 5. Ordenar: primero los que tienen más items, luego por precio
        comercios_ordenados = sorted(
            comercios_data.values(),
            key=lambda x: (-x['items_encontrados'], x['total'])
        )

        # 6. Mejor opción = mayor cobertura al menor precio
        mejor_opcion = comercios_ordenados[0] if comercios_ordenados else None

        ahorro_vs_peor = 0
        if len(comercios_ordenados) > 1:
            peor = max(comercios_ordenados, key=lambda x: x['total'])
            if mejor_opcion:
                ahorro_vs_peor = round(peor['total'] - mejor_opcion['total'], 2)

        # 7. Comercio de faltantes: el que tiene el mejor precio para los
        #    productos que le faltan al mejor comercio
        comercio_faltantes = None
        if mejor_opcion and mejor_opcion['items_faltantes']:
            faltantes_data = defaultdict(lambda: {"items": [], "subtotal": 0})

            for nombre_faltante in mejor_opcion['items_faltantes']:
                # Buscar el item original
                item_obj = next((i for i in items if i.get('nombre_item') == nombre_faltante), None)
                if not item_obj:
                    continue
                item_id = item_obj['id_item']
                cantidad = item_obj.get('cantidad', 1)
                productos = productos_por_item.get(item_id, [])

                # Excluir el comercio principal — buscar el más barato entre el resto
                candidatos = [p for p in productos if p.get('comercio_prod') != mejor_opcion['comercio']]
                if candidatos:
                    mas_barato = min(candidatos, key=lambda p: float(p['precio_prod']))
                    prov_f = mas_barato['comercio_prod']
                    precio = float(mas_barato['precio_prod']) * cantidad
                    faltantes_data[prov_f]['items'].append({
                        "nombre": nombre_faltante,
                        "cantidad": cantidad,
                        "precio_unitario": float(mas_barato['precio_prod']),
                        "subtotal": round(precio, 2)
                    })
                    faltantes_data[prov_f]['subtotal'] += precio

            if faltantes_data:
                # El comercio que cubre más faltantes al menor costo
                mejor_faltante_prov = min(faltantes_data.items(), key=lambda x: x[1]['subtotal'])
                prov_nombre = mejor_faltante_prov[0]
                info_coords_f = coords_por_comercio.get(prov_nombre, {})
                comercio_faltantes = {
                    "comercio": prov_nombre,
                    "items": mejor_faltante_prov[1]['items'],
                    "subtotal": round(mejor_faltante_prov[1]['subtotal'], 2),
                    "distancia_km": info_coords_f.get('distancia_km'),
                    "direccion": info_coords_f.get('direccion', '')
                }

        # 8. Alternativa completa: el comercio completo más barato (distinto al mejor)
        alternativa_completa = None
        completos = [p for p in comercios_ordenados if p['completo'] and (not mejor_opcion or p['comercio'] != mejor_opcion['comercio'])]
        if completos:
            mejor_completo = min(completos, key=lambda x: x['total'])
            alternativa_completa = {
                "comercio": mejor_completo['comercio'],
                "total": mejor_completo['total'],
                "distancia_km": mejor_completo.get('distancia_km'),
                "direccion": mejor_completo.get('direccion', '')
            }

        # 9. División óptima
        division = defaultdict(lambda: {"items": [], "subtotal": 0})
        division_total = 0

        for item in items:
            item_id = item['id_item']
            cantidad = item.get('cantidad', 1)
            productos = productos_por_item.get(item_id, [])
            if productos:
                mas_barato = min(productos, key=lambda p: float(p['precio_prod']))
                prov = mas_barato['comercio_prod']
                precio = float(mas_barato['precio_prod']) * cantidad
                division[prov]['items'].append({
                    "nombre": item['nombre_item'],
                    "cantidad": cantidad,
                    "precio_unitario": float(mas_barato['precio_prod']),
                    "subtotal": round(precio, 2)
                })
                division[prov]['subtotal'] += precio
                division_total += precio

        division_formateada = []
        for prov, data in sorted(division.items(), key=lambda x: x[1]['subtotal']):
            info_coords_d = coords_por_comercio.get(prov, {})
            division_formateada.append({
                "comercio": prov,
                "items": data['items'],
                "subtotal": round(data['subtotal'], 2),
                "distancia_km": info_coords_d.get('distancia_km'),
                "direccion": info_coords_d.get('direccion', '')
            })

        ahorro_division = round(mejor_opcion['total'] - division_total, 2) if mejor_opcion and division_total > 0 else 0

        return {
            "lista_id": lista_id,
            "items_count": len(items),
            "items_sin_precio": items_sin_precio,
            "comercios": comercios_ordenados,
            "mejor_opcion": {
                "comercio": mejor_opcion['comercio'],
                "total": mejor_opcion['total'],
                "ahorro_vs_peor": ahorro_vs_peor,
                "completo": mejor_opcion['completo'],
                "detalle_productos": mejor_opcion['detalle_productos'],
                "distancia_km": mejor_opcion.get('distancia_km'),
                "direccion": mejor_opcion.get('direccion', '')
            } if mejor_opcion else None,
            "comercio_faltantes": comercio_faltantes,
            "alternativa_completa": alternativa_completa,
            "division_sugerida": {
                "total": round(division_total, 2),
                "comercios": division_formateada,
                "ahorro_vs_unico": ahorro_division,
                "cantidad_comercios": len(division_formateada)
            } if len(division_formateada) > 1 else None
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error optimizando lista {lista_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ---------------------------------------------------
# ALERTAS DE PRECIOS
# ---------------------------------------------------

class AlertaCreate(BaseModel):
    id_prod: str
    precio_objetivo: float

@app.post("/api/v1/alertas", tags=["Alertas"])
def crear_alerta(
    alerta: AlertaCreate,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        # Desactivar alerta anterior del mismo producto
        db.supabase.table("alertas_precio")\
            .update({"activa": False})\
            .eq("user_id", db.current_user["id"])\
            .eq("id_prod", alerta.id_prod)\
            .eq("activa", True)\
            .execute()
        
        res = db.supabase.table("alertas_precio").insert({
            "user_id": db.current_user["id"],
            "id_prod": alerta.id_prod,
            "precio_objetivo": alerta.precio_objetivo,
            "activa": True,
            "notificada": False
        }).execute()
        return {"message": "Alerta creada", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/alertas", tags=["Alertas"])
def mis_alertas(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        res = db.supabase.table("alertas_precio")\
            .select("*, producto(nombre_prod, precio_prod, imagen_prod, comercio_prod)")\
            .eq("user_id", db.current_user["id"])\
            .eq("activa", True)\
            .order("fecha_creacion", desc=True)\
            .execute()
        return {"count": len(res.data), "results": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/alertas/{alerta_id}", tags=["Alertas"])
def eliminar_alerta(
    alerta_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        db.supabase.table("alertas_precio")\
            .update({"activa": False})\
            .eq("id", alerta_id)\
            .eq("user_id", db.current_user["id"])\
            .execute()
        return {"message": "Alerta eliminada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def verificar_alertas(db: DatabaseManager, product_id: str, nuevo_precio: float):
    """Verifica alertas activas cuando cambia un precio. Llama desde update_product."""
    try:
        alertas = db.supabase.table("alertas_precio")\
            .select("*, users(email_user), producto(nombre_prod)")\
            .eq("id_prod", product_id)\
            .eq("activa", True)\
            .lte("precio_objetivo", nuevo_precio)\
            .eq("notificada", False)\
            .execute()
        
        for alerta in alertas.data or []:
            db.supabase.table("alertas_precio")\
                .update({
                    "notificada": True,
                    "fecha_notificacion": datetime.now().isoformat()
                })\
                .eq("id", alerta["id"])\
                .execute()
            
            print(f"🔔 ALERTA TRIGGERED: {alerta['producto']['nombre_prod']} "
                  f"bajó a ${nuevo_precio} (objetivo: ${alerta['precio_objetivo']}) "
                  f"→ user: {alerta['users']['email_user']}")
            
    except Exception as e:
        print(f"⚠️ Error verificando alertas: {e}")

import random, string

def generar_codigo(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.post("/api/v1/listas/{lista_id}/compartir", tags=["Listas"])
def compartir_lista(
    lista_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Genera un código para compartir una lista"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        # Verificar que la lista pertenece al usuario
        lista = db.supabase.table('lista_compra')\
            .select('id_lista, user_id')\
            .eq('id_lista', lista_id)\
            .eq('activa', True)\
            .limit(1)\
            .execute()
        
        if not lista.data:
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        
        # Generar código único
        for _ in range(10):
            codigo = generar_codigo()
            try:
                res = db.supabase.table('lista_compartida').insert({
                    "id_lista": lista_id,
                    "codigo": codigo,
                    "creado_por": db.current_user["id"],
                    "expira_en": (datetime.now() + timedelta(days=7)).isoformat()
                }).execute()
                if res.data:
                    return {
                        "codigo": codigo,
                        "link": f"https://comparapp.com/listas/compartida/{codigo}",
                        "expira_en": res.data[0]['expira_en']
                    }
            except Exception:
                continue  # Código duplicado, intentar otro
        
        raise HTTPException(status_code=500, detail="No se pudo generar código")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/listas/compartida/{codigo}", tags=["Listas"])
def ver_lista_compartida(
    codigo: str,
    db: DatabaseManager = Depends(get_db)
):
    """Ver una lista compartida por código (sin autenticación)"""
    try:
        comp = db.supabase.table('lista_compartida')\
            .select('*, lista_compra(*)')\
            .eq('codigo', codigo)\
            .eq('activo', True)\
            .gt('expira_en', datetime.now().isoformat())\
            .limit(1)\
            .execute()
        
        if not comp.data:
            raise HTTPException(status_code=404, detail="Código inválido o expirado")

        comp_data = comp.data[0]
        
        # Incrementar usos
        db.supabase.table('lista_compartida')\
            .update({"usos": comp_data.get('usos', 0) + 1})\
            .eq('id', comp_data['id'])\
            .execute()
        
        lista_id = comp_data['id_lista']
        
        # Obtener items
        items_res = db.supabase.table('lista_item')\
            .select('*')\
            .eq('id_lista', lista_id)\
            .execute()
        
        return {
            "lista": comp_data['lista_compra'],
            "items": items_res.data or [],
            "compartido_por": comp_data['creado_por'],
            "fecha_compartido": comp_data['fecha_creacion']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/listas/compartida/{codigo}/copiar", tags=["Listas"])
def copiar_lista_compartida(
    codigo: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Copiar una lista compartida a mi perfil"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        # Obtener lista compartida
        comp = db.supabase.table('lista_compartida')\
            .select('id_lista')\
            .eq('codigo', codigo)\
            .eq('activo', True)\
            .limit(1)\
            .execute()
        
        if not comp.data:
            raise HTTPException(status_code=404, detail="Código inválido")

        comp_data = comp.data[0]
        
        lista_orig = db.supabase.table('lista_compra')\
            .select('*, lista_item(*)')\
            .eq('id_lista', comp_data['id_lista'])\
            .limit(1)\
            .execute()
        
        if not lista_orig.data:
            raise HTTPException(status_code=404, detail="Lista no encontrada")

        lista_orig_data = lista_orig.data[0]
        
        # Crear nueva lista
        now = datetime.now().isoformat()
        nueva = db.supabase.table('lista_compra').insert({
            "user_id": db.current_user["id"],
            "nombre_lista": lista_orig_data['nombre_lista'] + " (copia)",
            "fecha_creacion": now,
            "fecha_modificacion": now,
            "activa": True
        }).execute()
        
        nueva_id = nueva.data[0]['id_lista']
        
        # Copiar items
        for item in lista_orig_data.get('lista_item', []):
            db.supabase.table('lista_item').insert({
                "id_lista": nueva_id,
                "nombre_item": item['nombre_item'],
                "cantidad": item.get('cantidad', 1),
                "unidad": item.get('unidad', ''),
                "marca": item.get('marca', ''),
                "acepta_sustitucion": item.get('acepta_sustitucion', True),
                "prioridad": item.get('prioridad', 'importante'),
                "estado": 'pendiente',
                "notas": item.get('notas', '')
            }).execute()
        
        return {"message": "Lista copiada", "id_lista": nueva_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# ENDPOINTS DE LISTAS DE COMPRA
# ---------------------------------------------------

@app.get("/api/v1/listas", tags=["Listas"])
def get_listas(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene todas las listas activas del usuario autenticado"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    listas, error = db.get_listas_by_user(db.current_user["id"])
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"count": len(listas), "results": listas}


@app.post("/api/v1/listas", tags=["Listas"])
def create_lista(
    nombre_lista: str = Body(..., embed=True),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Crea una nueva lista de compra"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    if not nombre_lista or not nombre_lista.strip():
        raise HTTPException(status_code=400, detail="El nombre es requerido")
    
    user_id = db.current_user["id"]
    print(f"📋 Creando lista '{nombre_lista}' para user_id={user_id}")
    
    lista, error = db.create_lista(user_id, nombre_lista.strip())
    if error:
        print(f"❌ Error create_lista: {error}")
        raise HTTPException(status_code=400, detail=error)
    
    print(f"✅ Lista creada: {lista}")
    return {"message": "Lista creada", "data": lista}


@app.get("/api/v1/listas/{lista_id}", tags=["Listas"])
def get_lista(
    lista_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene una lista con sus items"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    user_id = db.current_user["id"]
    print(f"📋 GET lista {lista_id} para user_id={user_id}")
    
    lista, error = db.get_lista_by_id(lista_id, user_id)
    if error:
        print(f"❌ Error get_lista: {error} | lista_id={lista_id} | user_id={user_id}")
        raise HTTPException(status_code=404, detail=error)
    return lista


@app.put("/api/v1/listas/{lista_id}", tags=["Listas"])
def update_lista(
    lista_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Actualiza el nombre de una lista"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    lista, error = db.update_lista(lista_id, db.current_user["id"], data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Lista actualizada", "data": lista}


@app.delete("/api/v1/listas/{lista_id}", tags=["Listas"])
def delete_lista(
    lista_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Elimina (desactiva) una lista"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    success, msg = db.delete_lista(lista_id, db.current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


# ── Items ──

@app.get("/api/v1/listas/{lista_id}/items", tags=["Listas"])
def get_items_lista(
    lista_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Obtiene los items de una lista"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    lista, error = db.get_lista_by_id(lista_id, db.current_user["id"])
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {"items": lista.get("items", [])}


@app.post("/api/v1/listas/{lista_id}/items", tags=["Listas"])
def add_item(
    lista_id: str,
    item_data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Agrega un item a una lista"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    item, error = db.add_item_to_lista(lista_id, db.current_user["id"], item_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Item agregado", "data": item}


@app.put("/api/v1/items/{item_id}", tags=["Listas"])
def update_item(
    item_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Actualiza un item (cantidad, estado, notas, etc.)"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    item, error = db.update_item(item_id, db.current_user["id"], data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Item actualizado", "data": item}


@app.delete("/api/v1/items/{item_id}", tags=["Listas"])
def delete_item(
    item_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """Elimina un item"""
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    success, msg = db.delete_item(item_id, db.current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


# ---------------------------------------------------
# Punto de entrada (para ejecutar con uvicorn)
# ---------------------------------------------------

# ============================================================
# ENDPOINTS: Registro de comercios + aprobación + carga de productos
# Pegar en main.py, antes del bloque "if __name__ == '__main__':"
# Requiere: from fastapi import UploadFile, File  (agregar al import de fastapi si falta)
# Requiere: import uuid (agregar arriba si falta)
# ============================================================

# ---------- 1. Listar comercios disponibles (para el selector en registro) ----------
@app.get("/api/v1/comercios-disponibles", tags=["Comercio Users"])
def listar_comercios_disponibles(db: DatabaseManager = Depends(get_db)):
    """
    Devuelve los comercios activos que todavía no tienen un usuario dueño
    vinculado y verificado — son los que aparecen en el selector de registro.
    """
    try:
        res = db.supabase.table("comercio") \
            .select("id_comer, nombre_comer, direccion_comer, cate_comer") \
            .eq("activo_comer", True) \
            .order("nombre_comer") \
            .execute()
        return {"count": len(res.data or []), "results": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 2. Registro de comercio (usuario + vínculo a comercio existente) ----------
@app.post("/api/v1/register-comercio", tags=["Comercio Users"])
def register_comercio_user(
    email: str = Body(...),
    password: str = Body(...),
    nombre_completo: str = Body(...),
    telefono: Optional[str] = Body(None),
    id_comer: str = Body(..., description="UUID del comercio ya creado por el admin"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Registra un usuario que será dueño/encargado de un comercio existente.
    Queda con comercio_verificado_user = false hasta que el admin lo apruebe.
    """
    # Verificar que el comercio exista y esté activo
    comercio_res = db.supabase.table("comercio") \
        .select("id_comer, nombre_comer") \
        .eq("id_comer", id_comer) \
        .eq("activo_comer", True) \
        .limit(1) \
        .execute()

    if not comercio_res.data:
        raise HTTPException(status_code=404, detail="El comercio seleccionado no existe o no está activo")

    nombre_comer = comercio_res.data[0]['nombre_comer']

    # Verificar que ese comercio no tenga ya un dueño verificado
    existente = db.supabase.table("users") \
        .select("id_user") \
        .eq("id_comer", id_comer) \
        .eq("comercio_verificado_user", True) \
        .execute()
    if existente.data:
        raise HTTPException(status_code=400, detail="Este comercio ya tiene un usuario verificado asignado")

    # Crear el usuario base (reusa la lógica de register_user)
    success, msg, user_data = db.register_user(email, password, nombre_completo, telefono)
    if not success:
        raise HTTPException(status_code=400, detail=msg)

    # Marcarlo como comercio pendiente y vincularlo
    try:
        db.supabase.table("users").update({
            "es_comercio_user": True,
            "comercio_verificado_user": False,
            "id_comer": id_comer,
            "rol_user": "comercio"
        }).eq("id_user", user_data["id_user"]).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usuario creado pero error al vincular comercio: {str(e)}")

    return {
        "message": f"Registro recibido. Tu acceso para '{nombre_comer}' está pendiente de aprobación.",
        "user": user_data
    }


def _contar_admins_activos(db: DatabaseManager, excluir_id: Optional[str] = None) -> int:
    """Cuenta administradores activos, excepto excluir_id (para validar 'me quedaría 0')."""
    query = db.supabase.table("users").select("id_user").eq("rol_user", "admin").eq("activo_user", True)
    if excluir_id:
        query = query.neq("id_user", excluir_id)
    res = query.execute()
    return len(res.data or [])


# ---------- 2.9 Admin: gestión de usuarios ----------
@app.get("/api/v1/admin/usuarios", tags=["Admin"])
def listar_usuarios(
    q: Optional[str] = Query(None, description="Busca por email o nombre"),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")

    try:
        query = db.supabase.table("users").select(
            "id_user, email_user, nombre_completo_user, rol_user, es_comercio_user, "
            "comercio_verificado_user, activo_user, avatar_url_user, fecha_registro_user, "
            "id_comer, comercio!users_id_comer_fkey(nombre_comer)"
        ).order("fecha_registro_user", desc=True)

        if q and q.strip():
            term = q.strip()
            query = query.or_(f"email_user.ilike.%{term}%,nombre_completo_user.ilike.%{term}%")

        res = query.execute()
        return {"count": len(res.data or []), "results": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/admin/usuarios/{user_id}/rol", tags=["Admin"])
def cambiar_rol_usuario(
    user_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")

    nuevo_rol = (data.get("rol") or "").strip()
    if nuevo_rol not in ("usuario", "comercio", "admin"):
        raise HTTPException(status_code=400, detail="Rol inválido. Debe ser usuario, comercio o admin")

    # No te podés cambiar el rol a vos mismo — evita auto-degradarte o
    # auto-promoverte sin que quede claro quién lo hizo.
    mi_id = (db.current_user or {}).get("id")
    if user_id == mi_id:
        raise HTTPException(status_code=400, detail="No podés cambiar tu propio rol. Pedile a otro administrador.")

    actual = db.supabase.table("users").select("id_user, rol_user").eq("id_user", user_id).limit(1).execute()
    if not actual.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    rol_actual = actual.data[0].get("rol_user")

    # Si le estás sacando el rol admin a alguien, asegurate de que no sea el último
    if rol_actual == "admin" and nuevo_rol != "admin":
        if _contar_admins_activos(db, excluir_id=user_id) < 1:
            raise HTTPException(status_code=400, detail="No podés sacarle el rol de admin al último administrador activo")

    try:
        db.supabase.table("users").update({"rol_user": nuevo_rol}).eq("id_user", user_id).execute()
        return {"message": f"Rol actualizado a '{nuevo_rol}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/admin/usuarios/{user_id}/estado", tags=["Admin"])
def cambiar_estado_usuario(
    user_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")

    nuevo_activo = data.get("activo")
    if not isinstance(nuevo_activo, bool):
        raise HTTPException(status_code=400, detail="El campo 'activo' debe ser true o false")

    mi_id = (db.current_user or {}).get("id")
    if user_id == mi_id and not nuevo_activo:
        raise HTTPException(status_code=400, detail="No podés desactivar tu propia cuenta")

    actual = db.supabase.table("users").select("id_user, rol_user, activo_user").eq("id_user", user_id).limit(1).execute()
    if not actual.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    fila = actual.data[0]

    if fila.get("rol_user") == "admin" and fila.get("activo_user") and not nuevo_activo:
        if _contar_admins_activos(db, excluir_id=user_id) < 1:
            raise HTTPException(status_code=400, detail="No podés desactivar al último administrador activo")

    try:
        db.supabase.table("users").update({"activo_user": nuevo_activo}).eq("id_user", user_id).execute()
        return {"message": "Usuario activado" if nuevo_activo else "Usuario desactivado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 3. Admin: listar comercios pendientes de aprobación ----------
@app.get("/api/v1/admin/comercios-pendientes", tags=["Comercio Users"])
def listar_comercios_pendientes(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")

    try:
        res = db.supabase.table("users") \
            .select("id_user, email_user, nombre_completo_user, telefono_user, fecha_registro_user, id_comer, comercio!users_id_comer_fkey(nombre_comer, direccion_comer)") \
            .eq("es_comercio_user", True) \
            .eq("comercio_verificado_user", False) \
            .order("fecha_registro_user", desc=True) \
            .execute()
        return {"count": len(res.data or []), "results": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 4. Admin: aprobar comercio ----------
@app.post("/api/v1/admin/comercios/{user_id}/aprobar", tags=["Comercio Users"])
def aprobar_comercio_user(
    user_id: str,
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")

    try:
        res = db.supabase.table("users").update({
            "comercio_verificado_user": True,
            "motivo_rechazo_comercio": None
        }).eq("id_user", user_id).execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": "Comercio aprobado correctamente", "data": res.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 5. Admin: rechazar comercio ----------
@app.post("/api/v1/admin/comercios/{user_id}/rechazar", tags=["Comercio Users"])
def rechazar_comercio_user(
    user_id: str,
    motivo: Optional[str] = Body(None, embed=True),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")

    try:
        res = db.supabase.table("users").update({
            "comercio_verificado_user": False,
            "es_comercio_user": False,
            "id_comer": None,
            "motivo_rechazo_comercio": motivo or "No se especificó un motivo"
        }).eq("id_user", user_id).execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": "Comercio rechazado", "data": res.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 6. Estado del comercio logueado (para el guard de navegación) ----------
@app.get("/api/v1/mi-comercio", tags=["Comercio Users"])
def mi_estado_comercio(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        res = db.supabase.table("users") \
            .select("es_comercio_user, comercio_verificado_user, motivo_rechazo_comercio, id_comer, comercio!users_id_comer_fkey(id_comer, nombre_comer, logo_comer, plan_comer, plan_vencimiento_comer)") \
            .eq("id_user", db.current_user["id"]) \
            .limit(1) \
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        data = res.data[0]
        comercio_info = data.get("comercio") or {}

        if comercio_info:
            es_premium = db.is_admin() or db._es_premium_vigente(comercio_info)
            cantidad_actual = db._contar_productos_activos(comercio_info.get("nombre_comer", ""))
            data["plan"] = {
                "es_premium": es_premium,
                "productos_activos": cantidad_actual,
                "limite_productos": None if es_premium else LIMITE_PRODUCTOS_PLAN_FREE
            }

        return data
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 7. Subida de imagen de producto al bucket de Supabase Storage ----------
@app.post("/api/v1/upload-imagen-producto", tags=["Comercio Users"])
async def upload_imagen_producto(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Sube una imagen al bucket product-images y devuelve la URL pública.
    Disponible para admin y comercios verificados.
    """
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    rol = db.get_user_role()
    if rol not in ("admin", "comercio"):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")

    # Validar tipo de archivo
    ext = (file.filename or "").split(".")[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado (usar jpg, png o webp)")

    try:
        contenido = await file.read()

        # --- Optimización: redimensionar y comprimir a JPEG liviano ---
        # Reduce fotos de varios MB (cámara de celular) a ~30-60KB, sin perder
        # calidad visible en la vitrina. Ahorra storage y acelera la carga.
        from io import BytesIO
        from PIL import Image, ImageOps

        MAX_W, MAX_H = 800, 800   # lado máximo; suficiente para la ficha de producto
        try:
            img = Image.open(BytesIO(contenido))
            img = ImageOps.exif_transpose(img)          # respeta orientación del celular
            if img.mode in ("RGBA", "P", "LA"):
                fondo = Image.new("RGB", img.size, (255, 255, 255))
                img_rgb = img.convert("RGBA")
                fondo.paste(img_rgb, mask=img_rgb.split()[-1])  # aplana transparencia sobre blanco
                img = fondo
            else:
                img = img.convert("RGB")
            img.thumbnail((MAX_W, MAX_H), Image.LANCZOS)

            buf = BytesIO()
            img.save(buf, format="JPEG", quality=82, optimize=True)
            contenido = buf.getvalue()
        except Exception as e_opt:
            # Si por lo que sea no se puede optimizar, subimos el original.
            print(f"⚠️ No se pudo optimizar la imagen, se sube el original: {e_opt}")

        # Tras optimizar, siempre queda como .jpg
        nombre_archivo = f"productos/{uuid.uuid4()}.jpg"

        db.supabase.storage.from_("product-images").upload(
            nombre_archivo,
            contenido,
            {"content-type": "image/jpeg"}
        )

        url_publica = db.supabase.storage.from_("product-images").get_public_url(nombre_archivo)
        return {"url": url_publica}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")


# ---------- 7.5. Logo del comercio (lo sube el propio comercio verificado) ----------
@app.post("/api/v1/comercio-panel/logo", tags=["Comercio Users"])
async def subir_logo_comercio(
    logo: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    El comercio verificado sube su propio logo. Se guarda en comercio.logo_comer
    y queda visible para todos los usuarios en el carrusel de comercios del dashboard.
    Solo puede tocar SU PROPIO id_comer (viene del token, no de un parámetro).
    """
    set_user_from_token(db, authorization)
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    id_comer = db.current_user.get("id_comer")
    if not db.current_user.get("comercio_verificado_user") or not id_comer:
        raise HTTPException(status_code=403, detail="Solo comercios verificados pueden actualizar su logo")

    ext = (logo.filename or "").split(".")[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado (usar jpg, png o webp)")

    try:
        contenido = await logo.read()
        nombre_archivo = f"logos-comercio/{id_comer}.{ext}"
        db.supabase.storage.from_("product-images").upload(
            nombre_archivo,
            contenido,
            {"content-type": logo.content_type or "image/jpeg", "upsert": "true"}
        )
        url_publica = db.supabase.storage.from_("product-images").get_public_url(nombre_archivo)

        db.supabase.table("comercio").update({"logo_comer": url_publica}).eq("id_comer", id_comer).execute()

        return {"url": url_publica}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el logo: {str(e)}")


# ============================================================
# ENDPOINT: Registro de comercio vía Google OAuth
# Pegar en main.py junto a los demás endpoints de "Comercio Users"
# ============================================================

@app.post("/api/v1/register-comercio-google", tags=["Comercio Users"])
def register_comercio_google(
    data: dict = Body(...),
    db: DatabaseManager = Depends(get_db)
):
    """
    Vincula una cuenta de Google ya autenticada (via Supabase OAuth)
    a un comercio existente, dejando comercio_verificado_user=false.
    El frontend llama esto desde /auth/callback cuando detecta que
    el usuario venía del flujo de registro de comercio.
    """
    try:
        access_token = data.get("access_token")
        email = data.get("email", "")
        nombre_completo = data.get("nombre_completo", "")
        id_comer = data.get("id_comer")

        if not access_token:
            raise HTTPException(status_code=400, detail="Token requerido")
        if not id_comer:
            raise HTTPException(status_code=400, detail="id_comer requerido")

        # Verificar que el comercio exista y esté activo
        comercio_res = db.supabase.table("comercio") \
            .select("id_comer, nombre_comer") \
            .eq("id_comer", id_comer) \
            .eq("activo_comer", True) \
            .limit(1) \
            .execute()

        if not comercio_res.data:
            raise HTTPException(status_code=404, detail="El comercio seleccionado no existe o no está activo")

        nombre_comer = comercio_res.data[0]['nombre_comer']

        # Verificar el token con Supabase para obtener el id real del usuario
        # OJO: esto debe ir ANTES de chequear si el comercio ya tiene dueño verificado,
        # porque si no, el dueño legítimo re-logueándose se bloquea a sí mismo
        # (ver "este comercio ya tiene un usuario verificado asignado" — bug recurrente).
        try:
            user_resp = db.supabase.auth.get_user(access_token)
            supabase_user_id = user_resp.user.id
            user_email = user_resp.user.email or email
            meta = user_resp.user.user_metadata or {}
            user_nombre = meta.get("full_name") or meta.get("name") or nombre_completo or user_email
        except Exception:
            if not email:
                raise HTTPException(status_code=401, detail="Token inválido y sin datos de respaldo")
            supabase_user_id = None
            user_email = email
            user_nombre = nombre_completo or email

        if not supabase_user_id:
            raise HTTPException(status_code=401, detail="No se pudo verificar la identidad de Google")

        # Normalizar contra la fila real en 'users': esta identidad de Auth (Google) puede no
        # tener fila propia si la persona ya se registró antes con email/password para el mismo
        # email. Sin este fallback, el insert de más abajo choca con la restricción UNIQUE de
        # email_user (error 'duplicate key value violates unique constraint users_email_user_key').
        fila_existente = db.supabase.table("users").select("*").eq("id_user", supabase_user_id).execute()
        if not fila_existente.data:
            fila_existente = db.supabase.table("users").select("*").eq("email_user", user_email).execute()
        id_user_real = fila_existente.data[0]["id_user"] if fila_existente.data else supabase_user_id

        # Verificar que ese comercio no tenga ya un dueño verificado QUE NO SEA este mismo usuario
        existente = db.supabase.table("users") \
            .select("id_user") \
            .eq("id_comer", id_comer) \
            .eq("comercio_verificado_user", True) \
            .execute()
        if existente.data and any(u["id_user"] != id_user_real for u in existente.data):
            raise HTTPException(status_code=400, detail="Este comercio ya tiene un usuario verificado asignado")

        existing_user = fila_existente

        if existing_user.data:
            user_data = existing_user.data[0]
            nombre_final = user_data.get("nombre_completo_user") or user_nombre
            ya_verificado_aqui = (
                user_data.get("id_comer") == id_comer
                and user_data.get("comercio_verificado_user") is True
            )
            if ya_verificado_aqui:
                # Es el dueño legítimo re-logueándose: no lo degradamos a pendiente otra vez
                return {
                    "message": f"Ya tenés acceso verificado a '{nombre_comer}'.",
                    "user": {
                        "id": id_user_real,
                        "email": user_email,
                        "nombre_completo": nombre_final,
                        "rol": "comercio",
                        "es_comercio_user": True,
                        "comercio_verificado_user": True,
                        "id_comer": id_comer,
                        "access_token": access_token
                    }
                }
            # Ya existía (por ejemplo, ya era usuario normal, con esta identidad o con otra
            # para el mismo email) — lo convertimos a comercio pendiente.
            # Mantenemos el nombre que ya tenía en la BD, no lo pisamos con el de Google
            db.supabase.table("users").update({
                "es_comercio_user": True,
                "comercio_verificado_user": False,
                "id_comer": id_comer,
                "rol_user": "comercio"
            }).eq("id_user", id_user_real).execute()
        else:
            # Crear el usuario nuevo, directamente como comercio pendiente
            new_user = {
                "id_user": supabase_user_id,
                "email_user": user_email,
                "nombre_completo_user": user_nombre,
                "rol_user": "comercio",
                "es_comercio_user": True,
                "comercio_verificado_user": False,
                "id_comer": id_comer,
                "activo_user": True,
            }
            result = db.supabase.table("users").insert(new_user).execute()
            user_data = result.data[0] if result.data else new_user
            nombre_final = user_nombre

        return {
            "message": f"Registro recibido. Tu acceso para '{nombre_comer}' está pendiente de aprobación.",
            "user": {
                "id": id_user_real,
                "email": user_email,
                "nombre_completo": nombre_final,
                "rol": "comercio",
                "es_comercio_user": True,
                "comercio_verificado_user": False,
                "id_comer": id_comer,
                "access_token": access_token
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _autorizar_import(db: DatabaseManager, comercio_id: str) -> bool:
    """
    Permite importar si es admin, o si es un comercio verificado sobre SU PROPIO id_comer.
    Lanza HTTPException si no corresponde. Devuelve True si es admin (sin tope de plan).
    En esta etapa: admin + comercio. A futuro se puede dejar solo el comercio.
    """
    if not db.current_user:
        raise HTTPException(status_code=401, detail="No autenticado. Iniciá sesión de nuevo.")
    if db.is_admin():
        return True
    es_duenio = (
        db.current_user.get("comercio_verificado_user") is True
        and str(db.current_user.get("id_comer")) == str(comercio_id)
    )
    if not es_duenio:
        raise HTTPException(status_code=403, detail="No tenés permiso para importar en este comercio")
    return False

# ============================================================
#  IMPORTADOR DE PRODUCTOS POR ARCHIVO  —  endpoint de IMPORTAR
#  Pegar en main.py junto al endpoint de preview, ANTES de
#  `if __name__ == "__main__":`.
#
#  - Solo admin (mismo guard que el preview).
#  - Reusa db.create_product / db.update_product  →  historial de
#    precios y alertas se manejan solos, no se duplica lógica.
#  - El admin NO tiene tope de plan (el límite es solo para
#    cuentas 'comercio'), así que carga sin restricción.
#  - Guarda ean_prod, cate_prod y cate_id (categoría automática
#    por palabra clave sobre el nombre).
#  - Mismo mapeo/parseo que el preview (para que los números
#    coincidan con lo previsualizado).
# ============================================================

# ------------------------------------------------------------
#  Reglas de categoría (id de la tabla cate_producto).
#  El ORDEN es la prioridad: frases específicas primero,
#  palabras genéricas al final. Gana el primer match.
#  Rubros: 1 Almacen · 2 Bebidas · 3 Carniceria · 4 Limpieza
#          5 Verduleria · 6 Otros · 7 Ferreteria · 8 Lacteos
#          10 Servicios · 11 Higiene Personal
# ------------------------------------------------------------
REGLAS_CATEGORIA = [
    # --- frases ambiguas primero ---
    ("JABON EN POLVO", 4, "Limpieza"), ("JABON LIQUIDO", 4, "Limpieza"),
    ("JABON BLANCO", 4, "Limpieza"), ("JABON EN PAN", 4, "Limpieza"),
    ("JABON DE TOCADOR", 11, "Higiene Personal"),
    ("PURE DE TOMATE", 1, "Almacen"), ("SALSA DE TOMATE", 1, "Almacen"),
    ("EXTRACTO DE TOMATE", 1, "Almacen"), ("DULCE DE LECHE", 8, "Lacteos"),
    ("PAPAS FRITAS", 1, "Almacen"), ("QUESO CREMA", 8, "Lacteos"),
    ("ALCOHOL EN GEL", 11, "Higiene Personal"),
    ("ALCOHOL EN AEROSOL", 11, "Higiene Personal"),
    ("BOLSA PARA HORNO", 1, "Almacen"), ("BOLSAS PARA HORNO", 1, "Almacen"),
    ("CREMA DE LECHE", 8, "Lacteos"), ("CREMA PARA BATIR", 8, "Lacteos"),
    ("CREMA CORPORAL", 11, "Higiene Personal"), ("CREMA DE MANOS", 11, "Higiene Personal"),
    ("CREMA PARA COCINAR", 1, "Almacen"), ("CREMA CHANTILLY", 1, "Almacen"),
    # --- Bebidas ---
    ("CERVEZA", 2, "Bebidas"), ("GASEOSA", 2, "Bebidas"), ("COCA COLA", 2, "Bebidas"),
    ("SPRITE", 2, "Bebidas"), ("FANTA", 2, "Bebidas"), ("PASO DE LOS TOROS", 2, "Bebidas"),
    ("AGUA", 2, "Bebidas"), ("SODA", 2, "Bebidas"), ("VINO", 2, "Bebidas"),
    ("FERNET", 2, "Bebidas"), ("JUGO", 2, "Bebidas"), ("VODKA", 2, "Bebidas"),
    ("WHISKY", 2, "Bebidas"), ("APERITIVO", 2, "Bebidas"), ("ENERGIZANTE", 2, "Bebidas"),
    ("SPEED", 2, "Bebidas"), ("AMARGO", 2, "Bebidas"), ("GANCIA", 2, "Bebidas"),
    ("SIDRA", 2, "Bebidas"), ("CHAMPAGNE", 2, "Bebidas"), ("TERMA", 2, "Bebidas"),
    ("LICOR", 2, "Bebidas"), (" GIN ", 2, "Bebidas"), ("ANIS", 2, "Bebidas"),
    ("FRIZZE", 2, "Bebidas"), ("APEROL", 2, "Bebidas"), ("CAMPARI", 2, "Bebidas"),
    ("CHOCOLATADA", 2, "Bebidas"),
    # --- Lacteos ---
    ("LECHE", 8, "Lacteos"), ("YOGUR", 8, "Lacteos"), ("YOGHUR", 8, "Lacteos"),
    ("QUESO", 8, "Lacteos"), ("MANTECA", 8, "Lacteos"), ("RICOTA", 8, "Lacteos"),
    ("MARGARINA", 8, "Lacteos"), ("DANONINO", 8, "Lacteos"), ("POSTRE", 8, "Lacteos"),
    # --- Carniceria ---
    ("CARNE", 3, "Carniceria"), ("POLLO", 3, "Carniceria"), ("MILANESA", 3, "Carniceria"),
    ("CHORIZO", 3, "Carniceria"), ("MORCILLA", 3, "Carniceria"), ("BONDIOLA", 3, "Carniceria"),
    ("MATAMBRE", 3, "Carniceria"), ("ASADO", 3, "Carniceria"), ("HAMBURGUESA", 3, "Carniceria"),
    ("SALCHICHA", 3, "Carniceria"), ("COSTILLA", 3, "Carniceria"), ("PECHUGA", 3, "Carniceria"),
    ("CERDO", 3, "Carniceria"), ("PESCADO", 3, "Carniceria"), ("MERLUZA", 3, "Carniceria"),
    ("VACIO", 3, "Carniceria"), ("NALGA", 3, "Carniceria"), ("PECETO", 3, "Carniceria"),
    ("CUADRIL", 3, "Carniceria"), ("JAMON", 3, "Carniceria"), ("SALAME", 3, "Carniceria"),
    ("MORTADELA", 3, "Carniceria"), ("PANCETA", 3, "Carniceria"), ("FIAMBRE", 3, "Carniceria"),
    ("SALCHICHON", 3, "Carniceria"),
    # --- Limpieza ---
    ("DETERGENTE", 4, "Limpieza"), ("LAVANDINA", 4, "Limpieza"), ("SUAVIZANTE", 4, "Limpieza"),
    ("LIMPIADOR", 4, "Limpieza"), ("LUSTRAMUEBLE", 4, "Limpieza"), ("INSECTICIDA", 4, "Limpieza"),
    ("DESINFECTANTE", 4, "Limpieza"), ("CLORO", 4, "Limpieza"), ("LAVAVAJILLA", 4, "Limpieza"),
    (" CIF ", 4, "Limpieza"), ("AYUDIN", 4, "Limpieza"), ("ESPONJA", 4, "Limpieza"),
    ("VIRULANA", 4, "Limpieza"), ("TRAPO", 4, "Limpieza"), ("RESIDUO", 4, "Limpieza"),
    ("AROMATIZANTE", 4, "Limpieza"), (" AER ", 4, "Limpieza"), ("POWER POCKET", 4, "Limpieza"),
    ("ANTIGRASA", 4, "Limpieza"), ("CERA ", 4, "Limpieza"), ("ALCOHOL", 4, "Limpieza"),
    ("ZIPLOC", 4, "Limpieza"), ("DESODORANTE DE AMBIENTE", 4, "Limpieza"), ("PLUMERO", 4, "Limpieza"),
    ("BLEM", 4, "Limpieza"),
    # --- Higiene Personal ---
    ("SHAMPOO", 11, "Higiene Personal"), ("SHAMPU", 11, "Higiene Personal"),
    ("ACONDICIONADOR", 11, "Higiene Personal"), ("DESODORANTE", 11, "Higiene Personal"),
    ("PASTA DENTAL", 11, "Higiene Personal"), ("CREMA DENTAL", 11, "Higiene Personal"),
    ("CEPILLO DENTAL", 11, "Higiene Personal"), ("ENJUAGUE BUCAL", 11, "Higiene Personal"),
    ("PAÑAL", 11, "Higiene Personal"), ("PANAL", 11, "Higiene Personal"),
    ("TOALLITA", 11, "Higiene Personal"), ("TOALLA FEMENINA", 11, "Higiene Personal"),
    ("PROTECTOR", 11, "Higiene Personal"), ("ALGODON", 11, "Higiene Personal"),
    ("HISOPO", 11, "Higiene Personal"), ("AFEITAR", 11, "Higiene Personal"),
    ("GILLETTE", 11, "Higiene Personal"), ("PAPEL HIGIENICO", 11, "Higiene Personal"),
    ("COLONIA", 11, "Higiene Personal"), ("TALCO", 11, "Higiene Personal"),
    ("JABON", 11, "Higiene Personal"),  # jabon suelto -> tocador (despues de los de limpieza)
    # --- Ferreteria ---
    ("FOCO", 7, "Ferreteria"), ("LAMPARA", 7, "Ferreteria"), (" PILA", 7, "Ferreteria"),
    ("CINTA", 7, "Ferreteria"), ("PEGAMENTO", 7, "Ferreteria"), ("VELA", 7, "Ferreteria"),
    ("FOSFORO", 7, "Ferreteria"), ("ENCENDEDOR", 7, "Ferreteria"), ("MATAFUEGO", 7, "Ferreteria"),
    ("MECHERO", 7, "Ferreteria"), ("CANDADO", 7, "Ferreteria"),
    # --- Verduleria ---
    ("PAPA", 5, "Verduleria"), ("CEBOLLA", 5, "Verduleria"), ("LECHUGA", 5, "Verduleria"),
    ("ZANAHORIA", 5, "Verduleria"), ("MANZANA", 5, "Verduleria"), ("BANANA", 5, "Verduleria"),
    ("NARANJA", 5, "Verduleria"), ("LIMON", 5, "Verduleria"), ("TOMATE", 5, "Verduleria"),
    ("ZAPALLO", 5, "Verduleria"), ("MORRON", 5, "Verduleria"),
    # --- Servicios ---
    ("RECARGA", 10, "Servicios"), ("SALDO", 10, "Servicios"), ("CARGA VIRTUAL", 10, "Servicios"),
    # --- Almacen (lo mas generico al final) ---
    ("ACEITE", 1, "Almacen"), ("ARROZ", 1, "Almacen"), ("FIDEO", 1, "Almacen"),
    ("FIDEOS", 1, "Almacen"),
    ("HARINA", 1, "Almacen"), ("YERBA", 1, "Almacen"), ("AZUCAR", 1, "Almacen"),
    ("POLENTA", 1, "Almacen"), ("LENTEJA", 1, "Almacen"), ("POROTO", 1, "Almacen"),
    ("GARBANZO", 1, "Almacen"), ("GALLETITA", 1, "Almacen"), ("GALLETA", 1, "Almacen"),
    ("BIZCOCHO", 1, "Almacen"), ("MERMELADA", 1, "Almacen"), ("CAFE", 1, "Almacen"),
    ("MATE COCIDO", 1, "Almacen"), ("CACAO", 1, "Almacen"), ("MAYONESA", 1, "Almacen"),
    ("KETCHUP", 1, "Almacen"), ("MOSTAZA", 1, "Almacen"), ("VINAGRE", 1, "Almacen"),
    ("CALDO", 1, "Almacen"), ("SOPA", 1, "Almacen"), ("PAN RALLADO", 1, "Almacen"),
    ("REBOZADOR", 1, "Almacen"), ("ATUN", 1, "Almacen"), ("ARVEJA", 1, "Almacen"),
    ("CHOCLO", 1, "Almacen"), ("PURE", 1, "Almacen"), ("FLAN", 1, "Almacen"),
    ("GELATINA", 1, "Almacen"), ("SNACK", 1, "Almacen"), ("TURRON", 1, "Almacen"),
    ("ALFAJOR", 1, "Almacen"), ("CARAMELO", 1, "Almacen"), ("CHUPETIN", 1, "Almacen"),
    ("MANI ", 1, "Almacen"), ("ACEITUNA", 1, "Almacen"), ("CONSERVA", 1, "Almacen"),
    ("DULCE", 1, "Almacen"), ("CHOCOLATE", 1, "Almacen"), ("GOLOSINA", 1, "Almacen"),
    ("CHICLE", 1, "Almacen"), ("PAN LACTAL", 1, "Almacen"), ("TAPA", 1, "Almacen"),
    ("PREPIZZA", 1, "Almacen"), ("CONDIMENTO", 1, "Almacen"), ("ESPECIA", 1, "Almacen"),
    ("ADEREZO", 1, "Almacen"), ("AJI", 1, "Almacen"), ("ALMIDON", 1, "Almacen"),
    ("MAIZENA", 1, "Almacen"), ("AVENA", 1, "Almacen"), ("BOMBON", 1, "Almacen"),
    ("BOCADITO", 1, "Almacen"), ("SEMOLA", 1, "Almacen"), ("PANIFICAD", 1, "Almacen"),
    ("BUDIN", 1, "Almacen"), ("MAGDALENA", 1, "Almacen"), ("OBLEA", 1, "Almacen"),
    ("CEREAL", 1, "Almacen"), ("PANQUEQUE", 1, "Almacen"), ("REINA MORA", 1, "Almacen"),
    ("CAPELETI", 1, "Almacen"), ("RAVIOL", 1, "Almacen"), ("SORRENTINO", 1, "Almacen"),
    ("COMINO", 1, "Almacen"), ("OREGANO", 1, "Almacen"), ("PIMENTON", 1, "Almacen"),
    ("COCO RALLADO", 1, "Almacen"),
]
RUBRO_DEFAULT = (6, "Otros")


def clasificar_rubro(nombre: str):
    """Devuelve (cate_id, cate_prod) segun palabra clave. Default: Otros."""
    n = " " + (nombre or "").upper() + " "
    for frase, cid, cnom in REGLAS_CATEGORIA:
        if frase in n:
            return cid, cnom
    return RUBRO_DEFAULT


@app.post("/api/v1/comercios/{comercio_id}/productos/importar", tags=["Comercio Import"])
async def importar_productos(
    comercio_id: str,
    file: UploadFile = File(...),
    # --- Mapeo (mismo preset que el preview; columnas en base 0) ---
    encoding: str = Form("latin-1"),
    separador: str = Form(";"),
    filas_saltar: int = Form(5),
    col_nombre: int = Form(2),
    col_precio: int = Form(9),
    col_ean: int = Form(0),
    col_marca: int = Form(6),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Importa (upsert) los productos de un archivo al comercio indicado.
    - Match por EAN (12-13 dig) y, si no, por nombre normalizado.
    - Existente  -> update de precio (y backfill de EAN si faltaba).
    - Nuevo      -> create con ean_prod, marca, categoria automatica,
                    comercio_prod = nombre del comercio.
    El historial de precios y las alertas los maneja db (create/update_product).
    Solo admin.
    """
    import io, csv, re

    set_user_from_token(db, authorization)
    es_admin = _autorizar_import(db, comercio_id)

    # 1) Comercio (nombre para comercio_prod y para cruzar sus productos)
    com = db.supabase.table("comercio")\
        .select("nombre_comer, plan_comer")\
        .eq("id_comer", comercio_id).limit(1).execute()
    if not com.data:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    nombre_comer = com.data[0]["nombre_comer"]
    plan_comer = (com.data[0].get("plan_comer") or "free").lower()

    # 2) Leer y parsear el archivo
    try:
        contenido = await file.read()
        texto = contenido.decode(encoding, errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo ({encoding}): {e}")

    lector = csv.reader(io.StringIO(texto), delimiter=separador)
    filas = list(lector)
    filas = filas[filas_saltar:] if filas_saltar > 0 else filas

    # 3) Helpers (mismos que el preview)
    def celda(fila, idx):
        return (fila[idx].strip() if 0 <= idx < len(fila) else "")

    def parse_precio(s):
        s = (s or "").strip()
        if not s:
            return None
        s = s.replace(".", "").replace(",", ".")   # locale AR
        try:
            v = float(s)
            return v if v > 0 else None
        except ValueError:
            return None

    def norm_nombre(s):
        return re.sub(r"\s+", " ", (s or "").strip().lower())

    def ean_valido(s):
        s = (s or "").strip()
        if not s or "e+" in s.lower():
            return None
        return s if re.fullmatch(r"\d{12,13}", s) else None

    # 4) Productos que YA tiene el comercio (para decidir update vs create)
    existentes = db.supabase.table("producto")\
        .select("id_prod, nombre_prod, ean_prod")\
        .ilike("comercio_prod", nombre_comer)\
        .eq("activo_prod", True).limit(5000).execute()
    por_ean, por_nombre, tiene_ean = {}, {}, {}
    for p in (existentes.data or []):
        e = (p.get("ean_prod") or "").strip()
        pid = p["id_prod"]
        if e:
            por_ean[e] = pid
        n = norm_nombre(p.get("nombre_prod"))
        if n:
            por_nombre.setdefault(n, pid)
            tiene_ean[pid] = bool(e)

    # Cupo de plan: solo aplica cuando importa el propio comercio en plan free
    cant_actual = len(existentes.data or [])
    aplicar_limite = (not es_admin) and (plan_comer == "free")
    cupo_restante = (LIMITE_PRODUCTOS_PLAN_FREE - cant_actual) if aplicar_limite else None

    # 5) Recorrer y ejecutar
    creados = actualizados = omitidos = duplicados = omitidos_por_plan = 0
    por_rubro = {}
    errores = []
    creados_ean = set()      # EANs ya creados en ESTE archivo (evita duplicar)
    creados_nombre = set()   # nombres ya creados en ESTE archivo

    for fila in filas:
        nombre = celda(fila, col_nombre)
        precio = parse_precio(celda(fila, col_precio))
        ean = ean_valido(celda(fila, col_ean))
        marca = celda(fila, col_marca) or None

        # mismas omisiones que el preview
        if not nombre and precio is None:
            continue
        if not nombre or precio is None:
            omitidos += 1
            continue

        nnorm = norm_nombre(nombre)

                # --- match contra lo que YA existe: SOLO por EAN ---
        # (los nombres se están corrigiendo, así que el match por nombre
        #  crearía duplicados; por eso lo eliminamos.)
        if not ean:
            omitidos_sin_ean += 1
            continue

        pid = por_ean.get(ean)

        if pid:
            # --- ACTUALIZAR: solo el precio ---
            ok, msg = db.update_product(pid, {"precio_prod": precio})
            if ok:
                actualizados += 1
            else:
                errores.append({"nombre": nombre, "error": msg})
            continue

        # --- ¿ya lo creamos en ESTE archivo? entonces es duplicado interno ---
        if (ean and ean in creados_ean) or (nnorm in creados_nombre):
            duplicados += 1
            continue

        # --- límite de plan: solo cuenta cuando importa el propio comercio en plan free ---
        if cupo_restante is not None and creados >= cupo_restante:
            omitidos_por_plan += 1
            continue

        # --- CREAR: nuevo, con categoria automatica ---
        cate_id, cate_prod = clasificar_rubro(nombre)
        nuevo = {
            "nombre_prod": nombre,
            "precio_prod": precio,
            "ean_prod": ean,               # puede ser None
            "marca_prod": marca,
            "cate_prod": cate_prod,
            "cate_id": cate_id,            # int (FK a cate_producto.id)
            "comercio_prod": nombre_comer,
            "unidad_prod": "Unidad",       # NOT NULL en la tabla; default generico
            "cantidad_prod": 1,            # NOT NULL en la tabla; default generico
            "activo_prod": True,
        }
        ok, msg = db.create_product(nuevo)
        if ok:
            creados += 1
            por_rubro[cate_prod] = por_rubro.get(cate_prod, 0) + 1
            if ean:
                creados_ean.add(ean)
            creados_nombre.add(nnorm)
        else:
            errores.append({"nombre": nombre, "error": msg})

    return {
        "comercio": nombre_comer,
        "plan": plan_comer,
        "creados": creados,
        "actualizados": actualizados,
        "omitidos": omitidos,
        "omitidos_por_plan": omitidos_por_plan,
        "duplicados": duplicados,
        "errores": len(errores),
        "limite_plan_free": LIMITE_PRODUCTOS_PLAN_FREE if aplicar_limite else None,
        "por_rubro": dict(sorted(por_rubro.items(), key=lambda kv: -kv[1])),
        "detalle_errores": errores[:30],
    }


# ============================================================
# IMPORTACIÓN DE PRODUCTOS POR ARCHIVO — Paso 1: PREVISUALIZACIÓN
# Pegar en main.py, ANTES del bloque  if __name__ == "__main__":
# No escribe nada en la base: solo analiza y clasifica.
# El mapeo viene con el preset del POS de tus comercios por defecto,
# pero es parametrizable (si aparece otro formato, se cambian los números).
# ============================================================

@app.post("/api/v1/comercios/{comercio_id}/productos/preview", tags=["Comercio Import"])
async def preview_import_productos(
    comercio_id: str,
    file: UploadFile = File(...),
    # --- Mapeo (preset del POS actual; columnas en base 0) ---
    encoding: str = Form("latin-1"),
    separador: str = Form(";"),
    filas_saltar: int = Form(5),
    col_nombre: int = Form(2),
    col_precio: int = Form(9),
    col_ean: int = Form(0),
    col_marca: int = Form(6),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Analiza un archivo de productos y devuelve qué se ACTUALIZARÍA, qué se
    CREARÍA y qué se OMITIRÍA (con motivo), sin tocar la base.
    Solo admin (por ahora la carga la hace el admin desde el detalle del comercio).
    """
    import io, csv, re

    set_user_from_token(db, authorization)
    _autorizar_import(db, comercio_id)

    # 1) Comercio (para el nombre y para cruzar sus productos)
    com = db.supabase.table("comercio")\
        .select("nombre_comer, plan_comer")\
        .eq("id_comer", comercio_id).limit(1).execute()
    if not com.data:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    nombre_comer = com.data[0]["nombre_comer"]
    plan_comer = (com.data[0].get("plan_comer") or "free").lower()

    # 2) Leer y parsear el archivo
    try:
        contenido = await file.read()
        texto = contenido.decode(encoding, errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo ({encoding}): {e}")

    lector = csv.reader(io.StringIO(texto), delimiter=separador)
    filas = list(lector)
    filas = filas[filas_saltar:] if filas_saltar > 0 else filas

    # 3) Helpers
    def celda(fila, idx):
        return (fila[idx].strip() if 0 <= idx < len(fila) else "")

    def parse_precio(s):
        s = (s or "").strip()
        if not s:
            return None
        # locale AR: punto = miles, coma = decimales
        s = s.replace(".", "").replace(",", ".")
        try:
            v = float(s)
            return v if v > 0 else None
        except ValueError:
            return None

    def norm_nombre(s):
        return re.sub(r"\s+", " ", (s or "").strip().lower())

    def ean_valido(s):
        s = (s or "").strip()
        if not s or "e+" in s.lower():   # descarta notación científica (EAN roto por Excel)
            return None
        return s if re.fullmatch(r"\d{12,13}", s) else None

    # 4) Productos que YA tiene el comercio (para clasificar)
    existentes = db.supabase.table("producto")\
        .select("id_prod, nombre_prod, ean_prod")\
        .ilike("comercio_prod", nombre_comer)\
        .eq("activo_prod", True).limit(5000).execute()
    por_ean, por_nombre = {}, {}
    for p in (existentes.data or []):
        e = (p.get("ean_prod") or "").strip()
        if e:
            por_ean[e] = p["id_prod"]
        n = norm_nombre(p.get("nombre_prod"))
        if n:
            por_nombre.setdefault(n, p["id_prod"])
    cant_actual = len(existentes.data or [])

    # 5) Clasificar
    actualizar, crear, omitidos = [], [], []
    for fila in filas:
        nombre = celda(fila, col_nombre)
        precio = parse_precio(celda(fila, col_precio))
        ean = ean_valido(celda(fila, col_ean))
        marca = celda(fila, col_marca)

        if not nombre and precio is None:
            continue  # fila totalmente vacía / basura: se ignora en silencio
        if not nombre:
            omitidos.append({"nombre": "(sin nombre)", "motivo": "fila sin nombre"})
            continue
        if precio is None:
            omitidos.append({"nombre": nombre, "motivo": "sin precio"})
            continue

        item = {"nombre": nombre, "precio": precio, "ean": ean, "marca": marca}
        if ean and ean in por_ean:
            item["match"] = "EAN"
            actualizar.append(item)
        elif norm_nombre(nombre) in por_nombre:
            item["match"] = "nombre"
            actualizar.append(item)
        else:
            crear.append(item)

    # 6) Chequeo de límite de plan
    total_despues = cant_actual + len(crear)
    excede_plan = (plan_comer == "free") and (total_despues > LIMITE_PRODUCTOS_PLAN_FREE)

    return {
        "comercio": nombre_comer,
        "plan": plan_comer,
        "resumen": {
            "actualizar": len(actualizar),
            "crear": len(crear),
            "omitidos": len(omitidos),
            "productos_actuales": cant_actual,
            "total_despues": total_despues
        },
        "excede_plan_free": excede_plan,
        "limite_plan_free": LIMITE_PRODUCTOS_PLAN_FREE,
        "muestra_actualizar": actualizar[:15],
        "muestra_crear": crear[:15],
        "omitidos": omitidos[:50],
        "mapeo_usado": {
            "encoding": encoding, "separador": separador, "filas_saltar": filas_saltar,
            "col_nombre": col_nombre, "col_precio": col_precio,
            "col_ean": col_ean, "col_marca": col_marca
        }
    }

# ============================================================
#  BACKFILL DE EAN  —  endpoint de una sola vez
#  Pegar en main.py junto a los otros endpoints de "Comercio Import",
#  ANTES de  `if __name__ == "__main__":`.
#
#  Para qué sirve:
#  Rellena ean_prod en los productos YA cargados del comercio que
#  todavía no lo tengan, tomando el EAN del CSV y matcheando por
#  NOMBRE normalizado. Está pensado para correr UNA vez, antes de
#  pasar el importador a "match solo-EAN".
#
#  Seguridad de datos:
#  - NO pisa EAN existentes: solo toca productos con ean_prod vacío.
#  - dry_run=True por DEFECTO: primero previsualiza, no escribe nada.
#    Revisás el reporte y, si está OK, lo volvés a correr con
#    dry_run=false para aplicar.
#  - No asigna el mismo EAN a dos productos distintos en la misma corrida.
#  - Update directo (solo ean_prod): no toca fecha_prod ni el historial.
#
#  ⚠️ El match es por NOMBRE. Corré esto con un CSV cuyos nombres
#     coincidan con los de la base ACTUAL. Si ya corregiste nombres,
#     esos productos van a quedar en "sin_match_en_csv" y hay que
#     resolverlos aparte.
# ============================================================

@app.post("/api/v1/comercios/{comercio_id}/productos/backfill-ean", tags=["Comercio Import"])
async def backfill_ean_productos(
    comercio_id: str,
    file: UploadFile = File(...),
    # --- Mapeo (mismo preset que el importador; columnas en base 0) ---
    encoding: str = Form("latin-1"),
    separador: str = Form(";"),
    filas_saltar: int = Form(5),
    col_nombre: int = Form(2),
    col_ean: int = Form(0),
    # --- Seguridad: por defecto NO escribe, solo informa ---
    dry_run: bool = Form(True),
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Rellena ean_prod (por nombre) en los productos del comercio que no lo tengan.
    dry_run=True (default) => no escribe, solo devuelve qué haría.
    Solo admin o comercio verificado sobre su propio id_comer.
    """
    import io, csv, re

    set_user_from_token(db, authorization)
    _autorizar_import(db, comercio_id)

    # 1) Comercio (nombre para cruzar sus productos)
    com = db.supabase.table("comercio")\
        .select("nombre_comer")\
        .eq("id_comer", comercio_id).limit(1).execute()
    if not com.data:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    nombre_comer = com.data[0]["nombre_comer"]

    # 2) Leer y parsear el archivo
    try:
        contenido = await file.read()
        texto = contenido.decode(encoding, errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo ({encoding}): {e}")

    lector = csv.reader(io.StringIO(texto), delimiter=separador)
    filas = list(lector)
    filas = filas[filas_saltar:] if filas_saltar > 0 else filas

    # 3) Helpers (mismos criterios que el importador)
    def celda(fila, idx):
        return (fila[idx].strip() if 0 <= idx < len(fila) else "")

    def norm_nombre(s):
        return re.sub(r"\s+", " ", (s or "").strip().lower())

    def ean_valido(s):
        s = (s or "").strip()
        if not s or "e+" in s.lower():
            return None
        return s if re.fullmatch(r"\d{12,13}", s) else None

    # 4) Mapa nombre_normalizado -> EAN (desde el CSV). Primera aparición gana.
    ean_por_nombre = {}
    for fila in filas:
        n = norm_nombre(celda(fila, col_nombre))
        ean = ean_valido(celda(fila, col_ean))
        if n and ean:
            ean_por_nombre.setdefault(n, ean)

    # 5) Productos del comercio (para detectar los que están sin EAN)
    existentes = db.supabase.table("producto")\
        .select("id_prod, nombre_prod, ean_prod")\
        .ilike("comercio_prod", nombre_comer)\
        .eq("activo_prod", True).limit(5000).execute()

    actualizados = 0
    sin_match = 0
    ya_tenian = 0
    ean_repetido = 0
    sin_ean_total = 0
    errores = []
    plan_cambios = []            # para dry_run: qué se asignaría
    eans_ya_asignados = set()    # no dar el mismo EAN a dos productos

    for p in (existentes.data or []):
        pid = p["id_prod"]
        ean_actual = (p.get("ean_prod") or "").strip()
        if ean_actual:
            ya_tenian += 1
            continue

        sin_ean_total += 1
        n = norm_nombre(p.get("nombre_prod"))
        ean = ean_por_nombre.get(n)

        if not ean:
            sin_match += 1
            continue
        if ean in eans_ya_asignados:
            ean_repetido += 1
            continue

        eans_ya_asignados.add(ean)
        plan_cambios.append({
            "id_prod": pid,
            "nombre_prod": p.get("nombre_prod"),
            "ean_asignado": ean
        })

        if not dry_run:
            try:
                db.supabase.table("producto")\
                    .update({"ean_prod": ean})\
                    .eq("id_prod", pid).execute()
                actualizados += 1
            except Exception as e:
                errores.append({"id_prod": pid, "error": str(e)})

    return {
        "comercio": nombre_comer,
        "dry_run": dry_run,
        "productos_sin_ean": sin_ean_total,
        "eans_disponibles_en_csv": len(ean_por_nombre),
        # en dry_run informa cuántos SE ASIGNARÍAN; en real, cuántos se aplicaron
        "backfilleados": (len(plan_cambios) if dry_run else actualizados),
        "sin_match_en_csv": sin_match,
        "ean_repetido_omitido": ean_repetido,
        "ya_tenian_ean": ya_tenian,
        "errores": len(errores),
        "muestra_cambios": plan_cambios[:40],
        "detalle_errores": errores[:20],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)