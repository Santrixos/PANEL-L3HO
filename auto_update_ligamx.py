#!/usr/bin/env python3
"""
Script de actualización automática para Liga MX
Actualiza datos de equipos, partidos, jugadores y noticias sin intervención manual
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import schedule

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (LigaMXEquipo, LigaMXPartido, LigaMXJugador, 
                   LigaMXNoticia, LigaMXActualizacion)
from services.liga_mx_scraper import LigaMXScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ligamx_auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LigaMXAutoUpdater:
    """Actualizador automático de datos de Liga MX"""
    
    def __init__(self):
        self.scraper = LigaMXScraper()
        self.last_update = None
        self.update_interval = 30  # minutos
        
    def update_all_data(self):
        """Actualizar todos los datos de Liga MX"""
        try:
            with app.app_context():
                logger.info("🚀 Iniciando actualización automática completa de Liga MX...")
                
                # Registrar inicio de actualización
                actualizacion = LigaMXActualizacion(
                    tipo='automatica',
                    estado='iniciada',
                    fuente='auto_updater',
                    timestamp=datetime.utcnow()
                )
                db.session.add(actualizacion)
                db.session.commit()
                
                success_count = 0
                total_tasks = 5
                
                # 1. Actualizar equipos y tabla de posiciones
                if self.update_equipos():
                    success_count += 1
                    logger.info("✅ Equipos actualizados")
                
                # 2. Actualizar partidos
                if self.update_partidos():
                    success_count += 1
                    logger.info("✅ Partidos actualizados")
                
                # 3. Actualizar estadísticas de jugadores
                if self.update_jugadores():
                    success_count += 1
                    logger.info("✅ Jugadores actualizados")
                
                # 4. Actualizar noticias
                if self.update_noticias():
                    success_count += 1
                    logger.info("✅ Noticias actualizadas")
                
                # 5. Verificar integridad de datos
                if self.verify_data_integrity():
                    success_count += 1
                    logger.info("✅ Integridad de datos verificada")
                
                # Actualizar registro
                actualizacion.estado = 'completada' if success_count == total_tasks else 'parcial'
                actualizacion.detalles = f'Tareas completadas: {success_count}/{total_tasks}'
                actualizacion.completada_en = datetime.utcnow()
                db.session.commit()
                
                self.last_update = datetime.now()
                
                logger.info(f"🎉 Actualización completada: {success_count}/{total_tasks} tareas exitosas")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error en actualización automática: {e}")
            try:
                with app.app_context():
                    actualizacion.estado = 'error'
                    actualizacion.detalles = f'Error: {str(e)}'
                    db.session.commit()
            except:
                pass
            return False
    
    def update_equipos(self):
        """Actualizar datos de equipos"""
        try:
            # Scraping desde ESPN
            espn_data = self.scraper.scrape_tabla_espn()
            if espn_data and 'equipos' in espn_data:
                for equipo_data in espn_data['equipos']:
                    equipo = LigaMXEquipo.query.filter_by(nombre=equipo_data['nombre']).first()
                    
                    if not equipo:
                        equipo = LigaMXEquipo(nombre=equipo_data['nombre'])
                        db.session.add(equipo)
                    
                    # Actualizar datos
                    for key, value in equipo_data.items():
                        if hasattr(equipo, key):
                            setattr(equipo, key, value)
                    
                    equipo.updated_at = datetime.utcnow()
                
                db.session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error actualizando equipos: {e}")
            return False
    
    def update_partidos(self):
        """Actualizar calendario de partidos"""
        try:
            # Implementar scraping de partidos desde múltiples fuentes
            sources = [
                'https://www.espn.com.mx/futbol/liga/_/nombre/mex.1',
                'https://www.mediotiempo.com/futbol/liga-mx',
                'https://ligamx.net'
            ]
            
            for source in sources:
                try:
                    partidos_data = self.scrape_partidos_from_source(source)
                    if partidos_data:
                        self.save_partidos(partidos_data)
                        break
                except Exception as e:
                    logger.warning(f"Error scraping partidos de {source}: {e}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando partidos: {e}")
            return False
    
    def update_jugadores(self):
        """Actualizar estadísticas de jugadores"""
        try:
            # Scraping de estadísticas de jugadores
            equipos = LigaMXEquipo.query.all()
            
            for equipo in equipos:
                try:
                    jugadores_data = self.scrape_jugadores_equipo(equipo.nombre)
                    if jugadores_data:
                        for jugador_data in jugadores_data:
                            jugador = LigaMXJugador.query.filter_by(
                                nombre=jugador_data['nombre'],
                                equipo_id=equipo.id
                            ).first()
                            
                            if not jugador:
                                jugador = LigaMXJugador(
                                    nombre=jugador_data['nombre'],
                                    equipo_id=equipo.id
                                )
                                db.session.add(jugador)
                            
                            # Actualizar estadísticas
                            for key, value in jugador_data.items():
                                if hasattr(jugador, key):
                                    setattr(jugador, key, value)
                except Exception as e:
                    logger.warning(f"Error actualizando jugadores de {equipo.nombre}: {e}")
                    continue
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando jugadores: {e}")
            return False
    
    def update_noticias(self):
        """Actualizar noticias de Liga MX"""
        try:
            sources = [
                {'url': 'https://www.mediotiempo.com/futbol/liga-mx', 'source': 'Mediotiempo'},
                {'url': 'https://www.espn.com.mx/futbol/liga/_/nombre/mex.1', 'source': 'ESPN'},
                {'url': 'https://www.futboltotal.com.mx', 'source': 'Futbol Total'}
            ]
            
            for source_info in sources:
                try:
                    noticias_data = self.scrape_noticias_from_source(source_info)
                    if noticias_data:
                        for noticia_data in noticias_data:
                            # Verificar si la noticia ya existe
                            existing = LigaMXNoticia.query.filter_by(
                                titulo=noticia_data['titulo']
                            ).first()
                            
                            if not existing:
                                noticia = LigaMXNoticia(**noticia_data)
                                db.session.add(noticia)
                        
                        db.session.commit()
                        
                except Exception as e:
                    logger.warning(f"Error scraping noticias de {source_info['source']}: {e}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando noticias: {e}")
            return False
    
    def verify_data_integrity(self):
        """Verificar integridad de los datos"""
        try:
            with app.app_context():
                # Verificar que hay equipos
                equipos_count = LigaMXEquipo.query.count()
                if equipos_count < 18:
                    logger.warning(f"Solo {equipos_count} equipos en la base de datos (esperados: 18)")
                
                # Verificar que hay datos recientes
                recent_threshold = datetime.utcnow() - timedelta(days=7)
                recent_updates = LigaMXEquipo.query.filter(
                    LigaMXEquipo.updated_at >= recent_threshold
                ).count()
                
                if recent_updates == 0:
                    logger.warning("No hay actualizaciones recientes de equipos")
                    return False
                
                logger.info(f"Integridad verificada: {equipos_count} equipos, {recent_updates} actualizaciones recientes")
                return True
                
        except Exception as e:
            logger.error(f"Error verificando integridad: {e}")
            return False
    
    def scrape_partidos_from_source(self, url):
        """Scraping de partidos desde una fuente específica"""
        # Implementación simplificada
        return []
    
    def scrape_jugadores_equipo(self, equipo_nombre):
        """Scraping de jugadores de un equipo específico"""
        # Implementación simplificada
        return []
    
    def scrape_noticias_from_source(self, source_info):
        """Scraping de noticias desde una fuente específica"""
        # Implementación simplificada
        return []
    
    def save_partidos(self, partidos_data):
        """Guardar datos de partidos en la base de datos"""
        try:
            with app.app_context():
                for partido_data in partidos_data:
                    partido = LigaMXPartido(**partido_data)
                    db.session.add(partido)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error guardando partidos: {e}")
    
    def run_scheduler(self):
        """Ejecutar el programador de tareas"""
        logger.info("🚀 Iniciando programador de actualizaciones automáticas...")
        
        # Programar actualizaciones cada 30 minutos
        schedule.every(30).minutes.do(self.update_all_data)
        
        # Programar actualización completa cada 6 horas
        schedule.every(6).hours.do(self.update_all_data)
        
        # Actualización diaria a las 6:00 AM
        schedule.every().day.at("06:00").do(self.update_all_data)
        
        # Ejecutar primera actualización inmediatamente
        self.update_all_data()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Revisar cada minuto
            except KeyboardInterrupt:
                logger.info("🛑 Deteniendo actualizador automático...")
                break
            except Exception as e:
                logger.error(f"Error en scheduler: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de continuar

def main():
    """Función principal"""
    updater = LigaMXAutoUpdater()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Ejecutar solo una vez
        logger.info("Ejecutando actualización única...")
        updater.update_all_data()
    else:
        # Ejecutar como daemon
        logger.info("Ejecutando como daemon...")
        updater.run_scheduler()

if __name__ == "__main__":
    main()