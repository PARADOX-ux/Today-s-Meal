# Aaj Kya Banaye? - Indian Vegetarian Recipe Suggestion App

## Overview

This is a Flask-based web application that helps Indian users decide what to cook by suggesting vegetarian dishes based on available ingredients. The app uses AI-powered cooking instructions through OpenAI's GPT-4o model and provides a mobile-friendly interface with Indian-themed styling.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology Stack**: HTML5, TailwindCSS (via CDN), Vanilla JavaScript
- **Design Pattern**: Server-side rendered templates with client-side interactivity
- **Styling**: Custom Tailwind configuration with Indian color themes (saffron, green tones)
- **Responsiveness**: Mobile-first responsive design using TailwindCSS utilities

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: Simple MVC pattern with route handlers, template rendering, and JSON data storage
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python's built-in logging module for debugging

### Data Storage Solutions
- **Primary Database**: PostgreSQL with SQLAlchemy ORM for all recipe data
- **Recipe Storage**: Normalized database schema with separate tables for recipes, ingredients, steps, tags, and user favorites
- **Session Management**: Flask sessions with database-backed user tracking
- **User Favorites**: Server-side favorites storage with user session association
- **Data Migration**: Automated migration from JSON to PostgreSQL database completed

## Key Components

### Core Flask Application (`app.py`)
- **Recipe Loading**: JSON file parsing with error handling
- **Matching Algorithm**: Ingredient comparison logic with percentage calculation
- **Route Handlers**: Main application endpoints
- **Session Management**: User state persistence

### AI Integration (`openai_helper.py`)
- **OpenAI Client**: Integration with GPT-4o model
- **Prompt Engineering**: Specialized prompts for Indian cooking instructions
- **Response Formatting**: Structured JSON responses with cooking steps, tips, and cultural context
- **Error Handling**: API call failure management

### Database Schema (`models.py`)
- **Recipe Model**: Core recipe information with relationships to ingredients, steps, tags, and favorites
- **Ingredient Model**: Normalized ingredient storage with many-to-many recipe relationships
- **Recipe Steps**: Ordered cooking instructions with step numbers
- **Tags System**: Dietary preferences and recipe categories (Jain, Satvik, Quick, Healthy, etc.)
- **User Favorites**: Session-based user tracking with favorite recipe associations
- **Data Integrity**: Foreign key constraints and unique constraints for data consistency

### Frontend Components (`templates/index.html`, `static/script.js`)
- **Ingredient Selection**: Multi-select checkboxes and manual input with database-driven ingredient list
- **Recipe Display**: Card-based layout with match percentages and real-time favorite status
- **Interactive Features**: Server-side favorites functionality, filtering options, persistent user sessions
- **UI Components**: Responsive design with Indian cultural elements and database-backed interactions

## Data Flow

1. **User Input**: Users select ingredients via checkboxes or manual input loaded from database
2. **Recipe Matching**: Backend queries PostgreSQL database and calculates ingredient match percentages
3. **Result Filtering**: Database queries filter recipes by match percentage and user dietary preferences
4. **Favorites Management**: Server-side favorites storage with session-based user tracking
5. **AI Enhancement**: When user selects "Cook This", GPT-4o generates detailed instructions
6. **Response Delivery**: Structured cooking instructions returned with cultural context and tips

## External Dependencies

### Required APIs
- **OpenAI API**: GPT-4o model for generating cooking instructions
- **Environment Variable**: `OPENAI_API_KEY` for authentication

### CDN Dependencies
- **TailwindCSS**: Frontend styling framework
- **Font Awesome**: Icon library for UI elements

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM for database operations
- **psycopg2-binary**: PostgreSQL database adapter
- **OpenAI**: API client library
- **Standard Library**: json, logging, os, uuid modules

## Deployment Strategy

### Environment Configuration
- **Development**: Uses fallback values for missing environment variables
- **Production**: Requires proper `SESSION_SECRET` and `OPENAI_API_KEY` configuration
- **File Structure**: Simple flat structure suitable for Replit deployment

### Replit Compatibility
- **Entry Point**: `main.py` imports the Flask app
- **Static Assets**: Organized in standard Flask structure (`static/`, `templates/`)
- **Database Integration**: PostgreSQL database automatically created and configured
- **Environment Variables**: Configured through Replit's environment variable system
- **Data Migration**: `migrate_data.py` script for initial database population

### Scalability Considerations
- **Database Architecture**: PostgreSQL with proper indexing and normalized schema for optimal performance
- **Concurrent Users**: Database-backed architecture supports multiple simultaneous users
- **Session Management**: Server-side user tracking with database persistence
- **Query Optimization**: SQLAlchemy ORM with optimized queries for recipe matching and filtering
- **Future Enhancements**: Could add database connection pooling and caching for higher traffic

### Security Features
- **Session Secret**: Configurable secret key for session security
- **Input Validation**: Basic input sanitization for ingredient matching
- **API Key Management**: Environment variable-based API key storage