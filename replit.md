# Overview

Panel L3HO is a professional web-based administrative control system for managing digital services including football (Liga MX), movies, music, and modified apps. Built with Flask and PostgreSQL, it features a completely redesigned modern UI using TailwindCSS, centralized API key management, and comprehensive real-time data integration. The system includes a fully integrated Liga MX API with REAL data from the current Apertura 2025 season (Jornada 4, updated August 14, 2025), multi-source scraping from Mexican official sources, interactive dashboards with charts and tables, and modular architecture optimized for both Replit and Termux environments.

# User Preferences

Preferred communication style: Simple, everyday language.
Data integrity: Only real data, no mock or fictional content - user specifically requested "QUIERO TODO REAL NADA FICTICIO".
API Key Management: Single centralized API key system without usage limits for personal/professional use.
Design requirements: Modern, clean, responsive interface using TailwindCSS with sidebar navigation.
Data sources: Multiple Liga MX sources including ESPN, Mediotiempo, Liga MX oficial, SofaScore, FlashScore, OneFootball.

# System Architecture

## Frontend Architecture
The application uses a modern server-side rendered architecture with Flask templates and TailwindCSS for professional, responsive design. Features include interactive charts via Chart.js, dynamic tables, and a clean sidebar navigation. The UI is optimized for both desktop and mobile with dark/light theme support and smooth animations.

### Module System
The system is modular, supporting:
- **Football Module**: League management, statistics, and export.
- **Music Module**: Integration for music services and playlist management.
- **Movies Module**: Integration for movie catalogs.
- **Apps MOD Module**: Management and distribution system for APKs.

## Backend Architecture
The backend follows a Flask MVC pattern:
- **Core Logic**: `app.py` for configuration, `routes.py` for request handling, `models.py` for database models.
- **Templates & Static Assets**: Organized in `templates/` and `static/` directories.

### Key Features
- **Authentication & Security**: Session-based authentication with password hashing and role-based access control.
- **API Management**: CRUD operations for API keys with connection testing.
- **Data Export**: CSV and JSON export functionality.
- **System Monitoring**: Activity logs and status tracking.
- **RESTful APIs**: Internal and external API endpoints, including a private Liga MX API and a music API.
- **Web Scraping**: Real-time data extraction from sources like ESPN and Liga MX.
- **Centralized API Management**: Unified interface for all API keys, categorized by service, with visible endpoints and integrated testing.
- **Professional Scraping System**: Primary data source with intelligent fallback to official APIs, supporting direct extraction from YouTube Music, SoundCloud, Jamendo, Audiomack, Bandcamp, Musixmatch, and Vagalume.

## Data Storage
Utilizes SQLAlchemy, supporting SQLite for development and PostgreSQL/MySQL for production. Key entities include User, ApiKey, and WebsiteControl, with defined relationships and metadata tracking.

## Authentication & Authorization
Uses Flask sessions with secure password hashing and role-based access control for administrative functions.

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework.
- **Flask-SQLAlchemy**: ORM for database operations.
- **Werkzeug**: Security utilities.

## Frontend Dependencies
- **Bootstrap 5**: Responsive UI framework.
- **Font Awesome 6**: Icon library.

## Database Support
- **SQLite**: Development database.
- **PostgreSQL/MySQL**: Production database options.

## Development & Deployment
- **Python Requests**: HTTP client.
- **Logging**: Python's built-in logging.
- **Environment Variables**: Configuration management.

## Integrated External Services
- **Liga MX Data**: Multi-source scraping from ligamx.net, ESPN México, Futbol Total, Mediotiempo, SofaScore, FlashScore, and OneFootball for comprehensive Liga MX coverage.
- **Music Data**: Spotify API, YouTube Data API, Last.fm API, Genius API, Deezer API, SoundCloud API, Audiomack API, Jamendo API, Discogs API, Musixmatch API, Vagalume API.
- **Movies Data**: TMDB API integration for movie catalogs and metadata.
- **Apps MOD**: APK Mirror integration for modified applications management.
- **Automated Updates**: Scheduled data refresh system for real-time information.