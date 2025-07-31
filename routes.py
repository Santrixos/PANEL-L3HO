from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, ApiKey, WebsiteControl
from datetime import datetime
import requests
import os

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
    
    return render_template('dashboard.html', stats=stats, recent_websites=recent_websites)

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
        new_status = request.json.get('status')
        
        if new_status in ['active', 'inactive', 'maintenance']:
            website.status = new_status
            website.last_check = datetime.utcnow()
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Estado actualizado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Estado inválido'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

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

# Call this function when the app starts
with app.app_context():
    create_admin_user()
