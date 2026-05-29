# routers/categorias.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import CategoriaProducto
from pydantic import BaseModel
from uuid import UUID

router = APIRouter(prefix="/categorias", tags=["categorias"])

# ─── Schemas ───
class CategoriaBase(BaseModel):
    nombre_cate: str
    icono_cate: str | None = None
    color: str | None = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre_cate: str | None = None
    icono_cate: str | None = None
    color: str | None = None

class CategoriaResponse(CategoriaBase):
    id_cate: UUID
    cantidad_prod: int = 0

    class Config:
        from_attributes = True

# ─── Endpoints ───

@router.get("", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    """Lista todas las categorías con conteo de productos."""
    categorias = db.query(CategoriaProducto).all()

    resultado = []
    for cat in categorias:
        cantidad = db.query(Producto).filter(Producto.cate_prod == cat.nombre_cate).count()
        resultado.append({
            "id_cate": cat.id_cate,
            "nombre_cate": cat.nombre_cate,
            "icono_cate": cat.icono_cate,
            "color": cat.color,
            "cantidad_prod": cantidad
        })

    return resultado

@router.get("/{id_cate}", response_model=CategoriaResponse)
def obtener_categoria(id_cate: UUID, db: Session = Depends(get_db)):
    """Obtiene una categoría por ID."""
    categoria = db.query(CategoriaProducto).filter(CategoriaProducto.id_cate == id_cate).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    cantidad = db.query(Producto).filter(Producto.cate_prod == categoria.nombre_cate).count()
    return {
        "id_cate": categoria.id_cate,
        "nombre_cate": categoria.nombre_cate,
        "icono_cate": categoria.icono_cate,
        "color": categoria.color,
        "cantidad_prod": cantidad
    }

@router.post("", response_model=CategoriaResponse, status_code=201)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    """Crea una nueva categoría."""
    existe = db.query(CategoriaProducto).filter(
        CategoriaProducto.nombre_cate == categoria.nombre_cate
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")

    nueva = CategoriaProducto(**categoria.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {
        "id_cate": nueva.id_cate,
        "nombre_cate": nueva.nombre_cate,
        "icono_cate": nueva.icono_cate,
        "color": nueva.color,
        "cantidad_prod": 0
    }

@router.put("/{id_cate}", response_model=CategoriaResponse)
def actualizar_categoria(
    id_cate: UUID, 
    categoria: CategoriaUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza una categoría existente."""
    existente = db.query(CategoriaProducto).filter(CategoriaProducto.id_cate == id_cate).first()
    if not existente:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    update_data = categoria.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existente, key, value)

    db.commit()
    db.refresh(existente)

    cantidad = db.query(Producto).filter(Producto.cate_prod == existente.nombre_cate).count()
    return {
        "id_cate": existente.id_cate,
        "nombre_cate": existente.nombre_cate,
        "icono_cate": existente.icono_cate,
        "color": existente.color,
        "cantidad_prod": cantidad
    }

@router.delete("/{id_cate}", status_code=204)
def eliminar_categoria(id_cate: UUID, db: Session = Depends(get_db)):
    """Elimina una categoría (solo si no tiene productos asociados)."""
    categoria = db.query(CategoriaProducto).filter(CategoriaProducto.id_cate == id_cate).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    cantidad = db.query(Producto).filter(Producto.cate_prod == categoria.nombre_cate).count()
    if cantidad > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar: tiene {cantidad} productos asociados"
        )

    db.delete(categoria)
    db.commit()
    return None
