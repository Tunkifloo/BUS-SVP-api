# 🚌 Sistema de Ventas de Pasajes de Bus - Backend API

Sistema completo de gestión y venta de pasajes de bus desarrollado con **FastAPI** y **PostgreSQL**, implementando arquitectura hexagonal (Clean Architecture) para garantizar mantenibilidad y escalabilidad.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Autenticación](#-autenticación)
- [Base de Datos](#-base-de-datos)
- [Desarrollo](#-desarrollo)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [Contribución](#-contribución)

## ✨ Características

### 🎯 Funcionalidades Principales
- **Gestión de Usuarios**: Registro, autenticación y perfiles
- **Gestión de Empresas**: Administración de compañías de transporte
- **Gestión de Buses**: Control de flota y mantenimiento
- **Gestión de Rutas**: Definición de trayectos y precios
- **Gestión de Horarios**: Programación de viajes
- **Sistema de Reservas**: Reserva y cancelación de asientos
- **Selección de Asientos**: Mapa visual de disponibilidad
- **Autenticación JWT**: Seguridad robusta con roles
- **Notificaciones por Email**: Confirmaciones automáticas
- **Generación de PDFs**: Boletos electrónicos

### 🔧 Características Técnicas
- **Arquitectura Hexagonal**: Separación clara de responsabilidades
- **Async/Await**: Operaciones asíncronas para mejor rendimiento
- **Validación Robusta**: Validaciones de negocio y datos
- **Logging Completo**: Trazabilidad de operaciones
- **Manejo de Errores**: Respuestas consistentes
- **Documentación Automática**: Swagger/OpenAPI
- **CORS Configurado**: Integración con frontend
- **Middleware Personalizado**: Autenticación y logging

## 🏗️ Arquitectura

```
app/
├── 📁 application/          # Casos de uso y DTOs
│   ├── dto/                 # Data Transfer Objects
│   ├── handlers/            # Manejadores de eventos
│   ├── interfaces/          # Interfaces de servicios
│   └── use_cases/           # Lógica de aplicación
├── 📁 core/                 # Configuración y excepciones
│   ├── config.py            # Configuración global
│   ├── exceptions.py        # Excepciones personalizadas
│   └── security.py          # Seguridad y JWT
├── 📁 domain/               # Lógica de negocio
│   ├── entities/            # Entidades de dominio
│   ├── repositories/        # Interfaces de repositorios
│   ├── services/            # Servicios de dominio
│   └── value_objects/       # Objetos de valor
├── 📁 infrastructure/       # Implementaciones técnicas
│   ├── database/            # Acceso a datos
│   ├── external/            # Servicios externos
│   └── web/                 # API REST
└── 📁 shared/               # Utilidades compartidas
    ├── constants.py         # Constantes del sistema
    ├── decorators.py        # Decoradores útiles
    ├── utils.py             # Funciones utilitarias
    └── validators.py        # Validadores personalizados
```

## 🛠️ Tecnologías

### Backend Core
- **FastAPI** 0.104.1 - Framework web moderno y rápido
- **Python** 3.11+ - Lenguaje de programación
- **SQLAlchemy** 1.4.53 - ORM para base de datos
- **AsyncPG** - Driver PostgreSQL asíncrono
- **Pydantic** - Validación de datos

### Base de Datos
- **PostgreSQL** 17+ - Base de datos principal
- **Alembic** - Migraciones de BD

### Autenticación & Seguridad
- **Python-JOSE** - Manejo de JWT
- **Passlib** - Hashing de contraseñas
- **Bcrypt** - Algoritmo de cifrado

### Servicios Externos
- **AIOSMTPLIB** - Envío de emails asíncronos
- **ReportLab** - Generación de PDFs
- **Email-Validator** - Validación de emails

### Desarrollo
- **Uvicorn** - Servidor ASGI
- **Python-dotenv** - Variables de entorno
- **Pytz** - Manejo de zonas horarias

## 📋 Requisitos Previos

- **Python** 3.11 o superior
- **PostgreSQL** 17 o superior
- **Git** para control de versiones
- **pip** para gestión de paquetes

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/bus-system-backend.git
cd bus-system-backend
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL
```sql
-- Conectar como superusuario postgres
psql -U postgres

-- Crear base de datos
CREATE DATABASE bus_system_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Peru.1252'
    LC_CTYPE = 'Spanish_Peru.1252';

-- Verificar creación
\l bus_system_db;
```

## ⚙️ Configuración

### 1. Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:tu_password@localhost:5432/bus_system_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=bus_system_db
DATABASE_USER=postgres
DATABASE_PASSWORD=tu_password

# Application Settings
APP_NAME="Sistema de Ventas de Pasajes"
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=tu_secret_key_muy_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM_EMAIL=tu-email@gmail.com

# File Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 2. Inicializar Base de Datos
```bash
# Probar conexión
python test_connection.py

# Crear tablas
python init_db.py
```

## 🎮 Uso

### 1. Ejecutar el Servidor
```bash
# Desarrollo
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Verificar Funcionamiento
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Documentación interactiva
# Abrir en navegador: http://localhost:8000/docs
```

### 3. Crear Usuario Administrador
```bash
# Usar endpoint de registro con rol admin
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Administrador",
    "email": "admin@bus.com",
    "password": "admin123456",
    "role": "admin"
  }'
```

## 📚 API Endpoints

### 🔐 Autenticación
```http
POST   /api/v1/auth/register     # Registro de usuario
POST   /api/v1/auth/login        # Inicio de sesión
```

### 👥 Usuarios
```http
GET    /api/v1/users             # Listar usuarios (Admin)
GET    /api/v1/users/me          # Perfil actual
PUT    /api/v1/users/me          # Actualizar perfil
DELETE /api/v1/users/{id}        # Eliminar usuario (Admin)
```

### 🏢 Empresas
```http
GET    /api/v1/companies         # Listar empresas
POST   /api/v1/companies         # Crear empresa (Admin)
PUT    /api/v1/companies/{id}    # Actualizar empresa (Admin)
DELETE /api/v1/companies/{id}    # Eliminar empresa (Admin)
```

### 🚌 Buses
```http
GET    /api/v1/buses             # Listar buses
POST   /api/v1/buses             # Crear bus (Admin)
PUT    /api/v1/buses/{id}        # Actualizar bus (Admin)
DELETE /api/v1/buses/{id}        # Eliminar bus (Admin)
```

### 🛣️ Rutas
```http
GET    /api/v1/routes            # Listar rutas
GET    /api/v1/routes/search     # Buscar rutas disponibles
POST   /api/v1/routes            # Crear ruta (Admin)
PUT    /api/v1/routes/{id}       # Actualizar ruta (Admin)
DELETE /api/v1/routes/{id}       # Eliminar ruta (Admin)
```

### ⏰ Horarios
```http
GET    /api/v1/schedules         # Listar horarios (Admin)
POST   /api/v1/schedules         # Crear horario (Admin)
PUT    /api/v1/schedules/{id}    # Actualizar horario (Admin)
DELETE /api/v1/schedules/{id}    # Eliminar horario (Admin)
```

### 🎫 Reservas
```http
GET    /api/v1/reservations/my   # Mis reservas
POST   /api/v1/reservations      # Crear reserva
DELETE /api/v1/reservations/{id} # Cancelar reserva
```

### 🏥 Sistema
```http
GET    /api/v1/health            # Estado del sistema
GET    /api/v1/health/database   # Estado de la BD
```

## 🔑 Autenticación

### Obtener Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@email.com",
    "password": "password123"
  }'
```

### Usar Token
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer tu_token_jwt_aqui"
```

### Roles de Usuario
- **user**: Usuario normal (reservas)
- **company_admin**: Administrador de empresa
- **admin**: Administrador del sistema

## 🗄️ Base de Datos

### Modelos Principales
- **users**: Usuarios del sistema
- **companies**: Empresas de transporte
- **buses**: Flota de vehículos
- **routes**: Rutas de viaje
- **schedules**: Horarios programados
- **reservations**: Reservas de pasajeros

### Relaciones
```
companies (1) → (N) buses
companies (1) → (N) routes
routes (1) → (N) schedules
buses (1) → (N) schedules
users (1) → (N) reservations
schedules (1) → (N) reservations
```

## 👨‍💻 Desarrollo

### Estructura de Archivos Importantes
```
├── init_db.py              # Inicialización de BD
├── test_connection.py      # Prueba de conexión
├── requirements.txt        # Dependencias
├── .env                    # Variables de entorno
└── app/
    ├── main.py             # Punto de entrada
    └── [módulos...]
```

### Comandos Útiles
```bash
# Ejecutar con recarga automática
uvicorn app.main:app --reload

# Verificar sintaxis
python -m py_compile app/main.py

# Instalar nueva dependencia
pip install nueva-dependencia
pip freeze > requirements.txt
```

### Logging
Los logs se configuran en `app/core/config.py`:
```python
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🧪 Testing

### Endpoints Públicos para Pruebas
Durante el desarrollo, algunos endpoints están disponibles públicamente:

```bash
# Obtener empresas
GET /api/v1/companies/public

# Obtener rutas
GET /api/v1/routes/

# Crear reserva (prueba)
POST /api/v1/reservations/public
```

### Probar con cURL
```bash
# Buscar rutas
curl "http://localhost:8000/api/v1/routes/search?origin=Lima&destination=Cusco"

# Crear usuario
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@email.com", 
    "password": "password123"
  }'
```

## 🚀 Despliegue

### Variables de Producción
```env
DEBUG=False
SECRET_KEY=clave_super_secreta_produccion
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
```

### Con Docker (Opcional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Con Systemd
```ini
[Unit]
Description=Bus System API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contribución

### Flujo de Desarrollo
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código
- **PEP 8**: Estilo de código Python
- **Type Hints**: Anotaciones de tipos
- **Docstrings**: Documentación de funciones
- **Async/Await**: Para operaciones I/O

### Estructura de Commits
```
feat: agregar funcionalidad de reportes
fix: corregir validación de asientos
docs: actualizar README
refactor: mejorar estructura de reservas
```

## 📞 Soporte

### Problemas Comunes

**Error de conexión a BD:**
```bash
# Verificar PostgreSQL está ejecutándose
sudo systemctl status postgresql

# Probar conexión
python test_connection.py
```

**Error de dependencias:**
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

**Error de permisos:**
```bash
# En Linux/Mac
chmod +x *.py
```

### Contacto
- **Email**: soporte@bus-system.com
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/bus-system-backend/issues)
- **Documentación**: [Wiki](https://github.com/tu-usuario/bus-system-backend/wiki)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Desarrollado con ❤️ para modernizar el transporte interprovincial en Perú**

🌟 **¡No olvides dar una estrella al repositorio si te resulta útil!** 🌟
