"""
Rutas de la API Liga MX - Integrada con Panel L3HO
Sistema profesional de datos de fútbol mexicano
"""

from flask import jsonify, request, abort
from app import app, db
from models import User, LigaMXEquipo, LigaMXPosicion, LigaMXPartido, LigaMXJugador, LigaMXEstadisticaJugador, LigaMXNoticia, LigaMXActualizacion
from services.liga_mx import liga_mx_scraper
from datetime import datetime, timedelta
from functools import wraps
import json
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def require_api_key(f):
    """Decorador para validar API key en endpoints de Liga MX"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if api_key and api_key.startswith('Bearer '):
            api_key = api_key.replace('Bearer ', '')
        elif request.args.get('api_key'):
            api_key = request.args.get('api_key')
        else:
            return jsonify({
                'error': 'API key requerida',
                'message': 'Incluye tu API key en el header Authorization: Bearer YOUR_KEY o como parámetro ?api_key=YOUR_KEY'
            }), 401
        
        # Validar API key contra usuarios del panel
        user = User.query.filter_by(api_key=api_key, is_admin=True).first()
        if not user:
            return jsonify({
                'error': 'API key inválida',
                'message': 'La API key proporcionada no es válida o no tiene permisos'
            }), 401
        
        # Agregar usuario a la request para uso posterior
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

# ==================== ENDPOINTS PRINCIPALES ====================

@app.route('/api/liga-mx/info', methods=['GET'])
def liga_mx_info():
    """Documentación de la API Liga MX"""
    info = {
        'name': 'API Liga MX - Panel L3HO',
        'version': '1.0.0',
        'description': 'API profesional de Liga MX con datos en tiempo real',
        'authentication': 'API Key requerida (Bearer token o parámetro)',
        'base_url': request.url_root + 'api/liga-mx/',
        'endpoints': {
            '/tabla': 'Tabla de posiciones actual',
            '/calendario': 'Calendario de partidos',
            '/calendario?fecha=YYYY-MM-DD': 'Partidos de una fecha específica',
            '/resultados': 'Resultados recientes',
            '/equipos': 'Lista de todos los equipos',
            '/equipos/{nombre}': 'Información específica de un equipo',
            '/jugadores': 'Lista de jugadores',
            '/jugadores?equipo=NOMBRE': 'Jugadores de un equipo específico',
            '/estadisticas/goleadores': 'Tabla de goleadores',
            '/estadisticas/asistencias': 'Tabla de asistencias',
            '/noticias': 'Noticias generales de Liga MX',
            '/noticias?equipo=NOMBRE': 'Noticias de un equipo específico',
            '/actualizacion': 'Actualizar todos los datos (POST)',
            '/status': 'Estado del sistema'
        },
        'data_sources': [
            'ESPN México',
            'Liga MX Oficial',
            'FutbolTotal',
            'MedioTiempo',
            'SofaScore',
            'FlashScore',
            'OneFootball'
        ],
        'update_frequency': 'Cada 5-10 minutos',
        'response_format': 'JSON',
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(info)

@app.route('/api/liga-mx/tabla', methods=['GET'])
@require_api_key
def get_tabla_posiciones():
    """Obtener tabla de posiciones de Liga MX"""
    try:
        temporada = request.args.get('temporada', '2024')
        
        # Intentar obtener desde base de datos
        posiciones = db.session.query(LigaMXPosicion, LigaMXEquipo).join(
            LigaMXEquipo, LigaMXPosicion.equipo_id == LigaMXEquipo.id
        ).filter(LigaMXPosicion.temporada == temporada).order_by(LigaMXPosicion.posicion).all()
        
        if posiciones:
            tabla = []
            for pos, equipo in posiciones:
                tabla.append({
                    'posicion': pos.posicion,
                    'equipo': equipo.nombre,
                    'equipo_completo': equipo.nombre_completo,
                    'partidos_jugados': pos.partidos_jugados,
                    'ganados': pos.ganados,
                    'empatados': pos.empatados,
                    'perdidos': pos.perdidos,
                    'goles_favor': pos.goles_favor,
                    'goles_contra': pos.goles_contra,
                    'diferencia_goles': pos.diferencia_goles,
                    'puntos': pos.puntos,
                    'ultima_actualizacion': pos.ultima_actualizacion.isoformat()
                })
            
            return jsonify({
                'success': True,
                'data': tabla,
                'temporada': temporada,
                'total_equipos': len(tabla),
                'fuente': 'Base de datos Panel L3HO',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Si no hay datos en BD, hacer scraping
        tabla_scraping = liga_mx_scraper.scrape_tabla_posiciones()
        return jsonify({
            'success': True,
            'data': tabla_scraping,
            'temporada': temporada,
            'total_equipos': len(tabla_scraping),
            'fuente': 'Scraping en tiempo real',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo tabla: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/calendario', methods=['GET'])
@require_api_key
def get_calendario():
    """Obtener calendario de partidos"""
    try:
        fecha = request.args.get('fecha')
        equipo = request.args.get('equipo')
        temporada = request.args.get('temporada', '2024')
        
        query = db.session.query(LigaMXPartido, LigaMXEquipo.nombre.label('local'), 
                                LigaMXEquipo.nombre.label('visitante')).join(
            LigaMXEquipo, LigaMXPartido.equipo_local_id == LigaMXEquipo.id
        ).join(LigaMXEquipo, LigaMXPartido.equipo_visitante_id == LigaMXEquipo.id, aliased=True)
        
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                query = query.filter(db.func.date(LigaMXPartido.fecha_partido) == fecha_obj.date())
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido',
                    'message': 'Use formato YYYY-MM-DD'
                }), 400
        
        if equipo:
            query = query.filter(
                db.or_(LigaMXEquipo.nombre.ilike(f'%{equipo}%'),
                       LigaMXEquipo.nombre.ilike(f'%{equipo}%'))
            )
        
        partidos = query.filter(LigaMXPartido.temporada == temporada).order_by(LigaMXPartido.fecha_partido).all()
        
        if partidos:
            calendario = []
            for partido, local, visitante in partidos:
                calendario.append({
                    'id': partido.id,
                    'jornada': partido.jornada,
                    'equipo_local': local,
                    'equipo_visitante': visitante,
                    'fecha': partido.fecha_partido.isoformat() if partido.fecha_partido else None,
                    'estado': partido.estado,
                    'goles_local': partido.goles_local,
                    'goles_visitante': partido.goles_visitante,
                    'estadio': partido.estadio,
                    'arbitro': partido.arbitro,
                    'minuto_actual': partido.minuto_actual,
                    'ultima_actualizacion': partido.ultima_actualizacion.isoformat()
                })
            
            return jsonify({
                'success': True,
                'data': calendario,
                'total_partidos': len(calendario),
                'filtros': {
                    'fecha': fecha,
                    'equipo': equipo,
                    'temporada': temporada
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Fallback a scraping
        calendario_scraping = liga_mx_scraper.scrape_calendario()
        return jsonify({
            'success': True,
            'data': calendario_scraping,
            'total_partidos': len(calendario_scraping),
            'fuente': 'Scraping en tiempo real',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo calendario: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/equipos', methods=['GET'])
@require_api_key
def get_equipos():
    """Obtener lista de equipos"""
    try:
        equipos = LigaMXEquipo.query.filter_by(is_active=True).all()
        
        if equipos:
            equipos_data = []
            for equipo in equipos:
                equipos_data.append({
                    'id': equipo.id,
                    'nombre': equipo.nombre,
                    'nombre_completo': equipo.nombre_completo,
                    'ciudad': equipo.ciudad,
                    'estadio': equipo.estadio,
                    'fundacion': equipo.fundacion,
                    'logo_url': equipo.logo_url,
                    'colores': equipo.colores_primarios,
                    'sitio_web': equipo.sitio_web
                })
            
            return jsonify({
                'success': True,
                'data': equipos_data,
                'total_equipos': len(equipos_data),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Fallback a datos básicos
        equipos_basicos = liga_mx_scraper.get_equipos_info()
        return jsonify({
            'success': True,
            'data': equipos_basicos,
            'total_equipos': len(equipos_basicos),
            'fuente': 'Datos básicos del sistema',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo equipos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/equipos/<nombre>', methods=['GET'])
@require_api_key
def get_equipo_detalle(nombre):
    """Obtener información detallada de un equipo"""
    try:
        equipo = LigaMXEquipo.query.filter(LigaMXEquipo.nombre.ilike(f'%{nombre}%')).first()
        
        if not equipo:
            return jsonify({
                'success': False,
                'error': 'Equipo no encontrado',
                'message': f'No se encontró el equipo "{nombre}"'
            }), 404
        
        # Obtener estadísticas adicionales
        posicion_actual = LigaMXPosicion.query.filter_by(equipo_id=equipo.id).order_by(LigaMXPosicion.id.desc()).first()
        jugadores_count = LigaMXJugador.query.filter_by(equipo_id=equipo.id, is_active=True).count()
        ultimos_partidos = LigaMXPartido.query.filter(
            db.or_(LigaMXPartido.equipo_local_id == equipo.id,
                   LigaMXPartido.equipo_visitante_id == equipo.id)
        ).order_by(LigaMXPartido.fecha_partido.desc()).limit(5).all()
        
        equipo_data = {
            'id': equipo.id,
            'nombre': equipo.nombre,
            'nombre_completo': equipo.nombre_completo,
            'ciudad': equipo.ciudad,
            'estadio': equipo.estadio,
            'fundacion': equipo.fundacion,
            'logo_url': equipo.logo_url,
            'colores': equipo.colores_primarios,
            'sitio_web': equipo.sitio_web,
            'estadisticas': {
                'posicion_actual': posicion_actual.posicion if posicion_actual else None,
                'puntos': posicion_actual.puntos if posicion_actual else None,
                'partidos_jugados': posicion_actual.partidos_jugados if posicion_actual else None,
                'jugadores_activos': jugadores_count
            },
            'ultimos_partidos': len(ultimos_partidos),
            'ultima_actualizacion': equipo.updated_at.isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': equipo_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo detalle equipo: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/estadisticas/goleadores', methods=['GET'])
@require_api_key
def get_goleadores():
    """Obtener tabla de goleadores"""
    try:
        temporada = request.args.get('temporada', '2024')
        limit = int(request.args.get('limit', 20))
        
        # Intentar desde base de datos
        goleadores = db.session.query(
            LigaMXEstadisticaJugador.goles,
            LigaMXJugador.nombre,
            LigaMXEquipo.nombre.label('equipo')
        ).join(LigaMXJugador).join(LigaMXEquipo).filter(
            LigaMXEstadisticaJugador.temporada == temporada,
            LigaMXEstadisticaJugador.goles > 0
        ).order_by(LigaMXEstadisticaJugador.goles.desc()).limit(limit).all()
        
        if goleadores:
            goleadores_data = []
            for i, (goles, jugador, equipo) in enumerate(goleadores, 1):
                goleadores_data.append({
                    'posicion': i,
                    'jugador': jugador,
                    'equipo': equipo,
                    'goles': goles
                })
            
            return jsonify({
                'success': True,
                'data': goleadores_data,
                'temporada': temporada,
                'total_goleadores': len(goleadores_data),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Fallback a scraping
        goleadores_scraping = liga_mx_scraper.scrape_goleadores()
        return jsonify({
            'success': True,
            'data': goleadores_scraping[:limit],
            'temporada': temporada,
            'total_goleadores': len(goleadores_scraping),
            'fuente': 'Scraping en tiempo real',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo goleadores: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/noticias', methods=['GET'])
@require_api_key
def get_noticias():
    """Obtener noticias de Liga MX"""
    try:
        equipo = request.args.get('equipo')
        limit = int(request.args.get('limit', 10))
        
        query = LigaMXNoticia.query.filter_by(is_active=True)
        
        if equipo:
            equipo_obj = LigaMXEquipo.query.filter(LigaMXEquipo.nombre.ilike(f'%{equipo}%')).first()
            if equipo_obj:
                query = query.filter_by(equipo_id=equipo_obj.id)
        
        noticias = query.order_by(LigaMXNoticia.fecha_publicacion.desc()).limit(limit).all()
        
        if noticias:
            noticias_data = []
            for noticia in noticias:
                noticias_data.append({
                    'id': noticia.id,
                    'titulo': noticia.titulo,
                    'contenido': noticia.contenido[:200] + '...' if noticia.contenido and len(noticia.contenido) > 200 else noticia.contenido,
                    'url': noticia.url_externa,
                    'imagen': noticia.imagen_url,
                    'equipo': noticia.equipo.nombre if noticia.equipo else 'Liga MX',
                    'categoria': noticia.categoria,
                    'fecha_publicacion': noticia.fecha_publicacion.isoformat() if noticia.fecha_publicacion else None,
                    'fuente': noticia.fuente
                })
            
            return jsonify({
                'success': True,
                'data': noticias_data,
                'total_noticias': len(noticias_data),
                'filtros': {'equipo': equipo},
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Fallback a scraping
        noticias_scraping = liga_mx_scraper.scrape_noticias(equipo)
        return jsonify({
            'success': True,
            'data': noticias_scraping[:limit],
            'total_noticias': len(noticias_scraping),
            'fuente': 'Scraping en tiempo real',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo noticias: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/actualizacion', methods=['POST'])
@require_api_key
def actualizar_datos():
    """Actualizar todos los datos de Liga MX"""
    try:
        start_time = time.time()
        
        # Ejecutar actualización completa
        resultados = liga_mx_scraper.update_all_data()
        
        execution_time = time.time() - start_time
        
        # Registrar la actualización
        actualizacion = LigaMXActualizacion(
            tipo_actualizacion='completa',
            elementos_actualizados=resultados.get('stats', {}).get('total_items', 0),
            fuentes_consultadas=json.dumps(resultados.get('stats', {}).get('sources_used', [])),
            tiempo_ejecucion=execution_time,
            status='success',
            detalles=json.dumps(resultados.get('stats', {}))
        )
        
        db.session.add(actualizacion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Datos actualizados correctamente',
            'estadisticas': resultados.get('stats', {}),
            'tiempo_ejecucion': f"{execution_time:.2f}s",
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error actualizando datos: {e}")
        
        # Registrar error
        actualizacion = LigaMXActualizacion(
            tipo_actualizacion='completa',
            elementos_actualizados=0,
            tiempo_ejecucion=time.time() - start_time if 'start_time' in locals() else 0,
            status='error',
            errores=json.dumps({'error': str(e)})
        )
        
        db.session.add(actualizacion)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'error': 'Error actualizando datos',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/status', methods=['GET'])
def get_status():
    """Estado del sistema Liga MX API"""
    try:
        # Estadísticas generales
        total_equipos = LigaMXEquipo.query.count()
        total_partidos = LigaMXPartido.query.count()
        total_jugadores = LigaMXJugador.query.count()
        total_noticias = LigaMXNoticia.query.count()
        
        # Última actualización
        ultima_actualizacion = LigaMXActualizacion.query.order_by(LigaMXActualizacion.created_at.desc()).first()
        
        # Estado de las fuentes
        fuentes_estado = {
            'espn': 'activa',
            'ligamx': 'activa',
            'futboltotal': 'activa',
            'mediotiempo': 'activa',
            'sofascore': 'activa',
            'flashscore': 'activa',
            'onefootball': 'activa'
        }
        
        status_data = {
            'sistema': 'Liga MX API - Panel L3HO',
            'version': '1.0.0',
            'estado': 'operativo',
            'estadisticas': {
                'equipos': total_equipos,
                'partidos': total_partidos,
                'jugadores': total_jugadores,
                'noticias': total_noticias
            },
            'ultima_actualizacion': ultima_actualizacion.created_at.isoformat() if ultima_actualizacion else None,
            'fuentes': fuentes_estado,
            'cache_activo': len(liga_mx_scraper.cache),
            'uptime': datetime.utcnow().isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo status: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

# ==================== ENDPOINTS ADICIONALES ====================

@app.route('/api/liga-mx/resultados', methods=['GET'])
@require_api_key
def get_resultados():
    """Obtener resultados recientes"""
    try:
        dias = int(request.args.get('dias', 7))
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        
        resultados = db.session.query(LigaMXPartido, 
                                    LigaMXEquipo.nombre.label('local'),
                                    LigaMXEquipo.nombre.label('visitante')).join(
            LigaMXEquipo, LigaMXPartido.equipo_local_id == LigaMXEquipo.id
        ).join(LigaMXEquipo, LigaMXPartido.equipo_visitante_id == LigaMXEquipo.id, aliased=True).filter(
            LigaMXPartido.estado == 'finalizado',
            LigaMXPartido.fecha_partido >= fecha_limite
        ).order_by(LigaMXPartido.fecha_partido.desc()).all()
        
        resultados_data = []
        for partido, local, visitante in resultados:
            resultados_data.append({
                'equipo_local': local,
                'equipo_visitante': visitante,
                'goles_local': partido.goles_local,
                'goles_visitante': partido.goles_visitante,
                'fecha': partido.fecha_partido.isoformat(),
                'jornada': partido.jornada
            })
        
        return jsonify({
            'success': True,
            'data': resultados_data,
            'total_resultados': len(resultados_data),
            'periodo': f'{dias} días',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error obteniendo resultados',
            'message': str(e)
        }), 500

@app.route('/api/liga-mx/jugadores', methods=['GET'])
@require_api_key
def get_jugadores():
    """Obtener lista de jugadores"""
    try:
        equipo = request.args.get('equipo')
        posicion = request.args.get('posicion')
        limit = int(request.args.get('limit', 50))
        
        query = db.session.query(LigaMXJugador, LigaMXEquipo.nombre.label('equipo')).join(LigaMXEquipo)
        
        if equipo:
            query = query.filter(LigaMXEquipo.nombre.ilike(f'%{equipo}%'))
        
        if posicion:
            query = query.filter(LigaMXJugador.posicion.ilike(f'%{posicion}%'))
        
        jugadores = query.filter(LigaMXJugador.is_active == True).limit(limit).all()
        
        jugadores_data = []
        for jugador, equipo_nombre in jugadores:
            jugadores_data.append({
                'id': jugador.id,
                'nombre': jugador.nombre,
                'equipo': equipo_nombre,
                'posicion': jugador.posicion,
                'numero': jugador.numero_camisa,
                'edad': jugador.edad,
                'nacionalidad': jugador.nacionalidad
            })
        
        return jsonify({
            'success': True,
            'data': jugadores_data,
            'total_jugadores': len(jugadores_data),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error obteniendo jugadores',
            'message': str(e)
        }), 500