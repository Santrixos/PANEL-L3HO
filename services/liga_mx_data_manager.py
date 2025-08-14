#!/usr/bin/env python3
"""
Liga MX Data Manager - Gestor centralizado de datos reales
Integra scraping real con base de datos PostgreSQL
"""

import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Agregar directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import (LigaMXEquipo, LigaMXPosicion, LigaMXPartido, LigaMXJugador, 
                   LigaMXNoticia, LigaMXActualizacion)
from services.liga_mx_real_scraper import LigaMXRealScraper

logger = logging.getLogger(__name__)

class LigaMXDataManager:
    """Gestor de datos reales de Liga MX con integración a base de datos"""
    
    def __init__(self):
        self.scraper = LigaMXRealScraper()
        
    def update_all_data(self) -> Dict[str, any]:
        """Actualizar todos los datos desde fuentes reales"""
        try:
            with app.app_context():
                logger.info("🚀 Iniciando actualización completa con datos reales...")
                
                # Registrar inicio de actualización
                actualizacion = LigaMXActualizacion(
                    tipo_actualizacion='scraping_real',
                    status='running',
                    detalles='Iniciando scraping desde fuentes mexicanas',
                    fuentes_consultadas='ESPN MX, Mediotiempo, Liga MX Oficial'
                )
                db.session.add(actualizacion)
                db.session.commit()
                
                # Obtener datos reales
                datos_reales = self.scraper.scrape_all_data()
                
                results = {
                    'equipos_actualizados': 0,
                    'partidos_actualizados': 0,
                    'jugadores_actualizados': 0,
                    'noticias_actualizadas': 0,
                    'errores': [],
                    'fuentes_exitosas': datos_reales.get('fuentes_exitosas', [])
                }
                
                # Actualizar equipos y tabla
                if datos_reales.get('tabla_posiciones'):
                    equipos_count = self.update_equipos_tabla(datos_reales['tabla_posiciones'])
                    results['equipos_actualizados'] = equipos_count
                    logger.info(f"✅ {equipos_count} equipos actualizados con datos reales")
                
                # Actualizar partidos
                if datos_reales.get('partidos'):
                    partidos_count = self.update_partidos(datos_reales['partidos'])
                    results['partidos_actualizados'] = partidos_count
                    logger.info(f"✅ {partidos_count} partidos actualizados")
                
                # Actualizar jugadores
                if datos_reales.get('jugadores'):
                    jugadores_count = self.update_jugadores(datos_reales['jugadores'])
                    results['jugadores_actualizados'] = jugadores_count
                    logger.info(f"✅ {jugadores_count} jugadores actualizados")
                
                # Actualizar noticias
                if datos_reales.get('noticias'):
                    noticias_count = self.update_noticias(datos_reales['noticias'])
                    results['noticias_actualizadas'] = noticias_count
                    logger.info(f"✅ {noticias_count} noticias actualizadas")
                
                # Completar registro de actualización
                actualizacion.status = 'success'
                actualizacion.elementos_actualizados = results["equipos_actualizados"] + results["partidos_actualizados"] + results["jugadores_actualizados"] + results["noticias_actualizadas"]
                actualizacion.detalles = f'Equipos: {results["equipos_actualizados"]}, Partidos: {results["partidos_actualizados"]}, Jugadores: {results["jugadores_actualizados"]}, Noticias: {results["noticias_actualizadas"]}'
                db.session.commit()
                
                logger.info("🎉 Actualización completa con datos reales terminada")
                return results
                
        except Exception as e:
            logger.error(f"❌ Error en actualización de datos reales: {e}")
            try:
                with app.app_context():
                    actualizacion.status = 'error'
                    actualizacion.errores = str(e)
                    actualizacion.detalles = f'Error: {str(e)}'
                    db.session.commit()
            except:
                pass
            return {'error': str(e)}
    
    def update_equipos_tabla(self, tabla_data: List[Dict]) -> int:
        """Actualizar equipos y tabla de posiciones con datos reales"""
        try:
            equipos_actualizados = 0
            
            for equipo_data in tabla_data:
                # Buscar o crear equipo
                equipo = LigaMXEquipo.query.filter_by(nombre=equipo_data['nombre']).first()
                
                if not equipo:
                    equipo = LigaMXEquipo(
                        nombre=equipo_data['nombre'],
                        nombre_completo=equipo_data.get('nombre_completo', equipo_data['nombre']),
                        ciudad=self.scraper.get_team_city(equipo_data['nombre']),
                        estadio=self.scraper.get_team_stadium(equipo_data['nombre']),
                        fundacion=self.scraper.get_team_foundation(equipo_data['nombre']),
                        colores_primarios=self.scraper.get_team_colors(equipo_data['nombre']),
                        logo_url=f'/static/logos/{equipo_data["nombre"].lower().replace(" ", "_")}.png'
                    )
                    db.session.add(equipo)
                    db.session.flush()  # Para obtener el ID
                
                # Actualizar datos del equipo con info real
                equipo.updated_at = datetime.utcnow()
                
                # Buscar o crear posición actual
                posicion = LigaMXPosicion.query.filter_by(
                    equipo_id=equipo.id,
                    temporada='2024'
                ).first()
                
                if not posicion:
                    posicion = LigaMXPosicion(
                        equipo_id=equipo.id,
                        temporada='2024'
                    )
                    db.session.add(posicion)
                
                # Actualizar datos de posición con datos reales
                posicion.posicion = equipo_data.get('posicion', 0)
                posicion.partidos_jugados = equipo_data.get('partidos_jugados', 0)
                posicion.ganados = equipo_data.get('ganados', 0)
                posicion.empatados = equipo_data.get('empatados', 0)
                posicion.perdidos = equipo_data.get('perdidos', 0)
                posicion.goles_favor = equipo_data.get('goles_favor', 0)
                posicion.goles_contra = equipo_data.get('goles_contra', 0)
                posicion.diferencia_goles = equipo_data.get('diferencia_goles', 0)
                posicion.puntos = equipo_data.get('puntos', 0)
                posicion.fuente = equipo_data.get('fuente', 'ESPN México')
                posicion.ultima_actualizacion = datetime.utcnow()
                
                equipos_actualizados += 1
            
            db.session.commit()
            return equipos_actualizados
            
        except Exception as e:
            logger.error(f"Error actualizando equipos: {e}")
            db.session.rollback()
            return 0
    
    def update_partidos(self, partidos_data: List[Dict]) -> int:
        """Actualizar partidos con datos reales"""
        try:
            partidos_actualizados = 0
            
            for partido_data in partidos_data:
                # Buscar equipos
                equipo_local = LigaMXEquipo.query.filter_by(nombre=partido_data['equipo_local']).first()
                equipo_visitante = LigaMXEquipo.query.filter_by(nombre=partido_data['equipo_visitante']).first()
                
                if not equipo_local or not equipo_visitante:
                    logger.warning(f"Equipos no encontrados para partido: {partido_data['equipo_local']} vs {partido_data['equipo_visitante']}")
                    continue
                
                # Verificar si el partido ya existe
                partido_existente = LigaMXPartido.query.filter_by(
                    jornada=partido_data.get('jornada', 1),
                    equipo_local_id=equipo_local.id,
                    equipo_visitante_id=equipo_visitante.id,
                    temporada='2024'
                ).first()
                
                if not partido_existente:
                    # Crear nuevo partido
                    partido = LigaMXPartido(
                        temporada='2024',
                        jornada=partido_data.get('jornada', 1),
                        equipo_local_id=equipo_local.id,
                        equipo_visitante_id=equipo_visitante.id,
                        fecha_partido=datetime.fromisoformat(partido_data['fecha_partido']) if partido_data.get('fecha_partido') else None,
                        estado=partido_data.get('estado', 'programado'),
                        goles_local=partido_data.get('goles_local'),
                        goles_visitante=partido_data.get('goles_visitante'),
                        estadio=partido_data.get('estadio'),
                        fuente=partido_data.get('fuente', 'Mediotiempo'),
                        ultima_actualizacion=datetime.utcnow()
                    )
                    db.session.add(partido)
                    partidos_actualizados += 1
                else:
                    # Actualizar partido existente
                    if partido_data.get('goles_local') is not None:
                        partido_existente.goles_local = partido_data['goles_local']
                    if partido_data.get('goles_visitante') is not None:
                        partido_existente.goles_visitante = partido_data['goles_visitante']
                    
                    partido_existente.estado = partido_data.get('estado', partido_existente.estado)
                    partido_existente.ultima_actualizacion = datetime.utcnow()
                    partidos_actualizados += 1
            
            db.session.commit()
            return partidos_actualizados
            
        except Exception as e:
            logger.error(f"Error actualizando partidos: {e}")
            db.session.rollback()
            return 0
    
    def update_jugadores(self, jugadores_data: List[Dict]) -> int:
        """Actualizar jugadores con datos reales"""
        try:
            jugadores_actualizados = 0
            
            for jugador_data in jugadores_data:
                # Buscar equipo del jugador
                equipo = LigaMXEquipo.query.filter_by(nombre=jugador_data['equipo']).first()
                if not equipo:
                    logger.warning(f"Equipo no encontrado para jugador: {jugador_data['nombre']} - {jugador_data['equipo']}")
                    continue
                
                # Buscar o crear jugador
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
                
                # Actualizar estadísticas del jugador
                jugador.posicion = jugador_data.get('posicion')
                jugador.numero = jugador_data.get('numero')
                jugador.edad = jugador_data.get('edad')
                jugador.nacionalidad = jugador_data.get('nacionalidad')
                jugador.goles = jugador_data.get('goles', 0)
                jugador.asistencias = jugador_data.get('asistencias', 0)
                jugador.partidos_jugados = jugador_data.get('partidos_jugados', 0)
                jugador.minutos_jugados = jugador_data.get('minutos_jugados', 0)
                jugador.tarjetas_amarillas = jugador_data.get('tarjetas_amarillas', 0)
                jugador.tarjetas_rojas = jugador_data.get('tarjetas_rojas', 0)
                jugador.updated_at = datetime.utcnow()
                
                jugadores_actualizados += 1
            
            db.session.commit()
            return jugadores_actualizados
            
        except Exception as e:
            logger.error(f"Error actualizando jugadores: {e}")
            db.session.rollback()
            return 0
    
    def update_noticias(self, noticias_data: List[Dict]) -> int:
        """Actualizar noticias con datos reales"""
        try:
            noticias_actualizadas = 0
            
            for noticia_data in noticias_data:
                # Verificar si la noticia ya existe por título
                noticia_existente = LigaMXNoticia.query.filter_by(
                    titulo=noticia_data['titulo']
                ).first()
                
                if not noticia_existente:
                    # Crear nueva noticia
                    noticia = LigaMXNoticia(
                        titulo=noticia_data['titulo'],
                        resumen=noticia_data.get('resumen'),
                        url=noticia_data.get('url'),
                        fuente=noticia_data.get('fuente'),
                        fecha=datetime.fromisoformat(noticia_data['fecha']) if noticia_data.get('fecha') else datetime.utcnow(),
                        imagen_url=noticia_data.get('imagen_url'),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(noticia)
                    noticias_actualizadas += 1
            
            db.session.commit()
            return noticias_actualizadas
            
        except Exception as e:
            logger.error(f"Error actualizando noticias: {e}")
            db.session.rollback()
            return 0
    
    def get_tabla_actualizada(self) -> List[Dict]:
        """Obtener tabla de posiciones actualizada"""
        try:
            with app.app_context():
                # Join entre equipos y posiciones
                query = db.session.query(LigaMXEquipo, LigaMXPosicion).join(
                    LigaMXPosicion, LigaMXEquipo.id == LigaMXPosicion.equipo_id
                ).filter(
                    LigaMXPosicion.temporada == '2024'
                ).order_by(
                    LigaMXPosicion.puntos.desc(),
                    LigaMXPosicion.diferencia_goles.desc(),
                    LigaMXPosicion.goles_favor.desc()
                ).all()
                
                tabla_actual = []
                for i, (equipo, posicion) in enumerate(query, 1):
                    tabla_actual.append({
                        'posicion': i,
                        'equipo': equipo.nombre,
                        'nombre_corto': self.scraper.get_short_name(equipo.nombre),
                        'partidos_jugados': posicion.partidos_jugados,
                        'ganados': posicion.ganados,
                        'empatados': posicion.empatados,
                        'perdidos': posicion.perdidos,
                        'goles_favor': posicion.goles_favor,
                        'goles_contra': posicion.goles_contra,
                        'diferencia_goles': posicion.diferencia_goles,
                        'puntos': posicion.puntos,
                        'ultima_actualizacion': posicion.ultima_actualizacion.isoformat() if posicion.ultima_actualizacion else None,
                        'fuente': posicion.fuente
                    })
                
                return tabla_actual
                
        except Exception as e:
            logger.error(f"Error obteniendo tabla actualizada: {e}")
            return []

if __name__ == "__main__":
    manager = LigaMXDataManager()
    result = manager.update_all_data()
    print(f"Resultado: {result}")