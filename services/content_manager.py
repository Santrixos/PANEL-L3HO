"""
Gestor de contenido para Panel L3HO - Sistema centralizado
Maneja todas las secciones de contenido del panel maestro
"""

from app import db
from models import ContentSection, ContentItem, MediaFile, SystemLog, Notification
from services.futbol import FutbolService
from services.transmisiones import TransmisionesService
from services.movies import MoviesService
from services.music import MusicService
from services.mod_apps import ModAppsService
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any, Union
import json

class ContentManager:
    """Gestor centralizado de contenido para el panel maestro"""
    
    def __init__(self):
        self.futbol_service = FutbolService()
        self.transmisiones_service = TransmisionesService()
        self.movies_service = MoviesService()
        self.music_service = MusicService()
        self.mod_apps_service = ModAppsService()
    
    def initialize_default_sections(self):
        """Inicializa las secciones por defecto del sistema"""
        default_sections = [
            {
                'name': 'football',
                'title': 'Fútbol Liga MX',
                'description': 'API completa de datos de Liga MX con estadísticas en tiempo real',
                'icon': 'fa-futbol',
                'color_scheme': 'success',
                'sort_order': 1,
                'settings': {
                    'api_enabled': True,
                    'real_time_data': True,
                    'auto_update': True,
                    'sources': ['ESPN México', 'Liga MX Oficial']
                }
            },
            {
                'name': 'transmissions',
                'title': 'Transmisiones en Vivo',
                'description': 'Sistema de transmisiones en tiempo real y calendarios de partidos',
                'icon': 'fa-broadcast-tower',
                'color_scheme': 'danger',
                'sort_order': 2,
                'settings': {
                    'live_updates': True,
                    'notification_alerts': True,
                    'multiple_sources': True
                }
            },
            {
                'name': 'movies',
                'title': 'Películas',
                'description': 'Catálogo de películas con datos de TMDB',
                'icon': 'fa-film',
                'color_scheme': 'primary',
                'sort_order': 3,
                'settings': {
                    'requires_api_key': True,
                    'api_service': 'TMDB',
                    'auto_sync': False
                }
            },
            {
                'name': 'music',
                'title': 'Música',
                'description': 'Integración con Spotify para gestión musical',
                'icon': 'fa-music',
                'color_scheme': 'warning',
                'sort_order': 4,
                'settings': {
                    'requires_credentials': True,
                    'api_service': 'Spotify',
                    'auto_sync': False
                }
            },
            {
                'name': 'mod_apps',
                'title': 'Apps Modificadas',
                'description': 'Distribución y gestión de aplicaciones modificadas',
                'icon': 'fa-mobile-alt',
                'color_scheme': 'info',
                'sort_order': 5,
                'settings': {
                    'safety_checks': True,
                    'auto_scan': True,
                    'source': 'APKMirror'
                }
            }
        ]
        
        for section_data in default_sections:
            # Verificar si la sección ya existe
            existing = ContentSection.query.filter_by(name=section_data['name']).first()
            if not existing:
                section = ContentSection()
                section.name = section_data['name']
                section.title = section_data['title']
                section.description = section_data['description']
                section.icon = section_data['icon']
                section.color_scheme = section_data['color_scheme']
                section.sort_order = section_data['sort_order']
                section.set_settings(section_data['settings'])
                
                db.session.add(section)
        
        try:
            db.session.commit()
            self.log_system_action('INFO', 'CONTENT', 'Secciones por defecto inicializadas')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error inicializando secciones: {e}")
    
    def get_section_content(self, section_name: str, **kwargs) -> Dict[str, Any]:
        """Obtiene contenido dinámico de una sección específica"""
        try:
            section = ContentSection.query.filter_by(name=section_name, is_active=True).first()
            if not section:
                return {
                    'success': False,
                    'error': f'Sección {section_name} no encontrada'
                }
            
            # Obtener contenido según el tipo de sección
            if section_name == 'football':
                return self._get_football_content(**kwargs)
            elif section_name == 'transmissions':
                return self._get_transmissions_content(**kwargs)
            elif section_name == 'movies':
                return self._get_movies_content(**kwargs)
            elif section_name == 'music':
                return self._get_music_content(**kwargs)
            elif section_name == 'mod_apps':
                return self._get_mod_apps_content(**kwargs)
            else:
                # Contenido genérico desde base de datos
                return self._get_generic_content(section, **kwargs)
                
        except Exception as e:
            logging.error(f"Error obteniendo contenido de {section_name}: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
    def _get_football_content(self, content_type: str = 'tabla', **kwargs) -> Dict[str, Any]:
        """Obtiene contenido de fútbol"""
        try:
            if content_type == 'tabla':
                return self.futbol_service.get_liga_mx_tabla_completa()
            elif content_type == 'equipo':
                equipo_id = kwargs.get('equipo_id')
                if equipo_id:
                    return self.futbol_service.get_equipo_detallado(equipo_id)
            elif content_type == 'jugadores':
                equipo_id = kwargs.get('equipo_id')
                if equipo_id:
                    return self.futbol_service.get_jugadores_equipo(equipo_id)
            elif content_type == 'calendario':
                return self.futbol_service.get_calendario_completo()
            elif content_type == 'estadisticas':
                return self.futbol_service.get_estadisticas_generales()
            
            return {
                'success': False,
                'error': 'Tipo de contenido no válido'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo datos de fútbol: {str(e)}'
            }
    
    def _get_transmissions_content(self, **kwargs) -> Dict[str, Any]:
        """Obtiene contenido de transmisiones"""
        try:
            return self.transmisiones_service.get_partidos_en_vivo()
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo transmisiones: {str(e)}'
            }
    
    def _get_movies_content(self, content_type: str = 'popular', **kwargs) -> Dict[str, Any]:
        """Obtiene contenido de películas"""
        try:
            # Verificar si hay API key configurada
            api_key = kwargs.get('api_key')
            if api_key:
                self.movies_service.api_key = api_key
            
            if content_type == 'popular':
                page = kwargs.get('page', 1)
                return self.movies_service.get_popular_movies(page)
            elif content_type == 'search':
                query = kwargs.get('query', '')
                page = kwargs.get('page', 1)
                return self.movies_service.search_movies(query, page)
            
            return {
                'success': False,
                'error': 'Tipo de contenido no válido'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo películas: {str(e)}'
            }
    
    def _get_music_content(self, content_type: str = 'featured', **kwargs) -> Dict[str, Any]:
        """Obtiene contenido de música"""
        try:
            # Configurar credenciales si se proporcionan
            client_id = kwargs.get('client_id')
            client_secret = kwargs.get('client_secret')
            
            if client_id and client_secret:
                self.music_service.client_id = client_id
                self.music_service.client_secret = client_secret
            
            if content_type == 'featured':
                limit = kwargs.get('limit', 20)
                return self.music_service.get_featured_playlists(limit)
            elif content_type == 'search':
                query = kwargs.get('query', '')
                limit = kwargs.get('limit', 20)
                return self.music_service.search_tracks(query, limit)
            
            return {
                'success': False,
                'error': 'Tipo de contenido no válido'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo música: {str(e)}'
            }
    
    def _get_mod_apps_content(self, content_type: str = 'popular', **kwargs) -> Dict[str, Any]:
        """Obtiene contenido de apps modificadas"""
        try:
            if content_type == 'popular':
                category = kwargs.get('category', 'all')
                return self.mod_apps_service.get_popular_apps(category)
            elif content_type == 'search':
                query = kwargs.get('query', '')
                return self.mod_apps_service.search_app(query)
            
            return {
                'success': False,
                'error': 'Tipo de contenido no válido'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo apps: {str(e)}'
            }
    
    def _get_generic_content(self, section: ContentSection, **kwargs) -> Dict[str, Any]:
        """Obtiene contenido genérico de la base de datos"""
        try:
            # Obtener items de contenido de la sección
            query = section.content_items.filter_by(status='published')
            
            # Aplicar filtros si se proporcionan
            if kwargs.get('is_featured'):
                query = query.filter_by(is_featured=True)
            
            # Ordenar
            query = query.order_by(ContentItem.sort_order.asc(), ContentItem.created_at.desc())
            
            # Paginación
            page = kwargs.get('page', 1)
            per_page = kwargs.get('per_page', 20)
            
            items = query.paginate(page=page, per_page=per_page, error_out=False)
            
            content_items = []
            for item in items.items:
                content_items.append({
                    'id': item.id,
                    'title': item.title,
                    'description': item.description,
                    'content_data': item.get_content_data(),
                    'featured_image': item.featured_image,
                    'is_featured': item.is_featured,
                    'view_count': item.view_count,
                    'published_at': item.published_at.isoformat() if item.published_at else None,
                    'created_at': item.created_at.isoformat()
                })
            
            return {
                'success': True,
                'section': {
                    'name': section.name,
                    'title': section.title,
                    'description': section.description
                },
                'data': content_items,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': items.total,
                    'pages': items.pages
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo contenido genérico: {str(e)}'
            }
    
    def log_system_action(self, level: str, category: str, message: str, 
                         details: Optional[Dict] = None, user_id: Optional[int] = None):
        """Registra una acción del sistema"""
        try:
            log = SystemLog()
            log.level = level
            log.category = category
            log.message = message
            log.details = json.dumps(details) if details else None
            log.user_id = user_id
            
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logging.error(f"Error registrando log del sistema: {e}")
    
    def create_notification(self, title: str, message: str, 
                          notification_type: str = 'info', 
                          user_id: Optional[int] = None,
                          action_url: Optional[str] = None):
        """Crea una notificación del sistema"""
        try:
            notification = Notification()
            notification.title = title
            notification.message = message
            notification.notification_type = notification_type
            notification.user_id = user_id
            notification.action_url = action_url
            notification.is_system = user_id is None
            
            db.session.add(notification)
            db.session.commit()
            
            return True
        except Exception as e:
            logging.error(f"Error creando notificación: {e}")
            return False