import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from database_manager import DatabaseManager
from datetime import datetime
import re
from collections import defaultdict

db = DatabaseManager()

def normalize_name(nombre):
    if not nombre: return ''
    n = nombre.lower().strip()
    stopwords = {'de','del','la','el','los','las','un','una','y','o','e','u','por','para','con','sin'}
    n = ' '.join([w for w in n.split() if w not in stopwords])
    n = re.sub(r'[^a-z0-9]', '', n)
    return n

print('Obteniendo productos...')
resp = db.supabase.table('producto').select('id_prod,nombre_prod,precio_prod,provee_prod,fecha_prod').eq('activo_prod', True).execute()
products = resp.data or []
print(f'   {len(products)} productos activos')

groups = defaultdict(list)
for p in products:
    key = (normalize_name(p.get('nombre_prod','')), p.get('provee_prod','').strip().lower())
    if key[0] and key[1]:
        groups[key].append(p)

duplicates = {k:v for k,v in groups.items() if len(v) > 1}
if not duplicates:
    print('No hay duplicados')
    exit()

print(f'\n{len(duplicates)} grupos con duplicados')
for (norm, prov), group in list(duplicates.items())[:5]:
    print(f'  [{prov}]')
    for p in group:
        print(f'    - "{p["nombre_prod"]}" ${p["precio_prod"]}')

confirm = input('\nEscribir "fusionar" para confirmar: ')
if confirm.strip().lower() != 'fusionar':
    print('Cancelado')
    exit()

for (norm, prov), group in duplicates.items():
    sorted_prods = sorted(group, key=lambda x: x.get('fecha_prod') or '1970-01-01', reverse=True)
    master = sorted_prods[0]
    dups = sorted_prods[1:]
    master_id = master['id_prod']
    master_precio = master.get('precio_prod')
    master_nombre = master.get('nombre_prod','')
    for p in sorted_prods:
        if len(p.get('nombre_prod','').strip()) > len(master_nombre.strip()):
            master_nombre = p.get('nombre_prod','')
    
    if master_nombre != master.get('nombre_prod',''):
        db.supabase.table('producto').update({'nombre_prod': master_nombre}).eq('id_prod', master_id).execute()
    
    print(f"\n'{master_nombre}' ({prov})")
    for dup in dups:
        dup_id = dup['id_prod']
        dup_precio = dup.get('precio_prod')
        dup_fecha = dup.get('fecha_prod') or datetime.now().isoformat()
        
        if dup_precio is not None and dup_precio != master_precio:
            db.supabase.table('historial_precios').insert({
                'id_prod': master_id, 'precio': dup_precio, 'fecha_registro': dup_fecha
            }).execute()
            print(f'  + Precio ${dup_precio} migrado')
        
        db.supabase.table('producto').update({'activo_prod': False}).eq('id_prod', dup_id).execute()
        print(f'  + Desactivado: {dup["nombre_prod"]}')

print('\nMigracion completada')
