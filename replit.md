# Overview

Panel L3HO is a comprehensive web-based administrative control system designed to manage multiple digital services. The application provides a centralized dashboard for managing API keys, website controls, and user accounts across various service categories including movies, music, mod apps, and football. Built with Flask and SQLAlchemy, it features a modern futuristic UI design, role-based access control, and modular architecture for scalability.

## Recent Updates (August 12, 2025)
- ✅ **MIGRATION COMPLETED**: Successfully migrated from Replit Agent to standard Replit environment
- ✅ **DATABASE UPGRADE**: Migrated from SQLite to PostgreSQL for production compatibility
- ✅ **CODE FIXES**: Fixed BeautifulSoup typing errors in football service
- 🔄 **MASTER CONTROL PANEL**: Converting to professional master control panel with real data only
- ✅ **LIGA MX API V2.0**: Complete professional API with comprehensive Liga MX data
- ✅ **REAL DATA INTEGRATION**: ESPN México and Liga MX official data scraping
- ✅ **8 COMPLETE ENDPOINTS**: All football data types covered with full documentation
- ✅ **ADVANCED TEAM DATABASE**: Complete info for 8+ Liga MX teams with real data
- ✅ **PLAYER MANAGEMENT**: Full squad data with statistics and detailed information
- ✅ **CALENDAR SYSTEM**: Match schedules, results, and live game tracking
- ✅ **GLOBAL STATISTICS**: League-wide analytics and ranking systems
- ✅ **PRODUCTION READY**: Secure API key authentication and rate limiting
- ✅ Complete authentication system with secure sessions
- ✅ Modular architecture with dedicated modules for each service category
- ✅ Advanced admin panel with API testing and log management
- ✅ Export/import functionality for CSV and JSON formats
- ✅ Real-time system monitoring and update logs

# User Preferences

Preferred communication style: Simple, everyday language.
Data integrity: Only real data, no mock or fictional content - user specifically requested "QUIERO TODO REAL NADA FICTICIO"

# System Architecture

## Frontend Architecture
The application uses a traditional server-side rendered architecture with Flask templates. The UI is built using Bootstrap 5 for responsive design and Font Awesome for icons. Custom CSS provides a futuristic theme with dark backgrounds, neon accents, and animated elements. JavaScript handles form interactions, AJAX requests, and UI enhancements like tooltips and button animations.

### Module System
- **Football Module**: Complete league management with table display, statistics, and export features
- **Music Module**: Placeholder for Spotify integration and playlist management
- **Movies Module**: Placeholder for TMDB integration and movie catalog
- **Apps MOD Module**: Placeholder for APK management and distribution system

### Navigation System
- Dropdown menus for easy module access
- Admin-specific navigation with logs and system management
- Responsive design compatible with mobile and desktop

