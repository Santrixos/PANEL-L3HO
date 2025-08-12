"""
Rutas adicionales para el sistema de scraping de música
Panel L3HO - Sistema profesional de scraping
"""

from flask import jsonify, request, session, redirect, url_for, render_template
from app import app, db
from models import ApiKey
from services.scraping_musica import MusicScrapingService
from datetime import datetime
import logging

# Inicializar servicio de scraping
scraping_music = MusicScrapingService()

@app.route('/api/music/scraping/sources')
def api_music_scraping_sources():
    """API: Estado de las fuentes de scraping"""
    try:
        result = scraping_music.get_sources_status()
        result['api_version'] = '1.0'
        result['timestamp'] = datetime.now().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo fuentes: {str(e)}'
        }), 500

@app.route('/music/scraping-panel')
def scraping_music_panel():
    """Panel de administración del sistema de scraping"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Obtener estado de fuentes
        sources_status = scraping_music.get_sources_status()
        
        # Obtener estadísticas de caché
        cache_stats = scraping_music.get_cache_stats()
        
        return render_template('scraping_music_panel.html', 
                             sources_status=sources_status,
                             cache_stats=cache_stats)
        
    except Exception as e:
        logging.error(f"Error en panel de scraping: {e}")
        return render_template('error.html', 
                             error="Error cargando panel de scraping")

@app.route('/music/test-scraping/<source>')
def test_scraping_source(source):
    """Probar una fuente de scraping específica"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    try:
        # Probar búsqueda simple
        if source in scraping_music.sources:
            if source == 'youtube_music':
                test_result = scraping_music._scrape_youtube_music_songs("test", 1)
            elif source == 'soundcloud':
                test_result = scraping_music._scrape_soundcloud_songs("test", 1)
            elif source == 'jamendo':
                test_result = scraping_music._scrape_jamendo_songs("test", 1)
            elif source == 'audiomack':
                test_result = scraping_music._scrape_audiomack_songs("test", 1)
            elif source == 'bandcamp':
                test_result = scraping_music._scrape_bandcamp_songs("test", 1)
            elif source == 'musixmatch':
                test_result = scraping_music._scrape_musixmatch_lyrics("test", "test")
                test_result = [test_result] if test_result else []
            else:
                test_result = []
            
            if test_result:
                return jsonify({
                    'success': True,
                    'message': f'Fuente {source} funcionando correctamente',
                    'sample_results': len(test_result)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Fuente {source} no devolvió resultados'
                })
        else:
            return jsonify({
                'success': False,
                'message': f'Fuente {source} no encontrada'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error probando fuente {source}: {str(e)}'
        })

@app.route('/music/configure-scraping-sources', methods=['POST'])
def configure_scraping_sources():
    """Configurar estado de las fuentes de scraping"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
    
    try:
        data = request.get_json()
        
        if not data or 'sources' not in data:
            return jsonify({
                'success': False,
                'message': 'Datos de configuración requeridos'
            }), 400
        
        # Actualizar estado de fuentes
        for source_key, source_config in data['sources'].items():
            if source_key in scraping_music.sources:
                scraping_music.sources[source_key]['active'] = source_config.get('active', True)
                scraping_music.sources[source_key]['priority'] = source_config.get('priority', 1)
        
        # Registrar en base de datos como API Keys del sistema
        for source_key, source_info in scraping_music.sources.items():
            # Verificar si ya existe
            existing_api = ApiKey.query.filter_by(
                service_name='music_scraping',
                service_type=source_key
            ).first()
            
            if not existing_api:
                # Crear entrada en API Keys para el panel
                new_api = ApiKey()
                new_api.service_name = 'music_scraping'
                new_api.service_type = source_key
                new_api.api_key = f'scraping_{source_key}_internal'  # Clave interna
                new_api.description = source_info['name']
                new_api.is_active = source_info['active']
                new_api.endpoints = ','.join(source_info['methods'])
                
                db.session.add(new_api)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Configuración actualizada correctamente'
        })
        
    except Exception as e:
        logging.error(f"Error configurando fuentes de scraping: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500

@app.route('/music/scraping/demo')
def scraping_demo():
    """Demostración del sistema de scraping"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Realizar búsquedas de ejemplo
        demo_results = {}
        
        # Demo de canciones
        demo_results['songs'] = scraping_music.search_songs("love", 5)
        
        # Demo de álbumes
        demo_results['albums'] = scraping_music.search_albums("greatest hits", 3)
        
        # Demo de charts
        demo_results['charts'] = scraping_music.get_top_charts("global", 10)
        
        # Demo de letras
        demo_results['lyrics'] = scraping_music.get_song_lyrics("Imagine", "John Lennon")
        
        return render_template('scraping_demo.html', demo_results=demo_results)
        
    except Exception as e:
        logging.error(f"Error en demo de scraping: {e}")
        return render_template('error.html', 
                             error="Error cargando demostración")