# Library Management System

A simple, production-ready Library Management System built with Django, HTMX, and vanilla CSS.

## Features

- **Author Management** - Full CRUD operations for authors
- **Book Management** - Full CRUD operations for books
- **Search** - Search authors by name, books by title or author
- **Sorting** - Sort books by title, publication year, or author
- **Validations** - Server-side form validations (required fields, unique constraints, year limits)
- **HTMX** - Dynamic form submissions and list updates without full page reloads
- **Django Admin** - Customized admin panel with search, filters, and ordering
- **Responsive Design** - Clean, minimal UI that works on all screen sizes
- **Supabase Ready** - PostgreSQL configuration included for easy migration

## Tech Stack

- Python 3.x
- Django 5.1
- SQLite (default)
- PostgreSQL / Supabase (configured)
- HTMX 2.0
- HTML5
- Custom CSS (no frameworks)

## Installation Steps

### 1. Clone the repository

```bash
git clone <repository-url>
cd django-library
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your `DJANGO_SECRET_KEY`.

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Supabase Migration Guide

1. Create a new project on [Supabase](https://supabase.com)
2. Go to **Settings > Database** and copy your connection details
3. Update your `.env` file:

```env
DB_NAME=postgres
DB_USER=your-supabase-user
DB_PASSWORD=your-supabase-password
DB_HOST=db.your-project.supabase.co
DB_PORT=5432
```

4. In `library_system/settings.py`, uncomment the PostgreSQL `DATABASES` configuration and comment out the SQLite one
5. Run migrations:

```bash
python manage.py migrate
```

## Folder Structure

```
django-library/
├── library/                    # Main app
│   ├── migrations/             # Database migrations
│   ├── templates/
│   │   ├── 404.html            # Custom 404 page
│   │   └── library/
│   │       ├── base.html       # Base template
│   │       ├── home.html       # Home page
│   │       ├── author_list.html
│   │       ├── author_detail.html
│   │       ├── author_form.html
│   │       ├── author_confirm_delete.html
│   │       ├── book_list.html
│   │       ├── book_detail.html
│   │       ├── book_form.html
│   │       ├── book_confirm_delete.html
│   │       └── partials/       # HTMX partials
│   │           ├── author_row.html
│   │           ├── author_form.html
│   │           ├── book_row.html
│   │           └── book_form.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── library_system/             # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   └── css/
│       └── style.css
├── templates/                  # Project-level templates
├── .env                        # Environment variables
├── .env.example
├── .gitignore
├── db.sqlite3
├── manage.py
├── README.md
└── requirements.txt
```

## Future Improvements

- User authentication and role-based access control
- Book borrowing/returning system with due dates
- Fine calculation for overdue books
- Book cover image upload
- Pagination for large lists
- API endpoints (DRF)
- Unit and integration tests
- Docker support
- CI/CD pipeline

## License

MIT
