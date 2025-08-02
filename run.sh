#!/bin/bash

# Panel L3HO - Script de inicialización para Termux
# Este script instala dependencias y ejecuta la aplicación

echo "=========================================="
echo "Panel L3HO - Iniciando en Termux"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[INFO]${NC} Verificando dependencias..."

# Verificar si Python está instalado
if ! command -v python &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python no está instalado"
    echo -e "${YELLOW}[INSTALL]${NC} Instala Python con: pkg install python"
    exit 1
fi

# Verificar si pip está disponible
if ! command -v pip &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} pip no está disponible"
    echo -e "${YELLOW}[INSTALL]${NC} Instala pip con: pkg install python-pip"
    exit 1
fi

# Instalar dependencias de sistema necesarias para Termux
echo -e "${BLUE}[INFO]${NC} Instalando dependencias del sistema..."
pkg update -y
pkg install -y libxml2 libxslt libjpeg-turbo libpng zlib

# Instalar dependencias de Python
echo -e "${BLUE}[INFO]${NC} Instalando dependencias de Python..."
pip install --upgrade pip

# Lista de dependencias optimizadas para Termux
pip install Flask==3.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install Werkzeug==3.0.1
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
pip install trafilatura==1.6.4
pip install gunicorn==21.2.0

# Nota: psycopg2-binary puede requerir compilación en Termux
echo -e "${YELLOW}[WARNING]${NC} Intentando instalar soporte para PostgreSQL..."
pip install psycopg2-binary || echo -e "${YELLOW}[WARNING]${NC} PostgreSQL no disponible - usando SQLite"

# Configurar variables de entorno para Termux
export FLASK_APP=main.py
export FLASK_ENV=development
export SESSION_SECRET="termux_panel_l3ho_secret_key_2025"

# Para SQLite en Termux (fallback si PostgreSQL no está disponible)
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="sqlite:///panel_l3ho_termux.db"
    echo -e "${YELLOW}[INFO]${NC} Usando SQLite: panel_l3ho_termux.db"
fi

echo -e "${GREEN}[SUCCESS]${NC} Dependencias instaladas correctamente"
echo -e "${BLUE}[INFO]${NC} Iniciando Panel L3HO..."

# Crear directorio de logs si no existe
mkdir -p logs

# Ejecutar la aplicación
echo -e "${GREEN}[STARTING]${NC} Panel L3HO ejecutándose en http://localhost:5000"
echo -e "${YELLOW}[TIP]${NC} Para acceder desde otro dispositivo en la red local, usa la IP de tu dispositivo"
echo -e "${YELLOW}[TIP]${NC} Credenciales por defecto: admin / admin123"
echo ""

# Opción de ejecución: simple o con gunicorn
if [ "$1" = "simple" ]; then
    echo -e "${BLUE}[MODE]${NC} Ejecutando en modo simple (desarrollo)"
    python main.py
else
    echo -e "${BLUE}[MODE]${NC} Ejecutando con gunicorn (producción)"
    gunicorn --bind 0.0.0.0:5000 --workers 2 --reload main:app
fi