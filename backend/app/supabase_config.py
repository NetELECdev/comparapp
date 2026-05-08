# /supabase_config.py

"""
Configuración de Supabase para ComparApp
Archivo: supabase_config.py
"""

from dotenv import load_dotenv
load_dotenv()

import os
from typing import Optional

class SupabaseConfig:
    """Configuración centralizada para Supabase"""
   
    # Estas credenciales están en el Dashboard de Supabase > Settings > API
    SUPABASE_URL = "https://fbsugjqjbltvvyywfsal.supabase.co"  
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZic3VnanFqYmx0dnZ5eXdmc2FsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NTc5MDAsImV4cCI6MjA2MDMzMzkwMH0.WGPCnfur8MVDzW22WGF3n2K0Ai1xnVh0t0sK0MbYwoc"
   
    # Configuraciones adicionales
    TIMEOUT = 30  # Timeout para requests
    MAX_RETRIES = 3  # Máximo número de reintentos
   
    # Configuración de debug
    DEBUG = True  # Cambiar a False en producción
   
    # CONFIGURACIONES PARA REQUESTS
    CONNECTION_TIMEOUT = 10  # segundos
    READ_TIMEOUT = 30        # segundos
    RETRY_DELAY = 2          # segundos entre reintentos
    
    def __init__(self):
        """Inicializa la configuración de Supabase"""
        self.url = self.get_url()
        self.key = self.get_anon_key()
    
    def get_base_url(self) -> str:
        """Obtiene la URL base de Supabase"""
        return self.url
    
    def get_auth_url(self) -> str:
        """Obtiene la URL de autenticación"""
        return f"{self.url}/auth/v1"
    
    def get_rest_url(self) -> str:
        """Obtiene la URL de la API REST"""
        return f"{self.url}/rest/v1"
    
    def get_headers(self, access_token: str = None) -> dict:
        """Obtiene headers para requests"""
        headers = {
            "apikey": self.key,
            "Content-Type": "application/json"
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers
    
    def is_configured(self) -> bool:
        """Verifica si Supabase está configurado correctamente"""
        try:
            return bool(self.url and self.key and self.key.startswith('eyJ'))
        except:
            return False
    
    @classmethod
    def get_url(cls) -> str:
        """Obtiene la URL de Supabase"""
        url = os.getenv('SUPABASE_URL', cls.SUPABASE_URL)
        # Verificar que no sea la URL de ejemplo/placeholder
        if not url or url == "TU_URL_AQUI" or "example" in url.lower():
            raise ValueError(
                "SUPABASE_URL no está configurada correctamente. "
                "Ve al Dashboard de Supabase > Settings > API y copia tu Project URL real."
            )
        return url
   
    @classmethod
    def get_anon_key(cls) -> str:
        """Obtiene la clave anónima de Supabase"""
        key = os.getenv('SUPABASE_ANON_KEY', cls.SUPABASE_ANON_KEY)
        if not key or not key.startswith('eyJ'):
            raise ValueError(
                "SUPABASE_ANON_KEY no está configurada correctamente. "
                "Ve al Dashboard de Supabase > Settings > API y copia tu anon/public key real."
            )
        return key
   
    @classmethod
    def get_timeout(cls) -> int:
        """Obtiene el timeout configurado"""
        return int(os.getenv('SUPABASE_TIMEOUT', cls.TIMEOUT))
   
    @classmethod
    def get_max_retries(cls) -> int:
        """Obtiene el máximo número de reintentos"""
        return int(os.getenv('SUPABASE_MAX_RETRIES', cls.MAX_RETRIES))
   
    @classmethod
    def is_debug(cls) -> bool:
        """Verifica si está en modo debug"""
        return os.getenv('DEBUG', str(cls.DEBUG)).lower() == 'true'

# Configuración de tablas
class TableConfig:
    """Configuración de nombres de tablas"""
    USERS = "users"
    PROVEEDOR = "proveedor"
    PRODUCTO = "producto"

# Configuración de autenticación
class AuthConfig:
    """Configuración de autenticación"""
    TOKEN_EXPIRY_HOURS = 24
    REMEMBER_ME_DAYS = 30
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 128
   
    # Roles permitidos
    ROLES = {
        'USER': 'usuario',
        'PROVIDER': 'proveedor',
        'ADMIN': 'admin'
    }
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple:
        """Valida contraseña y retorna (es_válida, mensaje)"""
        if len(password) < AuthConfig.MIN_PASSWORD_LENGTH:
            return False, f"La contraseña debe tener al menos {AuthConfig.MIN_PASSWORD_LENGTH} caracteres"
        
        if len(password) > AuthConfig.MAX_PASSWORD_LENGTH:
            return False, f"La contraseña no puede tener más de {AuthConfig.MAX_PASSWORD_LENGTH} caracteres"
        
        return True, "Contraseña válida"

# INSTANCIA GLOBAL
supabase_config = SupabaseConfig()

