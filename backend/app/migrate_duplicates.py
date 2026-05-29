#!/usr/bin/env python3
"""migrate_duplicates.py v2 - con normalización de nombres"""

import os
import sys
import re
from datetime import datetime
from collections import defaultdict

try:
    from supabase_config import SupabaseConfig
    from supabase import create_client
except ImportError:
    print("❌ Error: No se encontró supabase_config.py")
    sys.exit(1)


def normalize_name(nombre: str) -> str:
    if not nombre:
        return ""
    normalized = nombre.lower().strip()
    stopwords = {'de', 'del', 'la', 'el', 'los', 'las', 'un', 'una', 'unos', 'unas',
                 'por', 'para', 'con', 'sin', 'sobre', 'entre', 'hacia', 'desde', 'y', 'o', 'e', 'u'}
    words = normalized.split()
    filtered = [w for w in words if w not in stopwords]
    normalized = ' '.join(filtered)
    normalized = re.sub(r'[^a-z0-9]', '', normalized)
    return normalized


def get_supabase_client():
    url = SupabaseConfig.get_url()
    key = os.getenv('SUPABASE_SERVICE_KEY', SupabaseConfig.get_anon_key())
    return create_client(url, key)


def fetch_all_active_products(supabase):
    print("📦 Obteniendo productos activos...")
    response = supabase.table('producto')\
        .select('id_prod, nombre_prod, precio_prod, provee_prod, fecha_prod, activo_prod')\
        .eq('activo_prod', True)\
        .execute()
    products = response.data or []
    print(f"   → {len(products)} productos encontrados")
    return products


def group_duplicates(products):
    groups = defaultdict(list)
    for p in products:
        prov = p.get('provee_prod', '').strip()
        nombre_norm = normalize_name(p.get('nombre_prod', ''))
        if nombre_norm and prov:
            groups[(nombre_norm, prov.lower())].append(p)
    return {k: v for k, v in groups.items() if len(v) > 1}


def merge_group(supabase, key, group):
    nombre_norm, proveedor = key
    sorted_prods = sorted(group, key=lambda x: x.get('fecha_prod') or '1970-01-01', reverse=True)
    master = sorted_prods[0]
    duplicates = sorted_prods[1:]
    master_id = master['id_prod']
    master_precio = master.get('precio_prod')
    
    # Nombre más largo
    master_nombre = master.get('nombre_prod', '')
    for p in sorted_prods:
        if len(p.get('nombre_prod', '').strip()) > len(master_nombre.strip()):
            master_nombre = p.get('nombre_prod', '')
    
    if master_nombre != master.get('nombre_prod', ''):
        supabase.table('producto').update({'nombre_prod': master_nombre}).eq('id_prod', master_id).execute()
    
    print(f"\n   🔀 '{master_nombre}' ({proveedor})")
    print(f"      Duplicados: {len(duplicates)}")
    
    migrated = 0
    for dup in duplicates:
        dup_id = dup['id_prod']
        dup_precio = dup.get('precio_prod')
        dup_fecha = dup.get('fecha_prod') or datetime.now().isoformat()
        
        if dup_precio is not None and dup_precio != master_precio:
            supabase.table('historial_precios').insert({
                'id_prod': master_id, 'precio': dup_precio, 'fecha_registro': dup_fecha
            }).execute()
            migrated += 1
            print(f"         ✓ Precio ${dup_precio} migrado")
        
        supabase.table('producto').update({'activo_prod': False}).eq('id_prod', dup_id).execute()
        print(f"         ✓ Duplicado desactivado")
    
    return migrated


def run_migration():
    print("=" * 60)
    print("  MIGRACIÓN: Fusionar duplicados (con normalización)")
    print("=" * 60)
    
    supabase = get_supabase_client()
    products = fetch_all_active_products(supabase)
    duplicates = group_duplicates(products)
    
    if not duplicates:
        print("✅ No hay duplicados.")
        return
    
    total = sum(len(v) - 1 for v in duplicates.values())
    print(f"\n🔍 Grupos: {len(duplicates)} | Duplicados: {total}")
    
    for (norm, prov), group in list(duplicates.items())[:3]:
        print(f"   • [{prov}] {norm}")
        for p in group:
            print(f"     - '{p.get('nombre_prod')}'")
    if len(duplicates) > 3:
        print(f"   ... y {len(duplicates) - 3} más")
    
    if input("\n⚡ Escribir 'fusionar' para confirmar: ").strip().lower() != 'fusionar':
        print("❌ Cancelado.")
        return
    
    migrated = sum(merge_group(supabase, k, v) for k, v in duplicates.items())
    print(f"\n✅ Listo. Precios migrados: {migrated}")


if __name__ == '__main__':
    run_migration()