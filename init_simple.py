"""
Script simple de inicialización Liga MX
"""

import os
import sys
import logging

# Configurar path para imports
sys.path.insert(0, '/home/runner/workspace')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inicializar base de datos con equipos Liga MX"""
    try:
        # Import directo sin depender de routes
        from app import app, db
        from models import LigaMXEquipo, ApiKey
        
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            logger.info("✅ Tablas creadas correctamente")
            
            # Verificar si ya hay equipos
            equipos_existentes = LigaMXEquipo.query.count()
            if equipos_existentes > 0:
                logger.info(f"⚠️ Ya existen {equipos_existentes} equipos en la base de datos")
                return True
            
            # Equipos Liga MX
            equipos = [
                ('América', 'Club de Fútbol América', 'Ciudad de México', 'Estadio Azteca'),
                ('Guadalajara', 'Club de Fútbol Guadalajara', 'Guadalajara', 'Estadio Akron'),
                ('Cruz Azul', 'Cruz Azul Fútbol Club', 'Ciudad de México', 'Estadio Azteca'),
                ('Pumas', 'Club Universidad Nacional', 'Ciudad de México', 'Estadio Olímpico Universitario'),
                ('Tigres', 'Club de Fútbol Tigres de la UANL', 'San Nicolás de los Garza', 'Estadio Universitario'),
                ('Monterrey', 'Club de Fútbol Monterrey', 'Monterrey', 'Estadio BBVA'),
                ('Santos', 'Club Santos Laguna', 'Torreón', 'Estadio Corona'),
                ('León', 'Club León', 'León', 'Estadio León'),
                ('Pachuca', 'Club de Fútbol Pachuca', 'Pachuca', 'Estadio Hidalgo'),
                ('Toluca', 'Deportivo Toluca Fútbol Club', 'Toluca', 'Estadio Nemesio Díez'),
                ('Atlas', 'Club de Fútbol Atlas', 'Guadalajara', 'Estadio Jalisco'),
                ('Puebla', 'Club de Fútbol Puebla', 'Puebla', 'Estadio Cuauhtémoc'),
                ('Necaxa', 'Club Necaxa', 'Aguascalientes', 'Estadio Victoria'),
                ('Mazatlán', 'Mazatlán Fútbol Club', 'Mazatlán', 'Estadio El Encanto'),
                ('FC Juárez', 'FC Juárez', 'Ciudad Juárez', 'Estadio Olímpico Benito Juárez'),
                ('Querétaro', 'Querétaro Fútbol Club', 'Querétaro', 'Estadio Corregidora'),
                ('Tijuana', 'Club Tijuana', 'Tijuana', 'Estadio Caliente'),
                ('San Luis', 'Atlético de San Luis', 'San Luis Potosí', 'Estadio Alfonso Lastras')
            ]
            
            equipos_creados = 0
            for nombre, nombre_completo, ciudad, estadio in equipos:
                equipo = LigaMXEquipo(
                    nombre=nombre,
                    nombre_completo=nombre_completo,
                    ciudad=ciudad,
                    estadio=estadio,
                    fundacion='1900'  # Año por defecto
                )
                db.session.add(equipo)
                equipos_creados += 1
                logger.info(f"➕ Agregado: {nombre}")
            
            # Commit equipos
            db.session.commit()
            logger.info(f"🏆 {equipos_creados} equipos de Liga MX creados exitosamente")
            
            # Verificar APIs de fútbol existentes
            apis_futbol = ApiKey.query.filter_by(service_name='football').count()
            logger.info(f"📊 APIs de fútbol configuradas: {apis_futbol}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {e}")
        return False

if __name__ == '__main__':
    logger.info("🚀 Iniciando configuración básica Liga MX...")
    success = init_database()
    if success:
        logger.info("✅ Inicialización completada")
    else:
        logger.error("❌ Inicialización falló")