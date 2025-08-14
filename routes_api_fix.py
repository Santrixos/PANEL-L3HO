# ==================== NUEVOS ENDPOINTS API LIGA MX ====================
import logging
from functools import wraps
from flask import jsonify, request
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)

def require_api_key(f):
    """Decorador para validar API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API Key requerida en header X-API-Key'
            }), 401
            
        # Validar API key
        from models import ApiKey
        valid_key = ApiKey.query.filter_by(api_key=api_key, is_active=True).first()
        if not valid_key:
            return jsonify({
                'success': False,
                'error': 'API Key inválida'
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function

def setup_api_routes(app):
    """Configurar todas las rutas de la API"""
    from models import (LigaMXEquipo, LigaMXPartido, LigaMXJugador, 
                       LigaMXNoticia, ApiKey)
    
    @app.route('/api/info')
    def api_info_page():
        """Documentación completa de la API"""
        try:
            # Obtener la API key principal
            main_api_key = ApiKey.query.filter_by(service_name='Liga MX Central API').first()
            api_key_value = main_api_key.api_key if main_api_key else 'L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED'
            
            from flask import render_template
            return render_template('api_info.html', api_key=api_key_value)
            
        except Exception as e:
            logger.error(f"Error cargando documentación API: {e}")
            from flask import render_template
            return render_template('api_info.html', api_key='L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED')

    @app.route('/api/ligamx/equipos', methods=['GET'])
    @require_api_key
    def api_equipos():
        """Endpoint para obtener todos los equipos"""
        try:
            equipos = LigaMXEquipo.query.all()
            
            # Filtro por equipo si se especifica
            equipo_filter = request.args.get('equipo')
            if equipo_filter:
                equipos = [e for e in equipos if equipo_filter.lower() in e.nombre.lower()]
            
            # Límite de resultados
            limit = request.args.get('limit', type=int)
            if limit:
                equipos = equipos[:limit]
            
            result = []
            for equipo in equipos:
                result.append({
                    'id': equipo.id,
                    'nombre': equipo.nombre,
                    'nombre_corto': getattr(equipo, 'nombre_corto', None) or equipo.nombre,
                    'ciudad': getattr(equipo, 'ciudad', None) or 'No especificada',
                    'estadio': getattr(equipo, 'estadio', None) or 'No especificado',
                    'fundado': getattr(equipo, 'fundado', None),
                    'escudo_url': f'/static/logos/{equipo.nombre.lower().replace(" ", "_")}.png',
                    'posicion': getattr(equipo, 'posicion', None),
                    'puntos': getattr(equipo, 'puntos', None),
                    'partidos_jugados': getattr(equipo, 'partidos_jugados', None),
                    'ganados': getattr(equipo, 'ganados', None),
                    'empatados': getattr(equipo, 'empatados', None),
                    'perdidos': getattr(equipo, 'perdidos', None),
                    'goles_favor': getattr(equipo, 'goles_favor', None),
                    'goles_contra': getattr(equipo, 'goles_contra', None),
                    'diferencia_goles': (getattr(equipo, 'goles_favor', 0) or 0) - (getattr(equipo, 'goles_contra', 0) or 0),
                    'updated_at': equipo.updated_at.isoformat() if getattr(equipo, 'updated_at', None) else None
                })
            
            return jsonify({
                'success': True,
                'data': result,
                'total': len(result),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error en API equipos: {e}")
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor'
            }), 500

    @app.route('/api/ligamx/tabla', methods=['GET'])
    @require_api_key
    def api_tabla_posiciones():
        """Endpoint para obtener la tabla de posiciones"""
        try:
            # Usar getattr para evitar errores de atributos
            equipos = LigaMXEquipo.query.all()
            
            # Ordenar manualmente
            equipos_data = []
            for equipo in equipos:
                puntos = getattr(equipo, 'puntos', 0) or 0
                gf = getattr(equipo, 'goles_favor', 0) or 0
                gc = getattr(equipo, 'goles_contra', 0) or 0
                diferencia = gf - gc
                
                equipos_data.append({
                    'equipo_obj': equipo,
                    'puntos': puntos,
                    'diferencia': diferencia,
                    'goles_favor': gf
                })
            
            # Ordenar por puntos, diferencia de goles y goles a favor
            equipos_data.sort(key=lambda x: (x['puntos'], x['diferencia'], x['goles_favor']), reverse=True)
            
            result = []
            for i, data in enumerate(equipos_data, 1):
                equipo = data['equipo_obj']
                result.append({
                    'posicion': i,
                    'equipo': equipo.nombre,
                    'partidos_jugados': getattr(equipo, 'partidos_jugados', 0) or 0,
                    'ganados': getattr(equipo, 'ganados', 0) or 0,
                    'empatados': getattr(equipo, 'empatados', 0) or 0,
                    'perdidos': getattr(equipo, 'perdidos', 0) or 0,
                    'goles_favor': data['goles_favor'],
                    'goles_contra': getattr(equipo, 'goles_contra', 0) or 0,
                    'diferencia_goles': data['diferencia'],
                    'puntos': data['puntos'],
                    'escudo_url': f'/static/logos/{equipo.nombre.lower().replace(" ", "_")}.png'
                })
            
            return jsonify({
                'success': True,
                'data': result,
                'total_equipos': len(result),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error en API tabla: {e}")
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor'
            }), 500

    @app.route('/api/ligamx/partidos', methods=['GET'])
    @require_api_key
    def api_partidos():
        """Endpoint para obtener partidos"""
        try:
            partidos = LigaMXPartido.query.all()
            
            # Ordenar por fecha si existe
            partidos_con_fecha = [p for p in partidos if getattr(p, 'fecha', None)]
            partidos_sin_fecha = [p for p in partidos if not getattr(p, 'fecha', None)]
            
            partidos_con_fecha.sort(key=lambda x: x.fecha, reverse=True)
            partidos = partidos_con_fecha + partidos_sin_fecha
            
            # Filtros
            fecha_filter = request.args.get('fecha')
            if fecha_filter:
                try:
                    fecha_obj = datetime.strptime(fecha_filter, '%Y-%m-%d').date()
                    partidos = [p for p in partidos if getattr(p, 'fecha', None) and p.fecha.date() == fecha_obj]
                except ValueError:
                    pass
            
            limit = request.args.get('limit', type=int)
            if limit:
                partidos = partidos[:limit]
            
            result = []
            for partido in partidos:
                result.append({
                    'id': partido.id,
                    'fecha': partido.fecha.isoformat() if getattr(partido, 'fecha', None) else None,
                    'jornada': getattr(partido, 'jornada', None),
                    'equipo_local': getattr(partido, 'equipo_local', {}).get('nombre', 'TBD') if hasattr(partido, 'equipo_local') else 'TBD',
                    'equipo_visitante': getattr(partido, 'equipo_visitante', {}).get('nombre', 'TBD') if hasattr(partido, 'equipo_visitante') else 'TBD',
                    'goles_local': getattr(partido, 'goles_local', None),
                    'goles_visitante': getattr(partido, 'goles_visitante', None),
                    'estado': getattr(partido, 'estado', None) or 'programado',
                    'estadio': getattr(partido, 'estadio', None),
                    'updated_at': partido.updated_at.isoformat() if getattr(partido, 'updated_at', None) else None
                })
            
            return jsonify({
                'success': True,
                'data': result,
                'total': len(result),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error en API partidos: {e}")
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor'
            }), 500

    @app.route('/api/ligamx/noticias', methods=['GET'])
    @require_api_key
    def api_noticias():
        """Endpoint para noticias de Liga MX"""
        try:
            noticias = LigaMXNoticia.query.all()
            
            # Ordenar por fecha si existe
            noticias_con_fecha = [n for n in noticias if getattr(n, 'fecha', None)]
            noticias_sin_fecha = [n for n in noticias if not getattr(n, 'fecha', None)]
            
            noticias_con_fecha.sort(key=lambda x: x.fecha, reverse=True)
            noticias = noticias_con_fecha + noticias_sin_fecha
            
            limit = request.args.get('limit', 10, type=int)
            noticias = noticias[:limit]
            
            result = []
            for noticia in noticias:
                result.append({
                    'id': noticia.id,
                    'titulo': getattr(noticia, 'titulo', ''),
                    'resumen': getattr(noticia, 'resumen', ''),
                    'url': getattr(noticia, 'url', ''),
                    'fuente': getattr(noticia, 'fuente', ''),
                    'fecha': noticia.fecha.isoformat() if getattr(noticia, 'fecha', None) else None,
                    'imagen_url': getattr(noticia, 'imagen_url', None)
                })
            
            return jsonify({
                'success': True,
                'data': result,
                'total': len(result),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error en API noticias: {e}")
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor'
            }), 500