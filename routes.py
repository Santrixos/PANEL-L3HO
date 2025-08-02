from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, ApiKey, WebsiteControl
from services.futbol import FutbolService
from services.transmisiones import TransmisionesService
from datetime import datetime
import requests
import os
import secrets
from functools import wraps

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('¡Bienvenido al Panel L3HO!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get statistics
    stats = {
        'total_apis': ApiKey.query.count(),
        'active_apis': ApiKey.query.filter_by(is_active=True).count(),
        'total_websites': WebsiteControl.query.count(),
        'active_websites': WebsiteControl.query.filter_by(status='active').count(),
        'movies_sites': WebsiteControl.query.filter_by(category='movies').count(),
        'music_sites': WebsiteControl.query.filter_by(category='music').count(),
        'mod_apps_sites': WebsiteControl.query.filter_by(category='mod_apps').count(),
        'football_sites': WebsiteControl.query.filter_by(category='football').count()
    }
    
    recent_websites = WebsiteControl.query.order_by(WebsiteControl.created_at.desc()).limit(5).all()
    
    # Obtener usuario actual
    user = User.query.filter_by(username=session['username']).first()
    
    # Generar API keys si no existen
    if user and not user.api_key:
        user.generate_api_key()
        db.session.commit()
    
    if user and not user.api_key_transmisiones:
        user.generate_api_key_transmisiones()
        db.session.commit()
    
    return render_template('dashboard.html', stats=stats, recent_websites=recent_websites, current_user=user)

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('dashboard'))
    
    apis = ApiKey.query.all()
    websites = WebsiteControl.query.all()
    users = User.query.all()
    
    return render_template('admin.html', apis=apis, websites=websites, users=users)

@app.route('/admin/api/add', methods=['POST'])
def add_api():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    try:
        api = ApiKey()
        api.service_name = request.form['service_name']
        api.service_type = request.form['service_type']
        api.api_key = request.form['api_key']
        api.api_url = request.form.get('api_url', '')
        api.description = request.form.get('description', '')
        db.session.add(api)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'API agregada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/admin/api/delete/<int:api_id>', methods=['DELETE'])
def delete_api(api_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    try:
        api = ApiKey.query.get_or_404(api_id)
        db.session.delete(api)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'API eliminada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/admin/website/add', methods=['POST'])
def add_website():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    try:
        website = WebsiteControl()
        website.name = request.form['name']
        website.category = request.form['category']
        website.url = request.form['url']
        website.api_key_id = request.form.get('api_key_id') or None
        website.description = request.form.get('description', '')
        db.session.add(website)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Sitio web agregado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/admin/website/delete/<int:website_id>', methods=['DELETE'])
