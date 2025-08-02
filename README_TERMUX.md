# Panel L3HO - Guía de Instalación para Termux

## Descripción
Panel L3HO es un sistema de gestión avanzado con APIs privadas de fútbol y transmisiones en vivo, optimizado para ejecutarse en Termux (Android).

## Características Principales
- **API de Fútbol Liga MX**: Datos históricos, estadísticas, plantillas completas
- **API de Transmisiones en Vivo**: Partidos en tiempo real, marcadores, eventos
- **Dual API System**: Claves API separadas e independientes
- **Panel de Administración**: Gestión completa desde interfaz web
- **Optimizado para Termux**: Compatible con Android/Termux

## Instalación Rápida

### 1. Preparar Termux
```bash
# Actualizar Termux
pkg update && pkg upgrade -y

# Instalar dependencias básicas
pkg install python git curl wget
```

### 2. Clonar o Descargar el Proyecto
```bash
# Si tienes git
git clone [URL_DEL_PROYECTO]
cd panel-l3ho

# O descargar archivos manualmente
```

### 3. Ejecutar Script de Instalación
```bash
# Hacer ejecutable el script
chmod +x run.sh

# Instalar y ejecutar
./run.sh
```

### 4. Ejecutar Manualmente (Alternativo)
```bash
# Instalar dependencias
pip install Flask Flask-SQLAlchemy requests beautifulsoup4 lxml trafilatura

# Ejecutar aplicación
python main.py
```

## Acceso a la Aplicación

### Local (en el mismo dispositivo)
- URL: `http://localhost:5000`
- Usuario: `admin`
- Contraseña: `admin123`

### Red Local (desde otros dispositivos)
1. Obtener la IP del dispositivo Android:
```bash
ifconfig | grep "inet "
```
2. Acceder desde otro dispositivo: `http://[IP_ANDROID]:5000`

## APIs Disponibles

### API de Fútbol (Liga MX)
**Base URL**: `http://localhost:5000/api/`
**Autenticación**: `?key=TU_API_KEY_FUTBOL`

**Endpoints:**
- `/api/info` - Documentación completa
- `/api/tabla` - Tabla de posiciones Liga MX
- `/api/equipos` - Lista de todos los equipos
- `/api/equipo?equipo=america` - Información detallada de equipo
- `/api/jugadores?equipo=chivas` - Plantilla de jugadores
- `/api/logo?equipo=pumas` - Logos y recursos visuales
- `/api/calendario` - Calendario de partidos
- `/api/estadisticas` - Estadísticas globales

### API de Transmisiones en Vivo
**Base URL**: `http://localhost:5000/api/transmisiones/`
**Autenticación**: `?key=TU_API_KEY_TRANSMISIONES`

**Endpoints:**
- `/api/transmisiones/info` - Documentación de transmisiones
- `/api/transmisiones` - Partidos en vivo
- `/api/transmisiones/detalle?id=PARTIDO_ID` - Detalles completos

### Ejemplo de Uso
```bash
# Obtener tabla de Liga MX
curl "http://localhost:5000/api/tabla?key=TU_API_KEY"

# Partidos en vivo
curl "http://localhost:5000/api/transmisiones?key=TU_API_KEY_TRANSMISIONES"
```

## Obtener Claves API

1. Acceder al panel: `http://localhost:5000`
2. Iniciar sesión con `admin` / `admin123`
3. En el dashboard verás la sección "Mis Claves API Privadas"
4. Copiar las claves para usar en tus solicitudes

## Configuración Avanzada

### Variables de Entorno
```bash
export SESSION_SECRET="tu_clave_secreta"
export DATABASE_URL="sqlite:///panel_l3ho.db"  # Para SQLite
export FLASK_ENV="production"                   # Para producción
```

### Ejecutar en Segundo Plano
```bash
# Con nohup
nohup python main.py &

# Con gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 --daemon main:app
```

## Solución de Problemas

### Error de Dependencias
```bash
# Reinstalar dependencias
pip install --upgrade pip
pip install --force-reinstall Flask requests beautifulsoup4
```

### Problemas de Red
```bash
# Verificar que el puerto 5000 esté libre
netstat -tuln | grep 5000

# Ejecutar en puerto diferente
export PORT=8080
python main.py
```

### Error de Permisos
```bash
# Dar permisos al script
chmod +x run.sh

# Verificar permisos de archivos
ls -la *.py
```

## Fuentes de Datos

### API de Fútbol
- **ESPN México**: Tabla de posiciones y estadísticas
- **Liga MX Oficial**: Información de equipos y jugadores
- **Transfermarkt**: Datos de mercado y valuaciones
- **Datos Estructurados**: Información completa de estadios y directivas

### API de Transmisiones
- **ESPN México (En Vivo)**: Partidos en tiempo real
- **Liga MX Oficial**: Resultados en vivo
- **OneFootball**: Datos complementarios
- **Google Sports**: Información de partidos

## Características Técnicas

- **Framework**: Flask 3.0 + SQLAlchemy
- **Base de Datos**: SQLite (por defecto) / PostgreSQL (opcional)
- **Web Scraping**: BeautifulSoup4 + lxml + trafilatura
- **Autenticación**: Claves API únicas por usuario
- **Compatibilidad**: Termux (Android), Linux, macOS, Windows

## Soporte y Desarrollo

Este es un proyecto privado desarrollado específicamente para uso personal.
Las APIs proporcionan datos reales obtenidos de fuentes oficiales y confiables.

### Estructura del Proyecto
```
panel-l3ho/
├── main.py              # Punto de entrada
├── app.py               # Configuración de Flask
├── routes.py            # Rutas y endpoints
├── models.py            # Modelos de base de datos
├── services/            # Servicios de scraping
│   ├── futbol.py        # API de fútbol
│   └── transmisiones.py # API de transmisiones
├── templates/           # Plantillas HTML
├── static/              # CSS, JS, assets
├── run.sh               # Script de instalación
└── README_TERMUX.md     # Esta documentación
```

¡Disfruta usando Panel L3HO en Termux! 🚀