"""
ComparApp - API Backend
Autor: Fernando Silva
Versión: 1.0
Descripción:
    API FastAPI que conecta con Supabase usando los módulos
    supabase_config.py y database_manager.py
"""




from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

# Importar los módulos locales
from database_manager import DatabaseManager
from supabase_config import SupabaseConfig

# ---------------------------------------------------
# Inicialización general
# ---------------------------------------------------

app = FastAPI(
    title="ComparApp API",
    version="1.0.0",
    description="API de comparación de precios conectada a Supabase"
)

# Configurar CORS (importante para frontend en Nuxt o apps móviles)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: limitar al dominio real (Netlify, Vercel, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del administrador de base de datos
db = DatabaseManager()

# ---------------------------------------------------
# Middleware de registro de peticiones
# ---------------------------------------------------

from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    # 🔍 Log personalizado
    print(f"🛰️  {request.method} {request.url.path}?{request.url.query} "
          f"→ {response.status_code} ({process_time:.2f}ms)")

    return response


# ---------------------------------------------------
# Utilidades / dependencias
# ---------------------------------------------------

def get_db() -> DatabaseManager:
    """
    Dependency injection para obtener una instancia del manejador de base de datos.
    Si más adelante querés agregar autenticación, este método centraliza el acceso.
    """
    return db

# ---------------------------------------------------
# Endpoint raíz
# ---------------------------------------------------

@app.get("/", tags=["General"])
def home():
    """
    Endpoint raíz para verificar que el backend esté en ejecución.
    """
    return {
        "status": "ok",
        "app": "ComparApp API",
        "version": "1.0.0",
        "supabase_url": SupabaseConfig.get_url(),
        "database_connected": db._test_connection_simple()
    }

# ---------------------------------------------------
# Endpoints de autenticación
# ---------------------------------------------------

@app.post("/api/v1/forgot-password", tags=["Auth"])
def forgot_password(
    email: str,
    db: DatabaseManager = Depends(get_db)
):
    """
    Envía un email con link para resetear la contraseña.
    Siempre devuelve 200 para no revelar si el email existe.
    """
    db.reset_password_email(email)
    return {"message": "Si el email existe, recibirás un link para resetear tu contraseña."}

@app.post("/api/v1/register", tags=["Auth"])
def register_user(
    email: str,
    password: str,
    nombre_completo: str,
    telefono: Optional[str] = None,
    db: DatabaseManager = Depends(get_db)
):
    """
    Registro de usuario en Supabase (tabla 'users')
    """
    success, msg, user_data = db.register_user(email, password, nombre_completo, telefono)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "user": user_data}


@app.post("/api/v1/login", tags=["Auth"])
def login_user(email: str, password: str, db: DatabaseManager = Depends(get_db)):
    """
    Inicio de sesión en Supabase Auth y tabla personalizada 'users'
    """
    success, msg, user_data = db.login_user(email, password)
    if not success:
        raise HTTPException(status_code=401, detail=msg)
    return {"message": msg, "user": user_data}


@app.post("/api/v1/logout", tags=["Auth"])
def logout_user(db: DatabaseManager = Depends(get_db)):
    """
    Cierra la sesión local del usuario (solo backend).
    """
    db.logout_user()
    return {"message": "Sesión cerrada correctamente."}

# ---------------------------------------------------
# Endpoints de productos
# ---------------------------------------------------

@app.get("/api/v1/products", tags=["Productos"])
def get_all_products(
    q: Optional[str] = Query("", description="Término de búsqueda opcional"),
    limit: Optional[int] = Query(None, description="Límite de resultados para sugerencias"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Obtiene todos los productos activos o los que coincidan con el término de búsqueda.
    """
    success, msg, products = db.search_products(q, limit=limit)
    if not success:
        raise HTTPException(status_code=404, detail=msg)
    
    # Aplicar límite si se solicita (para sugerencias rápidas)
    if limit and limit > 0:
        products = products[:limit]
    
    return {"count": len(products), "results": products}

@app.get("/api/v1/products/{product_id}", tags=["Productos"])
def get_product_by_id(
    product_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """
    Obtiene un producto específico por su ID.
    """
    try:
        response = db.supabase.table('producto')\
            .select('*')\
            .eq('id_prod', product_id)\
            .eq('activo_prod', True)\
            .limit(1)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")

@app.post("/api/v1/products", tags=["Productos"])
def create_product(product_data: dict, db: DatabaseManager = Depends(get_db)):
    """
    Crea un nuevo producto (solo usuarios con rol 'admin')
    """
    success, msg = db.create_product(product_data)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@app.put("/api/v1/products/{product_id}", tags=["Productos"])
def update_product(product_id: str, product_data: dict, db: DatabaseManager = Depends(get_db)):
    """
    Actualiza un producto existente (solo admin)
    """
    success, msg = db.update_product(product_id, product_data)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@app.delete("/api/v1/products/{product_id}", tags=["Productos"])
def delete_product(product_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Elimina un producto (solo admin)
    """
    success, msg = db.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# ---------------------------------------------------
# Endpoints de proveedores
# ---------------------------------------------------

@app.get("/api/v1/proveedores", tags=["Proveedores"])
def search_proveedores(
    search: Optional[str] = Query("", description="Texto a buscar (nombre o representante)"),
    sort_by: Optional[str] = Query("nombre", description="Campo de ordenamiento"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Busca proveedores activos por nombre o representante.
    """
    proveedores, error = db.search_proveedores(search, sort_by)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"count": len(proveedores), "results": proveedores}


@app.get("/api/v1/proveedores/{proveedor_id}", tags=["Proveedores"])
def get_proveedor_by_id(proveedor_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Devuelve un proveedor por su ID.
    """
    proveedor, error = db.get_proveedor_by_id(proveedor_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return proveedor


@app.post("/api/v1/proveedores", tags=["Proveedores"])
def create_proveedor(proveedor_data: dict, db: DatabaseManager = Depends(get_db)):
    """
    Inserta un nuevo proveedor.
    """
    proveedor, error = db.insert_proveedor(proveedor_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Proveedor agregado correctamente", "data": proveedor}


@app.put("/api/v1/proveedores/{proveedor_id}", tags=["Proveedores"])
def update_proveedor(proveedor_id: str, update_data: dict, db: DatabaseManager = Depends(get_db)):
    """
    Actualiza los datos de un proveedor existente.
    """
    proveedor, error = db.update_proveedor(proveedor_id, update_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Proveedor actualizado", "data": proveedor}

# ---------------------------------------------------
# Endpoints de búsqueda avanzada
# ---------------------------------------------------

@app.get("/api/v1/search/price", tags=["Búsqueda avanzada"])
def search_by_price(
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    term: Optional[str] = Query("", description="Término de búsqueda"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Búsqueda de productos por rango de precio.
    """
    results = db.search_productos_by_precio(min_price, max_price, term)
    return {"count": len(results), "results": results}


@app.get("/api/v1/search/date", tags=["Búsqueda avanzada"])
def search_by_date(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    term: Optional[str] = Query(""),
    db: DatabaseManager = Depends(get_db)
):
    """
    Búsqueda de productos por rango de fecha.
    """
    results = db.search_productos_by_fecha(fecha_desde, fecha_hasta, term)
    return {"count": len(results), "results": results}

# ---------------------------------------------------
# Apagado y limpieza
# ---------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():
    """
    Cierra conexiones activas al cerrar el servidor.
    """
    db.close_connections()
    print("💤 Servidor detenido correctamente.")

# ---------------------------------------------------
# Modo standalone
# ---------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
