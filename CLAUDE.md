# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ClassroomAI is a Django-based intelligent course management system that integrates Google Classroom API and LINE Bot services. It provides course management, homework tracking, note organization, and calendar synchronization features.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Testing
```bash
# Run all tests
python manage.py test

# Test specific apps
python manage.py test user
python manage.py test course  
python manage.py test line_bot
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## Architecture Overview

### Django Apps Structure
- **classroomai/**: Main project settings and configuration
- **user/**: User authentication and profile management
- **course/**: Course management, homework, and student API
- **line_bot/**: LINE Bot integration with middleware and flex templates

### Key Technologies
- **Django 5.2+** with Django REST Framework
- **MySQL** database with utf8mb4 encoding
- **LINE Bot SDK** for messaging integration
- **Google APIs** (Classroom, Calendar, OAuth)
- **CORS headers** for cross-origin requests

### Environment Variables
Required `.env` file variables:
- Database: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Django: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `ALLOWED_HOSTS`
- Google: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- LINE: `CHANNEL_SECRET`, `CHANNEL_TOKEN`, `LINE_CHANNEL_ID`, `VITE_LIFF_ID`
- Other: `N8N_NLP_URL`, `INTERNAL_API_TOKEN`

### API Structure
- Authentication: `/api/oauth/` endpoints
- Course management: `/api/classrooms/` endpoints  
- Homework: `/api/homework/` endpoints
- Student data: `/api/student/` and `/api/course/students/` endpoints

### Key Files
- `classroomai/settings.py`: Main configuration with environment variables
- `user/models.py`: User and authentication models
- `course/models.py`: Course, homework, and student models
- `line_bot/views.py`: LINE Bot webhook handling
- `line_bot/middleware.py`: Custom LINE role middleware

### Logging
- General logs: `logs/django.log`
- Error logs: `logs/django_errors.log`
- Configured in `settings.py:LOGGING`

## Development Notes
- Uses Chinese language (`zh-hant`) and Taipei timezone (`Asia/Taipei`)
- Requires MySQL database with proper permissions
- LINE Bot webhook must be configured with proper URL
- Google OAuth credentials must be set up in Google Cloud Console
- Environment variables must be configured in `.env` file