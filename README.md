# برنامه هفتگی کلاس‌ها

A simple, modern weekly class schedule built with **Django**, **Tailwind CSS**,
**PostgreSQL** and **Docker**. The public homepage is fully **Persian and RTL**
and shows the whole week at a glance, today's classes, and a clean mobile
day-by-day view with light/dark themes.

Classes are created, edited and deleted directly from the homepage — no Django
admin interaction is required for normal use.

> کلاس‌ها از صفحه اصلی برنامه ثبت و مدیریت می‌شوند و استفاده از پنل مدیریت Django برای استفاده روزمره ضروری نیست.

## Requirements

Only **Docker** and **Docker Compose** are required. Python, PostgreSQL and
Node.js do **not** need to be installed on the host — Tailwind is compiled
during the image build.

## Start

```bash
docker compose up --build
```

Then open http://localhost:8000.

## Stop

```bash
docker compose down
```

The database lives in a named Docker volume (`postgres_data`) and survives
`docker compose down`. Do **not** use `docker compose down -v` unless you
intentionally want to delete all data.

## Environment

Optional: copy `.env.example` to `.env` and adjust values. Sensible development
defaults are used when `.env` is absent.

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_DEBUG` | `1` for development, `0` for production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Database credentials |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Database address |

## Migrations

Migrations run automatically on container start. To run them manually:

```bash
docker compose exec web python manage.py migrate
```

## Managing classes from the homepage

1. Open http://localhost:8000.
2. Pick a day and click **افزودن کلاس** (or use the button inside each mobile day).
3. Fill in the modal form and submit; the class is saved to PostgreSQL.
4. Use **ویرایش** / **حذف** on any class card to edit or delete it.

All writes use Django `ModelForm` validation and POST/Redirect/GET, and the
currently viewed week is preserved after every action.

## Create an admin user (optional)

The Django admin remains available for technical administration, but it is not
part of the normal workflow.

```bash
docker compose exec web python manage.py createsuperuser
```

Then sign in at http://localhost:8000/admin.

## Load demo data

```bash
docker compose exec web python manage.py seed_demo
```

Use `--reset` to delete existing classes first:

```bash
docker compose exec web python manage.py seed_demo --reset
```

## Run tests

```bash
docker compose exec web python manage.py test
```

## Project layout

```text
config/                 Django project settings and URLs
schedules/              App: models, forms, admin, views, tests, seed_demo
  utils.py              Week math + dependency-free Jalali date helpers
  templatetags/         Persian digit / Jalali template filters
templates/              base.html + schedules/ templates and components
static/                 Tailwind source (src/), compiled CSS, and app.js
Dockerfile              Multi-stage: Tailwind build + Python runtime
docker-compose.yml      web + db services
docker-compose.prod.yml Optional production override (Gunicorn, WhiteNoise)
```

## Production notes

Build the production stack with Gunicorn:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

Set a real `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` and `DJANGO_DEBUG=0`.
Static files are collected automatically and served by WhiteNoise, so no
separate web server is required.

## Overlap policy

Overlapping classes are **allowed**: parallel sessions are legitimate in real
timetables. The behaviour is explicit in `ClassSession.overlapping()` and
covered by tests. Time ranges where `end_time <= start_time` are rejected.
