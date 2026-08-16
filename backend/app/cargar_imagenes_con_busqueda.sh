#!/bin/bash
# Script de integración: Búsqueda Web + Carga a Supabase
# Uso: ./cargar_imagenes_con_busqueda.sh archivo_productos.csv

set -e  # Detener en error

CSV_INPUT="$1"
OUTPUT_DIR="./salida_carga"

if [ -z "$CSV_INPUT" ]; then
    echo "❌ Uso: $0 archivo_productos.csv"
    exit 1
fi

if [ ! -f "$CSV_INPUT" ]; then
    echo "❌ Archivo no existe: $CSV_INPUT"
    exit 1
fi

echo "🚀 INICIANDO PROCESO COMPLETO DE IMÁGENES"
echo "========================================="
echo ""

# 1. Crear directorios
mkdir -p "$OUTPUT_DIR"

# 2. Buscar imágenes en toda la web
echo "📡 PASO 1: Buscando imágenes en la web..."
python buscar_imagenes_web.py \
    --csv "$CSV_INPUT" \
    --col-nombre "Descripción" \
    --col-ean "EAN" \
    --col-marca "Marca" \
    --output "$OUTPUT_DIR/resultados_busqueda.json" \
    --output-csv "$OUTPUT_DIR/imagenes_encontradas.csv" \
    --download-dir "$OUTPUT_DIR/imagenes" \
    --limit 9999 \
    --delay 1.5

if [ $? -ne 0 ]; then
    echo "❌ Error en la búsqueda de imágenes"
    exit 1
fi

echo ""
echo "📤 PASO 2: Cargando imágenes a Supabase..."
python cargar_imagenes_catalogo.py \
    --csv "$OUTPUT_DIR/imagenes_encontradas.csv" \
    --col-nombre "nombre" \
    --col-ean "ean" \
    --col-imagen "url_imagen" \
    --aplicar \
    --solo-sin-foto \
    --delay 0.5

if [ $? -ne 0 ]; then
    echo "❌ Error en la carga de imágenes"
    exit 1
fi

echo ""
echo "🎉 PROCESO COMPLETADO EXITOSAMENTE"
echo "==================================="
echo "📁 Resultados guardados en: $OUTPUT_DIR"
echo "   - resultados_busqueda.json: Detalle de búsquedas"
echo "   - imagenes_encontradas.csv: URLs encontradas"
echo "   - imagenes/: Imágenes descargadas localmente"
echo ""
echo "✅ Verificar en la vitrina que las imágenes se muestren correctamente."