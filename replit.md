# Overview

Panel L3HO is a comprehensive web-based administrative control system designed to manage multiple digital services. The application provides a centralized dashboard for managing API keys, website controls, and user accounts across various service categories including movies, music, mod apps, and football. Built with Flask and SQLAlchemy, it features a modern futuristic UI design, role-based access control, and modular architecture for scalability.

## Recent Updates (July 31, 2025)
- ✅ Complete authentication system with secure sessions
- ✅ Modular architecture with dedicated modules for each service category
- ✅ Football module with league tables, statistics, and data export functionality
- ✅ Advanced admin panel with API testing and log management
- ✅ RESTful API endpoints with API key validation for external integrations
- ✅ Export/import functionality for CSV and JSON formats
- ✅ Real-time system monitoring and update logs

# User Preferences

Preferred communication style: Simple, everyday language.

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