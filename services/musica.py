"""
Servicio profesional de música para Panel L3HO - Solo datos reales
Sistema completo con múltiples fuentes y descargas automáticas
"""

import requests
import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import hashlib
import base64
from urllib.parse import urlencode
import yt_dlp
from pydub import AudioSegment
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    spotipy = None

try:
    import lyricsgenius
except ImportError:
    lyricsgenius = None

class MusicService:
    """Servicio profesional de música con múltiples fuentes y descargas automáticas"""
    
    def __init__(self):
        self.storage_path = "storage/musica"
        self.cache_duration = 86400  # 24 horas
        
        # Asegurar que existe el directorio de almacenamiento
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(f"{self.storage_path}/cache", exist_ok=True)
        
        # APIs configuradas
        self.apis = {
            'youtube': None,
            'spotify': None,
            'lastfm': None,
            'genius': None,
            'deezer': None,
            'soundcloud': None,
            'audiomack': None,
            'jamendo': None,
            'discogs': None,
            'musixmatch': None
        }
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def configure_apis(self, api_keys: Dict[str, str]):
        """Configura todas las APIs con las claves proporcionadas"""
        try:
            # YouTube Data API
            if 'youtube' in api_keys:
                self.apis['youtube'] = api_keys['youtube']
            
            # Spotify API
            if spotipy and 'spotify_client_id' in api_keys and 'spotify_client_secret' in api_keys:
                try:
                    client_credentials_manager = SpotifyClientCredentials(
                        client_id=api_keys['spotify_client_id'],
                        client_secret=api_keys['spotify_client_secret']
                    )
                    self.apis['spotify'] = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                except Exception as e:
                    self.logger.error(f"Error configurando Spotify: {e}")
                    self.apis['spotify'] = None
            
            # Last.fm API
            if 'lastfm' in api_keys:
                self.apis['lastfm'] = api_keys['lastfm']
            
            # Genius API
            if lyricsgenius and 'genius' in api_keys:
                try:
                    self.apis['genius'] = lyricsgenius.Genius(api_keys['genius'])
                except Exception as e:
                    self.logger.error(f"Error configurando Genius: {e}")
                    self.apis['genius'] = None
            
            # Deezer API (no requiere clave)
            self.apis['deezer'] = "https://api.deezer.com"
            
            # SoundCloud API
            if 'soundcloud' in api_keys:
                self.apis['soundcloud'] = api_keys['soundcloud']
            
            # Otras APIs
            for api_name in ['audiomack', 'jamendo', 'discogs', 'musixmatch']:
                if api_name in api_keys:
                    self.apis[api_name] = api_keys[api_name]
            
            self.logger.info(f"APIs configuradas: {list(self.apis.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error configurando APIs: {e}")
    
    def search_songs(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Buscar canciones por nombre o artista"""
        try:
            results = []
            
            # Intentar con cada fuente hasta obtener resultados
            sources = ['spotify', 'youtube', 'deezer', 'lastfm', 'soundcloud']
            
            for source in sources:
                try:
                    if source == 'spotify' and self.apis['spotify']:
                        spotify_results = self._search_spotify_tracks(query, limit)
                        if spotify_results:
                            results.extend(spotify_results)
                            break
                    
                    elif source == 'youtube' and self.apis['youtube']:
                        youtube_results = self._search_youtube_music(query, limit)
                        if youtube_results:
                            results.extend(youtube_results)
                            break
                    
                    elif source == 'deezer':
                        deezer_results = self._search_deezer_tracks(query, limit)
                        if deezer_results:
                            results.extend(deezer_results)
                            break
                    
                    elif source == 'lastfm' and self.apis['lastfm']:
                        lastfm_results = self._search_lastfm_tracks(query, limit)
                        if lastfm_results:
                            results.extend(lastfm_results)
                            break
                    
                except Exception as e:
                    self.logger.warning(f"Error en fuente {source}: {e}")
                    continue
            
            if not results:
                return {
                    'success': False,
                    'error': 'No se encontraron resultados en ninguna fuente'
                }
            
            # Enriquecer resultados con información adicional
            enriched_results = []
            for song in results[:limit]:
                enriched_song = self._enrich_song_data(song)
                enriched_results.append(enriched_song)
            
            return {
                'success': True,
                'data': enriched_results,
                'total_results': len(enriched_results),
                'query': query,
                'sources_used': [s for s in sources if self.apis.get(s)],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error buscando canciones: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
    def search_albums(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Buscar álbumes por título o artista"""
        try:
            results = []
            sources = ['spotify', 'deezer', 'discogs', 'lastfm']
            
            for source in sources:
                try:
                    if source == 'spotify' and self.apis['spotify']:
                        spotify_results = self._search_spotify_albums(query, limit)
                        if spotify_results:
                            results.extend(spotify_results)
                            break
                    
                    elif source == 'deezer':
                        deezer_results = self._search_deezer_albums(query, limit)
                        if deezer_results:
                            results.extend(deezer_results)
                            break
                    
                    elif source == 'lastfm' and self.apis['lastfm']:
                        lastfm_results = self._search_lastfm_albums(query, limit)
                        if lastfm_results:
                            results.extend(lastfm_results)
                            break
                    
                except Exception as e:
                    self.logger.warning(f"Error en fuente {source} para álbumes: {e}")
                    continue
            
            # Enriquecer con información de canciones
            enriched_results = []
            for album in results[:limit]:
                enriched_album = self._enrich_album_data(album)
                enriched_results.append(enriched_album)
            
            return {
                'success': True,
                'data': enriched_results,
                'total_results': len(enriched_results),
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error buscando álbumes: {str(e)}'
            }
    
    def get_top_charts(self, country: str = 'global', chart_type: str = 'tracks', limit: int = 50) -> Dict[str, Any]:
        """Obtener top charts globales o por país"""
        try:
            results = []
            
            # Intentar con diferentes fuentes
            if self.apis['spotify']:
                results = self._get_spotify_top_charts(country, chart_type, limit)
            elif self.apis['lastfm']:
                results = self._get_lastfm_top_charts(country, chart_type, limit)
            else:
                results = self._get_deezer_top_charts(country, chart_type, limit)
            
            return {
                'success': True,
                'data': results,
                'chart_type': chart_type,
                'country': country,
                'total_results': len(results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo charts: {str(e)}'
            }
    
    def get_artist_details(self, artist_name: str) -> Dict[str, Any]:
        """Obtener detalles completos de un artista"""
        try:
            artist_data = {}
            
            # Buscar en Spotify primero
            if self.apis['spotify']:
                artist_data = self._get_spotify_artist_details(artist_name)
            
            # Enriquecer con Last.fm
            if self.apis['lastfm']:
                lastfm_data = self._get_lastfm_artist_details(artist_name)
                artist_data.update(lastfm_data)
            
            # Agregar biografía de Genius si está disponible
            if self.apis['genius']:
                genius_data = self._get_genius_artist_details(artist_name)
                artist_data.update(genius_data)
            
            if not artist_data:
                return {
                    'success': False,
                    'error': 'Artista no encontrado'
                }
            
            return {
                'success': True,
                'data': artist_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo datos del artista: {str(e)}'
            }
    
    def get_song_lyrics(self, song_title: str, artist_name: str) -> Dict[str, Any]:
        """Obtener letras de una canción"""
        try:
            lyrics = None
            source = None
            
            # Intentar con Genius primero
            if self.apis['genius']:
                try:
                    song = self.apis['genius'].search_song(song_title, artist_name)
                    if song:
                        lyrics = song.lyrics
                        source = 'Genius'
                except Exception as e:
                    self.logger.warning(f"Error con Genius: {e}")
            
            # Fallback a Musixmatch
            if not lyrics and self.apis['musixmatch']:
                lyrics = self._get_musixmatch_lyrics(song_title, artist_name)
                if lyrics:
                    source = 'Musixmatch'
            
            # Fallback a Vagalume (API gratuita brasileña)
            if not lyrics:
                lyrics = self._get_vagalume_lyrics(song_title, artist_name)
                if lyrics:
                    source = 'Vagalume'
            
            if not lyrics:
                return {
                    'success': False,
                    'error': 'Letras no encontradas'
                }
            
            return {
                'success': True,
                'data': {
                    'song_title': song_title,
                    'artist_name': artist_name,
                    'lyrics': lyrics,
                    'source': source
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo letras: {str(e)}'
            }
    
    def download_song(self, song_data: Dict[str, Any], quality: str = 'best') -> Dict[str, Any]:
        """Descargar canción en formato WAV de alta calidad"""
        try:
            # Generar nombre de archivo
            artist = self._sanitize_filename(song_data.get('artist', 'Unknown'))
            title = self._sanitize_filename(song_data.get('title', 'Unknown'))
            
            # Crear directorio para el artista
            artist_dir = os.path.join(self.storage_path, artist)
            os.makedirs(artist_dir, exist_ok=True)
            
            # Verificar si ya existe en caché
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
            
            # Descargar usando yt-dlp (mejor opción para calidad)
            download_url = song_data.get('stream_url') or song_data.get('youtube_url')
            
            if not download_url:
                # Buscar en YouTube si no hay URL directa
                search_query = f"{artist} {title}"
                download_url = self._find_youtube_url(search_query)
            
            if not download_url:
                return {
                    'success': False,
                    'error': 'No se encontró URL de descarga'
                }
            
            # Configurar yt-dlp para mejor calidad
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(artist_dir, f"{title}.%(ext)s"),
                'extractaudio': True,
                'audioformat': 'wav',
                'audioquality': 0,  # Mejor calidad
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '320',
                }]
            }
            
            # Descargar
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([download_url])
            
            # Verificar que se descargó
            if not os.path.exists(wav_path):
                # Buscar archivo descargado (puede tener extensión diferente)
                for file in os.listdir(artist_dir):
                    if title in file and file.endswith(('.wav', '.m4a', '.mp3', '.webm')):
                        downloaded_file = os.path.join(artist_dir, file)
                        
                        # Convertir a WAV si no es WAV
                        if not file.endswith('.wav'):
                            audio = AudioSegment.from_file(downloaded_file)
                            audio.export(wav_path, format="wav")
                            os.remove(downloaded_file)  # Eliminar archivo original
                        else:
                            os.rename(downloaded_file, wav_path)
                        break
            
            # Generar versión MP3 optimizada
            if os.path.exists(wav_path):
                audio = AudioSegment.from_wav(wav_path)
                audio.export(mp3_path, format="mp3", bitrate="320k")
            
            # Actualizar metadatos
            self._add_metadata(wav_path, song_data)
            self._add_metadata(mp3_path, song_data)
            
            return {
                'success': True,
                'message': 'Canción descargada exitosamente',
                'wav_path': wav_path,
                'mp3_path': mp3_path,
                'file_size_wav': os.path.getsize(wav_path),
                'file_size_mp3': os.path.getsize(mp3_path),
                'from_cache': False
            }
            
        except Exception as e:
            self.logger.error(f"Error descargando canción: {e}")
            return {
                'success': False,
                'error': f'Error en descarga: {str(e)}'
            }
    
    # Métodos privados para cada fuente de datos
    
    def _search_spotify_tracks(self, query: str, limit: int) -> List[Dict]:
        """Buscar canciones en Spotify"""
        try:
            results = self.apis['spotify'].search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_data = {
                    'id': track['id'],
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'explicit': track['explicit'],
                    'preview_url': track['preview_url'],
                    'release_date': track['album']['release_date'],
                    'cover_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'external_urls': track['external_urls'],
                    'source': 'Spotify'
                }
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            self.logger.error(f"Error buscando en Spotify: {e}")
            return []
    
    def _search_youtube_music(self, query: str, limit: int) -> List[Dict]:
        """Buscar canciones en YouTube"""
        try:
            # Usar YouTube Data API
            if not self.apis['youtube']:
                return []
            
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query + ' audio',
                'type': 'video',
                'videoCategoryId': '10',  # Música
                'maxResults': limit,
                'key': self.apis['youtube']
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            tracks = []
            for item in data.get('items', []):
                track_data = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'artist': item['snippet']['channelTitle'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'cover_art': item['snippet']['thumbnails']['high']['url'],
                    'youtube_url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    'source': 'YouTube'
                }
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            self.logger.error(f"Error buscando en YouTube: {e}")
            return []
    
    def _search_deezer_tracks(self, query: str, limit: int) -> List[Dict]:
        """Buscar canciones en Deezer"""
        try:
            url = f"{self.apis['deezer']}/search"
            params = {'q': query, 'limit': limit}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            tracks = []
            for track in data.get('data', []):
                track_data = {
                    'id': track['id'],
                    'title': track['title'],
                    'artist': track['artist']['name'],
                    'album': track['album']['title'],
                    'duration': track['duration'],
                    'preview_url': track['preview'],
                    'cover_art': track['album']['cover_medium'],
                    'release_date': track.get('release_date'),
                    'external_urls': {'deezer': track['link']},
                    'source': 'Deezer'
                }
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            self.logger.error(f"Error buscando en Deezer: {e}")
            return []
    
    def _enrich_song_data(self, song: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquecer datos de canción con información adicional"""
        # Agregar enlaces de descarga
        song['download_links'] = {
            'wav': f"/api/music/download/{song['id']}/wav",
            'mp3': f"/api/music/download/{song['id']}/mp3"
        }
        
        # Agregar género si no existe
        if 'genre' not in song and self.apis['lastfm']:
            song['genre'] = self._get_track_genre(song.get('title', ''), song.get('artist', ''))
        
        return song
    
    def _sanitize_filename(self, filename: str) -> str:
        """Limpiar nombre de archivo para el sistema de archivos"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()[:200]  # Limitar longitud
    
    def _find_youtube_url(self, search_query: str) -> Optional[str]:
        """Buscar URL de YouTube para una canción"""
        try:
            if not self.apis['youtube']:
                return None
            
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query + ' audio',
                'type': 'video',
                'videoCategoryId': '10',
                'maxResults': 1,
                'key': self.apis['youtube']
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                video_id = data['items'][0]['id']['videoId']
                return f"https://www.youtube.com/watch?v={video_id}"
            
            return None
        except Exception as e:
            self.logger.error(f"Error buscando YouTube URL: {e}")
            return None
    
    def _add_metadata(self, file_path: str, song_data: Dict[str, Any]):
        """Agregar metadatos a archivo de audio"""
        try:
            # Implementar con mutagen o similar para agregar metadatos ID3
            pass
        except Exception as e:
            self.logger.warning(f"Error agregando metadatos: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del caché"""
        try:
            total_files = 0
            total_size = 0
            artists = []
            
            for artist_dir in os.listdir(self.storage_path):
                artist_path = os.path.join(self.storage_path, artist_dir)
                if os.path.isdir(artist_path) and artist_dir != 'cache':
                    artists.append(artist_dir)
                    
                    for file in os.listdir(artist_path):
                        file_path = os.path.join(artist_path, file)
                        if os.path.isfile(file_path):
                            total_files += 1
                            total_size += os.path.getsize(file_path)
            
            return {
                'success': True,
                'data': {
                    'total_files': total_files,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'total_artists': len(artists),
                    'storage_path': self.storage_path,
                    'artists': sorted(artists)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo estadísticas: {str(e)}'
            }
    
    # Implementaciones faltantes para completar el servicio
    
    def _search_lastfm_tracks(self, query: str, limit: int) -> List[Dict]:
        """Buscar canciones en Last.fm"""
        try:
            if not self.apis['lastfm']:
                return []
            
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'track.search',
                'track': query,
                'api_key': self.apis['lastfm'],
                'format': 'json',
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            tracks = []
            if 'results' in data and 'trackmatches' in data['results']:
                for track in data['results']['trackmatches']['track']:
                    track_data = {
                        'id': f"lastfm_{track['name']}_{track['artist']}",
                        'title': track['name'],
                        'artist': track['artist'],
                        'listeners': track.get('listeners', 0),
                        'url': track.get('url', ''),
                        'source': 'Last.fm'
                    }
                    tracks.append(track_data)
            
            return tracks
        except Exception as e:
            self.logger.error(f"Error buscando en Last.fm: {e}")
            return []
    
    def _search_deezer_albums(self, query: str, limit: int) -> List[Dict]:
        """Buscar álbumes en Deezer"""
        try:
            url = f"{self.apis['deezer']}/search/album"
            params = {'q': query, 'limit': limit}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            albums = []
            for album in data.get('data', []):
                album_data = {
                    'id': album['id'],
                    'name': album['title'],
                    'artist': album['artist']['name'],
                    'release_date': album.get('release_date', ''),
                    'total_tracks': album.get('nb_tracks', 0),
                    'cover_art': album.get('cover_medium', ''),
                    'external_urls': {'deezer': album.get('link', '')},
                    'source': 'Deezer'
                }
                albums.append(album_data)
            
            return albums
        except Exception as e:
            self.logger.error(f"Error buscando álbumes en Deezer: {e}")
            return []
    
    def _search_lastfm_albums(self, query: str, limit: int) -> List[Dict]:
        """Buscar álbumes en Last.fm"""
        try:
            if not self.apis['lastfm']:
                return []
            
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'album.search',
                'album': query,
                'api_key': self.apis['lastfm'],
                'format': 'json',
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            albums = []
            if 'results' in data and 'albummatches' in data['results']:
                for album in data['results']['albummatches']['album']:
                    album_data = {
                        'id': f"lastfm_{album['name']}_{album['artist']}",
                        'name': album['name'],
                        'artist': album['artist'],
                        'url': album.get('url', ''),
                        'source': 'Last.fm'
                    }
                    albums.append(album_data)
            
            return albums
        except Exception as e:
            self.logger.error(f"Error buscando álbumes en Last.fm: {e}")
            return []
    
    def _get_spotify_top_charts(self, country: str, chart_type: str, limit: int) -> List[Dict]:
        """Obtener top charts de Spotify"""
        try:
            if not self.apis['spotify']:
                return []
            
            # Spotify no tiene charts públicos, usar playlists populares
            if chart_type == 'tracks':
                results = self.apis['spotify'].search(q='year:2024', type='playlist', limit=1)
                if results['playlists']['items']:
                    playlist_id = results['playlists']['items'][0]['id']
                    tracks = self.apis['spotify'].playlist_tracks(playlist_id, limit=limit)
                    
                    chart_data = []
                    for i, item in enumerate(tracks['items']):
                        track = item['track']
                        chart_data.append({
                            'position': i + 1,
                            'title': track['name'],
                            'artist': ', '.join([artist['name'] for artist in track['artists']]),
                            'album': track['album']['name'],
                            'popularity': track['popularity'],
                            'preview_url': track['preview_url'],
                            'cover_art': track['album']['images'][0]['url'] if track['album']['images'] else None
                        })
                    
                    return chart_data
            
            return []
        except Exception as e:
            self.logger.error(f"Error obteniendo charts de Spotify: {e}")
            return []
    
    def _get_lastfm_top_charts(self, country: str, chart_type: str, limit: int) -> List[Dict]:
        """Obtener top charts de Last.fm"""
        try:
            if not self.apis['lastfm']:
                return []
            
            url = "http://ws.audioscrobbler.com/2.0/"
            
            if chart_type == 'tracks':
                method = 'chart.getTopTracks'
            elif chart_type == 'artists':
                method = 'chart.getTopArtists'
            else:
                method = 'chart.getTopTracks'
            
            params = {
                'method': method,
                'api_key': self.apis['lastfm'],
                'format': 'json',
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            chart_data = []
            if chart_type == 'tracks' and 'tracks' in data:
                for i, track in enumerate(data['tracks']['track']):
                    chart_data.append({
                        'position': i + 1,
                        'title': track['name'],
                        'artist': track['artist']['name'],
                        'playcount': track.get('playcount', 0),
                        'listeners': track.get('listeners', 0),
                        'url': track.get('url', '')
                    })
            elif chart_type == 'artists' and 'artists' in data:
                for i, artist in enumerate(data['artists']['artist']):
                    chart_data.append({
                        'position': i + 1,
                        'name': artist['name'],
                        'playcount': artist.get('playcount', 0),
                        'listeners': artist.get('listeners', 0),
                        'url': artist.get('url', '')
                    })
            
            return chart_data
        except Exception as e:
            self.logger.error(f"Error obteniendo charts de Last.fm: {e}")
            return []
    
    def _get_deezer_top_charts(self, country: str, chart_type: str, limit: int) -> List[Dict]:
        """Obtener top charts de Deezer"""
        try:
            if chart_type == 'tracks':
                url = f"{self.apis['deezer']}/chart/0/tracks"
            elif chart_type == 'albums':
                url = f"{self.apis['deezer']}/chart/0/albums"
            else:
                url = f"{self.apis['deezer']}/chart/0/tracks"
            
            params = {'limit': limit}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            chart_data = []
            for i, item in enumerate(data.get('data', [])):
                if chart_type == 'tracks':
                    chart_data.append({
                        'position': i + 1,
                        'title': item['title'],
                        'artist': item['artist']['name'],
                        'album': item['album']['title'],
                        'duration': item['duration'],
                        'preview_url': item['preview'],
                        'cover_art': item['album']['cover_medium']
                    })
                elif chart_type == 'albums':
                    chart_data.append({
                        'position': i + 1,
                        'title': item['title'],
                        'artist': item['artist']['name'],
                        'total_tracks': item.get('nb_tracks', 0),
                        'cover_art': item.get('cover_medium', '')
                    })
            
            return chart_data
        except Exception as e:
            self.logger.error(f"Error obteniendo charts de Deezer: {e}")
            return []
    
    def _get_spotify_artist_details(self, artist_name: str) -> Dict[str, Any]:
        """Obtener detalles de artista en Spotify"""
        try:
            if not self.apis['spotify']:
                return {}
            
            results = self.apis['spotify'].search(q=f'artist:{artist_name}', type='artist', limit=1)
            if not results['artists']['items']:
                return {}
            
            artist = results['artists']['items'][0]
            
            # Obtener álbumes del artista
            albums = self.apis['spotify'].artist_albums(artist['id'], limit=20)
            
            return {
                'name': artist['name'],
                'id': artist['id'],
                'genres': artist['genres'],
                'popularity': artist['popularity'],
                'followers': artist['followers']['total'],
                'images': artist['images'],
                'external_urls': artist['external_urls'],
                'albums_total': albums['total'],
                'top_albums': [album['name'] for album in albums['items'][:5]]
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo artista en Spotify: {e}")
            return {}
    
    def _get_lastfm_artist_details(self, artist_name: str) -> Dict[str, Any]:
        """Obtener detalles de artista en Last.fm"""
        try:
            if not self.apis['lastfm']:
                return {}
            
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'artist.getInfo',
                'artist': artist_name,
                'api_key': self.apis['lastfm'],
                'format': 'json'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'artist' not in data:
                return {}
            
            artist = data['artist']
            return {
                'biography': artist.get('bio', {}).get('summary', ''),
                'playcount': artist.get('stats', {}).get('playcount', 0),
                'listeners': artist.get('stats', {}).get('listeners', 0),
                'url': artist.get('url', ''),
                'tags': [tag['name'] for tag in artist.get('tags', {}).get('tag', [])]
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo artista en Last.fm: {e}")
            return {}
    
    def _get_genius_artist_details(self, artist_name: str) -> Dict[str, Any]:
        """Obtener detalles de artista en Genius"""
        try:
            if not self.apis['genius']:
                return {}
            
            artist = self.apis['genius'].search_artist(artist_name)
            if artist:
                return {
                    'genius_id': artist.id,
                    'description': getattr(artist, 'description', ''),
                    'song_count': getattr(artist, 'song_count', 0)
                }
            
            return {}
        except Exception as e:
            self.logger.error(f"Error obteniendo artista en Genius: {e}")
            return {}
    
    def _get_musixmatch_lyrics(self, song_title: str, artist_name: str) -> Optional[str]:
        """Obtener letras de Musixmatch"""
        try:
            # Implementación básica - requiere API key de Musixmatch
            if not self.apis['musixmatch']:
                return None
            
            # Aquí iría la implementación real con Musixmatch API
            # Por ahora retorna None para fallback a otras fuentes
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo letras de Musixmatch: {e}")
            return None
    
    def _get_vagalume_lyrics(self, song_title: str, artist_name: str) -> Optional[str]:
        """Obtener letras de Vagalume (API brasileña gratuita)"""
        try:
            # API pública brasileña sin requerir clave
            url = "https://api.vagalume.com.br/search.php"
            params = {
                'art': artist_name,
                'mus': song_title,
                'fmt': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'mus' in data and len(data['mus']) > 0:
                return data['mus'][0].get('text', '')
            
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo letras de Vagalume: {e}")
            return None
    
    def _get_track_genre(self, title: str, artist: str) -> str:
        """Obtener género de una canción usando Last.fm"""
        try:
            if not self.apis['lastfm']:
                return 'Unknown'
            
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'track.getInfo',
                'track': title,
                'artist': artist,
                'api_key': self.apis['lastfm'],
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'track' in data and 'toptags' in data['track']:
                tags = data['track']['toptags']['tag']
                if tags and len(tags) > 0:
                    return tags[0]['name']
            
            return 'Unknown'
        except Exception as e:
            self.logger.warning(f"Error obteniendo género: {e}")
            return 'Unknown'
    
    def _enrich_album_data(self, album: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquecer datos de álbum con información adicional"""
        try:
            # Obtener canciones del álbum si es de Spotify
            if album.get('source') == 'Spotify' and self.apis['spotify']:
                album_tracks = self.apis['spotify'].album_tracks(album['id'])
                album['tracks'] = []
                
                for track in album_tracks['items']:
                    album['tracks'].append({
                        'name': track['name'],
                        'duration_ms': track['duration_ms'],
                        'track_number': track['track_number'],
                        'preview_url': track.get('preview_url')
                    })
            
            return album
        except Exception as e:
            self.logger.error(f"Error enriqueciendo álbum: {e}")
            return album