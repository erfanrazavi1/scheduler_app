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

Then open http://localhost:8000. This automatically loads
`docker-compose.override.yml`, which enables `DEBUG` and publishes port 8000
for local development.

## Stop

```bash
docker compose down
```

The database lives in a named Docker volume (`postgres_data`) and survives
`docker compose down`. Do **not** use `docker compose down -v` unless you
intentionally want to delete all data.

## Environment

Optional for local development: copy `.env.example` to `.env` and adjust
values. Sensible development defaults are used when `.env` is absent, and the
development override always forces `DJANGO_DEBUG=1` locally.

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django secret key (**required when `DEBUG=False`**) |
| `DJANGO_DEBUG` | `1` for development, `0` for production (default `0`) |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins allowed for POST (e.g. `https://scheduler.hesabinoo.ir`) |
| `DJANGO_TIME_ZONE` | Server time zone (default `Asia/Tehran`) |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Database credentials |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Database address (default `db:5432`) |
| `GUNICORN_WORKERS` / `GUNICORN_TIMEOUT` | Optional Gunicorn tuning (default `1` / `30`) |

HTTPS hardening (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`,
`SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`, …) is environment-driven and
defaults to safe production values; see `.env.example` for the overrides.

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
docker-compose.yml      Base: web + db services
docker-compose.override.yml  Local development (DEBUG + port 8000)
docker-compose.prod.yml Production (Gunicorn, web-edge, no host port)
```

## Production notes

Production is intended to run as an independent application on the same VPS:

```text
Cloudflare
    ↓
central nginx
    ↓
web-edge network
    ↓
scheduler-web:8000
    ↓
PostgreSQL (compose-internal only)
```

### Run production

1. Create the environment file and fill in real values:

   ```bash
   cp .env.example .env
   ```

   At minimum set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS=scheduler.hesabinoo.ir`,
   `DJANGO_CSRF_TRUSTED_ORIGINS=https://scheduler.hesabinoo.ir` and
   `POSTGRES_PASSWORD`.

2. Make sure the external Docker network used by the central proxy exists:

   ```bash
   docker network create web-edge   # once, on the VPS
   ```

3. Start the production stack (base + prod files only — the development
   override is intentionally excluded):

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

### What the production stack does

- Runs Gunicorn (`config.wsgi:application`) on port **8000**.
- Uses the `scheduler-web` network alias on the external `web-edge` network, so
  central nginx can route to `scheduler-web:8000`.
- **Does not publish port 8000 to the host** (only the development override
  does, for `http://localhost:8000`).
- Keeps PostgreSQL on the compose-internal network only; it is never published
  and never attached to `web-edge`.
- Runs migrations automatically on start and collects static files when
  `DEBUG=False`; static assets are served by WhiteNoise, so no separate web
  server is required.
- Keeps the database in the named `postgres_data` volume.

### Reverse proxy requirements

The proxy must forward `X-Forwarded-Proto` (`https`) for TLS-terminated
requests, because `SECURE_PROXY_SSL_HEADER` is set. This prevents redirect
loops. `SECURE_SSL_REDIRECT` is off by default and can be enabled once the
proxy is verified to send that header.

### Health check

`GET /healthz/` returns `{"status": "ok"}` and performs no database access.
Docker's healthcheck for the `web` service uses it.

## Security consideration (anonymous access)

> Authentication is intentionally not implemented yet. The current application allows anonymous creation, editing, and deletion of schedule entries. Authentication/authorization should be considered before exposing the application to an untrusted public audience.

CSRF protection, server-side form validation and POST-only writes are in
place, but any anonymous visitor can still modify the schedule. Treat this as a
known risk until authentication is added.

## Font dependency

The UI uses **Vazirmatn**, loaded at runtime from Google Fonts via `@import`
in `static/src/input.css`. If Google Fonts is unavailable the UI falls back to
`Tahoma`/`Arial`; text remains readable. Self-hosting the font is a possible
future improvement (it would require committing the font files).

## Overlap policy

Overlapping classes are **allowed**: parallel sessions are legitimate in real
timetables. The behaviour is explicit in `ClassSession.overlapping()` and
covered by tests. Time ranges where `end_time <= start_time` are rejected.
