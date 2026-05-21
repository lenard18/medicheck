# MediCheck IA — Documentación del proyecto

> Plataforma de salud digital con análisis de síntomas por inteligencia artificial, gestión de perfiles médicos y pacientes, asignación geográfica médico-paciente y panel de administración.

---

## Índice

1. [Descripción general](#1-descripción-general)
2. [Stack tecnológico](#2-stack-tecnológico)
3. [Arquitectura del sistema](#3-arquitectura-del-sistema)
4. [Requisitos previos](#4-requisitos-previos)
5. [Instalación y puesta en marcha](#5-instalación-y-puesta-en-marcha)
6. [Variables de entorno](#6-variables-de-entorno)
7. [Esquema de base de datos](#7-esquema-de-base-de-datos)
8. [API REST — referencia completa](#8-api-rest--referencia-completa)
9. [Frontend — vistas y componentes](#9-frontend--vistas-y-componentes)
10. [Roles y permisos](#10-roles-y-permisos)
11. [Flujo de autenticación](#11-flujo-de-autenticación)
12. [Flujo de completar perfil](#12-flujo-de-completar-perfil)
13. [Motor de IA — análisis de síntomas](#13-motor-de-ia--análisis-de-síntomas)
14. [Sistema de documentos médicos](#14-sistema-de-documentos-médicos)
15. [Usuarios de prueba (Seeder)](#15-usuarios-de-prueba-seeder)
16. [Estructura de carpetas](#16-estructura-de-carpetas)

---

## 1. Descripción general

MediCheck IA es una aplicación web full-stack que permite a los **pacientes** describir sus síntomas y recibir un análisis automático de gravedad (LEVE / MODERADO / GRAVE) usando un modelo de lenguaje local (Ollama). Los **médicos** pueden registrarse, subir sus documentos para verificación y gestionar sus pacientes asignados. Los **administradores** verifican médicos, gestionan usuarios y asignan médicos a pacientes según proximidad geográfica.

### Funcionalidades principales

| Módulo | Funcionalidad |
|--------|--------------|
| **Autenticación** | Registro, login con JWT, redirección por rol |
| **Consultas IA** | Análisis de síntomas con Ollama (llama3.2), fallback por palabras clave |
| **Perfil paciente** | Formulario multi-paso: datos personales, info médica, contacto emergencia, preferencias |
| **Perfil médico** | Formulario multi-paso: datos personales, datos profesionales, documentos |
| **Perfil CV** | Vista de solo lectura estilo hoja de vida para médicos y pacientes |
| **Panel médico** | Lista de pacientes asignados, consultas, alertas por email |
| **Mapa de ubicación** | Geolocalización en tiempo real con Leaflet/OpenStreetMap |
| **Admin — verificación** | Revisión de documentos médicos, cambio de estado |
| **Admin — usuarios** | Listado paginado con filtros (nombre, rol, ciudad, estado) |
| **Admin — asignación** | Asignación médico-paciente con mapa, orden por distancia Haversine |
| **Alertas** | Email automático al médico cuando el paciente registra consulta GRAVE o MODERADO |

---

## 2. Stack tecnológico

### Backend
| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Java | 17 | Lenguaje |
| Spring Boot | 3.5.x | Framework principal |
| Spring Security | 6.x | Autenticación y autorización |
| Spring Data JPA | 3.x | Persistencia con Hibernate 6 |
| PostgreSQL | 15+ | Base de datos relacional |
| jjwt | 0.11.5 | Generación y validación de tokens JWT |
| Lombok | latest | Reducción de boilerplate |
| Spring Mail | — | Envío de alertas por email (Gmail SMTP) |
| Ollama REST | — | Cliente HTTP hacia el modelo de IA local |

### Frontend
| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Vue 3 | 3.4.x | Framework SPA |
| Vue Router | 4.6.x | Enrutamiento del cliente |
| Axios | 1.x | Cliente HTTP con interceptores JWT |
| Leaflet | 1.9.x | Mapas interactivos (OpenStreetMap) |
| Vite | 5.x | Bundler y servidor de desarrollo |

### Infraestructura de IA
| Tecnología | Uso |
|-----------|-----|
| Ollama | Servidor de modelos LLM local |
| llama3.2:3b | Modelo de lenguaje para análisis de síntomas |

---

## 3. Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                         │
│                    Vue 3 SPA  —  puerto 5173                     │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Paciente │  │  Médico  │  │  Admin   │  │  Componentes     │ │
│  │ Dashboard│  │  Panel   │  │  Panel   │  │  Sidebar, Cards  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│                       Axios + JWT Token                           │
└─────────────────────────┬───────────────────────────────────────┘
                           │ HTTP/REST  (puerto 8080)
┌─────────────────────────▼───────────────────────────────────────┐
│                    BACKEND (Spring Boot)                          │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Security   │  │ Controllers  │  │       Services         │  │
│  │  JWT Filter │  │ Auth         │  │  ConsultaService       │  │
│  │  CORS       │  │ Consultas    │  │  OllamaService         │  │
│  │  Roles      │  │ Admin        │  │  AlertaService         │  │
│  └─────────────┘  │ Perfil*      │  │  ArchivoService        │  │
│                   │ Documentos   │  │  UsuarioService        │  │
│                   │ Ubicacion    │  └────────────────────────┘  │
│                   └──────────────┘                               │
│                           │                                      │
│             ┌─────────────┼────────────────┐                     │
│             │             │                │                     │
│        PostgreSQL     Filesystem        Ollama                   │
│        (tablas)       (./uploads)     (puerto 11434)             │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de una consulta IA

```
Paciente ingresa síntomas
        │
        ▼
POST /api/consultas
        │
        ▼
ConsultaService.crearConsulta()
        │
        ├──► OllamaService.analizar()  ──► Ollama API ──► JSON {nivel, recomendacion}
        │         │
        │    (si Ollama falla)
        │         └──► analizarNivelFallback()  (palabras clave hardcodeadas)
        │
        ▼
Guardar Consulta en BD
        │
        ├── nivel GRAVE o MODERADO + paciente tiene médico asignado?
        │         │
        │         └──► AlertaService.notificarMedico()  ──► Gmail SMTP
        │
        ▼
Responder al frontend con la consulta guardada
```

---

## 4. Requisitos previos

| Software | Versión mínima | Verificar con |
|---------|---------------|---------------|
| Java JDK | 17 | `java -version` |
| Maven | 3.8+ (o usar mvnw incluido) | `mvn -version` |
| Node.js | 18+ | `node -v` |
| npm | 9+ | `npm -v` |
| PostgreSQL | 15+ | `psql --version` |
| Ollama | latest | `ollama --version` |

> **Ollama es opcional.** Si no está disponible, el sistema usa un analizador de fallback por palabras clave que sigue funcionando correctamente.

---

## 5. Instalación y puesta en marcha

### 5.1 Base de datos

```sql
-- Crear la base de datos en PostgreSQL
CREATE DATABASE medicheck_db;
```

Hibernate crea las tablas automáticamente al iniciar el backend (`ddl-auto=update`).

### 5.2 Ollama (opcional)

```bash
# Instalar Ollama desde https://ollama.com
# Descargar el modelo de análisis
ollama pull llama3.2:3b

# Iniciar el servidor (queda corriendo en puerto 11434)
ollama serve
```

### 5.3 Backend

```bash
cd medicheck/backend

# Opción A: con Maven Wrapper (recomendado)
.\mvnw spring-boot:run          # Windows
./mvnw spring-boot:run          # Linux/Mac

# Opción B: compilar y ejecutar JAR
.\mvnw clean package -DskipTests
java -jar target/backend-0.0.1-SNAPSHOT.jar
```

El servidor arranca en **http://localhost:8080**

Al iniciar, el `DataSeeder` crea automáticamente los usuarios de prueba si no existen.

### 5.4 Frontend

```bash
cd medicheck/frontend

# Instalar dependencias
npm install

# Servidor de desarrollo
npm run dev
```

La aplicación queda disponible en **http://localhost:5173**

---

## 6. Variables de entorno

### Backend — `application.properties`

Todas las propiedades soportan variables de entorno como override:

| Propiedad | Variable de entorno | Valor por defecto | Descripción |
|-----------|-------------------|-------------------|-------------|
| `spring.datasource.url` | `DB_URL` | `jdbc:postgresql://localhost:5432/medicheck_db` | URL de conexión a PostgreSQL |
| `spring.datasource.username` | `DB_USER` | `postgres` | Usuario de PostgreSQL |
| `spring.datasource.password` | `DB_PASSWORD` | `medicheck123` | Contraseña de PostgreSQL |
| `spring.jpa.hibernate.ddl-auto` | `DDL_AUTO` | `update` | Estrategia de esquema (`update` / `create` / `validate`) |
| `jwt.secret` | `JWT_SECRET` | `medicheck-secret-key-...` | Clave HMAC para firmar tokens JWT |
| `jwt.expiration` | `JWT_EXPIRATION` | `86400000` | Expiración del token en ms (24 h) |
| `ollama.url` | `OLLAMA_URL` | `http://localhost:11434` | URL del servidor Ollama |
| `ollama.model` | `OLLAMA_MODEL` | `llama3.2:3b` | Nombre del modelo de IA |
| `spring.mail.username` | `MAIL_USER` | `tucorreo@gmail.com` | Cuenta de correo para alertas |
| `spring.mail.password` | `MAIL_PASS` | `tu-app-password` | Contraseña de aplicación de Gmail |
| `app.upload.dir` | `UPLOAD_DIR` | `./uploads` | Directorio para archivos subidos |
| `server.port` | — | `8080` | Puerto del servidor |

> **Seguridad en producción:** Cambia `JWT_SECRET` por una cadena aleatoria de mínimo 32 caracteres. Usa contraseña de aplicación de Gmail (no la contraseña de cuenta).

### Frontend — `.env`

```env
VITE_API_URL=http://localhost:8080/api
```

---

## 7. Esquema de base de datos

### Diagrama de entidades

```
usuarios
├── id (PK)
├── nombre
├── email (UNIQUE)
├── password (hash bcrypt)
├── rol  ENUM(PACIENTE, MEDICO, ADMIN)
├── medico_id (FK → usuarios.id, nullable)  ← paciente → su médico
└── fecha_registro

perfiles_medico                          perfiles_paciente
├── id (PK)                              ├── id (PK)
├── usuario_id (FK, UNIQUE)              ├── usuario_id (FK, UNIQUE)
│                                        │
├── -- Datos personales --               ├── -- Datos personales --
├── apellidos                            ├── apellidos
├── tipo_documento                       ├── tipo_documento
├── numero_documento                     ├── numero_documento
├── fecha_nacimiento                     ├── fecha_nacimiento
├── genero                               ├── genero
├── nacionalidad                         ├── telefono
├── telefono                             ├── direccion
├── direccion                            ├── ciudad
├── ciudad                               ├── departamento
├── pais                                 ├── pais
│                                        │
├── -- Datos profesionales --            ├── -- Info médica --
├── numero_licencia                      ├── grupo_sanguineo
├── numero_tarjeta_profesional           ├── alergias (TEXT)
├── numero_rethus                        ├── enfermedades_cronicas (TEXT)
├── especialidad                         ├── medicamentos_actuales (TEXT)
├── subespecialidad                      ├── antecedente_quirurgicos (TEXT)
├── universidad                          ├── antecedentes_familiares (TEXT)
├── anio_graduacion                      │
├── anios_experiencia                    ├── -- Contacto emergencia --
├── idiomas                              ├── nombre_contacto_emergencia
├── descripcion_profesional (TEXT)       ├── parentesco_contacto
├── servicios_ofrecidos (TEXT)           ├── telefono_contacto_emergencia
│                                        │
├── -- Disponibilidad --                 ├── -- Preferencias --
├── atencion_presencial                  ├── modalidad_presencial
├── atencion_virtual                     ├── modalidad_virtual
├── atencion_domiciliaria                ├── modalidad_domiciliaria
├── zona_cobertura                       ├── disponibilidad_horaria
├── disponibilidad_horaria               ├── ciudad_atencion
├── tarifa_consulta                      │
├── tiempo_promedio_llegada              ├── fecha_registro
│                                        └── fecha_actualizacion
├── -- Validación admin --
├── estado_validacion ENUM(PENDIENTE, EN_REVISION, VERIFICADO, RECHAZADO, SUSPENDIDO)
├── observaciones_admin (TEXT)
├── fecha_registro
├── fecha_revision
└── revisado_por

documentos_medicos
├── id (PK)
├── usuario_id (FK → usuarios.id)
├── tipo  ENUM(FOTOGRAFIA_PROFESIONAL, SELFIE_VALIDACION,
│              DOCUMENTO_IDENTIDAD_FRONTAL, DOCUMENTO_IDENTIDAD_REVERSO,
│              DIPLOMA_UNIVERSITARIO, TARJETA_PROFESIONAL,
│              CERTIFICADO_ESPECIALIZACION, CERTIFICADO_RETHUS,
│              ANTECEDENTES_DISCIPLINARIOS, CERTIFICADO_LABORAL,
│              SEGURO_MEDICO_PROFESIONAL)
├── ruta_archivo
├── nombre_original
├── content_type
├── tamano
├── estado  ENUM(PENDIENTE, EN_REVISION, VERIFICADO, RECHAZADO, SUSPENDIDO)
├── observaciones (TEXT)
├── fecha_subida
├── fecha_revision
└── revisado_por

consultas
├── id (PK)
├── usuario_id (FK → usuarios.id)
├── sintomas (VARCHAR 1000)
├── nivel  VARCHAR  — LEVE | MODERADO | GRAVE
├── recomendacion (VARCHAR 2000)
└── fecha_consulta

ubicaciones
├── id (PK)
├── usuario_id (FK, UNIQUE)
├── latitud
├── longitud
└── actualizado
```

---

## 8. API REST — referencia completa

> **Base URL:** `http://localhost:8080/api`
>
> **Autenticación:** `Authorization: Bearer <token>` en todos los endpoints protegidos.

### 8.1 Autenticación — `/api/auth`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `POST` | `/auth/login` | ❌ | Iniciar sesión. Retorna token JWT y `perfilCompleto` |
| `POST` | `/auth/registro` | ❌ | Crear cuenta. Retorna token JWT y `perfilCompleto: false` |
| `GET` | `/auth/me` | ✅ | Obtener datos del usuario autenticado |

**Body `POST /auth/login`:**
```json
{ "email": "usuario@email.com", "password": "Contraseña123!" }
```

**Response exitosa:**
```json
{
  "token": "eyJhbGci...",
  "email": "usuario@email.com",
  "nombre": "Juan Pérez",
  "rol": "PACIENTE",
  "perfilCompleto": false
}
```

**Body `POST /auth/registro`:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@email.com",
  "password": "Contraseña123!",
  "rol": "PACIENTE"
}
```

---

### 8.2 Consultas IA — `/api/consultas`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `POST` | `/consultas` | ✅ PACIENTE | Crear nueva consulta. Analiza síntomas con IA |
| `GET` | `/consultas/mis-consultas` | ✅ PACIENTE | Listar todas las consultas del usuario autenticado |

**Body `POST /consultas`:**
```json
{ "sintomas": "Tengo fiebre alta, dolor de cabeza y náuseas desde ayer" }
```

**Response:**
```json
{
  "id": 42,
  "sintomas": "Tengo fiebre alta...",
  "nivel": "MODERADO",
  "recomendacion": "Consulta con un médico en las próximas 24 horas...",
  "fechaConsulta": "2025-05-12T14:35:00"
}
```

> El campo `nivel` puede ser: `LEVE`, `MODERADO` o `GRAVE`.

---

### 8.3 Perfil del médico — `/api/medico`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/medico/perfil` | ✅ MEDICO | Obtener perfil profesional propio |
| `POST` | `/medico/perfil` | ✅ MEDICO | Crear o actualizar perfil profesional |
| `GET` | `/medico/mis-pacientes` | ✅ MEDICO | Listar pacientes asignados al médico |
| `GET` | `/medico/consultas-pacientes` | ✅ MEDICO | Todas las consultas de los pacientes asignados |
| `GET` | `/medico/pacientes-disponibles` | ✅ MEDICO | Pacientes sin médico asignado |
| `POST` | `/medico/asignar-paciente/{pacienteId}` | ✅ MEDICO | Asignarse un paciente |

---

### 8.4 Perfil del paciente — `/api/paciente`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/paciente/perfil` | ✅ PACIENTE | Obtener perfil propio |
| `POST` | `/paciente/perfil` | ✅ PACIENTE | Crear o actualizar perfil |

**Body `POST /paciente/perfil`** (campos principales):
```json
{
  "apellidos": "Gómez Pérez",
  "tipoDocumento": "Cédula de ciudadanía",
  "numeroDocumento": "1234567890",
  "fechaNacimiento": "1990-05-15",
  "genero": "Masculino",
  "telefono": "+57 300 000 0000",
  "ciudad": "Bogotá",
  "pais": "Colombia",
  "grupoSanguineo": "O+",
  "alergias": "Penicilina",
  "medicamentosActuales": "Ninguno",
  "nombreContactoEmergencia": "María Gómez",
  "parentescoContacto": "Madre",
  "telefonoContactoEmergencia": "+57 311 000 0000",
  "modalidadPresencial": true,
  "modalidadVirtual": false,
  "ciudadAtencion": "Bogotá"
}
```

---

### 8.5 Documentos médicos — `/api/documentos`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/documentos` | ✅ MEDICO | Listar mis documentos subidos |
| `POST` | `/documentos/subir` | ✅ MEDICO | Subir un documento (multipart/form-data) |
| `GET` | `/documentos/ver/{id}` | ✅ MEDICO/ADMIN | Visualizar archivo (sirve el binario) |

**`POST /documentos/subir`** — form-data:
```
archivo: <archivo binario>
tipo:    TARJETA_PROFESIONAL   (ver enum TipoDocumento)
```

**Tipos de documento disponibles:**

| Enum | Descripción |
|------|-------------|
| `FOTOGRAFIA_PROFESIONAL` | Fotografía profesional |
| `SELFIE_VALIDACION` | Selfie de validación |
| `DOCUMENTO_IDENTIDAD_FRONTAL` | Documento de identidad (frontal) |
| `DOCUMENTO_IDENTIDAD_REVERSO` | Documento de identidad (reverso) |
| `DIPLOMA_UNIVERSITARIO` | Diploma universitario |
| `TARJETA_PROFESIONAL` | Tarjeta profesional |
| `CERTIFICADO_ESPECIALIZACION` | Certificado de especialización |
| `CERTIFICADO_RETHUS` | Certificado RETHUS |
| `ANTECEDENTES_DISCIPLINARIOS` | Antecedentes disciplinarios |
| `CERTIFICADO_LABORAL` | Certificado laboral |
| `SEGURO_MEDICO_PROFESIONAL` | Seguro médico profesional |

---

### 8.6 Ubicación GPS — `/api/ubicacion`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `POST` | `/ubicacion` | ✅ Cualquier rol | Actualizar propia ubicación GPS |
| `GET` | `/ubicacion/mi-medico` | ✅ PACIENTE | Obtener ubicación del médico asignado |
| `GET` | `/ubicacion/mis-pacientes` | ✅ MEDICO | Ubicaciones de todos los pacientes asignados |

**Body `POST /ubicacion`:**
```json
{ "latitud": 4.7110, "longitud": -74.0721 }
```

---

### 8.7 Administración — `/api/admin`

> Todos los endpoints requieren rol **ADMIN**.

#### Médicos y verificación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/admin/medicos` | Listar todos los médicos con estado y conteo de documentos |
| `GET` | `/admin/medicos/{id}` | Detalle completo de un médico (perfil + documentos) |
| `PUT` | `/admin/medicos/{id}/estado` | Cambiar estado de validación del médico |
| `GET` | `/admin/documentos/pendientes` | Documentos en estado PENDIENTE |
| `PUT` | `/admin/documentos/{docId}/estado` | Cambiar estado de un documento |

**Body `PUT /admin/medicos/{id}/estado`:**
```json
{
  "estado": "VERIFICADO",
  "observaciones": "Todo correcto, médico verificado."
}
```

**Estados disponibles:** `PENDIENTE` → `EN_REVISION` → `VERIFICADO` / `RECHAZADO` / `SUSPENDIDO`

#### Usuarios paginados con filtros

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/admin/usuarios` | Listado paginado con filtros |

**Query params:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `pagina` | int (default 0) | Número de página (base 0) |
| `nombre` | string | Filtro por nombre o email (LIKE) |
| `rol` | string | `PACIENTE`, `MEDICO` o `ADMIN` |
| `ciudad` | string | Filtro por ciudad (LIKE) |
| `estado` | string | Estado de validación del perfil médico |

**Response:**
```json
{
  "contenido": [
    { "id": 1, "nombre": "Juan", "email": "juan@...", "rol": "PACIENTE", "ciudad": "Bogotá", "estado": "ACTIVO" }
  ],
  "paginaActual": 0,
  "totalPaginas": 3,
  "totalElementos": 42,
  "hayAnterior": false,
  "haySiguiente": true
}
```

#### Perfil completo de cualquier usuario

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/admin/perfil/{userId}` | Obtener perfil completo de médico o paciente |

**Response para MEDICO:**
```json
{
  "id": 5,
  "nombre": "Dr. Carlos López",
  "email": "carlos@...",
  "rol": "MEDICO",
  "perfil": { ...camposPerfilMedico... },
  "documentos": [ ...listaDocumentos... ]
}
```

#### Asignación médico-paciente

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/admin/asignacion/mapa` | Todos los pacientes y médicos con coordenadas GPS |
| `POST` | `/admin/asignacion` | Asignar un médico a un paciente |
| `DELETE` | `/admin/asignacion/{pacienteId}` | Quitar la asignación de un paciente |

**Body `POST /admin/asignacion`:**
```json
{ "pacienteId": 12, "medicoId": 5 }
```

#### Estadísticas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/admin/estadisticas` | Contadores globales del sistema |

**Response:**
```json
{
  "totalMedicos": 15,
  "totalPacientes": 120,
  "medicosVerificados": 8,
  "medicosPendientes": 5,
  "medicosEnRevision": 2
}
```

---

## 9. Frontend — vistas y componentes

### 9.1 Vistas (pages)

| Archivo | Ruta | Rol | Descripción |
|---------|------|-----|-------------|
| `LoginView.vue` | `/login` | Público | Formulario de inicio de sesión |
| `RegisterView.vue` | `/registro` | Público | Registro de cuenta (paciente o médico) |
| `PerfilPacienteView.vue` | `/perfil-paciente` | PACIENTE | Formulario de perfil en 4 pasos |
| `RegisterMedicoView.vue` | `/registro-medico` | MEDICO | Formulario de perfil en 3 pasos + documentos |
| `DashboardView.vue` | `/dashboard` | PACIENTE | Estadísticas y consultas recientes |
| `NuevaConsultaView.vue` | `/nueva-consulta` | PACIENTE | Ingreso de síntomas + resultado IA |
| `HistorialView.vue` | `/historial` | PACIENTE | Historial completo de consultas |
| `MapaView.vue` | `/mapa` | PACIENTE/MEDICO | Mapa GPS con ubicación de médico/pacientes |
| `PerfilCVView.vue` | `/mi-perfil` | PACIENTE/MEDICO | Vista CV de solo lectura del perfil propio |
| `PerfilCVView.vue` | `/admin/perfil/:userId` | ADMIN | Vista CV de cualquier usuario |
| `PanelMedicoView.vue` | `/panel-medico` | MEDICO | Panel con pacientes, consultas y alertas |
| `AdminView.vue` | `/admin` | ADMIN | Panel principal: verificación de médicos |
| `AdminUsuariosView.vue` | `/admin/usuarios` | ADMIN | Lista paginada + filtros de todos los usuarios |
| `AdminAsignacionView.vue` | `/admin/asignacion` | ADMIN | Mapa de asignación médico-paciente |

### 9.2 Componentes reutilizables

| Archivo | Uso |
|---------|-----|
| `Sidebar.vue` | Barra lateral de navegación (adaptada por rol) |
| `ConsultaCard.vue` | Tarjeta individual de consulta médica |

### 9.3 Servicios

| Archivo | Descripción |
|---------|-------------|
| `src/api/axios.js` | Instancia de axios con `baseURL`, interceptor de token JWT y manejo de 401 |
| `src/api/auth.js` | Métodos `authApi.login()` y `authApi.registro()` |

### 9.4 Router — lógica de guardas

El router (`src/router/index.js`) implementa tres guardas en `beforeEach`:

1. **Token inválido/expirado** → limpia localStorage y redirige a `/login`
2. **Ruta de rol incorrecto** → redirige al dashboard del rol del usuario
3. **Perfil incompleto** → si `mc_perfil_ok !== 'true'`, redirige al formulario de perfil del rol. Se exceptúan: `PerfilPaciente`, `RegistroMedico` y `MiPerfil`.

**Variables en `localStorage`:**

| Clave | Valor | Descripción |
|-------|-------|-------------|
| `mc_token` | JWT string | Token de autenticación |
| `mc_email` | email | Email del usuario |
| `mc_nombre` | string | Nombre del usuario |
| `mc_rol` | `PACIENTE` / `MEDICO` / `ADMIN` | Rol |
| `mc_perfil_ok` | `"true"` / `"false"` | Si el perfil está completado |

---

## 10. Roles y permisos

### Matriz de acceso a endpoints

| Endpoint | PACIENTE | MEDICO | ADMIN |
|----------|----------|--------|-------|
| `/api/auth/**` | ✅ | ✅ | ✅ |
| `/api/consultas/**` | ✅ | ❌ | ✅ |
| `/api/paciente/**` | ✅ | ❌ | ✅ |
| `/api/medico/**` | ❌ | ✅ | ✅ |
| `/api/documentos/**` | ❌ | ✅ | ✅ |
| `/api/ubicacion/**` | ✅ | ✅ | ✅ |
| `/api/admin/**` | ❌ | ❌ | ✅ |

### Acceso por rol en el frontend

| Vista | PACIENTE | MEDICO | ADMIN |
|-------|----------|--------|-------|
| Dashboard | ✅ | ❌ | ❌ |
| Nueva consulta | ✅ | ❌ | ❌ |
| Historial | ✅ | ❌ | ❌ |
| Mi perfil (CV) | ✅ | ✅ | ❌ |
| Perfil (form) | ✅ | ✅ | ❌ |
| Mapa | ✅ | ✅ | ❌ |
| Panel médico | ❌ | ✅ | ❌ |
| Admin panel | ❌ | ❌ | ✅ |
| Admin usuarios | ❌ | ❌ | ✅ |
| Admin asignación | ❌ | ❌ | ✅ |
| Admin perfil /:userId | ❌ | ❌ | ✅ |

---

## 11. Flujo de autenticación

```
Usuario                 Frontend              Backend
   │                       │                     │
   │── Ingresa email/pwd ──►│                     │
   │                       │── POST /auth/login ─►│
   │                       │                     │── Verificar credenciales
   │                       │                     │── Generar JWT (HS256, 24h)
   │                       │                     │── Verificar perfilCompleto en BD
   │                       │◄── {token, rol, perfilCompleto} ──│
   │                       │                     │
   │                       │── Guarda en localStorage:
   │                       │   mc_token, mc_rol, mc_email,
   │                       │   mc_nombre, mc_perfil_ok
   │                       │                     │
   │                       │── Si perfilCompleto = false:
   │                       │   Redirige a /perfil-paciente o /registro-medico
   │                       │                     │
   │                       │── Si completo:
   │                       │   Redirige a Dashboard/PanelMedico/Admin
```

**Estructura del JWT:**
```json
{
  "sub": "usuario@email.com",
  "iat": 1715000000,
  "exp": 1715086400
}
```

El `JwtFilter` intercepta cada request, extrae el email del token, carga el `UserDetails` desde BD y setea el `SecurityContext`.

---

## 12. Flujo de completar perfil

Tras registrarse, el usuario **no puede acceder a ninguna ruta protegida** hasta completar su perfil. El flujo es:

```
Registro exitoso
      │
      ▼
mc_perfil_ok = "false"  (siempre al registrar)
      │
      ▼
Router guard detecta mc_perfil_ok != "true"
      │
      ├── MEDICO   →  /registro-medico  (3 pasos + documentos)
      └── PACIENTE →  /perfil-paciente  (4 pasos)
                              │
                              ▼
                    Validación por paso (validarPaso(p))
                    Campos obligatorios por paso:
                    
   PACIENTE paso 0: apellidos, tipo doc, nº doc, fecha nacimiento, género, teléfono, país, ciudad
   PACIENTE paso 1: grupo sanguíneo, alergias, medicamentos actuales
   PACIENTE paso 2: nombre contacto emergencia, parentesco, teléfono emergencia
   PACIENTE paso 3: mínimo 1 modalidad + ciudad de atención
   
   MÉDICO paso 0: apellidos, tipo doc, nº doc, fecha nacimiento, género, teléfono, país, ciudad
   MÉDICO paso 1: nº licencia, especialidad, universidad, año de graduación
   MÉDICO paso 2: todos los documentos obligatorios subidos
                              │
                              ▼
                    finalizar() valida TODOS los pasos
                    → POST /paciente/perfil o /medico/perfil
                    → mc_perfil_ok = "true"
                    → Acceso desbloqueado a la aplicación
```

---

## 13. Motor de IA — análisis de síntomas

### Funcionamiento con Ollama

El servicio `OllamaService` envía los síntomas al modelo LLM con un prompt estructurado que obliga al modelo a responder en JSON:

```json
{
  "nivel": "LEVE | MODERADO | GRAVE",
  "recomendacion": "texto con la recomendación en español"
}
```

**Criterios de clasificación:**
- **GRAVE:** dolor en el pecho, dificultad respiratoria, pérdida de consciencia, sangrado severo
- **MODERADO:** fiebre alta, vómitos, mareos fuertes, dolor intenso
- **LEVE:** síntomas menores manejables en casa

### Fallback (Ollama no disponible)

Si `OllamaService` retorna `null` (Ollama caído o sin conexión), `ConsultaService` usa `analizarNivelFallback()` que detecta palabras clave en los síntomas con la misma lógica de clasificación.

### Alertas automáticas

Si el nivel es `GRAVE` o `MODERADO` **y** el paciente tiene un médico asignado, `AlertaService` envía un email al médico via Gmail SMTP con:
- Nombre del paciente
- Nivel de gravedad
- Síntomas reportados
- Recomendación del sistema

---

## 14. Sistema de documentos médicos

### Subida de archivos

Los documentos se guardan en el sistema de archivos local bajo `./uploads/medicos/{usuarioId}/{uuid}.ext`.

- Tamaño máximo por archivo: **10 MB**
- Tamaño máximo por request: **50 MB**
- Si el médico sube un documento del mismo tipo dos veces, el archivo anterior se elimina y se reemplaza.

### Ciclo de vida de un documento

```
PENDIENTE  →  EN_REVISION  →  VERIFICADO
                          →  RECHAZADO
                          →  SUSPENDIDO
```

El admin puede cambiar el estado desde el Panel Admin o desde la vista de Perfil CV del médico.

### Visualización segura

El endpoint `GET /api/documentos/ver/{id}` verifica que:
1. El solicitante sea el dueño del documento **O** tenga rol ADMIN
2. El archivo exista físicamente en disco

Retorna el binario con el `Content-Type` original y header `Content-Disposition: inline` para visualización en el navegador.

> **Importante:** En el frontend, el botón "Ver documento" usa `axios` con `responseType: 'blob'` para enviar el token JWT. Los enlaces `<a href>` directos **no funcionan** porque no incluyen el header de autorización.

---

## 15. Usuarios de prueba (Seeder)

El `DataSeeder` crea automáticamente los siguientes usuarios al iniciar el backend:

### Usuarios principales

| Rol | Email | Contraseña | Notas |
|-----|-------|-----------|-------|
| ADMIN | `admin@medicheck.com` | `Admin2024!` | Acceso total al panel de administración |
| MEDICO | `medico@medicheck.com` | `Medico2024!` | Médico de prueba con perfil pre-cargado |
| PACIENTE | `paciente@medicheck.com` | `Paciente2024!` | Paciente de prueba base |

### Pacientes de prueba (20 registros)

Correos del `paciente1@test.com` al `paciente20@test.com`, todos con contraseña `Paciente2024!`.

El seeder es **idempotente**: si el usuario ya existe, no lo vuelve a crear. En cada arranque también:
- Corrige roles que pudieran haber quedado `NULL` en la base de datos
- Actualiza el constraint `CHECK` de la columna `rol`

---

## 16. Estructura de carpetas

```
medicheck/
├── README.md
│
├── backend/
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/medicheck/backend/
│       │   ├── BackendApplication.java          ← Punto de entrada
│       │   │
│       │   ├── config/
│       │   │   ├── AppConfig.java               ← Beans globales (RestTemplate, ObjectMapper, PasswordEncoder)
│       │   │   ├── DataSeeder.java              ← Datos de prueba al arrancar
│       │   │   ├── GlobalExceptionHandler.java  ← Manejo global de errores HTTP
│       │   │   ├── JwtFilter.java               ← Filtro de autenticación JWT
│       │   │   ├── JwtUtil.java                 ← Generación y validación de tokens
│       │   │   └── SecurityConfig.java          ← Configuración de Spring Security y CORS
│       │   │
│       │   ├── controller/
│       │   │   ├── AdminController.java         ← /api/admin/**
│       │   │   ├── AuthController.java          ← /api/auth/**
│       │   │   ├── ConsultaController.java      ← /api/consultas/**
│       │   │   ├── DocumentoController.java     ← /api/documentos/**
│       │   │   ├── MedicoController.java        ← /api/medico/** (panel médico)
│       │   │   ├── PerfilMedicoController.java  ← /api/medico/perfil
│       │   │   ├── PerfilPacienteController.java← /api/paciente/perfil
│       │   │   ├── UbicacionController.java     ← /api/ubicacion/**
│       │   │   └── UsuarioController.java       ← /api/usuarios/**
│       │   │
│       │   ├── dto/
│       │   │   ├── AuthResponse.java            ← Respuesta de login/registro
│       │   │   ├── ConsultaDTO.java             ← Request de nueva consulta
│       │   │   ├── LoginRequest.java            ← Request de login
│       │   │   ├── PerfilMedicoDTO.java         ← Request de perfil médico
│       │   │   ├── PerfilPacienteDTO.java       ← Request de perfil paciente
│       │   │   └── RegistroDTO.java             ← Request de registro
│       │   │
│       │   ├── model/
│       │   │   ├── Consulta.java
│       │   │   ├── DocumentoMedico.java
│       │   │   ├── EstadoValidacion.java        ← Enum: PENDIENTE, EN_REVISION, VERIFICADO, RECHAZADO, SUSPENDIDO
│       │   │   ├── PerfilMedico.java
│       │   │   ├── PerfilPaciente.java
│       │   │   ├── Rol.java                    ← Enum: PACIENTE, MEDICO, ADMIN
│       │   │   ├── TipoDocumento.java           ← Enum: 11 tipos de documento
│       │   │   ├── Ubicacion.java
│       │   │   └── Usuario.java
│       │   │
│       │   ├── repository/
│       │   │   ├── ConsultaRepository.java
│       │   │   ├── DocumentoMedicoRepository.java
│       │   │   ├── PerfilMedicoRepository.java
│       │   │   ├── PerfilPacienteRepository.java
│       │   │   ├── UbicacionRepository.java
│       │   │   └── UsuarioRepository.java       ← JpaSpecificationExecutor para filtros dinámicos
│       │   │
│       │   └── service/
│       │       ├── AlertaService.java           ← Envío de emails al médico
│       │       ├── ArchivoService.java          ← Guardar/eliminar archivos en disco
│       │       ├── ConsultaService.java         ← Orquesta IA + fallback + alertas
│       │       ├── OllamaService.java           ← Cliente HTTP a la API de Ollama
│       │       └── UsuarioService.java          ← CRUD de usuarios
│       │
│       └── resources/
│           └── application.properties
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── .env                                 ← VITE_API_URL
    └── src/
        ├── main.js                          ← Punto de entrada Vue
        ├── App.vue                          ← Root component
        ├── api/
        │   ├── axios.js                     ← Instancia axios con interceptores JWT
        │   └── auth.js                      ← Métodos login/registro
        ├── router/
        │   └── index.js                     ← Rutas + guardas de autenticación y perfil
        ├── components/
        │   ├── Sidebar.vue                  ← Navegación lateral (adaptada por rol)
        │   └── ConsultaCard.vue             ← Tarjeta de consulta
        └── views/
            ├── LoginView.vue
            ├── RegisterView.vue
            ├── PerfilPacienteView.vue        ← Form multi-paso paciente
            ├── RegisterMedicoView.vue        ← Form multi-paso médico
            ├── PerfilCVView.vue             ← Vista CV (propio o admin)
            ├── DashboardView.vue
            ├── NuevaConsultaView.vue
            ├── HistorialView.vue
            ├── MapaView.vue
            ├── PanelMedicoView.vue
            ├── AdminView.vue
            ├── AdminUsuariosView.vue
            └── AdminAsignacionView.vue
```

---

*Documentación generada para MediCheck IA · 2025*
