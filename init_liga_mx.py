"""
Script de inicialización para la API Liga MX
Poblar base de datos con equipos y configuración inicial
"""

from app import app, db
from models import LigaMXEquipo, ApiKey
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_liga_mx_equipos():
    """Inicializar equipos de Liga MX en la base de datos"""
    equipos_data = [
        {
            'nombre': 'América',
            'nombre_completo': 'Club de Fútbol América',
            'ciudad': 'Ciudad de México',
            'estadio': 'Estadio Azteca',
            'fundacion': '1916',
            'colores_primarios': 'Amarillo, Azul',
            'sitio_web': 'https://www.clubamerica.com.mx'
        },
        {
            'nombre': 'Guadalajara',
            'nombre_completo': 'Club de Fútbol Guadalajara',
            'ciudad': 'Guadalajara',
            'estadio': 'Estadio Akron',
            'fundacion': '1906',
            'colores_primarios': 'Rojo, Blanco',
            'sitio_web': 'https://www.chivas.com'
        },
        {
            'nombre': 'Cruz Azul',
            'nombre_completo': 'Cruz Azul Fútbol Club',
            'ciudad': 'Ciudad de México',
            'estadio': 'Estadio Azteca',
            'fundacion': '1927',
            'colores_primarios': 'Azul, Blanco',
            'sitio_web': 'https://www.cruzazul.com.mx'
        },
        {
            'nombre': 'Pumas',
            'nombre_completo': 'Club Universidad Nacional',
            'ciudad': 'Ciudad de México',
            'estadio': 'Estadio Olímpico Universitario',
            'fundacion': '1954',
            'colores_primarios': 'Azul, Dorado',
            'sitio_web': 'https://www.pumas.mx'
        },
        {
            'nombre': 'Tigres',
            'nombre_completo': 'Club de Fútbol Tigres de la UANL',
            'ciudad': 'San Nicolás de los Garza',
            'estadio': 'Estadio Universitario',
            'fundacion': '1960',
            'colores_primarios': 'Amarillo, Azul',
            'sitio_web': 'https://www.tigres.com.mx'
        },
        {
            'nombre': 'Monterrey',
            'nombre_completo': 'Club de Fútbol Monterrey',
            'ciudad': 'Monterrey',
            'estadio': 'Estadio BBVA',
            'fundacion': '1945',
            'colores_primarios': 'Azul, Blanco',
            'sitio_web': 'https://www.rayados.com'
        },
        {
            'nombre': 'Santos',
            'nombre_completo': 'Club Santos Laguna',
            'ciudad': 'Torreón',
            'estadio': 'Estadio Corona',
            'fundacion': '1983',
            'colores_primarios': 'Verde, Blanco',
            'sitio_web': 'https://www.santos.mx'
        },
        {
            'nombre': 'León',
            'nombre_completo': 'Club León',
            'ciudad': 'León',
            'estadio': 'Estadio León',
            'fundacion': '1944',
            'colores_primarios': 'Verde, Blanco',
            'sitio_web': 'https://www.clubleonfc.mx'
        },
        {
            'nombre': 'Pachuca',
            'nombre_completo': 'Club de Fútbol Pachuca',
            'ciudad': 'Pachuca',
            'estadio': 'Estadio Hidalgo',
            'fundacion': '1901',
            'colores_primarios': 'Azul, Blanco',
            'sitio_web': 'https://www.pachuca.mx'
        },
        {
            'nombre': 'Toluca',
            'nombre_completo': 'Deportivo Toluca Fútbol Club',
            'ciudad': 'Toluca',
            'estadio': 'Estadio Nemesio Díez',
            'fundacion': '1917',
            'colores_primarios': 'Rojo, Blanco',
            'sitio_web': 'https://www.deportivotoluca.com.mx'
        },
        {
            'nombre': 'Atlas',
            'nombre_completo': 'Club de Fútbol Atlas',
            'ciudad': 'Guadalajara',
            'estadio': 'Estadio Jalisco',
            'fundacion': '1916',
            'colores_primarios': 'Rojo, Negro',
            'sitio_web': 'https://www.atlasfc.com.mx'
        },
        {
            'nombre': 'Puebla',
            'nombre_completo': 'Club de Fútbol Puebla',
            'ciudad': 'Puebla',
            'estadio': 'Estadio Cuauhtémoc',
            'fundacion': '1944',
            'colores_primarios': 'Azul, Blanco',
            'sitio_web': 'https://www.clubpuebla.com'
        },
        {
            'nombre': 'Necaxa',
            'nombre_completo': 'Club Necaxa',
            'ciudad': 'Aguascalientes',
            'estadio': 'Estadio Victoria',
            'fundacion': '1923',
            'colores_primarios': 'Rojo, Blanco',
            'sitio_web': 'https://www.clubnecaxa.mx'
        },
        {
            'nombre': 'Mazatlán',
            'nombre_completo': 'Mazatlán Fútbol Club',
            'ciudad': 'Mazatlán',
            'estadio': 'Estadio El Encanto',
            'fundacion': '2020',
            'colores_primarios': 'Morado, Blanco',
            'sitio_web': 'https://www.mazatlanfc.mx'
        },
        {
            'nombre': 'FC Juárez',
            'nombre_completo': 'FC Juárez',
            'ciudad': 'Ciudad Juárez',
            'estadio': 'Estadio Olímpico Benito Juárez',
            'fundacion': '2015',
            'colores_primarios': 'Verde, Rojo',
            'sitio_web': 'https://www.fcjuarez.mx'
        },
        {
            'nombre': 'Querétaro',
            'nombre_completo': 'Querétaro Fútbol Club',
            'ciudad': 'Querétaro',
            'estadio': 'Estadio Corregidora',
            'fundacion': '1950',
            'colores_primarios': 'Azul, Negro',
            'sitio_web': 'https://www.queretarofc.mx'
        },
        {
            'nombre': 'Tijuana',
            'nombre_completo': 'Club Tijuana',
            'ciudad': 'Tijuana',
            'estadio': 'Estadio Caliente',
            'fundacion': '2007',
            'colores_primarios': 'Rojo, Negro',
            'sitio_web': 'https://www.clubtijuana.mx'
        },
        {
            'nombre': 'San Luis',
            'nombre_completo': 'Atlético de San Luis',
            'ciudad': 'San Luis Potosí',
            'estadio': 'Estadio Alfonso Lastras',
            'fundacion': '2013',
            'colores_primarios': 'Rojo, Azul',
            'sitio_web': 'https://www.atleticodesanluis.mx'
        }
    ]
    
    logger.info("Inicializando equipos de Liga MX...")
    
    equipos_creados = 0
    for equipo_data in equipos_data:
        # Verificar si el equipo ya existe
        equipo_existente = LigaMXEquipo.query.filter_by(nombre=equipo_data['nombre']).first()
        
        if not equipo_existente:
            nuevo_equipo = LigaMXEquipo(**equipo_data)
            db.session.add(nuevo_equipo)
            equipos_creados += 1
            logger.info(f"✅ Creado equipo: {equipo_data['nombre']}")
        else:
            logger.info(f"⚠️ Equipo ya existe: {equipo_data['nombre']}")
    
    try:
        db.session.commit()
        logger.info(f"🏆 Inicialización completada: {equipos_creados} equipos nuevos creados")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al guardar equipos: {e}")
        return False

