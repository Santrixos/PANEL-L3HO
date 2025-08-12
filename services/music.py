"""
Servicio de música para Panel L3HO - Solo datos reales
API conectada con Spotify Web API
"""

import requests
import base64
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any

class MusicService:
    """Servicio para gestionar música con datos reales de Spotify"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        self.base_url = "https://api.spotify.com/v1"
        self.session = requests.Session()
    
    def is_configured(self) -> bool:
        """Verifica si el servicio está configurado correctamente"""
        return self.client_id is not None and self.client_secret is not None
    
    def _get_access_token(self) -> bool:
        """Obtiene token de acceso de Spotify"""
        if not self.is_configured():
            return False
        
        # Verificar si el token actual sigue siendo válido
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return True
        
        try:
            # Codificar credenciales
            credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post('https://accounts.spotify.com/api/token', 
                                   headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Token expira en 3600 segundos, renovar 5 minutos antes
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'] - 300)
            
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            return True
            
        except requests.RequestException as e:
            logging.error(f"Error obteniendo token de Spotify: {e}")
            return False
    
    def get_featured_playlists(self, limit: int = 20) -> Dict[str, Any]:
        """Obtiene playlists destacadas de Spotify"""
        if not self._get_access_token():
            return {
                'success': False,
                'error': 'Credenciales de Spotify no configuradas',
                'configuration_required': True
            }
        
        try:
            response = self.session.get(f"{self.base_url}/browse/featured-playlists",
                                      params={'limit': limit, 'country': 'MX'})
            response.raise_for_status()
            
            data = response.json()
            
            playlists = []
            for playlist in data.get('playlists', {}).get('items', []):
                playlists.append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist.get('description', ''),
                    'image': playlist['images'][0]['url'] if playlist.get('images') else None,
                    'tracks_total': playlist['tracks']['total'],
                    'owner': playlist['owner']['display_name'],
                    'external_url': playlist['external_urls']['spotify']
                })
            
            return {
                'success': True,
                'data': playlists,
                'message': data.get('message', 'Playlists destacadas')
            }
            
        except requests.RequestException as e:
            logging.error(f"Error obteniendo playlists: {e}")
            return {
                'success': False,
                'error': 'Error conectando con Spotify API'
            }
    
    def search_tracks(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Busca canciones en Spotify"""
        if not self._get_access_token():
            return {
                'success': False,
                'error': 'Credenciales de Spotify no configuradas',
                'configuration_required': True
            }
        
        try:
            response = self.session.get(f"{self.base_url}/search",
                                      params={
                                          'q': query,
                                          'type': 'track',
                                          'limit': limit,
                                          'market': 'MX'
                                      })
            response.raise_for_status()
            
            data = response.json()
            
            tracks = []
            for track in data.get('tracks', {}).get('items', []):
                tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'preview_url': track.get('preview_url'),
                    'image': track['album']['images'][0]['url'] if track['album'].get('images') else None,
                    'external_url': track['external_urls']['spotify']
                })
            
            return {
                'success': True,
                'data': tracks,
                'query': query
            }
            
        except requests.RequestException as e:
            logging.error(f"Error buscando música: {e}")
            return {
                'success': False,
                'error': 'Error en la búsqueda'
            }