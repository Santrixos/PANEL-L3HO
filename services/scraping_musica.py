"""
Sistema de scraping profesional para música - Panel L3HO
Extracción de datos reales de múltiples fuentes sin dependencia de APIs oficiales
"""

import requests
import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import hashlib
from urllib.parse import urljoin, urlparse, quote_plus
import yt_dlp
from pydub import AudioSegment
from bs4 import BeautifulSoup
import re
import random

class MusicScrapingService:
    """Servicio de scraping profesional para música con múltiples fuentes"""
    
    def __init__(self):
        self.storage_path = "storage/musica"
        self.cache_duration = 86400  # 24 horas
        
        # Crear directorios
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(f"{self.storage_path}/cache", exist_ok=True)
        
        # Fuentes de scraping disponibles
        self.sources = {
            'youtube_music': {
                'name': 'Scraping YouTube Music',
                'active': True,
                'priority': 1,
                'methods': ['search_songs', 'search_albums', 'get_charts', 'download']
            },
            'soundcloud': {
                'name': 'Scraping SoundCloud',
                'active': True,
                'priority': 2,
                'methods': ['search_songs', 'search_albums', 'download']
            },
            'jamendo': {
                'name': 'Scraping Jamendo',
                'active': True,
                'priority': 3,
                'methods': ['search_songs', 'search_albums', 'download']
            },
            'audiomack': {
                'name': 'Scraping Audiomack',
                'active': True,
                'priority': 4,
                'methods': ['search_songs', 'search_albums']
            },
            'musixmatch': {
                'name': 'Scraping Musixmatch',
                'active': True,
                'priority': 5,
                'methods': ['get_lyrics']
            },
            'vagalume': {
                'name': 'Scraping Vagalume',
                'active': True,
                'priority': 6,
                'methods': ['get_lyrics']
            },
            'bandcamp': {
                'name': 'Scraping Bandcamp',
                'active': True,
                'priority': 7,
                'methods': ['search_songs', 'search_albums', 'download']
            }
        }
        
        # Headers para evitar detección
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def search_songs(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Buscar canciones usando scraping de múltiples fuentes"""
        try:
            results = []
            sources_used = []
            
            # Obtener fuentes activas ordenadas por prioridad
            active_sources = sorted(
                [(k, v) for k, v in self.sources.items() if v['active'] and 'search_songs' in v['methods']],
                key=lambda x: x[1]['priority']
            )
            
            for source_key, source_info in active_sources:
                try:
                    self.logger.info(f"Buscando en {source_info['name']}: {query}")
                    
                    if source_key == 'youtube_music':
                        source_results = self._scrape_youtube_music_songs(query, limit)
                    elif source_key == 'soundcloud':
                        source_results = self._scrape_soundcloud_songs(query, limit)
                    elif source_key == 'jamendo':
                        source_results = self._scrape_jamendo_songs(query, limit)
                    elif source_key == 'audiomack':
                        source_results = self._scrape_audiomack_songs(query, limit)
                    elif source_key == 'bandcamp':
                        source_results = self._scrape_bandcamp_songs(query, limit)
                    else:
                        continue
                    
                    if source_results:
                        results.extend(source_results)
                        sources_used.append(source_info['name'])
                        
                        # Si ya tenemos suficientes resultados, parar
                        if len(results) >= limit:
                            results = results[:limit]
                            break
                            
                except Exception as e:
                    self.logger.error(f"Error en fuente {source_key}: {e}")
                    continue
            
            if not results:
                return {
                    'success': False,
                    'error': 'No se encontraron resultados en ninguna fuente'
                }
            
            # Enriquecer resultados
            enriched_results = []
            for song in results:
                enriched_song = self._enrich_song_data(song)
                enriched_results.append(enriched_song)
            
            return {
                'success': True,
                'data': enriched_results,
                'total_results': len(enriched_results),
                'query': query,
                'sources_used': sources_used,
                'scraping_method': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda de canciones: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
    def search_albums(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Buscar álbumes usando scraping"""
        try:
            results = []
            sources_used = []
            
            active_sources = sorted(
                [(k, v) for k, v in self.sources.items() if v['active'] and 'search_albums' in v['methods']],
                key=lambda x: x[1]['priority']
            )
            
            for source_key, source_info in active_sources:
                try:
                    self.logger.info(f"Buscando álbumes en {source_info['name']}: {query}")
                    
                    if source_key == 'youtube_music':
                        source_results = self._scrape_youtube_music_albums(query, limit)
                    elif source_key == 'soundcloud':
                        source_results = self._scrape_soundcloud_albums(query, limit)
                    elif source_key == 'jamendo':
                        source_results = self._scrape_jamendo_albums(query, limit)
                    elif source_key == 'bandcamp':
                        source_results = self._scrape_bandcamp_albums(query, limit)
                    else:
                        continue
                    
                    if source_results:
                        results.extend(source_results)
                        sources_used.append(source_info['name'])
                        
                        if len(results) >= limit:
                            results = results[:limit]
                            break
                            
                except Exception as e:
                    self.logger.error(f"Error en fuente {source_key}: {e}")
                    continue
            
            # Enriquecer álbumes con lista de canciones
            enriched_results = []
            for album in results:
                enriched_album = self._enrich_album_data(album)
                enriched_results.append(enriched_album)
            
            return {
                'success': True,
                'data': enriched_results,
                'total_results': len(enriched_results),
                'query': query,
                'sources_used': sources_used,
                'scraping_method': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error buscando álbumes: {str(e)}'
            }
    
    def get_top_charts(self, country: str = 'global', limit: int = 50) -> Dict[str, Any]:
        """Obtener top charts por scraping"""
        try:
            results = []
            sources_used = []
            
            # Priorizar fuentes que tienen charts
            sources_with_charts = ['youtube_music', 'soundcloud', 'jamendo']
            
            for source_key in sources_with_charts:
                if not self.sources[source_key]['active']:
                    continue
                    
                try:
                    self.logger.info(f"Obteniendo charts de {self.sources[source_key]['name']}")
                    
                    if source_key == 'youtube_music':
                        source_results = self._scrape_youtube_charts(country, limit)
                    elif source_key == 'soundcloud':
                        source_results = self._scrape_soundcloud_charts(country, limit)
                    elif source_key == 'jamendo':
                        source_results = self._scrape_jamendo_charts(country, limit)
                    else:
                        continue
                    
                    if source_results:
                        results.extend(source_results)
                        sources_used.append(self.sources[source_key]['name'])
                        break  # Usar solo la primera fuente exitosa para charts
                        
                except Exception as e:
                    self.logger.error(f"Error obteniendo charts de {source_key}: {e}")
                    continue
            
            return {
                'success': True,
                'data': results[:limit],
                'country': country,
                'sources_used': sources_used,
                'scraping_method': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo charts: {str(e)}'
            }
    
    def get_song_lyrics(self, song_title: str, artist_name: str) -> Dict[str, Any]:
        """Obtener letras por scraping"""
        try:
            lyrics = None
            source = None
            
            # Fuentes de letras ordenadas por prioridad
            lyrics_sources = ['musixmatch', 'vagalume']
            
            for source_key in lyrics_sources:
                if not self.sources[source_key]['active']:
                    continue
                    
                try:
                    self.logger.info(f"Buscando letras en {self.sources[source_key]['name']}")
                    
                    if source_key == 'musixmatch':
                        lyrics = self._scrape_musixmatch_lyrics(song_title, artist_name)
                        source = 'Musixmatch (Scraping)'
                    elif source_key == 'vagalume':
                        lyrics = self._scrape_vagalume_lyrics(song_title, artist_name)
                        source = 'Vagalume (Scraping)'
                    
                    if lyrics:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error obteniendo letras de {source_key}: {e}")
                    continue
            
            if not lyrics:
                return {
                    'success': False,
                    'error': 'Letras no encontradas en ninguna fuente'
                }
            
            return {
                'success': True,
                'data': {
                    'song_title': song_title,
                    'artist_name': artist_name,
                    'lyrics': lyrics,
                    'source': source,
                    'scraping_method': True
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo letras: {str(e)}'
            }
    
    def download_song(self, song_data: Dict[str, Any], quality: str = 'best') -> Dict[str, Any]:
        """Descargar canción usando la mejor fuente disponible"""
        try:
            artist = self._sanitize_filename(song_data.get('artist', 'Unknown'))
            title = self._sanitize_filename(song_data.get('title', 'Unknown'))
            
            # Crear directorio para el artista
            artist_dir = os.path.join(self.storage_path, artist)
            os.makedirs(artist_dir, exist_ok=True)
            
            # Verificar caché
            wav_path = os.path.join(artist_dir, f"{title}.wav")
            mp3_path = os.path.join(artist_dir, f"{title}.mp3")
            
            if os.path.exists(wav_path) and os.path.exists(mp3_path):
                return {
                    'success': True,
                    'message': 'Canción ya existe en caché',
                    'wav_path': wav_path,
                    'mp3_path': mp3_path,
                    'from_cache': True
                }
            
            # Obtener URL de descarga de la mejor fuente
            download_url = self._get_download_url(song_data)
            
            if not download_url:
                return {
                    'success': False,
                    'error': 'No se encontró URL de descarga'
                }
            
            # Descargar usando yt-dlp o requests según la fuente
            success = self._download_from_url(download_url, wav_path, mp3_path, song_data)
            
            if success:
                return {
                    'success': True,
                    'message': 'Canción descargada exitosamente',
                    'wav_path': wav_path,
                    'mp3_path': mp3_path,
                    'file_size_wav': os.path.getsize(wav_path) if os.path.exists(wav_path) else 0,
                    'file_size_mp3': os.path.getsize(mp3_path) if os.path.exists(mp3_path) else 0,
                    'from_cache': False,
                    'scraping_method': True
                }
            else:
                return {
                    'success': False,
                    'error': 'Error en la descarga'
                }
                
        except Exception as e:
            self.logger.error(f"Error descargando canción: {e}")
            return {
                'success': False,
                'error': f'Error en descarga: {str(e)}'
            }
    
    # Métodos de scraping específicos para cada fuente
    
    def _scrape_youtube_music_songs(self, query: str, limit: int) -> List[Dict]:
        """Scraping de YouTube Music"""
        try:
            # Usar yt-dlp para búsqueda
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'default_search': 'ytsearch'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
                
                songs = []
                if search_results and 'entries' in search_results:
                    for entry in search_results['entries']:
                        song_data = {
                            'id': entry.get('id'),
                            'title': entry.get('title', ''),
                            'artist': entry.get('uploader', ''),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'thumbnail': entry.get('thumbnail'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'source': 'YouTube Music (Scraping)',
                            'download_url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                        }
                        songs.append(song_data)
                
                return songs
                
        except Exception as e:
            self.logger.error(f"Error scraping YouTube Music: {e}")
            return []
    
    def _scrape_soundcloud_songs(self, query: str, limit: int) -> List[Dict]:
        """Scraping de SoundCloud"""
        try:
            # SoundCloud tiene una API no oficial accesible
            search_url = "https://soundcloud.com/search/sounds"
            params = {'q': query}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Buscar datos JSON embebidos en la página
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all('script')
            
            songs = []
            for script in scripts:
                if script.string and 'window.__sc_hydration' in script.string:
                    # Extraer datos de la hidratación de SoundCloud
                    try:
                        # Parsear JSON embebido
                        json_match = re.search(r'window\.__sc_hydration\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(1))
                            
                            for item in data:
                                if isinstance(item, dict) and 'hydratable' in item:
                                    hydratable = item['hydratable']
                                    if hydratable == 'sound' and 'data' in item:
                                        track = item['data']
                                        
                                        song_data = {
                                            'id': track.get('id'),
                                            'title': track.get('title', ''),
                                            'artist': track.get('user', {}).get('username', ''),
                                            'duration': track.get('duration', 0) // 1000,  # Convertir a segundos
                                            'play_count': track.get('playback_count', 0),
                                            'favorite_count': track.get('favoritings_count', 0),
                                            'thumbnail': track.get('artwork_url'),
                                            'url': track.get('permalink_url'),
                                            'source': 'SoundCloud (Scraping)',
                                            'stream_url': track.get('stream_url')
                                        }
                                        songs.append(song_data)
                                        
                                        if len(songs) >= limit:
                                            break
                    except json.JSONDecodeError:
                        continue
                
                if len(songs) >= limit:
                    break
            
            return songs[:limit]
            
        except Exception as e:
            self.logger.error(f"Error scraping SoundCloud: {e}")
            return []
    
    def _scrape_jamendo_songs(self, query: str, limit: int) -> List[Dict]:
        """Scraping de Jamendo (música libre)"""
        try:
            # Jamendo tiene API pública gratuita
            api_url = "https://api.jamendo.com/v3.0/tracks/"
            params = {
                'client_id': 'e8b1da57',  # Client ID público de Jamendo
                'format': 'json',
                'search': query,
                'limit': limit,
                'include': 'musicinfo+licenses+stats'
            }
            
            response = requests.get(api_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            songs = []
            for track in data.get('results', []):
                song_data = {
                    'id': track.get('id'),
                    'title': track.get('name', ''),
                    'artist': track.get('artist_name', ''),
                    'album': track.get('album_name', ''),
                    'duration': track.get('duration', 0),
                    'releasedate': track.get('releasedate'),
                    'thumbnail': track.get('album_image'),
                    'url': track.get('shareurl'),
                    'source': 'Jamendo (Scraping)',
                    'download_url': track.get('audio'),
                    'license': track.get('license_ccurl'),
                    'genre': ', '.join([tag['name'] for tag in track.get('musicinfo', {}).get('tags', {}).get('genres', [])])
                }
                songs.append(song_data)
            
            return songs
            
        except Exception as e:
            self.logger.error(f"Error scraping Jamendo: {e}")
            return []
    
    def _scrape_audiomack_songs(self, query: str, limit: int) -> List[Dict]:
        """Scraping de Audiomack"""
        try:
            search_url = "https://www.audiomack.com/search"
            params = {'q': query}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            songs = []
            # Buscar elementos de canciones en la página
            song_elements = soup.find_all('article', class_='item-container')
            
            for element in song_elements[:limit]:
                try:
                    title_elem = element.find('h2', class_='title')
                    artist_elem = element.find('h3', class_='subtitle')
                    image_elem = element.find('img', class_='image')
                    link_elem = element.find('a', href=True)
                    
                    if title_elem and artist_elem:
                        song_data = {
                            'id': f"audiomack_{hash(title_elem.get_text() + artist_elem.get_text())}",
                            'title': title_elem.get_text().strip(),
                            'artist': artist_elem.get_text().strip(),
                            'thumbnail': image_elem.get('src') if image_elem else None,
                            'url': f"https://www.audiomack.com{link_elem.get('href')}" if link_elem else None,
                            'source': 'Audiomack (Scraping)'
                        }
                        songs.append(song_data)
                        
                except Exception as e:
                    self.logger.warning(f"Error procesando elemento Audiomack: {e}")
                    continue
            
            return songs
            
        except Exception as e:
            self.logger.error(f"Error scraping Audiomack: {e}")
            return []
    
    def _scrape_bandcamp_songs(self, query: str, limit: int) -> List[Dict]:
        """Scraping de Bandcamp"""
        try:
            search_url = "https://bandcamp.com/search"
            params = {'q': query, 'item_type': 't'}  # 't' para tracks
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            songs = []
            # Buscar elementos de resultados
            result_items = soup.find_all('li', class_='searchresult')
            
            for item in result_items[:limit]:
                try:
                    title_elem = item.find('div', class_='heading').find('a')
                    artist_elem = item.find('div', class_='subhead')
                    img_elem = item.find('div', class_='art').find('img')
                    
                    if title_elem and artist_elem:
                        song_data = {
                            'id': f"bandcamp_{hash(title_elem.get_text() + artist_elem.get_text())}",
                            'title': title_elem.get_text().strip(),
                            'artist': artist_elem.get_text().replace('by ', '').strip(),
                            'thumbnail': img_elem.get('src') if img_elem else None,
                            'url': title_elem.get('href'),
                            'source': 'Bandcamp (Scraping)'
                        }
                        songs.append(song_data)
                        
                except Exception as e:
                    self.logger.warning(f"Error procesando elemento Bandcamp: {e}")
                    continue
            
            return songs
            
        except Exception as e:
            self.logger.error(f"Error scraping Bandcamp: {e}")
            return []