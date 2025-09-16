# ClassroomAI Project Overview

This directory contains the backend API for the ClassroomAI project. It's a Django-based application that integrates with Google Classroom, Google Calendar, and LINE Bot services.

## Key Technologies

- Python 3.8+
- Django 4.2
- Django REST Framework 3.15
- MySQL 8.0
- Google APIs (Classroom, Calendar)
- LINE Bot SDK

## Project Structure

The main project code is located in the `classroomai` directory:

```
classroomai/
├── classroomai/          # Main Django project settings and URL configuration
├── user/                 # User registration, authentication, and profile management
├── course/               # Course, homework, note, and calendar management
├── line_bot/             # LINE Bot integration (webhooks, messaging, group bindings)
├── api_v2/               # Enhanced API functionality (newer version)
├── templates/            # HTML templates (e.g., post-OAuth success page)
├── logs/                 # Application logs (django.log, django_errors.log)
├── requirements.txt      # Python dependencies
├── manage.py             # Django management script
└── .env                  # Environment variables (not in repo, needs to be created)
```

## Core Functionality

1.  **User & Registration**:
    - Pre-registration via LINE LIFF
    - Google OAuth 2.0 integration for Classroom/Calendar permissions
    - User profile management

2.  **Course & Homework Management**:
    - Create/list courses in Google Classroom
    - Create/update/delete homework assignments
    - Fetch homework lists and submission statistics

3.  **Student Notes**:
    - Create/query/update/delete student notes
    - Automatic course classification for notes
    - Search and pagination support

4.  **Google Calendar Integration**:
    - Create/update/delete/query calendar events
    - Manage event attendees

5.  **LINE Bot Integration**:
    - Webhook handling for LINE messages
    - Course binding via group codes
    - AI response push notifications
    - Flex message template rendering

## Setup & Running

1.  **Environment Setup**:
    - Create a virtual environment: `python -m venv venv`
    - Activate it:
        - Windows: `venv\Scripts\activate`
        - macOS/Linux: `source venv/bin/activate`
    - Install dependencies: `pip install -r requirements.txt`

2.  **Environment Variables**:
    - Create a `.env` file in the `classroomai` directory with necessary variables (see `settings.py` for required keys).

3.  **Database Migration**:
    - Run migrations: `python manage.py migrate`

4.  **Running the Server**:
    - Start the development server: `python manage.py runserver`

## API Documentation

Detailed API documentation is available in `classroomai/README.md`. It includes endpoint specifications, request/response formats, and authentication details.

## Testing

Run tests using Django's test runner:
- All tests: `python manage.py test`
- App-specific tests: `python manage.py test user`, `python manage.py test course`, `python manage.py test line_bot`