#!/usr/bin/env python3
"""
Sistema de actualización automática para Liga MX 2025
Actualiza datos cada 30 minutos desde fuentes mexicanas reales
"""

import schedule
import time
import logging
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('liga_mx_auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_liga_mx_data():
    """Función para actualizar datos de Liga MX desde fuentes reales"""
    try:
        logger.info("🚀 INICIANDO ACTUALIZACIÓN AUTOMÁTICA LIGA MX 2025")
        
        # Importar el data manager
        from services.liga_mx_data_manager import LigaMXDataManager
        
        # Crear instancia y actualizar
        data_manager = LigaMXDataManager()
        result = data_manager.update_all_data()
        
        if 'error' in result:
            logger.error(f"❌ Error en actualización automática: {result['error']}")
            return False
        
        logger.info(f"✅ ACTUALIZACIÓN COMPLETADA:")
        logger.info(f"   • Equipos actualizados: {result.get('equipos_actualizados', 0)}")
        logger.info(f"   • Jugadores actualizados: {result.get('jugadores_actualizados', 0)}")
        logger.info(f"   • Noticias actualizadas: {result.get('noticias_actualizadas', 0)}")
        logger.info(f"   • Fuentes exitosas: {len(result.get('fuentes_exitosas', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FALLO EN ACTUALIZACIÓN AUTOMÁTICA: {str(e)}")
        return False

def main():
    """Función principal del actualizador automático"""
    logger.info("🤖 Sistema de actualización automática Liga MX 2025 iniciado")
    logger.info("📅 Programado para ejecutarse cada 30 minutos")
    
    # Programar actualización cada 30 minutos
    schedule.every(30).minutes.do(update_liga_mx_data)
    
    # Ejecutar una actualización inicial
    logger.info("⚡ Ejecutando actualización inicial...")
    update_liga_mx_data()
    
    # Mantener el programa corriendo
    logger.info("⏰ Sistema en espera... Próxima actualización en 30 minutos")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Revisar cada minuto si hay tareas pendientes
            
        except KeyboardInterrupt:
            logger.info("⏹️ Sistema de actualización automática detenido por el usuario")
            break
        except Exception as e:
            logger.error(f"❌ Error en el bucle principal: {str(e)}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

if __name__ == "__main__":
    main()