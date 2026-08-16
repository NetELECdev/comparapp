#!/usr/bin/env python3
"""
BÚSQUEDA DE IMÁGENES EN MÚLTIPLES FUENTES WEB
Diseñado para ComparApp - Busca imágenes de productos en toda la web.

FUENTES SOPORTADAS:
  1. Google Custom Search API (imágenes de toda la web)
  2. Open Food Facts (alimentos empaquetados)
  3. Wikipedia (productos conocidos)
  4. DuckDuckGo (búsqueda alternativa)
  5. Flickr (Creative Commons)

USO:
    # Búsqueda básica (usa todas las fuentes):
    python buscar_imagenes_web.py --csv productos.csv --output resultados.json

    # Búsqueda con límite y sin descargar:
    python buscar_imagenes_web.py --csv productos.csv --no-download --limit 10

    # Fuentes específicas:
    python buscar_imagenes_web.py --csv productos.csv --fuentes google,off

    # Generar CSV para cargar_imagenes_catalogo.py:
    python buscar_imagenes_web.py --csv productos.csv --output-csv imagenes_encontradas.csv

REQUISITOS:
    pip install requests pillow beautifulsoup4 python-dotenv

VARIABLES DE ENTORNO (.env):
    GOOGLE_API_KEY=tu_api_key
    GOOGLE_CSE_ID=tu_cse_id
    SUPABASE_URL=https://...
    SUPABASE_SERVICE_KEY=tu_service_role_key
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# ─── Configuración ───────────────────────────────────────────────────────────
MAX_W, MAX_H = 800, 800
JPEG_QUALITY = 82
USER_AGENT = "ComparApp/1.0 (comparapp.home@gmail.com) - Buscador Imagenes"

# Headers para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ─── Fuentes de Búsqueda ────────────────────────────────────────────────────

@dataclass
class FuenteBusqueda:
    """Clase base para fuentes de búsqueda de imágenes."""
    nombre: str
    prioridad: int  # 1 = más prioritario

    def buscar(self, query: str) -> List[str]:
        """Busca imágenes y retorna lista de URLs."""
        raise NotImplementedError


class GoogleImages(FuenteBusqueda):
    """Búsqueda en Google usando Custom Search API."""
    
    def __init__(self):
        super().__init__("google", 1)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self.disponible = bool(self.api_key and self.cse_id)

    def buscar(self, query: str) -> List[str]:
        if not self.disponible:
            return []
        
        # Buscar imágenes
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "searchType": "image",
            "num": 5,
            "imgSize": "medium",
            "safe": "active"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return [item["link"] for item in data.get("items", [])]
        except Exception as e:
            print(f"    ⚠️ Error en Google: {e}")
        
        return []


class OpenFoodFacts(FuenteBusqueda):
    """Búsqueda en Open Food Facts (especializado en alimentos)."""
    
    def __init__(self):
        super().__init__("off", 2)

    def buscar(self, query: str) -> List[str]:
        urls = []
        
        # Primero intentar por EAN si el query parece un código
        if query.isdigit() and len(query) in (8, 13):
            product_url = f"https://world.openfoodfacts.org/api/v2/product/{query}.json"
            try:
                resp = requests.get(product_url, headers={"User-Agent": USER_AGENT}, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == 1:
                        product = data.get("product", {})
                        for key in ["image_url", "image_front_url", "image_front_small_url"]:
                            if product.get(key):
                                urls.append(product[key])
                        return urls
            except Exception:
                pass
        
        # Búsqueda por texto
        search_url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 3
        }
        
        try:
            resp = requests.get(search_url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for product in data.get("products", []):
                    for key in ["image_url", "image_front_url"]:
                        if product.get(key):
                            urls.append(product[key])
                            break
                return urls
        except Exception as e:
            print(f"    ⚠️ Error en OFF: {e}")
        
        return urls


class WikipediaImages(FuenteBusqueda):
    """Búsqueda en Wikipedia (bueno para productos conocidos)."""
    
    def __init__(self):
        super().__init__("wikipedia", 3)

    def buscar(self, query: str) -> List[str]:
        urls = []
        
        # Buscar artículo en Wikipedia
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1
        }
        
        try:
            resp = requests.get(search_url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("search", [])
                if pages:
                    title = pages[0]["title"]
                    # Obtener imágenes del artículo
                    img_params = {
                        "action": "query",
                        "titles": title,
                        "prop": "images",
                        "format": "json",
                        "imlimit": 3
                    }
                    resp2 = requests.get(search_url, params=img_params, headers={"User-Agent": USER_AGENT}, timeout=30)
                    if resp2.status_code == 200:
                        data2 = resp2.json()
                        for page in data2.get("query", {}).get("pages", {}).values():
                            for img in page.get("images", []):
                                if not img.get("title", "").lower().endswith((".svg", ".png")):
                                    # Obtener URL de la imagen
                                    img_url = self._get_image_url(img.get("title", ""))
                                    if img_url:
                                        urls.append(img_url)
        except Exception as e:
            print(f"    ⚠️ Error en Wikipedia: {e}")
        
        return urls

    def _get_image_url(self, filename: str) -> Optional[str]:
        """Obtiene la URL real de una imagen de Wikipedia."""
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": filename,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }
        try:
            resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for page in data.get("query", {}).get("pages", {}).values():
                    if page.get("imageinfo"):
                        return page["imageinfo"][0]["url"]
        except Exception:
            pass
        return None


class DuckDuckGoImages(FuenteBusqueda):
    """Búsqueda en DuckDuckGo (alternativa gratuita a Google)."""
    
    def __init__(self):
        super().__init__("duckduckgo", 4)

    def buscar(self, query: str) -> List[str]:
        urls = []
        url = "https://duckduckgo.com/i.js"
        params = {
            "q": query,
            "o": "json",
            "p": 1,
            "f": ",,,",
            "l": "en-us",
            "s": 0
        }
        
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for result in data.get("results", [])[:3]:
                    if result.get("image"):
                        urls.append(result["image"])
        except Exception as e:
            print(f"    ⚠️ Error en DuckDuckGo: {e}")
        
        return urls


class FlickrImages(FuenteBusqueda):
    """Búsqueda en Flickr (Creative Commons)."""
    
    def __init__(self):
        super().__init__("flickr", 5)
        self.api_key = os.getenv("FLICKR_API_KEY")
        self.disponible = bool(self.api_key)

    def buscar(self, query: str) -> List[str]:
        if not self.disponible:
            return []
        
        urls = []
        url = "https://api.flickr.com/services/rest/"
        params = {
            "method": "flickr.photos.search",
            "api_key": self.api_key,
            "text": query,
            "content_type": 1,  # Photos only
            "license": "1,2,3,4,5,6",  # Creative Commons
            "media": "photos",
            "per_page": 3,
            "format": "json",
            "nojsoncallback": 1,
            "sort": "relevance"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for photo in data.get("photos", {}).get("photo", []):
                    farm = photo.get("farm")
                    server = photo.get("server")
                    photo_id = photo.get("id")
                    secret = photo.get("secret")
                    if all([farm, server, photo_id, secret]):
                        img_url = f"https://farm{farm}.staticflickr.com/{server}/{photo_id}_{secret}_z.jpg"
                        urls.append(img_url)
        except Exception as e:
            print(f"    ⚠️ Error en Flickr: {e}")
        
        return urls


# ─── Sistema de Búsqueda ───────────────────────────────────────────────────

class BuscadorImagenes:
    """Orquestador de búsqueda en múltiples fuentes."""
    
    def __init__(self, fuentes: Optional[List[str]] = None):
        self.fuentes_disponibles = {
            "google": GoogleImages(),
            "off": OpenFoodFacts(),
            "wikipedia": WikipediaImages(),
            "duckduckgo": DuckDuckGoImages(),
            "flickr": FlickrImages()
        }
        
        # Si no se especifican fuentes, usar todas
        if fuentes is None:
            fuentes = list(self.fuentes_disponibles.keys())
        
        self.fuentes = [
            self.fuentes_disponibles[fuente]
            for fuente in fuentes
            if fuente in self.fuentes_disponibles
        ]
        # Ordenar por prioridad
        self.fuentes.sort(key=lambda x: x.prioridad)
        
        # Cache de búsquedas para evitar duplicados
        self.cache = {}
    
    def buscar(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """
        Busca imágenes en todas las fuentes configuradas.
        Retorna: {
            'imagenes': [{'url': str, 'fuente': str}, ...],
            'total_encontradas': int,
            'fuentes_usadas': [str, ...]
        }
        """
        # Revisar caché
        cache_key = f"{query}_{limit}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        resultados = []
        fuentes_usadas = []
        
        for fuente in self.fuentes:
            if len(resultados) >= limit:
                break
            
            print(f"      🔍 Buscando en {fuente.nombre}...", end="")
            urls = fuente.buscar(query)
            print(f" {len(urls)} encontradas")
            
            if urls:
                fuentes_usadas.append(fuente.nombre)
                for url in urls:
                    if len(resultados) >= limit:
                        break
                    # Evitar duplicados
                    if not any(r["url"] == url for r in resultados):
                        resultados.append({
                            "url": url,
                            "fuente": fuente.nombre
                        })
            
            # Pequeña pausa entre fuentes
            time.sleep(0.5)
        
        # Guardar en caché
        resultado = {
            "imagenes": resultados,
            "total_encontradas": len(resultados),
            "fuentes_usadas": fuentes_usadas,
            "query": query
        }
        self.cache[cache_key] = resultado
        return resultado


# ─── Procesamiento de Imágenes ─────────────────────────────────────────────

def descargar_y_optimizar(url: str) -> Optional[bytes]:
    """Descarga y optimiza una imagen desde URL."""
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=30, stream=True)
        
        if resp.status_code != 200:
            return None
        
        # Verificar que es una imagen
        content_type = resp.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            return None
        
        raw = resp.content
        
        # Optimizar con PIL
        try:
            img = Image.open(BytesIO(raw))
            # Exif transpose
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except:
                pass
            
            # Convertir a RGB
            if img.mode in ("RGBA", "P", "LA"):
                fondo = Image.new("RGB", img.size, (255, 255, 255))
                rgba = img.convert("RGBA")
                fondo.paste(rgba, mask=rgba.split()[-1])
                img = fondo
            else:
                img = img.convert("RGB")
            
            # Redimensionar
            img.thumbnail((MAX_W, MAX_H), Image.LANCZOS)
            
            # Guardar optimizado
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            return buf.getvalue()
        except Exception as e:
            print(f"    ⚠️ No se pudo optimizar: {e}")
            return raw
            
    except Exception as e:
        print(f"    ⚠️ Error descargando: {e}")
        return None


def es_url_imagen_valida(url: str) -> bool:
    """Verifica si la URL parece ser de una imagen válida."""
    # Extensiones de imagen comunes
    extensiones = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")
    url_lower = url.lower()
    return any(url_lower.endswith(ext) for ext in extensiones) or "images" in url_lower


# ─── Procesamiento Principal ──────────────────────────────────────────────

def leer_csv(csv_path: str, col_nombre: str, col_ean: str = None, 
             col_marca: str = None, skip_rows: int = 0,
             delimitador: str = ";", encoding: str = "utf-8") -> List[Dict]:
    """Lee CSV y prepara productos para búsqueda."""
    productos = []
    
    with open(csv_path, "r", encoding=encoding, newline="") as f:
        # Saltar filas de encabezado
        for _ in range(skip_rows):
            f.readline()
        
        reader = csv.DictReader(f, delimiter=delimitador)
        
        for row in reader:
            nombre = (row.get(col_nombre) or "").strip()
            if not nombre:
                continue
            
            ean = (row.get(col_ean) or "").strip() if col_ean else ""
            marca = (row.get(col_marca) or "").strip() if col_marca else ""
            
            # Crear queries de búsqueda
            queries = []
            if ean:
                queries.append(ean)
            queries.append(nombre)
            if marca:
                queries.append(f"{nombre} {marca}")
            queries.append(f"{nombre} producto")
            
            productos.append({
                "nombre": nombre,
                "ean": ean,
                "marca": marca,
                "queries": queries[:4],  # Limitar queries
                "raw": row
            })
    
    return productos


def generar_nombre_archivo(producto: Dict, url: str) -> str:
    """Genera nombre único para la imagen descargada."""
    # Hash de la URL para evitar duplicados
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    
    # Limpiar nombre del producto
    nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '_', producto["nombre"])[:30]
    
    return f"{nombre_limpio}_{url_hash}.jpg"


def main():
    parser = argparse.ArgumentParser(
        description="Busca imágenes de productos en múltiples fuentes web",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--csv", required=True, help="Ruta al CSV de productos")
    parser.add_argument("--col-nombre", required=True, help="Columna con nombre del producto")
    parser.add_argument("--col-ean", help="Columna con EAN (opcional)")
    parser.add_argument("--col-marca", help="Columna con marca (opcional)")
    parser.add_argument("--delimitador", default=";", help="Delimitador del CSV")
    parser.add_argument("--encoding", default="utf-8", help="Encoding del CSV")
    parser.add_argument("--skip-rows", type=int, default=0, help="Filas de encabezado a saltar")
    
    parser.add_argument("--output", default="resultados_busqueda.json", 
                        help="JSON de salida con resultados")
    parser.add_argument("--output-csv", help="CSV de salida para cargar_imagenes_catalogo.py")
    parser.add_argument("--download-dir", default="./imagenes_buscadas", 
                        help="Carpeta para descargar imágenes")
    
    parser.add_argument("--fuentes", default="google,off,wikipedia,duckduckgo,flickr",
                        help="Fuentes a usar (separadas por coma)")
    parser.add_argument("--limit", type=int, default=10, 
                        help="Límite de productos a procesar")
    parser.add_argument("--max-imagenes", type=int, default=3, 
                        help="Máximo de imágenes por producto")
    parser.add_argument("--no-download", action="store_true", 
                        help="No descargar imágenes, solo buscar URLs")
    parser.add_argument("--delay", type=float, default=2.0, 
                        help="Segundos entre productos")
    
    args = parser.parse_args()
    
    # ─── Configurar fuentes ────────────────────────────────────────────────
    fuentes_list = [f.strip() for f in args.fuentes.split(",") if f.strip()]
    buscador = BuscadorImagenes(fuentes_list)
    
    # ─── Leer productos ────────────────────────────────────────────────────
    print("📖 Leyendo CSV...")
    productos = leer_csv(
        args.csv,
        col_nombre=args.col_nombre,
        col_ean=args.col_ean,
        col_marca=args.col_marca,
        skip_rows=args.skip_rows,
        delimitador=args.delimitador,
        encoding=args.encoding
    )
    print(f"   {len(productos)} productos encontrados\n")
    
    # ─── Procesar productos ───────────────────────────────────────────────
    resultados = []
    resultados_csv = []
    download_dir = Path(args.download_dir)
    if not args.no_download:
        download_dir.mkdir(parents=True, exist_ok=True)
    
    total = min(args.limit, len(productos))
    encontrados = 0
    fallidos = 0
    
    for i, prod in enumerate(productos[:total], 1):
        print(f"\n[{i}/{total}] {prod['nombre']}")
        if prod["ean"]:
            print(f"   EAN: {prod['ean']}")
        if prod["marca"]:
            print(f"   Marca: {prod['marca']}")
        
        # Buscar en todas las fuentes
        todas_las_imagenes = []
        todas_fuentes = []
        
        for query in prod["queries"]:
            if not query:
                continue
            print(f"   🔎 Query: '{query}'")
            resultado = buscador.buscar(query, limit=args.max_imagenes)
            todas_las_imagenes.extend(resultado["imagenes"])
            todas_fuentes.extend(resultado["fuentes_usadas"])
            
            # Si ya tenemos suficientes, salir
            if len(todas_las_imagenes) >= args.max_imagenes:
                break
        
        # Eliminar duplicados por URL
        vistas = set()
        imagenes_unicas = []
        for img in todas_las_imagenes:
            if img["url"] not in vistas:
                vistas.add(img["url"])
                imagenes_unicas.append(img)
        
        imagenes_unicas = imagenes_unicas[:args.max_imagenes]
        
        print(f"   ✅ Encontradas: {len(imagenes_unicas)} imágenes únicas")
        
        # Procesar cada imagen
        imagenes_procesadas = []
        for img in imagenes_unicas:
            # Descargar y optimizar (si no es --no-download)
            local_path = None
            if not args.no_download:
                print(f"      📥 Descargando: {img['url'][:60]}...", end="")
                data = descargar_y_optimizar(img["url"])
                if data:
                    filename = generar_nombre_archivo(prod, img["url"])
                    local_file = download_dir / filename
                    with open(local_file, "wb") as f:
                        f.write(data)
                    local_path = str(local_file)
                    print(f" OK ({len(data)//1024} KB)")
                    encontrados += 1
                else:
                    print(" ❌")
                    fallidos += 1
            else:
                # Si no descargamos, solo guardamos la URL
                print(f"      ✅ URL: {img['url'][:60]}...")
            
            imagenes_procesadas.append({
                "url": img["url"],
                "fuente": img["fuente"],
                "local_path": local_path
            })
        
        # Guardar resultado
        resultado_item = {
            "nombre": prod["nombre"],
            "ean": prod["ean"],
            "marca": prod["marca"],
            "imagenes": imagenes_procesadas,
            "total_encontradas": len(imagenes_procesadas),
            "fuentes_utilizadas": list(set(todas_fuentes))
        }
        resultados.append(resultado_item)
        
        # Para CSV de salida (cargar_imagenes_catalogo.py)
        for img in imagenes_procesadas[:1]:  # Solo la primera imagen
            resultados_csv.append({
                "nombre": prod["nombre"],
                "ean": prod["ean"],
                "marca": prod["marca"],
                "url_imagen": img["url"],
                "fuente": img["fuente"],
                "local_path": img["local_path"] or ""
            })
        
        time.sleep(args.delay)
    
    # ─── Guardar resultados ────────────────────────────────────────────────
    
    # JSON detallado
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "total_procesados": len(resultados),
            "total_encontrados": encontrados,
            "total_fallidos": fallidos,
            "resultados": resultados
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Resultados guardados en: {args.output}")
    
    # CSV para cargar_imagenes_catalogo.py
    if args.output_csv:
        with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["nombre", "ean", "marca", "url_imagen", "fuente", "local_path"])
            writer.writeheader()
            writer.writerows(resultados_csv)
        print(f"✅ CSV para carga guardado en: {args.output_csv}")
        print(f"   (Usalo con: cargar_imagenes_catalogo.py --csv {args.output_csv} --col-nombre nombre --col-ean ean --col-imagen url_imagen --aplicar)")
    
    # ─── Estadísticas ──────────────────────────────────────────────────────
    print("\n" + "="*50)
    print("📊 ESTADÍSTICAS")
    print("="*50)
    print(f"   Productos procesados: {len(resultados)}")
    print(f"   Imágenes encontradas: {encontrados}")
    print(f"   Fallos de descarga: {fallidos}")
    
    # Resumen por fuente
    fuentes_uso = {}
    for r in resultados:
        for fuente in r.get("fuentes_utilizadas", []):
            fuentes_uso[fuente] = fuentes_uso.get(fuente, 0) + 1
    
    if fuentes_uso:
        print("\n   Fuentes exitosas:")
        for fuente, count in sorted(fuentes_uso.items(), key=lambda x: -x[1]):
            print(f"     - {fuente}: {count} productos")
    
    print("\n💡 Próximos pasos:")
    print(f"   1. Revisar el JSON: cat {args.output}")
    if args.output_csv:
        print(f"   2. Ejecutar carga: python cargar_imagenes_catalogo.py --csv {args.output_csv} --col-nombre nombre --col-ean ean --col-imagen url_imagen --aplicar")
    print("   3. Verificar en la vitrina que las imágenes se muestren correctamente")


if __name__ == "__main__":
    main()