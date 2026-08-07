import requests

BASE_URL = "http://localhost:8000/api/v1"
EMAIL    = "netelectaller@gmail.com"
PASSWORD = "03126900"

PRODUCT_ID = "04e21d1f-828c-4b8a-8f87-da1db66a260d"   # de un producto repetido entre comercios
IMG = "https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/carniceria.jpg"

# Login
r = requests.post(f"{BASE_URL}/login", json={"email": EMAIL, "password": PASSWORD})
token = (r.json().get("user") or {}).get("access_token")
print("Token OK" if token else "SIN TOKEN")

# Propagar imagen
resp = requests.put(
    f"{BASE_URL}/products/{PRODUCT_ID}/imagen",
    headers={"Authorization": f"Bearer {token}"},
    json={"imagen_prod": IMG},
)
print("Status:", resp.status_code)
print(resp.json())