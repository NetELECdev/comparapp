"""
ARCHIVO: historial_endpoints.py
Pegá este contenido al final de main.py, ANTES del bloque
`if __name__ == "__main__":` (o después, no importa en FastAPI).

Estos endpoints sirven el historial de precios al frontend.
"""

# ---------------------------------------------------
# Endpoints de HISTORIAL DE PRECIOS
# ---------------------------------------------------

@app.get("/api/v1/historial/{product_id}", tags=["Historial"])
def get_historial_producto(
    product_id: str,
    dias: Optional[int] = Query(90, description="Días de historial a traer (default 90)"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Devuelve el historial de precios de un producto con estadísticas.
    """
    try:
        from datetime import datetime, timedelta

        # Fecha límite según parámetro
        fecha_desde = (datetime.now() - timedelta(days=dias)).isoformat()

        # Historial ordenado por fecha ASC (para el gráfico)
        historial_res = db.supabase.table('historial_precios')\
            .select('precio, fecha_registro')\
            .eq('id_prod', product_id)\
            .gte('fecha_registro', fecha_desde)\
            .order('fecha_registro', desc=False)\
            .execute()

        registros = historial_res.data or []

        # Precio actual del producto (ya es numeric, no necesita conversión)
        prod_res = db.supabase.table('producto')\
            .select('precio_prod')\
            .eq('id_prod', product_id)\
            .eq('activo_prod', True)\
            .limit(1)\
            .execute()

        if not prod_res.data or len(prod_res.data) == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        precio_actual = prod_res.data[0]['precio_prod']  # ← ya es numeric/float

        # Calcular referencias históricas
        ahora = datetime.now()

        def precio_hace(dias_atras: int):
            """Busca el precio más cercano a N días atrás."""
            limite = ahora - timedelta(days=dias_atras)
            candidatos = [
                r for r in registros
                if datetime.fromisoformat(str(r['fecha_registro']).replace('Z', '+00:00').replace('+00:00', '')) <= limite
            ]
            if candidatos:
                return candidatos[-1]['precio']  # ← ya es numeric
            return None

        precio_7d  = precio_hace(7)
        precio_30d = precio_hace(30)

        # % variación respecto a 30d
        variacion_30d = None
        if precio_actual and precio_30d and precio_30d > 0:
            variacion_30d = round((precio_actual - precio_30d) / precio_30d * 100, 1)

        # % variación respecto a 7d
        variacion_7d = None
        if precio_actual and precio_7d and precio_7d > 0:
            variacion_7d = round((precio_actual - precio_7d) / precio_7d * 100, 1)

        # Mín / máx histórico
        precios_lista = [r['precio'] for r in registros]
        precios_lista.append(precio_actual)

        precio_minimo = min(precios_lista) if precios_lista else None
        precio_maximo = max(precios_lista) if precios_lista else None

        # Serie para el gráfico (incluye precio actual al final)
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
    Útil para cargar precios históricos iniciales.
    """
    set_user_from_token(db, authorization)
    if not db.is_admin():
        raise HTTPException(status_code=403, detail="Solo administradores")
    try:
        from datetime import datetime
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