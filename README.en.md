# ErrHub

Lightweight exception collection and management platform. Backend with Flask + PostgreSQL, frontend with Vue 3 + Element Plus, one-click deployment via Docker.

[中文版](./README.md)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | Python 3.12 / Flask / SQLAlchemy / Gunicorn |
| Database | PostgreSQL 15 |
| Cache | Redis 6 |
| Frontend | Vue 3 / Element Plus / Vite / vue-i18n |
| Reverse Proxy | Nginx (Alpine) |
| Package Manager | uv (backend) / pnpm (frontend) |

---

## Project Structure

```
err-hub/
├── backend/          # Flask API service
│   ├── app/
│   │   ├── api/v1/   # API routes
│   │   ├── models/   # Data models
│   │   ├── static/   # SDK static files (error-feedback.js)
│   │   └── ...
│   └── Dockerfile
├── frontend/         # Vue 3 admin dashboard
│   ├── src/
│   │   ├── i18n/     # Internationalization configuration
│   │   └── ...
│   └── Dockerfile
└── docker/
    ├── docker-compose.yml
    ├── nginx/        # Gateway Nginx configuration
    ├── volumes/      # Persistent data directory
    └── .env          # Environment variables (copy from .env.example)
```

---

## Quick Start

### Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- Make (optional, can use docker compose commands directly)

### 1. Configure Environment Variables

```bash
cd docker
cp .env.example .env
# Edit .env, modify passwords, ports, etc. as needed
```

Key Configuration Items:

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_PORT` | `80` | Exposed port |
| `SECRET_KEY` | - | Flask Session secret key, **must change in production** |
| `JWT_SECRET_KEY` | - | JWT signing secret key, **must change in production** |
| `SUPERADMIN_USERNAME` | `admin` | Super admin username |
| `SUPERADMIN_PASSWORD` | `admin123` | Super admin initial password |
| `DATA_RETENTION_DAYS` | `90` | Error data retention days |
| `POSTGRES_PASSWORD` | `errhub` | Database password |

### 2. Build and Start with One Click

```bash
make up        # Build images + start all services
```

Or execute step by step:

```bash
make build     # Build images only
make start     # Start containers only
```

After startup, visit `http://<your-ip>:<GATEWAY_PORT>` to access the admin dashboard.

---

## Make Commands

| Command | Description |
|---------|-------------|
| `make build` | Build api and web images |
| `make up` | Build and start all services (background) |
| `make start` | Start existing containers |
| `make stop` | Stop all containers (retain data) |
| `make restart` | Restart all containers |
| `make down` | Stop and delete containers and network |
| `make rebuild` | Rebuild api/gateway images and force restart (**use this after code changes**) |
| `make rebuild-all` | Rebuild all images and force restart |
| `make logs` | View all service logs in real-time |
| `make logs-api` | View only API service logs |
| `make status` | Check container status |
| `make clean` | Stop containers and delete volumes (**use with caution, will lose data**) |

---

## How to Apply Code Changes

After modifying backend code or Nginx configuration:

```bash
make rebuild          # Rebuild api image + force restart api and gateway
```

After modifying frontend code:

```bash
make rebuild-all      # Rebuild all images
```

---

## Web SDK Integration

Simply include in your HTML page, no dependencies required:

```html
<script src="http://your-domain/sdk/error-feedback.js"
        data-api-token="Project API Token"
        data-auto-capture="true"
        data-environment="production"
        data-before-send="onBeforeErrorSend">
</script>

<script>
  // Manual reporting
  ErrHub.report('TypeError', 'Button click failed', { severity: 'error' });

  // Capture Error object
  try { riskyOp(); } catch (e) { ErrHub.captureException(e); }

  // Before send callback (optional)
  window.onBeforeErrorSend = function (payload) {
    payload.context.user_id = currentUser?.id;
    return payload;   // Return false to cancel reporting
  };
</script>
```

**Script Tag Attributes:**

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `data-api-token` | Yes | - | Project API Token (obtained after creating project in admin dashboard) |
| `data-auto-capture` | No | `true` | Auto capture unhandled exceptions and Promise rejections |
| `data-environment` | No | `production` | Environment identifier |
| `data-before-send` | No | - | Callback function name on window, triggered before reporting |

**window.ErrHub Methods:**

| Method | Description |
|--------|-------------|
| `ErrHub.report(type, message, opts?)` | Manually report an error |
| `ErrHub.captureException(error, opts?)` | Report Error object (auto parses name/message/stack) |
| `ErrHub.flush()` | Send all pending errors in queue immediately |

**beforeSend Callback Rules:**
- Return `payload` (modified if needed) → continue reporting
- No return → continue reporting original payload
- Return `false` → cancel this report
- Throw exception → silently fall back, still send original payload

---

## API Authentication

### Admin Dashboard API (JWT)

```
POST /api/v1/auth/login
Content-Type: application/json
{ "username": "admin", "password": "admin123" }

→ { "access_token": "..." }

# Subsequent requests include:
Authorization: Bearer <access_token>
```

### Error Reporting API (API Token)

```
POST /api/v1/errors
X-API-Token: <Project API Token>
Content-Type: application/json
{
  "exception_type": "ValueError",
  "message": "invalid input"
}
```

---

## Data Persistence

Data is stored in `docker/volumes/` directory:

```
docker/volumes/
├── postgres/    # PostgreSQL data files
└── redis/       # Redis dump.rdb
```

**Backup:** Simply package the `docker/volumes/` directory.

**Reset:** `make clean` deletes volumes, then `make up` initializes empty database.

---

## Internationalization (i18n)

Frontend uses [vue-i18n](https://vue-i18n.intlify.dev/) for multi-language support, currently supports **Chinese (zh-CN)** and **English (en)**.

### Language Detection and Switching

- **First visit:** Auto detect browser `navigator.language`, use Chinese for `zh` prefix, fallback to English for other languages
- **Manual switch:** Click language switch dropdown in top navigation
- **Preference persistence:** User's language choice is saved in `localStorage` under `locale` key, used on next visit

### Directory Structure

```
frontend/src/i18n/
├── index.js              # i18n initialization, language detection logic
└── locales/
    ├── zh-CN.js          # Chinese language pack
    └── en.js             # English language pack
```

### Add New Language

1. Create new language file in `frontend/src/i18n/locales/` (e.g., `ja.js`), fill translations following existing key structure
2. In `frontend/src/i18n/index.js`:
   - Import new language pack, add to `messages` object
   - Append `{ code: 'ja', label: '日本語' }` to `languages` array
   - Add browser language prefix mapping in `langMap` (e.g., `ja: 'ja'`)
3. For Element Plus integration, import corresponding Element Plus locale (e.g., `element-plus/es/locale/lang/ja`) and add condition in `App.vue`'s `elementLocale` computed

**No need to modify any component templates**, language switch menu will automatically render based on `languages` array.

### Add New Translation Keys

1. Add same key path to both `zh-CN.js` and `en.js`
2. Use in components via `t('key.path')` or in templates via `{{ t('key.path') }}`

**Notes:**
- In vue-i18n, `{` and `}` are special characters for interpolation syntax, to display literal braces use `{'{'}` and `{'}'}` escape
- For example, to display `{"user_id": "123"}`, write: `"like {'{'}\"user_id\": \"123\"{'}'}"`
