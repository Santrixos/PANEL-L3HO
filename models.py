from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(64), unique=True)  # API key personal del usuario para fútbol
    api_key_transmisiones = db.Column(db.String(64), unique=True)  # API key separada para transmisiones
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_api_key(self):
        """Genera una API key única para el usuario (fútbol)"""
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        return self.api_key
    
    def generate_api_key_transmisiones(self):
        """Genera una API key única para transmisiones en vivo"""
        if not self.api_key_transmisiones:
            self.api_key_transmisiones = secrets.token_hex(32)
        return self.api_key_transmisiones

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)  # movies, music, mod_apps, football
    service_type = db.Column(db.String(50), nullable=False)   # tmdb, spotify, apk_mirror, football_api, etc.
    api_key = db.Column(db.String(512), nullable=False)
    api_url = db.Column(db.String(512))
    description = db.Column(db.Text)
    endpoints = db.Column(db.Text)  # Lista de endpoints separados por comas
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WebsiteControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # movies, music, mod_apps, football
    url = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, inactive, maintenance
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_key.id'))
    description = db.Column(db.Text)
    last_check = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    api_key = db.relationship('ApiKey', backref='websites')

# Nuevos modelos para el Panel Maestro Profesional

class ContentSection(db.Model):
    """Secciones de contenido administrables desde el panel"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # movies, music, mod_apps, football, etc.
    title = db.Column(db.String(200), nullable=False)  # Título mostrado al usuario
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    icon = db.Column(db.String(50), default='fa-cog')  # Font Awesome icon
    color_scheme = db.Column(db.String(20), default='primary')  # Bootstrap color
    sort_order = db.Column(db.Integer, default=0)
    settings = db.Column(db.Text)  # JSON con configuraciones específicas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== MODELOS LIGA MX API ====================

class LigaMXEquipo(db.Model):
    """Modelo para equipos de Liga MX"""
    __tablename__ = 'liga_mx_equipos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    nombre_completo = db.Column(db.String(200))
    ciudad = db.Column(db.String(100))
    estadio = db.Column(db.String(200))
    fundacion = db.Column(db.String(4))
    logo_url = db.Column(db.String(500))
    colores_primarios = db.Column(db.String(100))
    sitio_web = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    posiciones = db.relationship('LigaMXPosicion', backref='equipo_info', lazy='dynamic')
    partidos_local = db.relationship('LigaMXPartido', foreign_keys='LigaMXPartido.equipo_local_id', backref='equipo_local_info', lazy='dynamic')
    partidos_visitante = db.relationship('LigaMXPartido', foreign_keys='LigaMXPartido.equipo_visitante_id', backref='equipo_visitante_info', lazy='dynamic')

class LigaMXPosicion(db.Model):
    """Tabla de posiciones Liga MX"""
    __tablename__ = 'liga_mx_posiciones'
    
    id = db.Column(db.Integer, primary_key=True)
    temporada = db.Column(db.String(20), nullable=False, default='2024')
    jornada = db.Column(db.Integer, default=1)
    equipo_id = db.Column(db.Integer, db.ForeignKey('liga_mx_equipos.id'), nullable=False)
    posicion = db.Column(db.Integer, nullable=False)
    partidos_jugados = db.Column(db.Integer, default=0)
    ganados = db.Column(db.Integer, default=0)
    empatados = db.Column(db.Integer, default=0)
    perdidos = db.Column(db.Integer, default=0)
    goles_favor = db.Column(db.Integer, default=0)
    goles_contra = db.Column(db.Integer, default=0)
    diferencia_goles = db.Column(db.Integer, default=0)
    puntos = db.Column(db.Integer, default=0)
    fuente = db.Column(db.String(100))
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LigaMXPartido(db.Model):
    """Partidos y calendario Liga MX"""
    __tablename__ = 'liga_mx_partidos'
    
    id = db.Column(db.Integer, primary_key=True)
    temporada = db.Column(db.String(20), nullable=False, default='2024')
    jornada = db.Column(db.Integer, nullable=False)
    equipo_local_id = db.Column(db.Integer, db.ForeignKey('liga_mx_equipos.id'), nullable=False)
    equipo_visitante_id = db.Column(db.Integer, db.ForeignKey('liga_mx_equipos.id'), nullable=False)
    fecha_partido = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='programado')  # programado, en_vivo, finalizado, suspendido
    goles_local = db.Column(db.Integer, default=0)
    goles_visitante = db.Column(db.Integer, default=0)
    estadio = db.Column(db.String(200))
    arbitro = db.Column(db.String(200))
    asistencia = db.Column(db.Integer)
    minuto_actual = db.Column(db.Integer)
    fuente = db.Column(db.String(100))
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LigaMXJugador(db.Model):
    """Jugadores Liga MX"""
    __tablename__ = 'liga_mx_jugadores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('liga_mx_equipos.id'), nullable=False)
    posicion = db.Column(db.String(50))  # portero, defensa, medio, delantero
    numero_camisa = db.Column(db.Integer)
    edad = db.Column(db.Integer)
    nacionalidad = db.Column(db.String(100))
    altura = db.Column(db.String(10))
    peso = db.Column(db.String(10))
    pie_habil = db.Column(db.String(20))
    valor_mercado = db.Column(db.String(50))
    foto_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con equipo
    equipo = db.relationship('LigaMXEquipo', backref='jugadores')

class LigaMXEstadisticaJugador(db.Model):
    """Estadísticas de jugadores Liga MX"""
    __tablename__ = 'liga_mx_estadisticas_jugadores'
    
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('liga_mx_jugadores.id'), nullable=False)
    temporada = db.Column(db.String(20), nullable=False, default='2024')
    partidos_jugados = db.Column(db.Integer, default=0)
    goles = db.Column(db.Integer, default=0)
    asistencias = db.Column(db.Integer, default=0)
    tarjetas_amarillas = db.Column(db.Integer, default=0)
    tarjetas_rojas = db.Column(db.Integer, default=0)
    minutos_jugados = db.Column(db.Integer, default=0)
    fuente = db.Column(db.String(100))
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con jugador
    jugador = db.relationship('LigaMXJugador', backref='estadisticas')

class LigaMXNoticia(db.Model):
    """Noticias Liga MX"""
    __tablename__ = 'liga_mx_noticias'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(500), nullable=False)
    resumen = db.Column(db.Text)  # Cambio de contenido a resumen
    url = db.Column(db.String(1000))  # Cambio de url_externa a url
    imagen_url = db.Column(db.String(500))
    equipo_id = db.Column(db.Integer, db.ForeignKey('liga_mx_equipos.id'))
    categoria = db.Column(db.String(100))  # transferencias, resultados, general
    fecha = db.Column(db.DateTime, default=datetime.utcnow)  # Cambio de fecha_publicacion a fecha
    fuente = db.Column(db.String(100))
    hash_contenido = db.Column(db.String(64), unique=True)  # Para evitar duplicados
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con equipo
    equipo = db.relationship('LigaMXEquipo', backref='noticias')

class LigaMXActualizacion(db.Model):
    """Log de actualizaciones del sistema Liga MX"""
    __tablename__ = 'liga_mx_actualizaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_actualizacion = db.Column(db.String(100), nullable=False)  # tabla, calendario, jugadores, etc.
    elementos_actualizados = db.Column(db.Integer, default=0)
    fuentes_consultadas = db.Column(db.Text)  # JSON con fuentes usadas
    errores = db.Column(db.Text)  # JSON con errores encontrados
    tiempo_ejecucion = db.Column(db.Float)  # Segundos
    status = db.Column(db.String(20), default='success')  # success, error, partial
    detalles = db.Column(db.Text)  # JSON con detalles adicionales
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con contenido - comentada temporalmente
    # content_items = db.relationship('ContentItem', backref='section', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_settings(self):
        """Obtiene las configuraciones como diccionario"""
        if self.settings:
            try:
                return json.loads(self.settings)
            except:
                return {}
        return {}
    
    def set_settings(self, settings_dict):
        """Establece las configuraciones desde un diccionario"""
        self.settings = json.dumps(settings_dict)

# Modelos de contenido temporalmente comentados para evitar errores de relación
# class ContentItem(db.Model):
#     """Items de contenido individual para cada sección"""

class MediaFile(db.Model):
    """Archivos multimedia subidos al sistema"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    mime_type = db.Column(db.String(100))
    file_type = db.Column(db.String(20))  # image, video, audio, document
    content_item_id = db.Column(db.Integer, db.ForeignKey('content_item.id'))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)  # Para versionado de archivos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con usuario
    uploader = db.relationship('User', backref='uploaded_files')

