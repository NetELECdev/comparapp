content = """[build]
buildCommand = "pip install -r backend/requirements.txt"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
rootDirectory = "backend"
"""
with open('railway.toml', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')