"""
Utilidades para Panel L3HO - Conversión de audio, caché y validación
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import requests
from pydub import AudioSegment
import logging

class CacheManager:
    """Gestor de caché para optimizar descargas y consultas"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_duration = 86400  # 24 horas por defecto
        
        # Crear directorio de caché si no existe
        os.makedirs(cache_dir, exist_ok=True)
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
    
    def get_cache_key(self, data: Union[str, Dict]) -> str:
        """Generar clave única para el caché"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Obtener datos del caché si están válidos"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            # Verificar si el caché ha expirado
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age > self.cache_duration:
                os.remove(cache_file)
                return None
            
            # Cargar datos
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            self.logger.debug(f"Cache hit para clave: {cache_key}")
            return cached_data
            
        except Exception as e:
            self.logger.warning(f"Error leyendo caché {cache_key}: {e}")
            return None
    
    def cache_data(self, cache_key: str, data: Dict[str, Any]) -> bool:
        """Guardar datos en caché"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            # Agregar timestamp
            data['_cached_at'] = datetime.now().isoformat()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"Datos guardados en caché: {cache_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando en caché {cache_key}: {e}")
            return False
    
    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """Limpiar caché (todo o por patrón)"""
        cleared = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    if pattern is None or pattern in filename:
                        os.remove(os.path.join(self.cache_dir, filename))
                        cleared += 1
            
            self.logger.info(f"Caché limpiado: {cleared} archivos eliminados")
            return cleared
            
        except Exception as e:
            self.logger.error(f"Error limpiando caché: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del caché"""
        try:
            total_files = 0
            total_size = 0
            oldest_file = None
            newest_file = None
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    file_stat = os.stat(file_path)
                    
                    total_files += 1
                    total_size += file_stat.st_size
                    
                    if oldest_file is None or file_stat.st_mtime < oldest_file:
                        oldest_file = file_stat.st_mtime
                    
                    if newest_file is None or file_stat.st_mtime > newest_file:
                        newest_file = file_stat.st_mtime
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'oldest_cache': datetime.fromtimestamp(oldest_file).isoformat() if oldest_file else None,
                'newest_cache': datetime.fromtimestamp(newest_file).isoformat() if newest_file else None,
                'cache_duration_hours': self.cache_duration / 3600
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de caché: {e}")
            return {'error': str(e)}

class AudioConverter:
    """Conversor de audio con diferentes formatos y calidades"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_audio(self, input_path: str, output_path: str, 
                     output_format: str = 'mp3', quality: str = 'high') -> Dict[str, Any]:
        """Convertir archivo de audio entre formatos"""
        try:
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'error': 'Archivo de entrada no existe'
                }
            
            # Cargar audio
            audio = AudioSegment.from_file(input_path)
            
            # Configurar parámetros según calidad
            export_params = self._get_export_params(output_format, quality)
            
            # Convertir
            audio.export(output_path, format=output_format, **export_params)
            
            # Verificar que se creó el archivo
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'output_format': output_format,
                    'file_size': file_size,
                    'quality': quality,
                    'duration': len(audio) / 1000.0  # Duración en segundos
                }
            else:
                return {
                    'success': False,
                    'error': 'Error en la conversión'
                }
                
        except Exception as e:
            self.logger.error(f"Error convirtiendo audio: {e}")
            return {
                'success': False,
                'error': f'Error de conversión: {str(e)}'
            }
    
    def _get_export_params(self, output_format: str, quality: str) -> Dict[str, Any]:
        """Obtener parámetros de exportación según formato y calidad"""
        params = {}
        
        if output_format == 'mp3':
            if quality == 'high':
                params['bitrate'] = '320k'
            elif quality == 'medium':
                params['bitrate'] = '192k'
            elif quality == 'low':
                params['bitrate'] = '128k'
        
        elif output_format == 'wav':
            if quality == 'high':
                params['parameters'] = ['-acodec', 'pcm_s24le']  # 24-bit
            else:
                params['parameters'] = ['-acodec', 'pcm_s16le']  # 16-bit
        
        elif output_format == 'flac':
            if quality == 'high':
                params['parameters'] = ['-compression_level', '8']
            else:
                params['parameters'] = ['-compression_level', '5']
        
        return params
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Obtener información detallada de un archivo de audio"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            return {
                'success': True,
                'data': {
                    'duration_seconds': len(audio) / 1000.0,
                    'duration_formatted': self._format_duration(len(audio) / 1000.0),
                    'sample_rate': audio.frame_rate,
                    'channels': audio.channels,
                    'bits_per_sample': audio.sample_width * 8,
                    'file_size': os.path.getsize(file_path),
                    'file_format': file_path.split('.')[-1].upper()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analizando audio: {str(e)}'
            }
    
    def _format_duration(self, seconds: float) -> str:
        """Formatear duración en formato legible"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

class ApiValidator:
    """Validador para claves de API y requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_api_key(self, api_key: str, service: str) -> Dict[str, Any]:
        """Validar una clave de API específica"""
        try:
            if service.lower() == 'youtube':
                return self._validate_youtube_api(api_key)
            elif service.lower() == 'spotify':
                return self._validate_spotify_api(api_key)
            elif service.lower() == 'lastfm':
                return self._validate_lastfm_api(api_key)
            elif service.lower() == 'genius':
                return self._validate_genius_api(api_key)
            else:
                return {
                    'success': True,
                    'message': f'Validación no implementada para {service}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error validando API {service}: {str(e)}'
            }
    
    def _validate_youtube_api(self, api_key: str) -> Dict[str, Any]:
        """Validar YouTube Data API"""
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': 'test',
                'maxResults': 1,
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'YouTube API válida',
                    'quota_used': response.headers.get('X-RateLimit-Used', 'N/A')
                }
            else:
                return {
                    'success': False,
                    'error': f'API inválida: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error validando YouTube API: {str(e)}'
            }
    
    def _validate_spotify_api(self, credentials: str) -> Dict[str, Any]:
        """Validar Spotify API (formato: client_id:client_secret)"""
        try:
            if ':' not in credentials:
                return {
                    'success': False,
                    'error': 'Formato inválido. Usar: client_id:client_secret'
                }
            
            client_id, client_secret = credentials.split(':', 1)
            
            # Probar autenticación
            auth_url = "https://accounts.spotify.com/api/token"
            auth_headers = {
                'Authorization': f'Basic {self._encode_base64(f"{client_id}:{client_secret}")}'
            }
            auth_data = {'grant_type': 'client_credentials'}
            
            response = requests.post(auth_url, headers=auth_headers, data=auth_data, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Spotify API válida'
                }
            else:
                return {
                    'success': False,
                    'error': f'Credenciales inválidas: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error validando Spotify API: {str(e)}'
            }
    
    def _validate_lastfm_api(self, api_key: str) -> Dict[str, Any]:
        """Validar Last.fm API"""
        try:
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'chart.getTopArtists',
                'api_key': api_key,
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'error' not in data:
                    return {
                        'success': True,
                        'message': 'Last.fm API válida'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'API inválida: {data.get("message", "Error desconocido")}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Error HTTP: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error validando Last.fm API: {str(e)}'
            }
    
    def _validate_genius_api(self, api_key: str) -> Dict[str, Any]:
        """Validar Genius API"""
        try:
            url = "https://api.genius.com/search"
            headers = {'Authorization': f'Bearer {api_key}'}
            params = {'q': 'test'}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Genius API válida'
                }
            else:
                return {
                    'success': False,
                    'error': f'API inválida: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error validando Genius API: {str(e)}'
            }
    
    def _encode_base64(self, text: str) -> str:
        """Codificar texto en base64"""
        import base64
        return base64.b64encode(text.encode()).decode()
    
    def validate_request_data(self, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Validar datos de request"""
        try:
            missing_fields = []
            
            for field in required_fields:
                if field not in data or not data[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
                }
            
            return {
                'success': True,
                'message': 'Datos válidos'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error validando datos: {str(e)}'
            }

class FileManager:
    """Gestor de archivos para el sistema de música"""
    
    def __init__(self, base_path: str = "storage"):
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        
        # Crear directorios necesarios
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(os.path.join(base_path, "musica"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "temp"), exist_ok=True)
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Limpiar archivos temporales antiguos"""
        try:
            temp_dir = os.path.join(self.base_path, "temp")
            cleaned = 0
            current_time = time.time()
            
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                file_age = current_time - os.path.getctime(file_path)
                
                if file_age > (max_age_hours * 3600):
                    os.remove(file_path)
                    cleaned += 1
            
            self.logger.info(f"Archivos temporales limpiados: {cleaned}")
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error limpiando archivos temporales: {e}")
            return 0
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Obtener uso de disco del sistema"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(self.base_path)
            
            return {
                'success': True,
                'data': {
                    'total_gb': round(total / (1024**3), 2),
                    'used_gb': round(used / (1024**3), 2),
                    'free_gb': round(free / (1024**3), 2),
                    'usage_percent': round((used / total) * 100, 2)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo uso de disco: {str(e)}'
            }

# Instancias globales para usar en el sistema
cache_manager = CacheManager()
audio_converter = AudioConverter()
api_validator = ApiValidator()
file_manager = FileManager()