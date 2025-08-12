"""
Servicio de películas para Panel L3HO - Solo datos reales
API conectada con The Movie Database (TMDB)
"""

import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any

class MoviesService:
    """Servicio para gestionar películas con datos reales de TMDB"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
    
    def is_configured(self) -> bool:
        """Verifica si el servicio está configurado correctamente"""
        return self.api_key is not None
    
    def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """Obtiene películas populares de TMDB"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'API key de TMDB no configurada',
                'configuration_required': True
            }
        
        try:
            response = self.session.get(f"{self.base_url}/movie/popular", params={'page': page})
            response.raise_for_status()
            
            data = response.json()
            
            movies = []
            for movie in data.get('results', []):
                movies.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'poster_path': f"{self.image_base_url}/w500{movie['poster_path']}" if movie.get('poster_path') else None,
                    'backdrop_path': f"{self.image_base_url}/w1280{movie['backdrop_path']}" if movie.get('backdrop_path') else None,
                    'release_date': movie['release_date'],
                    'vote_average': movie['vote_average'],
                    'vote_count': movie['vote_count'],
                    'popularity': movie['popularity']
                })
            
            return {
                'success': True,
                'data': movies,
                'total_pages': data['total_pages'],
                'current_page': page,
                'total_results': data['total_results']
            }
            
        except requests.RequestException as e:
            logging.error(f"Error obteniendo películas populares: {e}")
            return {
                'success': False,
                'error': 'Error conectando con TMDB API'
            }
    
    def search_movies(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Busca películas por nombre"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'API key de TMDB no configurada',
                'configuration_required': True
            }
        
        try:
            response = self.session.get(f"{self.base_url}/search/movie", 
                                      params={'query': query, 'page': page})
            response.raise_for_status()
            
            data = response.json()
            
            movies = []
            for movie in data.get('results', []):
                movies.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'poster_path': f"{self.image_base_url}/w500{movie['poster_path']}" if movie.get('poster_path') else None,
                    'release_date': movie['release_date'],
                    'vote_average': movie['vote_average']
                })
            
            return {
                'success': True,
                'data': movies,
                'query': query,
                'total_results': data['total_results']
            }
            
        except requests.RequestException as e:
            logging.error(f"Error buscando películas: {e}")
            return {
                'success': False,
                'error': 'Error en la búsqueda'
            }