def init_liga_mx_api_config():
    """Configurar APIs para Liga MX en el sistema"""
    
    # Configuraciones de APIs para fútbol
    apis_futbol = [
        {
            'service_name': 'football',
            'service_type': 'Liga MX ESPN',
            'api_key': 'scraping_based',
            'api_url': 'https://www.espn.com.mx/futbol/liga/_/nombre/mex.1',
            'description': 'Scraping de datos de Liga MX desde ESPN México',
            'endpoints': 'tabla,calendario,resultados,estadisticas,goleadores,noticias'
        },
        {
            'service_name': 'football',
            'service_type': 'Liga MX Oficial',
            'api_key': 'scraping_based',
            'api_url': 'https://ligamx.net',
            'description': 'Datos oficiales de Liga MX',
            'endpoints': 'equipos,partidos,estadisticas,tabla'
        },
        {
            'service_name': 'football',
            'service_type': 'FutbolTotal',
            'api_key': 'scraping_based',
            'api_url': 'https://www.futboltotal.com.mx',
            'description': 'Noticias y análisis de fútbol mexicano',
            'endpoints': 'noticias,analisis,transferencias'
        },
        {
            'service_name': 'football',
            'service_type': 'MedioTiempo',
            'api_key': 'scraping_based',
            'api_url': 'https://www.mediotiempo.com/futbol/liga-mx',
            'description': 'Portal de noticias deportivas mexicanas',
            'endpoints': 'noticias,resultados,calendario'
        },
        {
            'service_name': 'football',
            'service_type': 'SofaScore',
            'api_key': 'scraping_based',
            'api_url': 'https://www.sofascore.com/es/torneo/futbol/mexico/liga-mx/123',
            'description': 'Estadísticas detalladas y resultados en vivo',
            'endpoints': 'estadisticas,resultados_vivo,jugadores'
        }
    ]
    
    logger.info("Configurando APIs de fútbol...")
    
    apis_creadas = 0
    for api_data in apis_futbol:
        # Verificar si la API ya existe
        api_existente = ApiKey.query.filter_by(
            service_name=api_data['service_name'],
            service_type=api_data['service_type']
        ).first()
        
        if not api_existente:
            nueva_api = ApiKey(**api_data)
            db.session.add(nueva_api)
            apis_creadas += 1
            logger.info(f"✅ API configurada: {api_data['service_type']}")
        else:
            logger.info(f"⚠️ API ya existe: {api_data['service_type']}")
    
    try:
        db.session.commit()
        logger.info(f"🔑 APIs configuradas: {apis_creadas} nuevas APIs creadas")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al guardar APIs: {e}")
        return False

def run_initialization():
    """Ejecutar inicialización completa de Liga MX"""
    logger.info("🚀 Iniciando configuración de Liga MX API...")
    
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        
        # Inicializar equipos
        equipos_ok = init_liga_mx_equipos()
        
        # Configurar APIs
        apis_ok = init_liga_mx_api_config()
        
        if equipos_ok and apis_ok:
            logger.info("✅ Inicialización de Liga MX completada exitosamente")
            return True
        else:
            logger.error("❌ Errores durante la inicialización")
            return False

if __name__ == '__main__':
    run_initialization()