# ---------------------------------------------------------------------------
# Stage 1: compile Tailwind CSS. Node is isolated here and never ships in the
# final runtime image.
# ---------------------------------------------------------------------------
FROM node:20-alpine AS css-builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY tailwind.config.js ./
COPY static/src ./static/src
COPY static/js ./static/js
COPY templates ./templates
COPY schedules ./schedules
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: runtime image (Python only).
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=css-builder /app/static/css/app.css ./static/css/app.css

RUN sed -i 's/\r$//' ./entrypoint.sh \
    && chmod +x ./entrypoint.sh \
    && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
