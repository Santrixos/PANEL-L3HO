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
    
    # Relación con contenido
    content_items = db.relationship('ContentItem', backref='section', lazy='dynamic', cascade='all, delete-orphan')
    
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

class ContentItem(db.Model):
    """Items de contenido individual para cada sección"""
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('content_section.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    content_data = db.Column(db.Text)  # JSON con datos específicos del contenido
    featured_image = db.Column(db.String(512))  # URL de imagen principal
    status = db.Column(db.String(20), default='published')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con usuario
    creator = db.relationship('User', backref='created_content')
    
    # Relación con archivos
    media_files = db.relationship('MediaFile', backref='content_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_content_data(self):
        """Obtiene los datos de contenido como diccionario"""
        if self.content_data:
            try:
                return json.loads(self.content_data)
            except:
                return {}
        return {}
    
    def set_content_data(self, data_dict):
        """Establece los datos de contenido desde un diccionario"""
        self.content_data = json.dumps(data_dict)

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
