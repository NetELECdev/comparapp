# -*- coding: utf-8 -*-
"""
Importa los productos del CSV al comercio (endpoint /importar).
ESCRIBE en la base. Se loguea solo, sube el archivo, imprime el resumen.
"""
import json
import requests

# ===== COMPLETAR =====
EMAIL    = "netelectaller@gmail.com"
PASSWORD = "03126900"
ARCHIVO  = "listado_de_productos_recortado.csv"

BASE_URL = "http://localhost:8000/api/v1"
# =====================

COMERCIO_ID = "4332ad42-3243-4cb6-a0c0-3deaacb8d6e3"   # Carniceria "Los Amigos"

# 1) Login para obtener el token
print("Logueando...")
r = requests.post(f"{BASE_URL}/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
if r.status_code != 200:
    print("ERROR en login:", r.status_code, r.text[:300])
    raise SystemExit
data = r.json()
token = (data.get("user") or {}).get("access_token") or data.get("access_token")
if not token:
    print("No encontré el token. Respuesta:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:800])
    raise SystemExit
print("Token OK")

# 2) Llamar al IMPORT con el archivo (mapeo con los defaults del POS)
print("Subiendo archivo al import... (puede tardar varios minutos)")
with open(ARCHIVO, "rb") as f:
    resp = requests.post(
        f"{BASE_URL}/comercios/{COMERCIO_ID}/productos/importar",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (ARCHIVO, f, "text/csv")},
        timeout=900,
    )

# 3) Mostrar la respuesta cruda (funciona con el formato del importar)
print("Status:", resp.status_code)
try:
    out = resp.json()
except Exception:
    print(resp.text[:1000]); raise SystemExit

print(json.dumps(out, indent=2, ensure_ascii=False))