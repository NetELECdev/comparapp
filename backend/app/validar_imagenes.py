#!/usr/bin/env python3
"""
VALIDADOR DE IMÁGENES ENCONTRADAS
Verifica que las URLs de imagen sean accesibles y tengan buen tamaño.
"""

import json
import sys
from typing import List, Dict
import requests
from PIL import Image
from io import BytesIO

def validar_imagen(url: str) -> Dict:
    """Valida una URL de imagen."""
    resultado = {
        "url": url,
        "valida": False,
        "tamano": 0,
        "dimensiones": (0, 0),
        "error": None
    }
    
    try:
        resp = requests.get(url, timeout=10, stream=True)
        if resp.status_code != 200:
            resultado["error"] = f"HTTP {resp.status_code}"
            return resultado
        
        # Verificar tamaño
        content_length = int(resp.headers.get("content-length", 0))
        resultado["tamano"] = content_length
        
        if content_length < 1024:  # Menos de 1KB
            resultado["error"] = "Imagen muy pequeña (<1KB)"
            return resultado
        
        # Verificar dimensiones
        img = Image.open(BytesIO(resp.content))
        resultado["dimensiones"] = img.size
        resultado["valida"] = True
        
        if img.size[0] < 100 or img.size[1] < 100:
            resultado["error"] = f"Dimensiones muy pequeñas: {img.size}"
            resultado["valida"] = False
            
    except Exception as e:
        resultado["error"] = str(e)
    
    return resultado

def main():
    if len(sys.argv) < 2:
        print("Uso: python validar_imagenes.py resultados_busqueda.json")
        sys.exit(1)
    
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    
    resultados = data.get("resultados", [])
    total = len(resultados)
    validas = 0
    invalidas = 0
    
    print(f"🔍 Validando {total} imágenes...\n")
    
    for item in resultados:
        print(f"\n📦 {item['nombre']}")
        for img in item.get("imagenes", []):
            print(f"   URL: {img['url'][:60]}...")
            validacion = validar_imagen(img['url'])
            if validacion["valida"]:
                print(f"   ✅ VÁLIDA - {validacion['dimensiones'][0]}x{validacion['dimensiones'][1]} - {validacion['tamano']//1024}KB")
                validas += 1
            else:
                print(f"   ❌ INVÁLIDA - {validacion['error']}")
                invalidas += 1
    
    print("\n" + "="*50)
    print(f"📊 Total: {validas + invalidas}")
    print(f"✅ Válidas: {validas}")
    print(f"❌ Inválidas: {invalidas}")

if __name__ == "__main__":
    main()