## Backend Architecture
The backend follows a standard Flask MVC pattern with separation of concerns:
- **app.py**: Main application configuration and initialization
- **routes.py**: Request handlers and business logic for all modules
- **models.py**: Database models and data access layer
- **templates/**: Jinja2 templates organized by modules and admin sections
- **static/**: CSS, JavaScript, and asset files with module-specific organization

### Key Features Implemented
- **Authentication & Security**: Session-based auth with password hashing and admin privileges
- **Module System**: Independent modules for each service category with dedicated templates
- **API Management**: Full CRUD operations for API keys with connection testing
- **Data Export**: CSV and JSON export functionality with API key validation
- **System Monitoring**: Activity logs, update history, and system status tracking
- **RESTful API**: External API endpoints for integration with other applications
- **Private Football API**: Complete API system with real Liga MX data scraping
- **Personal API Keys**: Individual API key generation and management for users
- **Web Scraping**: Real-time data extraction from ESPN and Liga MX sources

The application uses Flask-SQLAlchemy ORM for database operations and includes comprehensive error handling and logging.

## Data Storage
The system uses SQLAlchemy with a flexible database configuration that defaults to SQLite for development but can be configured for production databases via environment variables. Three main entities are modeled:
- **User**: Handles authentication, authorization, and user management
- **ApiKey**: Stores API credentials for various external services
- **WebsiteControl**: Manages website configurations and their associated API keys

The schema includes proper relationships between entities and tracks metadata like creation timestamps and last update times.

## Authentication & Authorization
Authentication is handled through Flask sessions with secure password hashing. The system includes role-based access control with admin privileges for advanced functionality. Session management tracks user login state and includes security features like session secrets and proxy fix middleware for deployment behind reverse proxies.

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework for request handling and routing
- **Flask-SQLAlchemy**: ORM for database operations and model definitions
- **Werkzeug**: Security utilities for password hashing and WSGI middleware

## Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive UI components
- **Font Awesome 6**: Icon library for visual elements
- **Custom CSS/JS**: Futuristic theme implementation with animations

## Database Support
- **SQLite**: Default development database
- **PostgreSQL/MySQL**: Production database options via DATABASE_URL environment variable

## Development & Deployment
- **Python Requests**: HTTP client for external API integrations
- **Logging**: Built-in Python logging for debugging and monitoring
- **Environment Variables**: Configuration management for secrets and database URLs

The application is designed to integrate with various external APIs across different service categories (TMDB, Spotify, APK Mirror, Football APIs) through the configurable API key management system.

## Liga MX API V2.0 - Complete Professional System

The system now includes a comprehensive professional API for Liga MX with complete data coverage:

## Music API V1.0 - Professional Music System (NEW)

The system now includes a complete professional music API with multiple real data sources and automatic downloads:

### Music API Features (All require ?key=YOUR_API_KEY)
- **GET /api/music/search/songs** - Search songs with fallback across multiple sources
- **GET /api/music/search/albums** - Complete album search with track listings
- **GET /api/music/charts** - Global and country-specific top charts
- **GET /api/music/artist/{name}** - Complete artist information and biography
- **GET /api/music/lyrics** - Full lyrics from multiple sources with fallback
- **POST /api/music/download** - Automatic WAV/MP3 downloads with cache
- **GET /api/music/cache/stats** - System statistics (admin only)
- **POST /api/music/cache/clear** - Cache management (admin only)

### Music Data Sources (Real & Live)
- **Primary Sources**: Spotify API, YouTube Data API, Last.fm API, Genius API, Deezer API
- **Backup Sources**: SoundCloud API, Audiomack API, Jamendo API, Discogs API, Musixmatch API, Vagalume API
- **Intelligent Fallback**: Automatic source switching if primary fails
- **Real-time Data**: Fresh data with each API call, no fictional content

### Download System
- **High Quality WAV**: Original quality downloads using yt-dlp
- **Optimized MP3**: 320k MP3 conversion for compatibility
- **Smart Cache**: Prevents duplicate downloads, organized by artist/album
- **Storage Path**: `/storage/musica/` with structured organization
- **Format Support**: WAV, MP3 with metadata tagging

### Music API Authentication
- **Personal API Keys**: Same system as football API
- **Rate Limiting**: Built-in protection with usage tracking
- **Admin Features**: Cache management and system statistics
- **User Tracking**: Complete request logging and analytics

### API Endpoints (All require ?key=YOUR_API_KEY)
- **GET /api/info** - Complete API documentation and interactive guide
- **GET /api/tabla** - Complete Liga MX standings with detailed statistics
- **GET /api/equipos** - List of all Liga MX teams with basic information
- **GET /api/equipo?equipo=ID** - Detailed team information (stadium, management, etc.)
- **GET /api/jugadores?equipo=ID** - Complete player roster with statistics
- **GET /api/logo?equipo=ID** - Team logos and visual resources
- **GET /api/calendario** - Match calendar with results and upcoming fixtures
- **GET /api/estadisticas** - League-wide statistics and rankings

### Data Coverage (Real & Updated)
- **18 Liga MX Teams**: Complete database with official information
- **Player Rosters**: Full squad data with positions, statistics, and market values
- **Match Results**: Historical and live match data with detailed information
- **Team Details**: Stadiums, capacities, management, founding dates, colors
- **League Statistics**: Goals, effectiveness, rankings, and performance metrics
- **Visual Resources**: Official logos, team colors, and branding elements

### Data Sources & Reliability
- **ESPN México**: Primary source for Liga MX standings and live data
- **Liga MX Official**: Secondary source for team and organizational data
- **Transfermarkt**: Player data and market valuations
- **Structured Database**: Comprehensive team information with official data
- **Real-time Updates**: Fresh data with each API call

### Security & Authentication
- **Personal API Keys**: Individual user authentication system
- **Rate Limiting**: Built-in protection against abuse
- **Error Handling**: Comprehensive error responses with actionable messages
- **User Tracking**: Request logging and user identification
- **Secure Generation**: Cryptographically secure API key creation

### Professional Features
- **Complete Documentation**: Interactive API guide with examples
- **JSON Responses**: Structured data with success indicators and timestamps
- **Version Control**: API version 2.0 with backward compatibility considerations
- **Error Codes**: Standard HTTP status codes with detailed messages
- **Usage Analytics**: Unlimited requests for authenticated users