class SystemLog(db.Model):
    """Logs del sistema para auditoría y monitoreo"""
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    category = db.Column(db.String(50), nullable=False)  # AUTH, API, CONTENT, SYSTEM
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)  # JSON con detalles adicionales
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(512))
    endpoint = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con usuario
    user = db.relationship('User', backref='system_logs')

class Notification(db.Model):
    """Sistema de notificaciones internas"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), default='info')  # info, success, warning, error
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # null = para todos los admins
    is_read = db.Column(db.Boolean, default=False)
    is_system = db.Column(db.Boolean, default=False)  # Notificación del sistema
    action_url = db.Column(db.String(512))  # URL opcional para acción
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Relación con usuario
    user = db.relationship('User', backref='notifications')

class ScheduledTask(db.Model):
    """Tareas programadas para publicaciones automáticas"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # publish_content, backup_db, etc.
    scheduled_for = db.Column(db.DateTime, nullable=False)
    recurrence = db.Column(db.String(50))  # daily, weekly, monthly, once
    task_data = db.Column(db.Text)  # JSON con datos de la tarea
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con usuario
    creator = db.relationship('User', backref='scheduled_tasks')

class ApiUsage(db.Model):
    """Registro de uso de APIs para estadísticas"""
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(64), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(45))
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # En milisegundos
    request_data = db.Column(db.Text)  # JSON con datos de la petición
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con usuario
    user = db.relationship('User', backref='api_usage')