def delete_website(website_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    try:
        website = WebsiteControl.query.get(website_id)
        if not website:
            return jsonify({'success': False, 'message': 'Sitio web no encontrado'})
        db.session.delete(website)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Sitio web eliminado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/admin/website/status/<int:website_id>', methods=['PUT'])
def update_website_status(website_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    try:
        website = WebsiteControl.query.get(website_id)
        if not website:
            return jsonify({'success': False, 'message': 'Sitio web no encontrado'})
        
        data = request.get_json()
        new_status = data.get('status') if data else None
        
        if new_status in ['active', 'inactive', 'maintenance']:
            website.status = new_status
            website.last_check = datetime.utcnow()
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Estado actualizado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Estado inválido'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# API Protection decorator
def require_api_key(f):
    """Decorator para proteger rutas de API con clave personal"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('key')
        if not api_key:
            return jsonify({
                'error': 'API Key requerida',
                'message': 'Incluye el parámetro ?key=TU_API_KEY en la URL'
            }), 401
        
        # Verificar que la API key existe y pertenece a un usuario válido
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({
                'error': 'API Key inválida',
                'message': 'La clave proporcionada no es válida'
            }), 403
        
        # Pasar el usuario al endpoint
        return f(user, *args, **kwargs)
    return decorated_function

def require_transmisiones_api_key(f):
    """Decorator para proteger rutas de API de transmisiones con clave separada"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('key')
        if not api_key:
            return jsonify({
                'error': 'API Key de transmisiones requerida',
                'message': 'Incluye el parámetro ?key=TU_API_KEY_TRANSMISIONES en la URL'
            }), 401
        
        # Verificar que la API key de transmisiones existe y pertenece a un usuario válido
        user = User.query.filter_by(api_key_transmisiones=api_key).first()
        if not user:
            return jsonify({
                'error': 'API Key de transmisiones inválida',
                'message': 'La clave proporcionada no es válida para transmisiones'
            }), 403
        
        # Pasar el usuario al endpoint
        return f(user, *args, **kwargs)
    return decorated_function

# ========================================
# API PRIVADA DE FÚTBOL
# ========================================

@app.route('/api/tabla')
@require_api_key
def api_tabla_liga_mx(user):
    """API: Obtiene la tabla completa de posiciones de Liga MX con todos los datos"""
    try:
        futbol_service = FutbolService()
        tabla = futbol_service.get_liga_mx_tabla_completa()
        
        return jsonify({
            'success': True,
            'data': tabla,
            'api_version': '2.0',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/jugadores')
@require_api_key
def api_jugadores_equipo(user):
    """API: Obtiene plantilla completa de jugadores de un equipo específico"""
    equipo = request.args.get('equipo')
    if not equipo:
        return jsonify({
            'error': 'Parámetro requerido',
            'message': 'Incluye el parámetro ?equipo=NOMBRE_EQUIPO o ?equipo=ID_EQUIPO',
            'equipos_disponibles': ['america', 'chivas', 'cruz_azul', 'pumas', 'tigres', 'monterrey', 'santos', 'leon']
        }), 400
    
    try:
        futbol_service = FutbolService()
        jugadores = futbol_service.get_jugadores_equipo(equipo)
        
        return jsonify({
            'success': True,
            'data': jugadores,
            'api_version': '2.0',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/equipo')
@require_api_key
def api_equipo_detallado(user):
    """API: Obtiene información detallada completa de un equipo específico"""
    equipo = request.args.get('equipo')
    if not equipo:
        return jsonify({
            'error': 'Parámetro requerido',
            'message': 'Incluye el parámetro ?equipo=NOMBRE_EQUIPO o ?equipo=ID_EQUIPO',
            'equipos_disponibles': ['america', 'chivas', 'cruz_azul', 'pumas', 'tigres', 'monterrey', 'santos', 'leon']
        }), 400
    
    try:
        futbol_service = FutbolService()
        equipo_data = futbol_service.get_equipo_detallado(equipo)
        
        return jsonify({
            'success': True,
            'data': equipo_data,
            'api_version': '2.0',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/logo')
@require_api_key
def api_logo_equipo(user):
    """API: Obtiene el logo y recursos visuales de un equipo"""
    equipo = request.args.get('equipo')
    if not equipo:
        return jsonify({
            'error': 'Parámetro requerido',
            'message': 'Incluye el parámetro ?equipo=NOMBRE_EQUIPO o ?equipo=ID_EQUIPO'
        }), 400
    
    try:
        futbol_service = FutbolService()
        equipo_data = futbol_service.get_equipo_detallado(equipo)
        
        if not equipo_data.get('success'):
            return jsonify(equipo_data), 404
        
        logo_data = {
            'equipo_id': equipo_data['data']['equipo_id'],
            'nombre_completo': equipo_data['data']['informacion_basica']['nombre_completo'],
            'nombre_corto': equipo_data['data']['informacion_basica']['nombre_corto'],
            'logo_principal': equipo_data['data']['recursos']['logo_url'],
            'logo_alternativo': equipo_data['data']['recursos']['logo_alternativo'],
            'colores_primarios': equipo_data['data']['informacion_basica']['colores_primarios'],
            'colores_secundarios': equipo_data['data']['informacion_basica']['colores_secundarios']
        }
        
        return jsonify({
            'success': True,
            'data': logo_data,
            'api_version': '2.0',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/calendario')
@require_api_key
def api_calendario_liga_mx(user):
    """API: Obtiene el calendario completo de partidos con resultados y próximos juegos"""
    try:
        futbol_service = FutbolService()
        calendario = futbol_service.get_calendario_completo()
        
        return jsonify({
            'success': True,
            'data': calendario,
            'api_version': '2.0',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/estadisticas')
@require_api_key
def api_estadisticas_globales(user):
    """API: Obtiene estadísticas globales y rankings de Liga MX"""
    try:
        futbol_service = FutbolService()
        estadisticas = futbol_service.get_estadisticas_globales()
        
        return jsonify({
            'success': True,
            'data': estadisticas,
            'api_version': '2.0',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/equipos')
@require_api_key
def api_lista_equipos(user):
    """API: Lista todos los equipos de Liga MX con información básica"""
    try:
        futbol_service = FutbolService()
        equipos_lista = []
        
        for equipo_id in futbol_service.equipos_ligamx.keys():
            equipo_data = futbol_service.get_equipo_detallado(equipo_id)
            if equipo_data.get('success'):
                data = equipo_data['data']
                equipos_lista.append({
                    'equipo_id': equipo_id,
                    'nombre_completo': data['informacion_basica']['nombre_completo'],
                    'nombre_corto': data['informacion_basica']['nombre_corto'],
                    'nombre_oficial': data['informacion_basica']['nombre_oficial'],
                    'apodo': data['informacion_basica']['apodo'],
                    'ciudad': data['ubicacion']['ciudad'],
                    'estado': data['ubicacion']['estado'],
                    'estadio': data['estadio']['nombre'],
                    'capacidad': data['estadio']['capacidad'],
                    'fundacion': data['informacion_basica']['fundacion'],
                    'colores': data['informacion_basica']['colores_primarios'],
                    'logo_url': data['recursos']['logo_url'],
                    'sitio_web': data['medios_oficiales']['sitio_web']
                })
        
        return jsonify({
            'success': True,
            'data': {
                'liga': 'Liga MX',
                'temporada': '2024-25',
                'total_equipos': len(equipos_lista),
                'equipos': equipos_lista
            },
            'api_version': '2.0',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/info')
@require_api_key
def api_info(user):
    """API: Información completa y documentación de la API de fútbol"""
    return jsonify({
        'api_name': 'Panel L3HO - API Privada de Fútbol Liga MX',
        'version': '2.0',
        'descripcion': 'API completa y profesional para Liga MX con datos reales y actualizados',
        'liga': 'Liga MX',
        'temporada': '2024-25',
        'total_equipos': 18,
        'fuentes_datos': [
            'ESPN México',
            'Liga MX Oficial', 
            'Transfermarkt',
            'Datos estructurados con información oficial'
        ],
        'endpoints': {
            '/api/info': {
                'descripcion': 'Información general y documentación de la API',
                'parametros': 'key (requerido)',
                'ejemplo': '/api/info?key=TU_API_KEY'
            },
            '/api/tabla': {
                'descripcion': 'Tabla completa de posiciones con estadísticas detalladas',
                'parametros': 'key (requerido)',
                'ejemplo': '/api/tabla?key=TU_API_KEY',
                'datos_incluidos': [
                    'Posición, puntos, partidos jugados',
                    'Victorias, empates, derrotas',
                    'Goles a favor y en contra, diferencia',
                    'Efectividad porcentual',
                    'Información completa del equipo',
                    'Estadio, capacidad, colores, logos',
                    'Director técnico, presidente',
                    'Redes sociales oficiales'
                ]
            },
            '/api/equipos': {
                'descripcion': 'Lista completa de todos los equipos de Liga MX',
                'parametros': 'key (requerido)',
                'ejemplo': '/api/equipos?key=TU_API_KEY',
                'datos_incluidos': [
                    'Información básica de todos los equipos',
                    'Nombres completos y oficiales',
                    'Ubicación, estadios, capacidades',
                    'Fundación, colores, logos'
                ]
            },
            '/api/equipo': {
                'descripcion': 'Información detallada completa de un equipo específico',
                'parametros': 'key (requerido), equipo (requerido)',
                'ejemplo': '/api/equipo?equipo=america&key=TU_API_KEY',
                'equipos_disponibles': ['america', 'chivas', 'cruz_azul', 'pumas', 'tigres', 'monterrey', 'santos', 'leon'],
                'datos_incluidos': [
                    'Información básica completa',
                    'Ubicación y estadio detallado',
                    'Directiva actual',
                    'Estadísticas de temporada',
                    'Medios oficiales y redes sociales',
                    'Recursos visuales (logos)'
                ]
            },
            '/api/jugadores': {
                'descripcion': 'Plantilla completa de jugadores de un equipo',
                'parametros': 'key (requerido), equipo (requerido)',
                'ejemplo': '/api/jugadores?equipo=chivas&key=TU_API_KEY',
                'datos_incluidos': [
                    'Información personal completa',
                    'Posición y número',
                    'Edad, nacionalidad, características físicas',
                    'Estadísticas de temporada',
                    'Valor de mercado estimado',
                    'Organización por posiciones'
                ]
            },
            '/api/logo': {
                'descripcion': 'Logos y recursos visuales de un equipo',
                'parametros': 'key (requerido), equipo (requerido)',
                'ejemplo': '/api/logo?equipo=pumas&key=TU_API_KEY',
                'datos_incluidos': [
                    'Logo principal y alternativo',
                    'Colores oficiales primarios y secundarios',
                    'Información visual del equipo'
                ]
            },
            '/api/calendario': {
                'descripcion': 'Calendario completo con partidos pasados, en vivo y futuros',
                'parametros': 'key (requerido)',
                'ejemplo': '/api/calendario?key=TU_API_KEY',
                'datos_incluidos': [
                    'Partidos finalizados con resultados',
                    'Partidos en vivo',
                    'Partidos programados',
                    'Fecha, hora, estadio',
                    'Estado del partido, jornadas'
                ]
            },
            '/api/estadisticas': {
                'descripcion': 'Estadísticas globales y rankings de toda la liga',
                'parametros': 'key (requerido)',
                'ejemplo': '/api/estadisticas?key=TU_API_KEY',
                'datos_incluidos': [
                    'Estadísticas generales de liga',
                    'Líderes por categorías',
                    'Rankings de mejor ataque/defensa',
                    'Equipos más efectivos',
                    'Promedios de goles'
                ]
            }
        },
        'autenticacion': {
            'tipo': 'API Key personal',
            'parametro': 'key',
            'formato': '?key=TU_API_KEY_PERSONAL',
            'obtencion': 'Generar desde el panel de administración'
        },
        'formatos_respuesta': {
            'tipo': 'JSON',
            'estructura': {
                'success': 'boolean - Estado de la operación',
                'data': 'object - Datos solicitados',
                'api_version': 'string - Versión de la API',
                'usuario': 'string - Usuario autenticado',
                'timestamp': 'string - Timestamp ISO de la respuesta'
            }
        },
        'codigos_estado': {
            '200': 'Éxito - Datos obtenidos correctamente',
            '400': 'Error de parámetros - Faltan parámetros requeridos',
            '401': 'No autorizado - API Key requerida',
            '403': 'Prohibido - API Key inválida',
            '404': 'No encontrado - Recurso no existe',
            '500': 'Error interno del servidor'
        },
        'usuario_actual': user.username,
        'api_key_usuario': user.api_key,
        'solicitudes_realizadas': 'Ilimitadas',
        'actualizacion_datos': 'Tiempo real desde fuentes oficiales',
        'soporte_tecnico': 'Panel L3HO - Administración',
        'timestamp': datetime.now().isoformat()
    })

# ========================================
# API PRIVADA DE TRANSMISIONES EN VIVO
# ========================================

@app.route('/api/transmisiones')
@require_transmisiones_api_key
def api_transmisiones_en_vivo(user):
    """API Transmisiones: Obtiene todos los partidos en vivo con datos reales"""
    try:
        transmisiones_service = TransmisionesService()
        partidos = transmisiones_service.get_partidos_en_vivo()
        
        return jsonify({
            'success': True,
            'data': partidos,
            'api_version': '1.0',
            'api_type': 'transmisiones',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/transmisiones/detalle')
@require_transmisiones_api_key
def api_transmisiones_detalle(user):
    """API Transmisiones: Obtiene detalles completos de un partido específico"""
    partido_id = request.args.get('id')
    if not partido_id:
        return jsonify({
            'error': 'Parámetro requerido',
            'message': 'Incluye el parámetro ?id=ID_PARTIDO para obtener detalles'
        }), 400
    
    try:
        transmisiones_service = TransmisionesService()
        detalle = transmisiones_service.get_detalle_partido(partido_id)
        
        return jsonify({
            'success': True,
            'data': detalle,
            'api_version': '1.0',
            'api_type': 'transmisiones',
            'usuario': user.username,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@app.route('/api/transmisiones/info')
@require_transmisiones_api_key
def api_transmisiones_info(user):
    """API Transmisiones: Información y documentación de la API de transmisiones"""
    return jsonify({
        'api_name': 'Panel L3HO - API Privada de Transmisiones en Vivo',
        'version': '1.0',
        'descripcion': 'API especializada en datos en tiempo real de partidos de Liga MX',
        'liga': 'Liga MX',
        'temporada': '2024-25',
        'tipo_datos': 'Tiempo real',
        'fuentes_datos': [
            'ESPN México (En Vivo)',
            'Liga MX Oficial (Resultados en vivo)', 
            'OneFootball',
            'Google Sports'
        ],
        'endpoints': {
            '/api/transmisiones': {
                'descripcion': 'Lista todos los partidos en vivo y estados actuales',
                'parametros': 'key (requerido)',
                'ejemplo': '/api/transmisiones?key=TU_API_KEY_TRANSMISIONES',
                'datos_incluidos': [
                    'Partidos en vivo con marcador actual',
                    'Minuto del partido',
                    'Estado (en vivo, medio tiempo, finalizado)',
                    'Estadio y canal de transmisión',
                    'Partidos próximos y recientes del día'
                ]
            },
            '/api/transmisiones/detalle': {
                'descripcion': 'Detalles completos de un partido específico',
                'parametros': 'key (requerido), id (requerido)',
                'ejemplo': '/api/transmisiones/detalle?id=PARTIDO_ID&key=TU_API_KEY',
                'datos_incluidos': [
                    'Estadísticas detalladas (posesión, tiros, faltas)',
                    'Eventos del partido (goles, tarjetas)',
                    'Información de transmisión completa',
                    'Enlaces de seguimiento en vivo',
                    'Canales de TV y streaming disponibles'
                ]
            },
            '/api/transmisiones/info': {
                'descripcion': 'Información y documentación de la API',
                'parametros': 'key (requerido)',
                'ejemplo': '/api/transmisiones/info?key=TU_API_KEY'
            }
        },
        'diferencias_api_futbol': {
            'enfoque': 'Datos en tiempo real vs datos históricos/estadísticos',
            'actualizacion': 'Cada minuto vs diaria',
            'clave_api': 'Separada e independiente',
            'uso_recomendado': 'Seguimiento de partidos en vivo'
        },
        'autenticacion': {
            'tipo': 'API Key personal para transmisiones',
            'parametro': 'key',
            'formato': '?key=TU_API_KEY_TRANSMISIONES',
            'obtencion': 'Panel de administración - sección separada'
        },
        'canales_transmision': [
            'FOX Sports México',
            'ESPN México',
            'TUDN',
            'TV Azteca',
            'Televisa Deportes',
            'Claro Sports'
        ],
        'usuario_actual': user.username,
        'api_key_transmisiones': user.api_key_transmisiones,
        'solicitudes_realizadas': 'Ilimitadas',
        'actualizacion_datos': 'Tiempo real cada minuto',
        'timestamp': datetime.now().isoformat()
    })

# ========================================
# GESTIÓN DE API KEYS
# ========================================

@app.route('/admin/my-api-key')
def admin_my_api_key():
    """Panel para ver/generar la API key personal"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    # Generar API keys si no existen
    if not user.api_key:
        user.generate_api_key()
        db.session.commit()
    
    if not user.api_key_transmisiones:
        user.generate_api_key_transmisiones()
        db.session.commit()
        flash('API Key generada exitosamente.', 'success')
    
    return render_template('admin/api_key.html', user=user)

@app.route('/admin/regenerate-api-key', methods=['POST'])
def regenerate_api_key():
    """Regenera la API key del usuario"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'})
    
    # Generar nueva API key
    user.api_key = secrets.token_hex(32)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'API Key regenerada exitosamente',
        'new_key': user.api_key
    })

# Initialize admin user if it doesn't exist
def create_admin_user():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User()
        admin.username = 'admin'
        admin.email = 'admin@panell3ho.com'
        admin.is_admin = True
        admin.set_password('admin123')  # Change this in production
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin/admin123")

# Football/Sports module routes
@app.route('/football')
def football_module():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    leagues = [
        {'id': 'mx', 'name': 'Liga MX', 'country': 'México'},
        {'id': 'es', 'name': 'LaLiga', 'country': 'España'},
        {'id': 'en', 'name': 'Premier League', 'country': 'Inglaterra'},
        {'id': 'de', 'name': 'Bundesliga', 'country': 'Alemania'},
        {'id': 'it', 'name': 'Serie A', 'country': 'Italia'},
        {'id': 'fr', 'name': 'Ligue 1', 'country': 'Francia'}
    ]
    
    return render_template('modules/football.html', leagues=leagues)

@app.route('/music')
def music_module():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('modules/music.html')

@app.route('/movies')
def movies_module():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('modules/movies.html')

@app.route('/mod_apps')
def mod_apps_module():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('modules/mod_apps.html')

# API endpoints for data export
@app.route('/api/export/<category>')
def export_data(category):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get API key validation
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API Key required'}), 401
    
    # Validate API key
    valid_api = ApiKey.query.filter_by(api_key=api_key, is_active=True).first()
    if not valid_api:
        return jsonify({'error': 'Invalid API Key'}), 401
    
    try:
        if category == 'websites':
            websites = WebsiteControl.query.all()
            data = [{
                'id': w.id,
                'name': w.name,
                'category': w.category,
                'url': w.url,
                'status': w.status,
                'created_at': w.created_at.isoformat() if w.created_at else None
            } for w in websites]
        elif category == 'apis':
            apis = ApiKey.query.all()
            data = [{
                'id': a.id,
                'service_name': a.service_name,
                'service_type': a.service_type,
                'is_active': a.is_active,
                'created_at': a.created_at.isoformat() if a.created_at else None
            } for a in apis]
        else:
            return jsonify({'error': 'Invalid category'}), 400
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'exported_at': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint to check system status"""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API Key required'}), 401
    
    valid_api = ApiKey.query.filter_by(api_key=api_key, is_active=True).first()
    if not valid_api:
        return jsonify({'error': 'Invalid API Key'}), 401
    
    stats = {
        'total_apis': ApiKey.query.count(),
        'active_apis': ApiKey.query.filter_by(is_active=True).count(),
        'total_websites': WebsiteControl.query.count(),
        'active_websites': WebsiteControl.query.filter_by(status='active').count(),
        'last_updated': datetime.utcnow().isoformat(),
        'system_status': 'operational'
    }
    
    return jsonify(stats)

# Update logs and activity tracking
@app.route('/admin/logs')
def view_logs():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get recent website updates
    recent_updates = WebsiteControl.query.filter(
        WebsiteControl.last_check.isnot(None)
    ).order_by(WebsiteControl.last_check.desc()).limit(50).all()
    
    return render_template('admin/logs.html', recent_updates=recent_updates)

@app.route('/admin/api/test/<int:api_id>', methods=['POST'])
def test_api_connection(api_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    try:
        api = ApiKey.query.get(api_id)
        if not api:
            return jsonify({'success': False, 'message': 'API no encontrada'})
        
        # Test API connection based on service type
        test_url = api.api_url or 'https://httpbin.org/get'
        headers = {'Authorization': f'Bearer {api.api_key}'} if api.api_key else {}
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                'success': True, 
                'message': 'Conexión exitosa',
                'status_code': response.status_code
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Error de conexión: {response.status_code}'
            })
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'Timeout de conexión'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Error de conexión'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Call this function when the app starts
with app.app_context():
    create_admin_user()
