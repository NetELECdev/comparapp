# compara/database/database_manager.py

from typing import Tuple, List, Dict, Optional

from datetime import datetime
import requests
import json
from supabase import create_client, Client
from supabase_config import SupabaseConfig
import time
from supabase.lib.client_options import ClientOptions

class DatabaseManager:
    def __init__(self):
        self.session = requests.Session()
        self.current_user = None
        url = SupabaseConfig.get_url()
        key = SupabaseConfig.get_anon_key()
        self.supabase = create_client(url, key)

    def _test_connection_simple(self):
        """Test de conexión básico"""
        try:
            print("Verificando conexión...")
            response = self.supabase.table('producto').select('id_prod').limit(1).execute()
            
            if response:
                print("✓ Conexión verificada exitosamente")
                return True
            else:
                print("⚠️ Sin datos de respuesta")
                return False
                
        except Exception as e:
            print(f"⚠️ Error en test de conexión: {e}")
            return False

    def _test_connection_robust(self):
        """Prueba de conexión simple sin reintentos complejos"""
        try:
            print("Verificando conexión a Supabase...")
            
            # Test directo y simple
            response = self.supabase.table('producto').select('id_prod').limit(1).execute()
            
            if response and hasattr(response, 'data'):
                print("✓ Conexión a Supabase verificada exitosamente")
                return True
            else:
                print("⚠️ Conexión establecida pero sin datos de respuesta")
                return False
                
        except Exception as e:
            error_str = str(e).lower()
            
            if 'timeout' in error_str:
                print("✗ Timeout conectando a Supabase")
            elif 'connection' in error_str:
                print("✗ Error de conexión de red")
            else:
                print(f"✗ Error: {e}")
            
            return False

    def _setup_emergency_client(self):
        """Configuración de emergencia si falla todo lo demás"""
        try:
            print("Configurando cliente de emergencia...")
            
            url = SupabaseConfig.get_url()
            key = SupabaseConfig.get_anon_key()
            
            # Cliente básico sin configuraciones especiales
            from supabase import create_client
            self.supabase = create_client(url, key)
            
            print("✓ Cliente de emergencia configurado")
            
        except Exception as e:
            print(f"✗ Error crítico configurando cliente de emergencia: {e}")
            self.supabase = None


    def test_connection(self) -> Tuple[bool, str]:
        try:
            response = self.supabase.table('producto').select('id_prod').limit(1).execute()
            if response.data:
                return True, "Conexión a Supabase exitosa."
            else:
                return False, "Conexión fallida o sin datos."
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    # ==================== AUTENTICACIÓN ====================

    def register_user(self, email: str, password: str, nombre_completo: str, telefono: Optional[str] = None):
        if not self.supabase:
            return False, "Error: Base de datos no disponible", None
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres", None
        
        try:
            # 1️⃣ CREAR USUARIO EN SUPABASE AUTH (esto es lo que falta)
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "nombre_completo": nombre_completo
                    }
                }
            })
            
            if not auth_response.user:
                return False, "Error al crear usuario en autenticación", None
            
            # Usar el ID que generó Supabase Auth
            user_id = auth_response.user.id
            
            # 2️⃣ INSERTAR EN TU TABLA users CON EL MISMO ID
            response = self.supabase.table("users").insert({
                "id_user": user_id,  # ← ID de Supabase Auth, no UUID manual
                "email_user": email,
                "nombre_completo_user": nombre_completo,
                "telefono_user": telefono,
                "fecha_registro_user": datetime.now().isoformat(),
                "ultima_conexion_user": datetime.now().isoformat(),
                "rol_user": "usuario",
                "es_proveedor_user": False,
                "proveedor_verificado_user": False,
                "preferencias_user": json.dumps({
                    "security_version": "1.0",
                    "password_changed_at": datetime.now().isoformat()
                }),
                "activo_user": True,
                "fecha_actualizacion_user": datetime.now().isoformat()
            }).execute()
            
            if response.data:
                user_data = response.data[0]
                return True, "Usuario registrado exitosamente", {
                    "id_user": user_data.get("id_user"),
                    "email_user": user_data.get("email_user"),
                    "nombre_completo_user": user_data.get("nombre_completo_user"),
                    "rol_user": user_data.get("rol_user")
                }
            else:
                # Rollback: eliminar de Auth si falló la tabla
                self.supabase.auth.admin.delete_user(user_id)
                return False, "Error al crear usuario en la base de datos", None
                
        except Exception as e:
            success, error_message = self._handle_register_errors(e)
            return success, error_message, None
            
    def _handle_register_errors(self, error):
        """
        Manejo centralizado de errores de registro
        """
        error_msg = str(error).lower()  
                
        if "already registered" in error_msg or "already exists" in error_msg:
            return False, "Este email ya está registrado"
        elif "invalid email" in error_msg:
            return False, "Email inválido"
        elif "password" in error_msg:
            return False, "La contraseña no cumple los requisitos"
        elif "network" in error_msg or "connection" in error_msg:
            return False, "Error de conexión. Verifica tu internet"
        else:
            return False, f"Error en registro: {str(error)}"

    def _generate_password_hash(self, password: str) -> str:
        """Genera el hash de contraseña (debes implementar según tu sistema)"""
        import hashlib
        import secrets
        
        # Esto es un ejemplo - DEBES USAR EL MISMO MÉTODO que en tu proyecto KivyMD
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"pbkdf2_sha256$100000${salt}${hash_obj.hex()}"

    # También agrega este método para verificar si un usuario puede iniciar sesión
    def can_user_login(self, email):
        """
        Verifica si un usuario puede iniciar sesión (incluso sin confirmación de email)
        """
        try:
            # Buscar usuario en la tabla de perfiles
            response = self.supabase.table("perfiles").select("*").eq("email", email).execute()
            
            if response.data:
                return True, "Usuario encontrado"
            else:
                return False, "Usuario no encontrado"
                
        except Exception as e:
            print(f"Error verificando usuario: {e}")
            return False, "Error verificando usuario"

    def login_user(self, email: str, password: str) -> Tuple[bool, str, dict]:
        try:
            print(f"🔐 Intentando login para: {email}")
            
            # ✅ USAR EL MÉTODO NATIVO DE SUPABASE
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                print(f"✅ Login exitoso para: {email}")
                
                # Obtener datos adicionales de tu tabla users
                user_data_response = self.supabase.table("users").select("*").eq("email_user", email).execute()
                
                # Construir user_data compatible con tu sistema
                user_data = {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "user_metadata": auth_response.user.user_metadata or {},
                    "access_token": auth_response.session.access_token if hasattr(auth_response, 'session') else None
                }
                
                # Combinar con datos de tu tabla personalizada
                if user_data_response.data:
                    custom_data = user_data_response.data[0]
                    user_data.update({
                        "id_user": custom_data.get("id_user"),
                        "nombre_completo_user": custom_data.get("nombre_completo_user"),
                        "rol_user": custom_data.get("rol_user", "usuario"),
                        "telefono_user": custom_data.get("telefono_user"),
                        "activo_user": custom_data.get("activo_user", True)
                    })
                
                self.set_current_user(user_data)
                return True, "Login exitoso", user_data
            else:
                return False, "Error en la autenticación", {}
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error en login: {error_msg}")
            
            # Manejo específico de errores
            if "Invalid login credentials" in error_msg:
                return False, "Email o contraseña incorrectos", {}
            elif "Email not confirmed" in error_msg:
                return False, "Por favor verifica tu email antes de iniciar sesión", {}
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                return False, "Error de conexión. Verifica tu internet", {}
        
        return False, f"Error inesperado: {error_msg}", {}

    def logout_user(self) -> bool:
        self.current_user = None
        return True

    def is_user_logged_in(self) -> bool:
        return self.current_user is not None and 'access_token' in self.current_user

    def set_current_user(self, user_data):
        self.current_user = user_data

    def get_current_user(self):
        return self.current_user

    def get_user_role(self) -> str:
        if self.current_user and 'user_metadata' in self.current_user:
            return self.current_user['user_metadata'].get('rol', 'user')
        return 'user'

    def is_admin(self) -> bool:
        return self.get_user_role() == 'admin'

    # ==================== PRODUCTOS ====================

    def create_product(self, product_data: dict) -> Tuple[bool, str]:
        if not self.is_admin():
            return False, "Permisos insuficientes"
        try:
            product_data['fecha_prod'] = 'now()'
            response = self.supabase.table('producto').insert(product_data).execute()
            return (True, "Producto creado") if response.data else (False, "Error al crear producto")
        except Exception as e:
            return False, str(e)

    def update_product(self, product_id: str, product_data: dict) -> Tuple[bool, str]:
        if not self.is_admin():
            return False, "Permisos insuficientes"
        try:
            response = self.supabase.table('producto').update(product_data).eq('id_prod', product_id).execute()
            return (True, "Producto actualizado") if response.data else (False, "Error al actualizar")
        except Exception as e:
            return False, str(e)

    def delete_product(self, product_id: str) -> Tuple[bool, str]:
        if not self.is_admin():
            return False, "Permisos insuficientes"
        try:
            response = self.supabase.table('producto').delete().eq('id_prod', product_id).execute()
            return (True, "Producto eliminado") if response.data else (False, "No se eliminó el producto")
        except Exception as e:
            return False, str(e)

    def search_products(self, query: str, limit: int = None) -> Tuple[bool, str, List[dict]]:
        try:
            if query:
                # Buscar en nombre_prod primero (más común)
                response = self.supabase.table('producto')\
                    .select('*')\
                    .eq('activo_prod', True)\
                    .ilike('nombre_prod', f'%{query}%')\
                    .limit(limit or 50)\
                    .execute()
                
                # Si no hay resultados, buscar en descripción
                if not response.data:
                    response = self.supabase.table('producto')\
                        .select('*')\
                        .eq('activo_prod', True)\
                        .ilike('describe_prod', f'%{query}%')\
                        .limit(limit or 50)\
                        .execute()
                
                # Si no hay resultados, buscar en marca
                if not response.data:
                    response = self.supabase.table('producto')\
                        .select('*')\
                        .eq('activo_prod', True)\
                        .ilike('marca_prod', f'%{query}%')\
                        .limit(limit or 50)\
                        .execute()
            else:
                # Todos los productos activos (con límite por defecto)
                response = self.supabase.table('producto')\
                    .select('*')\
                    .eq('activo_prod', True)\
                    .limit(limit or 200)\
                    .execute()
            
            if response.data:
                self.save_search_history(query)
                return True, "Productos encontrados", response.data
            return False, "No se encontraron productos", []
            
        except Exception as e:
            print(f"Error en búsqueda de productos: {e}")
            return False, f"Error en la búsqueda: {str(e)}", []
            
    def get_product_by_id(self, product_id: str) -> Tuple[bool, str, Optional[dict]]:
        """Obtiene un producto por su ID"""
        try:
            response = self.supabase.table('producto')\
                .select('*')\
                .eq('id_prod', product_id)\
                .eq('activo_prod', True)\
                .limit(1)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return True, "Producto encontrado", response.data[0]
            return False, "Producto no encontrado", None
            
        except Exception as e:
            return False, f"Error: {str(e)}", None


    def _fallback_search_products(self, query: str) -> Tuple[bool, str, List[dict]]:
        """Búsqueda fallback cuando or_ no está disponible"""
        try:
            if not query:
                response = self.supabase.table('producto')\
                    .select('*')\
                    .eq('activo_prod', True)\
                    .execute()
                return True, "Productos encontrados", response.data
            
            # Buscar en múltiples campos individualmente
            all_results = []
            fields_to_search = ['nombre_prod', 'describe_prod', 'marca_prod']
            
            for field in fields_to_search:
                try:
                    response = self.supabase.table('producto')\
                        .select('*')\
                        .eq('activo_prod', True)\
                        .ilike(field, f'%{query}%')\
                        .execute()
                    
                    if response.data:
                        # Evitar duplicados
                        for item in response.data:
                            if item not in all_results:
                                all_results.append(item)
                except:
                    continue
            
            if all_results:
                self.save_search_history(query)
                return True, "Productos encontrados", all_results
            return False, "No se encontraron productos", []
            
        except Exception as e:
            print(f"Error en búsqueda fallback: {e}")
            return False, f"Error en la búsqueda: {str(e)}", []

    # ==================== HISTÓRICO DE BÚSQUEDAS ====================

    def save_search_history(self, search_term: str, search_type: str = 'general', 
                           precio_min: float = None, precio_max: float = None,
                           fecha_desde: str = None, fecha_hasta: str = None,
                           categoria: str = None, marca: str = None,
                           solo_activos: bool = True, results_count: int = 0) -> None:
        """Guarda una búsqueda en el historial"""
        if not self.is_user_logged_in():
            return
        try:
            user_id = self.current_user.get('id')
            data = {
                'user_id': user_id,
                'search_term': search_term,
                'search_type': search_type,
                'solo_activos': solo_activos,
                'results_count': results_count
            }
            
            # Agregar filtros opcionales
            if precio_min is not None:
                data['precio_min'] = precio_min
            if precio_max is not None:
                data['precio_max'] = precio_max
            if fecha_desde:
                data['fecha_desde'] = fecha_desde
            if fecha_hasta:
                data['fecha_hasta'] = fecha_hasta
            if categoria:
                data['categoria'] = categoria
            if marca:
                data['marca'] = marca
                
            self.supabase.table('search_history').insert(data).execute()
        except Exception as e:
            print(f"Error saving search history: {e}")
            
    def search_productos_by_precio(self, precio_min: float = None, precio_max: float = None, 
                                  search_term: str = "", solo_activos: bool = True) -> List[Dict]:
        """Busca productos por rango de precio"""
        try:
            query = self.supabase.table('producto').select('*')
            
            if solo_activos:
                query = query.eq('activo_prod', True)
            
            if precio_min is not None:
                query = query.gte('precio_prod', precio_min)
            
            if precio_max is not None:
                query = query.lte('precio_prod', precio_max)
                
            if search_term:
                query = query.ilike('nombre_prod', f'%{search_term}%')
            
            response = query.order('precio_prod', desc=False).execute()
            results = response.data or []
            
            # Guardar en historial
            term = search_term or f"Precio: ${precio_min or 0} - ${precio_max or '∞'}"
            self.save_search_history(
                search_term=term,
                search_type='precio',
                precio_min=precio_min,
                precio_max=precio_max,
                solo_activos=solo_activos,
                results_count=len(results)
            )
            
            return results
            
        except Exception as e:
            print(f"Error searching by price: {e}")
            return []

    def search_productos_by_fecha(self, fecha_desde: str = None, fecha_hasta: str = None,
                                 search_term: str = "", solo_activos: bool = True) -> List[Dict]:
        """Busca productos por rango de fecha"""
        try:
            query = self.supabase.table('producto').select('*')
            
            if solo_activos:
                query = query.eq('activo_prod', True)
            
            if fecha_desde:
                query = query.gte('fecha_prod', fecha_desde)
            
            if fecha_hasta:
                query = query.lte('fecha_prod', fecha_hasta)
                
            if search_term:
                query = query.ilike('nombre_prod', f'%{search_term}%')
            
            response = query.order('fecha_prod', desc=True).execute()
            results = response.data or []
            
            # Guardar en historial
            term = search_term or f"Fecha: {fecha_desde or 'inicio'} - {fecha_hasta or 'hoy'}"
            self.save_search_history(
                search_term=term,
                search_type='fecha',
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                solo_activos=solo_activos,
                results_count=len(results)
            )
            
            return results
            
        except Exception as e:
            print(f"Error searching by date: {e}")
            return []

    def get_search_history(self, search_type: str = None, limit: int = 20) -> List[Dict]:
        """Obtiene el historial de búsquedas del usuario"""
        if not self.is_user_logged_in():
            return []
        try:
            user_id = self.current_user.get('id')
            query = self.supabase.table('search_history').select('*').eq('user_id', user_id)
            
            if search_type:
                query = query.eq('search_type', search_type)
                
            response = query.order('created_at', desc=True).limit(limit).execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting search history: {e}")
            return []

    def repeat_search(self, history_id: str) -> List[Dict]:
        """Repite una búsqueda del historial"""
        try:
            # Obtener la búsqueda del historial
            response = self.supabase.table('search_history').select('*').eq('id', history_id).execute()
            if not response.data:
                return []
            
            search_data = response.data[0]
            search_type = search_data.get('search_type')
            
            # Ejecutar la búsqueda según el tipo
            if search_type == 'precio':
                return self.search_productos_by_precio(
                    precio_min=search_data.get('precio_min'),
                    precio_max=search_data.get('precio_max'),
                    search_term=search_data.get('search_term', ''),
                    solo_activos=search_data.get('solo_activos', True)
                )
            elif search_type == 'fecha':
                return self.search_productos_by_fecha(
                    fecha_desde=search_data.get('fecha_desde'),
                    fecha_hasta=search_data.get('fecha_hasta'),
                    search_term=search_data.get('search_term', ''),
                    solo_activos=search_data.get('solo_activos', True)
                )
            else:
                # Búsqueda general
                return self.search_productos_general(search_data.get('search_term', ''))
                
        except Exception as e:
            print(f"Error repeating search: {e}")
            return []

    # ==================== COMPARACIÓN DE BÚSQUEDAS ====================

    def get_user_product_matches(self) -> List[dict]:
        if not self.is_user_logged_in():
            return []
        try:
            user_id = self.current_user.get('id')
            response = self.supabase.table('user_search_product_matches').select('*').eq('id_user', user_id).execute()
            return response.data or []
        except:
            return []
    # Añadir al final de la clase DatabaseManager
    PERMISSION_MATRIX = {
        'admin': {
            'product': {
                'create': True,
                'read': True,
                'update': True,
                'delete': True,
                'manage_categories': True
            },
            'providers': {
                'manage': True
            }
        },
        'editor': {
            'product': {
                'create': True,
                'read': True,
                'update': True,
                'delete': False,
                'manage_categories': False
            },
            'providers': {
                'manage': False
            }
        },
        'usuario': {
            'product': {
                'create': False,
                'read': True,
                'update': False,
                'delete': False,
                'manage_categories': False
            },
            'providers': {
                'manage': False
            }
        }
    }

    def check_permission(self, module: str, action: str) -> bool:
        """Verifica si el usuario tiene permiso para una acción específica"""
        role = self.get_user_role()
        return self.PERMISSION_MATRIX.get(role, {}).get(module, {}).get(action, False)
    
    def get_role_display_name(self, role: str) -> str:
        """Devuelve el nombre legible del rol"""
        names = {
            'admin': 'Administrador',
            'editor': 'Editor',
            'usuario': 'Usuario'
        }
        return names.get(role, 'Usuario')
    
    # ===== MÉTODOS PARA PROVEEDORES =====
    def insert_proveedor(self, proveedor_data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """Inserta un nuevo proveedor en Supabase"""
        try:
            response = self.supabase.table('proveedor').insert(proveedor_data).execute()
            if response.data:
                return response.data[0], None
            return None, "No se recibieron datos del servidor"
        except Exception as e:
            return None, str(e)

    def update_proveedor(self, proveedor_id: str, update_data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """Actualiza un proveedor existente"""
        try:
            response = self.supabase.table('proveedor').update(update_data).eq('id_provee', proveedor_id).execute()
            if response.data:
                return response.data[0], None
            return None, "Proveedor no encontrado"
        except Exception as e:
            return None, str(e)

    def search_proveedores(self, search_text: str, sort_by: str = 'nombre') -> Tuple[List[Dict], Optional[str]]:
        """Busca proveedores - Compatible con Supabase 1.0.3"""
        try:
            if not search_text.strip():
                query = self.supabase.table('proveedor').select('*').eq('activo_provee', True)
                response = query.execute()
                return response.data, None
            
            # Múltiples consultas para simular OR
            queries = [
                self.supabase.table('proveedor').select('*').eq('activo_provee', True).ilike('nombre_provee', f'%{search_text}%'),
                self.supabase.table('proveedor').select('*').eq('activo_provee', True).ilike('representa_provee', f'%{search_text}%')
            ]
            
            # Ejecutar todas las consultas
            all_results = []
            seen_ids = set()
            
            for query in queries:
                response = query.execute()
                for item in response.data:
                    item_id = item.get('id_provee')
                    if item_id not in seen_ids:
                        all_results.append(item)
                        seen_ids.add(item_id)
            
            # Ordenar
            if sort_by == 'nombre':
                all_results.sort(key=lambda x: x.get('nombre_provee', '').lower())
            elif sort_by == 'categoria':
                all_results.sort(key=lambda x: x.get('cate_provee', '').lower())
            
            return all_results, None
            
        except Exception as e:
            return [], str(e)

    def get_proveedor_by_id(self, proveedor_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Obtiene un proveedor por su ID"""
        try:
            response = self.supabase.table('proveedor').select('*').eq('id_provee', proveedor_id).execute()
            if response.data:
                return response.data[0], None
            return None, "Proveedor no encontrado"
        except Exception as e:
            return None, str(e)

    def check_proveedor_exists(self, field: str, value: str) -> Tuple[bool, Optional[str]]:
        """Verifica si un proveedor existe por campo único (email, nombre, etc.)"""
        try:
            response = self.supabase.table('proveedor').select(field).eq(field, value).execute()
            return len(response.data) > 0, None
        except Exception as e:
            return False, str(e)

    def close_connections(self):
        """Cierra todas las conexiones de base de datos"""
        try:
            if hasattr(self, 'supabase') and self.supabase:
                # Supabase generalmente usa conexiones HTTP, no necesita cierre explícito
                # Pero si hay alguna sesión o cliente que necesite cerrarse, hazlo aquí
                print("✅ Conexiones de Supabase cerradas")
            
            if hasattr(self, 'db_connection') and self.db_connection:
                self.db_connection.close()
                print("✅ Conexión de base de datos cerrada")
                
        except Exception as e:
            print(f"❌ Error cerrando conexiones: {e}")
            raise

    # ============================================
    # Funciones Users
    # ============================================


    def get_all_users(self) -> Tuple[bool, str, List[dict]]:
        """Obtiene todos los usuarios del sistema"""
        if not self.is_admin():
            return False, "Permisos insuficientes", []
        try:
            response = self.supabase.table('users').select('*').order('fecha_registro_user', desc=True).execute()
            if response.data:
                return True, "Usuarios obtenidos", response.data
            return False, "No se encontraron usuarios", []
        except Exception as e:
            return False, str(e), []

    def get_user_by_id(self, user_id: str) -> Tuple[bool, str, dict]:
        """Obtiene un usuario por su ID"""
        if not self.is_admin():
            return False, "Permisos insuficientes", {}
        try:
            response = self.supabase.table('users').select('*').eq('id_user', user_id).execute()
            if response.data:
                return True, "Usuario encontrado", response.data[0]
            return False, "Usuario no encontrado", {}
        except Exception as e:
            return False, str(e), {}

    def reset_password_email(self, email: str) -> Tuple[bool, str]:
        """Envía email de recuperación de contraseña via Supabase Auth"""
        try:
            self.supabase.auth.reset_password_email(email)
            return True, "Email enviado"
        except Exception as e:
            print(f"Error enviando reset: {e}")
            return True, "Email enviado"  # Siempre True para no revelar si el email existe

    def update_user(self, user_id: str, user_data: dict) -> Tuple[bool, str]:
        """Actualiza un usuario existente"""
        if not self.is_admin():
            return False, "Permisos insuficientes"
        try:
            user_data['fecha_actualizacion_user'] = datetime.now().isoformat()
            response = self.supabase.table('users').update(user_data).eq('id_user', user_id).execute()
            return (True, "Usuario actualizado") if response.data else (False, "Error al actualizar")
        except Exception as e:
            return False, str(e)

    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        """Desactiva un usuario (no lo elimina físicamente)"""
        if not self.is_admin():
            return False, "Permisos insuficientes"
        try:
            # Marcar como inactivo en lugar de eliminar
            response = self.supabase.table('users').update({
                'activo_user': False,
                'fecha_actualizacion_user': datetime.now().isoformat()
            }).eq('id_user', user_id).execute()
            return (True, "Usuario eliminado") if response.data else (False, "No se eliminó el usuario")
        except Exception as e:
            return False, str(e)