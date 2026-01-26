# Place Reviews API

## Setup
1. Create virtual environment - 
2. pip install -r requirements.txt
3. Configure PostgreSQL
4. python manage.py migrate
5. python scripts/populate_data.py
6. python manage.py runserver

## Authentication
- JWT-based authentication
- Use Bearer token

## Key APIs
- POST /api/users/register/
- POST /api/users/login/
- GET /api/places/search/
- GET /api/places/<id>/

## Features
- Search places by name
- Filter by minimum rating
- Paginated results
- JWT authentication
