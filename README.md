# Portfolio Backend API

API REST completa construida con **FastAPI** para la gestión del portfolio personal. Incluye autenticación segura, gestión de contenido multi-dominio, analíticas en tiempo real, notificaciones por email y soporte WebSocket.

---

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Modelos de Base de Datos](#modelos-de-base-de-datos)
- [API Reference](#api-reference)
- [Seguridad](#seguridad)
- [WebSocket / Tiempo Real](#websocket--tiempo-real)
- [Servicio de Email](#servicio-de-email)
- [Variables de Entorno](#variables-de-entorno)
- [Cómo Correrlo](#cómo-correrlo)
- [Migraciones](#migraciones)

---

## Características

- Autenticación JWT con cookies HttpOnly + rotación de refresh tokens
- Protección CSRF doble submit cookie
- Hash de contraseñas con Argon2
- Restablecimiento de contraseña por código OTP de 6 dígitos via email
- Gestión de contenido para proyectos, blog, cursos, educación, experiencia y habilidades
- Soft delete y restauración en todos los dominios de contenido
- Información personal / perfil del portfolio
- Analíticas de visitas con seguimiento de eventos (page views, clicks, referrers)
- Dashboard de analíticas en tiempo real via Socket.IO
- Formulario de contacto público con rate limiting
- Emails HTML transaccionales via Gmail SMTP
- Soporte PostgreSQL (producción) y SQLite (desarrollo)
- Soporte Redis para despliegues distribuidos con Socket.IO

---

## Arquitectura

El proyecto sigue una **arquitectura en capas** inspirada en Domain-Driven Design (DDD):

```
app/
├── domain/          # Capa de dominio – núcleo de negocio
│   ├── entities/    # Dataclasses inmutables (modelos de negocio)
│   ├── schemas/     # Schemas Pydantic (validación entrada/salida)
│   └── repositories/# Interfaces abstractas de repositorios
│
├── infrastructure/  # Capa de infraestructura – detalles técnicos
│   ├── database/
│   │   ├── session.py   # Engine y SessionLocal SQLAlchemy
│   │   └── models/      # ORM models (tablas de BD)
│   ├── repositories/    # Implementaciones concretas de repositorios
│   └── realtime/        # Servidor Socket.IO para analíticas en tiempo real
│
├── services/        # Capa de servicios – lógica de negocio
│
├── api/             # Capa de API – controladores HTTP
│   ├── deps.py      # Inyección de dependencias
│   └── v1/
│       ├── router.py
│       └── endpoints/   # Un módulo por dominio
│
└── core/            # Configuración transversal
    ├── config.py    # Settings via Pydantic-settings + .env
    ├── security.py  # JWT, CSRF, hashing, OTP
    └── logging.py   # Configuración de logs
```

### Flujo de una petición

```
HTTP Request
    └─→ FastAPI Router
            └─→ Endpoint (validación Pydantic)
                    └─→ Service (lógica de negocio)
                            └─→ Repository Interface
                                    └─→ Repository Impl (SQLAlchemy)
                                            └─→ PostgreSQL / SQLite
```

---

## Stack Tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| **FastAPI** | 0.109.0 | Framework web ASGI |
| **SQLAlchemy** | 2.0.23 | ORM |
| **Alembic** | 1.18.1 | Migraciones de base de datos |
| **Pydantic v2** | 2.5.0 | Validación y serialización |
| **python-jose** | 3.3.0 | JWT (HS256) |
| **passlib[argon2]** | 1.7.4 | Hash de contraseñas |
| **python-socketio** | 5.10.0 | WebSocket / tiempo real |
| **uvicorn** | 0.24.0 | Servidor ASGI |
| **PostgreSQL** | 15 | Base de datos (producción) |
| **Redis** | — | Manager distribuido Socket.IO (opcional) |

---

## Estructura del Proyecto

```
back-end/
├── alembic/                    # Migraciones de base de datos
│   └── versions/
│       ├── 8e35d76f...         # Migración inicial (users, refresh_tokens)
│       ├── 7a114e2d...         # Campos de perfil de usuario
│       ├── c4bfa0de...         # Dominios de contenido (projects, blog, etc.)
│       ├── 9f2d8c1a...         # Personal info
│       ├── d2a91f7c...         # Skills
│       └── ff8c9276...         # Password reset codes
├── app/
│   ├── main.py                 # Inicialización de FastAPI + CORS + Socket.IO
│   ├── api/
│   │   ├── deps.py             # Dependencias (auth, CSRF, servicios)
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── personal_info.py
│   │           ├── projects.py
│   │           ├── blog.py
│   │           ├── courses.py
│   │           ├── education.py
│   │           ├── experience.py
│   │           ├── skills.py
│   │           ├── analytics.py
│   │           └── contact.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── domain/
│   │   ├── entities/           # User, Project, BlogPost, Course, Education,
│   │   │                       # Experience, Skill, PersonalInfo, AnalyticsEvent
│   │   ├── schemas/            # Pydantic Create/Update/Read schemas
│   │   └── repositories/      # Abstract interfaces
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   └── models/        # SQLAlchemy ORM models
│   │   ├── repositories/      # Implementaciones SQLAlchemy
│   │   └── realtime/
│   │       └── socket_server.py
│   └── services/              # Lógica de negocio por dominio
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── run_dev.py
```

---

## Modelos de Base de Datos

### `users`
| Columna | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `username` | String(50) | único, indexado |
| `email` | String(255) | único, indexado |
| `full_name` | String(255) | nullable |
| `bio` | Text | nullable |
| `location` | String(255) | nullable |
| `website` | String(500) | nullable |
| `company` | String(255) | nullable |
| `avatar_url` | String(500) | nullable |
| `hashed_password` | Text | Argon2 |
| `is_active` | Boolean | default=True |
| `created_at` / `updated_at` | DateTime TZ | |

### `refresh_tokens`
| Columna | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `user_id` | FK → users | indexado |
| `token_hash` | String(128) | indexado |
| `jti` | String(36) | JWT ID, indexado |
| `revoked` | Boolean | default=False |
| `expires_at` | DateTime TZ | |

### `password_reset_codes`
| Columna | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `user_id` | FK → users | indexado |
| `code_hash` | String(64) | HMAC-SHA256 |
| `expires_at` | DateTime TZ | 15 min |
| `used` | Boolean | one-time use |

### Tablas de contenido (`projects`, `blog_posts`, `courses`, `education`, `experiences`, `skills`)

Todos los dominios de contenido comparten una estructura base:

| Columna | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `title` | String(255) | requerido |
| `slug` | String(255) | único, indexado |
| `description` | String(1000) | nullable |
| `content` | Text | nullable, Markdown/rich text |
| `images` | JSONB | array de URLs |
| `metadata` | JSONB | datos flexibles por dominio |
| `visible` | Boolean | indexado, default=True |
| `order` | Integer | indexado, para ordenamiento |
| `created_at` / `updated_at` | DateTime TZ | |
| `deleted_at` | DateTime TZ | nullable — soft delete |

> `blog_posts` también tiene `published_at` (DateTime TZ, nullable) para publicación programada.

#### Campo `metadata` por dominio

| Dominio | Campos comunes en `metadata` |
|---|---|
| **projects** | `tech_stack`, `links`, `featured`, `category`, `status` |
| **courses** | `platform`, `instructor`, `certificate_url`, `completion_date`, `duration_hours`, `skills` |
| **education** | `institution`, `degree`, `field_of_study`, `start_date`, `end_date`, `gpa`, `achievements` |
| **experience** | `company`, `position`, `location`, `start_date`, `end_date`, `is_current`, `employment_type`, `tech_stack` |
| **skills** | `level`, `category`, `years_experience`, `icon` |

### `personal_info`
| Columna | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `full_name` | String(255) | requerido |
| `headline` | String(255) | nullable |
| `bio` | Text | nullable |
| `email` | String(255) | nullable |
| `phone` | String(50) | nullable |
| `location` | String(255) | nullable |
| `website` | String(2048) | nullable |
| `avatar_url` | String(2048) | nullable |
| `resume_url` | String(2048) | nullable |
| `social_links` | JSONB | dict URL por red social |
| `metadata` | JSONB | datos extra |
| `visible` / `order` | Boolean / Integer | |
| `deleted_at` | DateTime TZ | soft delete |

### `analytics_events`
| Columna | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `event_type` | String(50) | `page_view`, `project_click`, `external_link`, `contact_form`, `download` |
| `page_slug` | String(255) | nullable, indexado |
| `content_type` | String(50) | nullable (`project`, `blog`, `course`, …) |
| `content_id` | Integer | nullable, indexado |
| `referrer` | String(2000) | nullable |
| `user_agent` | Text | nullable |
| `ip_hash` | String(64) | SHA-256, anonimizado |
| `country` | String(2) | ISO alpha-2, nullable |
| `metadata` | JSONB | |
| `created_at` | DateTime TZ | indexado |

---

## API Reference

Base URL: `http://localhost:5003/api/v1`

Documentación interactiva: `http://localhost:5003/docs`

### Autenticación

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `POST` | `/auth/login` | Público | Login — devuelve cookies JWT |
| `POST` | `/auth/logout` | Protegido + CSRF | Cierra sesión y revoca refresh token |
| `POST` | `/auth/refresh` | CSRF | Renueva el access token |
| `POST` | `/auth/register` | Admin + CSRF | Crea un nuevo usuario |
| `POST` | `/auth/password-reset/request` | Público | Solicita código OTP por email |
| `POST` | `/auth/password-reset/confirm` | Público | Confirma código y cambia contraseña |

### Usuarios

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/users/me` | Protegido | Devuelve el usuario autenticado |
| `PUT` | `/users/me` | Protegido + CSRF | Actualiza perfil del usuario |

### Personal Info

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/personal-info` | Público | Lista registros visibles (`limit`, `offset`) |
| `GET` | `/personal-info/{id}` | Público | Obtiene un registro por ID |
| `GET` | `/personal-info/admin/all` | Protegido | Lista todos incluyendo ocultos/eliminados |
| `POST` | `/personal-info` | Protegido + CSRF | Crea registro |
| `PUT` | `/personal-info/{id}` | Protegido + CSRF | Actualiza registro |
| `DELETE` | `/personal-info/{id}` | Protegido + CSRF | Soft delete (`?hard=true` para permanente) |
| `POST` | `/personal-info/{id}/restore` | Protegido + CSRF | Restaura registro eliminado |

### Proyectos, Blog, Cursos, Educación, Experiencia, Habilidades

Todos los dominios de contenido siguen el mismo patrón:

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/{dominio}` | Público | Lista visibles y publicados (`limit`, `offset`) |
| `GET` | `/{dominio}/{slug}` | Público | Obtiene por slug |
| `GET` | `/{dominio}/admin/all` | Protegido | Lista todos (con filtros) |
| `GET` | `/{dominio}/admin/{id}` | Protegido | Obtiene por ID |
| `POST` | `/{dominio}` | Protegido + CSRF | Crea entrada |
| `PUT` | `/{dominio}/{id}` | Protegido + CSRF | Actualiza entrada |
| `DELETE` | `/{dominio}/{id}` | Protegido + CSRF | Soft delete (`?hard=true` para permanente) |
| `POST` | `/{dominio}/{id}/restore` | Protegido + CSRF | Restaura entrada eliminada |

> Dominios: `/projects`, `/blog`, `/courses`, `/education`, `/experience`, `/skills`

> Blog agrega el parámetro `include_scheduled` en admin para ver posts con publicación futura.

### Contacto

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `POST` | `/contact` | Público · Rate limit 3/60s | Envía mensaje al propietario del portfolio |

**Request body:**
```json
{
  "name": "string (2-100 chars)",
  "email": "valid@email.com",
  "message": "string (10-2000 chars)"
}
```

### Analíticas

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `POST` | `/analytics/track` | Público | Registra un evento genérico |
| `POST` | `/analytics/pageview` | Público | Registra un page view (`?page_slug=`) |
| `GET` | `/analytics/summary` | Protegido | Resumen del período (`?days=30`) |
| `GET` | `/analytics/top-content` | Protegido | Contenido más visitado |
| `GET` | `/analytics/views-by-date` | Protegido | Vistas agrupadas por fecha |
| `GET` | `/analytics/events` | Protegido | Lista de eventos con filtros |
| `GET` | `/analytics/page-views` | Protegido | Vistas de una página específica |
| `GET` | `/analytics/content-views/{type}/{id}` | Protegido | Vistas de un contenido específico |

---

## Seguridad

### Autenticación con JWT + Cookies

Los tokens se almacenan en cookies HttpOnly para prevenir acceso desde JavaScript:

| Cookie | Duración | HttpOnly | Descripción |
|---|---|---|---|
| `access_token` | 10 minutos | Sí | JWT de acceso |
| `refresh_token` | 14 días | Sí | JWT de refresco (revocable) |
| `csrf_token` | 14 días | No | Token CSRF legible por JS |

### Protección CSRF

Todos los endpoints que modifican estado (POST, PUT, DELETE) requieren:
- Cookie `csrf_token` presente
- Header `X-CSRF-Token` con el mismo valor

La validación falla con `403 Forbidden` si no coinciden.

### Hash de Contraseñas

Argon2 (ganador de la Password Hashing Competition) con los parámetros por defecto de passlib.

### Restablecimiento de Contraseña

1. Se genera un código OTP de 6 dígitos
2. Se almacena como HMAC-SHA256 en la base de datos con expiración de 15 minutos
3. Se envía por email al usuario
4. El código es de un solo uso (`used=True` al consumirse)
5. El endpoint siempre devuelve `202` — no revela si el email existe

### IP Hashing en Analíticas

Las IPs se almacenan como SHA-256 para respetar la privacidad de los visitantes. No se guardan IPs en texto plano.

---

## WebSocket / Tiempo Real

El servidor Socket.IO permite que el panel de administración reciba eventos de analíticas en tiempo real sin polling.

**Namespace:** `/analytics`  
**Room:** `analytics_admin`  
**Path:** `/socket.io`

### Autenticación WebSocket

Al conectarse, el servidor valida el JWT de la cookie de acceso. Solo usuarios activos y autenticados pueden unirse.

### Eventos emitidos (servidor → cliente)

| Evento | Descripción | Payload |
|---|---|---|
| `analytics:event` | Nuevo evento registrado | Objeto `AnalyticsEvent` completo |
| `analytics:summary` | Resumen actualizado | Total views, unique visitors, top pages, referrers, países |
| `analytics:top_content` | Contenido más visto | Lista con ID, tipo, título y conteo de vistas |

Los eventos se emiten automáticamente cada vez que se llama a `/analytics/track` o `/analytics/pageview`.

### Soporte Redis (distribución horizontal)

Configurar `SOCKETIO_REDIS_URL` para usar Redis como message broker en despliegues con múltiples instancias.

---

## Servicio de Email

Usa Gmail SMTP con contraseña de aplicación (App Password). Los emails son HTML con fallback en texto plano.

### Emails enviados

#### Restablecimiento de contraseña
- **Para:** el usuario que solicitó el reset
- **Asunto:** "Código de verificación para restablecer tu contraseña"
- Muestra el código OTP en grande, con tiempo de expiración

#### Formulario de contacto
- **Para:** `GMAIL_SENDER_EMAIL` (el propietario del portfolio)
- **Reply-To:** email del visitante
- **Asunto:** "Nuevo mensaje de contacto de {nombre}"
- Incluye nombre, email y mensaje del visitante

---

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/api_portfolio

# JWT
JWT_SECRET_KEY=tu_clave_secreta_muy_segura
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_DAYS=14

# Cookies
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=tudominio.com   # opcional

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://tudominio.com"]

# Email (Gmail SMTP)
GMAIL_SENDER_EMAIL=tu@gmail.com
GMAIL_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx
PASSWORD_RESET_CODE_EXPIRE_MINUTES=15

# Socket.IO
SOCKETIO_REDIS_URL=redis://localhost:6379   # opcional
```

> Para desarrollo local puedes omitir `DATABASE_URL` (usa SQLite) y `GMAIL_*` (los emails se loggean pero no se envían).

---

## Cómo Correrlo

### Desarrollo local (SQLite)

```bash
# 1. Clonar e instalar dependencias
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

# 2. Copiar variables de entorno
cp .env.example .env            # edita los valores

# 3. Aplicar migraciones
alembic upgrade head

# 4. Iniciar servidor
python run_dev.py
```

Servidor disponible en: `http://localhost:5003`  
Docs interactivos: `http://localhost:5003/docs`

---

### Con Docker (PostgreSQL)

```bash
# Levantar base de datos PostgreSQL
docker compose up -d postgres

# Aplicar migraciones apuntando a Postgres
# (asegúrate que DATABASE_URL en .env apunte a localhost:5432)
alembic upgrade head

# Correr la app
python run_dev.py
```

---

### Producción

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 5003 \
  --workers 4
```

> En producción asegúrate de establecer `COOKIE_SECURE=true` y servir la API bajo HTTPS.

---

## Migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Crear una nueva migración (autogenerada)
alembic revision --autogenerate -m "descripción del cambio"

# Ver historial
alembic history

# Revertir la última migración
alembic downgrade -1

# Ver migración actual
alembic current
```

> `alembic.ini` usa SQLite por defecto. Para apuntar a PostgreSQL asegúrate de que `DATABASE_URL` esté definida en tu `.env` — el `env.py` de Alembic lee esta variable en tiempo de ejecución.
- ✅ Arquitectura Clean (Domain-Driven Design)
- ✅ Migraciones de base de datos con Alembic
- ✅ Validación de datos con Pydantic
- ✅ CORS configurado

## 🛠️ Stack Tecnológico

- **Framework:** FastAPI
- **Base de datos:** PostgreSQL
- **ORM:** SQLAlchemy 2.0
- **Migraciones:** Alembic
- **Autenticación:** python-jose (JWT)
- **Hash de contraseñas:** Argon2
- **Validación:** Pydantic

## 📋 Requisitos Previos

- Python 3.11+
- PostgreSQL 14+
- pip o poetry

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd back-end
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
```

3. **Activar entorno virtual**
```bash
# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**

Crear archivo `.env` en la raíz del proyecto:

```env
PROJECT_NAME=api_portfolio
PORT=5003
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/api_portfolio
JWT_SECRET_KEY=tu-secret-key-super-segura-aqui
COOKIE_SECURE=false
COOKIE_SAMESITE=none
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

6. **Crear base de datos**
```bash
# Conectarse a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE api_portfolio;
```

7. **Ejecutar migraciones**
```bash
alembic upgrade head
```

## 🚦 Uso

### Desarrollo

```bash
python run_dev.py
```

La API estará disponible en: `http://localhost:5003`

### Documentación interactiva

- **Swagger UI:** http://localhost:5003/docs
- **ReDoc:** http://localhost:5003/redoc

## 📁 Estructura del Proyecto

```
back-end/
├── alembic/                    # Migraciones de base de datos
│   └── versions/
├── app/
│   ├── api/                    # Capa de API
│   │   ├── deps.py            # Dependencias
│   │   └── v1/
│   │       ├── endpoints/     # Endpoints
│   │       └── router.py
│   ├── core/                   # Configuración y utilidades core
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── domain/                 # Capa de dominio
│   │   ├── entities/          # Entidades de negocio
│   │   ├── repositories/      # Interfaces de repositorios
│   │   └── schemas/           # Schemas de validación
│   ├── infrastructure/         # Capa de infraestructura
│   │   ├── database/
│   │   │   ├── models/        # Modelos SQLAlchemy
│   │   │   └── session.py
│   │   └── repositories/      # Implementación de repositorios
│   ├── services/              # Lógica de negocio
│   └── main.py                # Punto de entrada
├── .env                        # Variables de entorno (no versionado)
├── .gitignore
├── alembic.ini
├── requirements.txt
├── run_dev.py                 # Script de desarrollo
└── README.md
```

## 🔑 Endpoints Principales

### Autenticación

- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/login` - Inicio de sesión
- `POST /api/v1/auth/logout` - Cierre de sesión
- `POST /api/v1/auth/refresh` - Refrescar token

### Usuarios

- `GET /api/v1/users/me` - Obtener usuario actual

### Analíticas (tracking desde frontend)

- `POST /api/v1/analytics/track` - Registra evento personalizado
- `POST /api/v1/analytics/pageview` - Registra vista de página

## ⚡ Realtime Analytics (Socket.IO)

Canal en tiempo real para dashboard admin de analíticas.

- **Path Socket.IO:** `/{SOCKETIO_PATH}` (por defecto: `/socket.io`)
- **Namespace:** `/analytics`
- **Acceso:** solo usuarios autenticados por cookie `access_token`
- **Escalado:** soporta múltiples instancias con Redis (`SOCKETIO_REDIS_URL`)

### Eventos emitidos por el backend

- `analytics:event` → último evento insertado
- `analytics:summary` → resumen de analíticas (`days` configurable)
- `analytics:top_content` → top de contenido (`days` y `limit` configurables)

### Variables de entorno realtime

```env
SOCKETIO_PATH=socket.io
SOCKETIO_NAMESPACE_ANALYTICS=/analytics
SOCKETIO_ANALYTICS_ROOM=analytics_admin
SOCKETIO_REDIS_URL=redis://localhost:6379/0
ANALYTICS_REALTIME_DAYS=30
ANALYTICS_REALTIME_TOP_LIMIT=10
```

## 📝 Migraciones

### Crear nueva migración
```bash
alembic revision --autogenerate -m "descripción del cambio"
```

### Aplicar migraciones
```bash
alembic upgrade head
```

### Revertir migración
```bash
alembic downgrade -1
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app
```

## 📦 Modelo de Usuario

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "string",
  "bio": "string",
  "location": "string",
  "website": "string",
  "company": "string",
  "avatar_url": "string"
}
```

## 🔒 Seguridad

- Hash de contraseñas con Argon2
- Tokens JWT con expiración configurable
- Cookies HTTP-only y Secure en producción
- Protección CSRF
- Validación de entrada con Pydantic

## 📄 Licencia

MIT

## 👤 Autor

Tu nombre
