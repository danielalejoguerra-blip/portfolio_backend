# Portfolio Backend API

API REST construida con FastAPI para el sistema de autenticación y gestión de usuarios del portfolio.

## 🚀 Características

- ✅ Autenticación JWT con cookies HTTP-only
- ✅ Refresh tokens con rotación automática
- ✅ Protección CSRF
- ✅ Hash de contraseñas con Argon2
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
