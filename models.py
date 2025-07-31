from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
