# Overview

Panel L3HO is a web-based administrative control system for managing various digital services including movies, music, mod apps, and football. It centralizes the management of API keys, website controls, and user accounts. Built with Flask and SQLAlchemy, it features a modern, futuristic UI, role-based access control, and a modular architecture for scalability. The project aims to provide a professional master control panel with real-time data integration, including a comprehensive Liga MX API and a robust music system with advanced scraping capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.
Data integrity: Only real data, no mock or fictional content - user specifically requested "QUIERO TODO REAL NADA FICTICIO".

# System Architecture

## Frontend Architecture
The application uses a server-side rendered architecture with Flask templates, Bootstrap 5 for responsiveness, and Font Awesome for icons. Custom CSS provides a futuristic dark theme with neon accents and animations. JavaScript handles interactions and UI enhancements.

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
- **Liga MX Data**: ESPN México, Liga MX Official, Transfermarkt (for player data).
- **Music Data**: Spotify API, YouTube Data API, Last.fm API, Genius API, Deezer API, SoundCloud API, Audiomack API, Jamendo API, Discogs API, Musixmatch API, Vagalume API (for music and lyrics).
- **Download System**: `yt-dlp` for audio downloads.
- **General APIs**: Placeholder integrations for TMDB (movies) and APK Mirror (mod apps).