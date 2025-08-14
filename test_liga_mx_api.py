"""
Script de prueba para la API Liga MX
"""

import requests
import json
import sys

def test_liga_mx_api():
    """Probar endpoints de la API Liga MX"""
    
    base_url = "http://localhost:5000"
    
    # Obtener información de la API
    print("🔍 Probando API Liga MX...")
    
    try:
        # Test 1: Info de la API (sin autenticación)
        response = requests.get(f"{base_url}/api/liga-mx/info")
        print(f"📋 Info API: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"   - Nombre: {info.get('name')}")
            print(f"   - Versión: {info.get('version')}")
            print(f"   - Endpoints: {len(info.get('endpoints', {}))}")
        
        # Test 2: Status del sistema (sin autenticación)
        response = requests.get(f"{base_url}/api/liga-mx/status")
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"   - Estado: {status['data'].get('estado')}")
            print(f"   - Equipos: {status['data']['estadisticas'].get('equipos')}")
        
        # Test 3: Intentar acceder a tabla (sin API key - debe fallar)
        response = requests.get(f"{base_url}/api/liga-mx/tabla")
        print(f"🏆 Tabla (sin auth): {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Autenticación funcionando correctamente")
        
        print("\n✅ Pruebas básicas completadas")
        print("📝 Para usar la API necesitas:")
        print("   1. Loguearte como admin en el panel")
        print("   2. Generar tu API key personal")
        print("   3. Usar la API key en el header: Authorization: Bearer YOUR_KEY")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    test_liga_mx_api()