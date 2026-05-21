# MediCheck — Plan de Desarrollo por Fases
### Documento para revisión del equipo · Mayo 2026
### Proyecto: Leonardo Gómez · Universidad de La Guajira · Ingeniería de Sistemas

---

## ESTADO ACTUAL DEL PROYECTO

MediCheck cuenta con un prototipo funcional completo con los siguientes módulos operativos:

- Autenticación con JWT (paciente, médico, admin)
- Triaje con IA (llama3.2:3b via Ollama local)
- Panel del médico con gestión de consultas
- Videoconsulta integrada (WebRTC + WebSocket)
- Botón SOS con GPS
- Mapa de ubicación de pacientes con ruta OSRM
- Validación de credenciales médicas
- Sistema de alertas de emergencia por email

---

## FASE 0 — BLINDAJE LEGAL Y SEGURIDAD ✅ COMPLETADA

**Objetivo:** Preparar el proyecto para mostrarse a usuarios reales sin riesgo legal ni responsabilidad por mal uso del sistema de IA.

### Cambios realizados en el código

| Archivo | Cambio realizado |
|---|---|
| `frontend/src/views/NuevaConsultaView.vue` | Aviso clínico obligatorio antes de consultar + checkbox de confirmación + contador de consultas disponibles |
| `frontend/src/components/ConsultaCard.vue` | Disclaimer legal amarillo debajo de cada resultado de IA |
| `frontend/src/views/RegisterView.vue` | Checkbox de consentimiento informado + modal con resumen de Términos de Uso |
| `frontend/src/views/PrivacidadView.vue` | Nueva página pública con Política de Privacidad completa (10 secciones, Ley 1581 de 2012) |
| `frontend/src/router/index.js` | Ruta `/privacidad` pública (sin autenticación requerida) |
| `backend/.../model/Usuario.java` | Nuevos campos: `consentimientoAceptado` (Boolean) + `fechaConsentimiento` (LocalDateTime) |
| `backend/.../model/Consulta.java` | Nuevos campos de trazabilidad: `ipOrigen` (String) + `versionIa` (String) |
| `backend/.../controller/AuthController.java` | Validación de consentimiento en registro — rechaza si `consentimientoAceptado = false` |
| `backend/.../service/RateLimiterService.java` | Nuevo servicio: máximo 10 consultas por hora por usuario (in-memory, thread-safe) |
| `backend/.../controller/ConsultaController.java` | Rate limiting + captura de IP + nuevo endpoint `GET /api/consultas/limite` |
| `backend/.../service/ConsultaService.java` | Guarda IP del solicitante y versión del modelo de IA en cada consulta |
| `backend/.../BackendApplication.java` | `@EntityScan` + `@EnableJpaRepositories` explícitos (fix crítico de compatibilidad JPA) |

### Qué ve cada usuario

**Paciente:**
- Al registrarse debe leer y aceptar Términos de Uso + Política de Privacidad
- Antes de enviar una consulta, ve un aviso clínico con 4 advertencias importantes
- Debe activar un checkbox confirmando que entiende los límites de la IA
- Cada resultado de análisis muestra un aviso legal en la tarjeta
- Un contador le indica cuántas consultas le quedan disponibles en la hora actual

**Médico:** Sin cambios visibles en su panel.

**Admin:** En base de datos puede auditar la IP de origen y versión de IA de cada consulta generada.

### Pendiente de decisión
> ¿Está aprobado el texto de la Política de Privacidad en `/privacidad`?
> Se recomienda revisión con un abogado o con el asesor jurídico de la universidad antes de lanzar a usuarios reales.

---

## FASE 1 — MVP COMERCIALMENTE VIABLE

**Objetivo:** Convertir MediCheck de prototipo técnico en un producto con modelo de negocio real, agenda profesional y prescripción médica. Esta es la fase que habilita los ingresos y hace el proyecto evaluable para Enactus.

---

### 1.1 Sistema de Pagos — PayU Colombia

**Por qué PayU:** Es el procesador de pagos líder en Colombia, acepta PSE, tarjetas, Nequi, Daviplata. Tiene sandbox gratuito para desarrollo. No requiere empresa constituida para pruebas.

**Archivos nuevos a crear:**

```
backend/
  model/Pago.java                    — Entidad: monto, estado, referencia PayU, fecha, consulta asociada
  repository/PagoRepository.java     — Repositorio JPA
  service/PagoService.java           — Lógica: crear orden, procesar confirmación PayU
  controller/PagoController.java     — Endpoints: POST /api/pagos/iniciar, POST /api/pagos/confirmacion

frontend/
  views/PagoView.vue                 — Pantalla de pago antes de enviar consulta
```

**Archivos a modificar:**

```
NuevaConsultaView.vue    — Agrega paso de pago antes de análisis de IA
AdminView.vue            — Nueva pestaña "Facturación" con historial de transacciones
```

**Requisito externo:** Crear cuenta gratuita en payulatam.com, obtener credenciales sandbox (`merchantId`, `accountId`, `apiKey`). Tiempo estimado: 30 minutos.

**Modelos de negocio posibles con este módulo:**

| Modelo | Precio sugerido |
|---|---|
| Pago por consulta | $5.000 – $15.000 COP |
| Suscripción mensual paciente | $30.000 – $50.000 COP/mes |
| Plan empresarial (B2B) | Tarifa por empleado/mes |

---

### 1.2 IA Médicamente Orientada

**Por qué:** El sistema prompt actual es genérico. Con un prompt estructurado clínicamente, el análisis pasa de ser una respuesta de chatbot a una orientación con formato médico real.

**Archivos a modificar:**

```
backend/service/OllamaService.java   — Reescritura completa del system prompt
```

**Estructura del nuevo análisis de IA:**
1. Síntoma principal identificado
2. Posibles causas diferenciales (3–5 opciones)
3. Signos de alarma específicos a vigilar
4. Cuándo exactamente ir a urgencias (criterios concretos)
5. Recomendación de seguimiento

**Sin requisitos externos.** El modelo llama3.2:3b local sigue siendo el mismo.

---

### 1.3 PWA — App Instalable sin App Store

**Por qué:** En el mercado objetivo (pacientes con acceso limitado), poder instalar MediCheck desde el navegador sin pasar por Play Store o App Store es una ventaja crítica de acceso.

**Archivos nuevos a crear:**

```
frontend/
  public/manifest.json              — Nombre, íconos, colores corporativos MediCheck
  public/service-worker.js          — Caché de pantallas principales para uso offline básico
```

**Archivos a modificar:**

```
frontend/vite.config.js             — Configurar plugin vite-plugin-pwa
frontend/index.html                 — Agregar meta tags PWA
```

**Resultado:** En Android y iOS aparece un banner automático "Instalar MediCheck". El ícono queda en la pantalla de inicio del teléfono como si fuera una app nativa.

**Sin requisitos externos.** Opcional: diseñar ícono PNG 512×512 con la marca MediCheck.

---

### 1.4 Agenda de Citas con Calendario

**Por qué:** El flujo actual es solo consulta de texto. Con agenda, el médico puede programar seguimientos y el paciente puede reservar citas, lo que abre un segundo canal de atención.

**Archivos nuevos a crear:**

```
backend/
  model/Cita.java                   — Entidad: fecha, hora, médico, paciente, estado
  repository/CitaRepository.java
  service/CitaService.java
  controller/CitaController.java    — GET /api/citas/disponibilidad/{medicoId}, POST /api/citas/reservar, PUT /api/citas/{id}/confirmar

frontend/
  views/AgendaView.vue              — Vista paciente: calendario con disponibilidad del médico
```

**Archivos a modificar:**

```
PanelMedicoView.vue    — Sección "Mi agenda" + configuración de horarios disponibles
router/index.js        — Nueva ruta /agenda
Sidebar.vue            — Agregar ítem "Agenda" en menú paciente
```

**Sin requisitos externos.**

---

### 1.5 Receta Médica Digital en PDF

**Por qué:** Es uno de los elementos de mayor credibilidad para un médico. Una prescripción con número de licencia, nombre del médico y QR de verificación convierte MediCheck en una herramienta de trabajo real para el profesional.

**Archivos nuevos a crear:**

```
backend/
  model/Receta.java                 — Entidad: medicamentos, dosis, frecuencia, duración, médico firmante
  service/RecetaService.java        — Generación del PDF con Apache PDFBox
  controller/RecetaController.java  — POST /api/medico/receta, GET /api/medico/receta/{id}/pdf
```

**Archivos a modificar:**

```
PanelMedicoView.vue    — Formulario de prescripción dentro de cada consulta
```

**Contenido del PDF generado:**
- Membrete MediCheck con logo y colores corporativos
- Datos del médico: nombre completo, número de licencia médica, especialidad
- Datos del paciente: nombre, documento, fecha
- Lista de medicamentos con dosis, frecuencia y duración
- Código QR de verificación de autenticidad
- Número único de receta

**Sin requisitos externos.** Se agrega la dependencia `pdfbox-app` en `pom.xml`.

---

### Impacto total de Fase 1 por usuario

**Paciente:** Puede pagar su consulta con PSE o tarjeta, agendar citas en un calendario visual, instalar MediCheck en su celular como app, y recibir recetas médicas digitales en PDF.

**Médico:** Recibe compensación económica por cada consulta, gestiona su propia agenda con horarios disponibles, emite prescripciones profesionales con su nombre y número de licencia.

**Admin:** Visualiza todos los pagos realizados, puede configurar precios y modelos de cobro, accede al historial de recetas generadas y puede auditar el sistema completo.

---

## FASE 2 — ESCALABILIDAD Y CONFIANZA

**Objetivo:** Agregar los módulos que generan retención de usuarios a largo plazo, confianza médica y diferenciación frente a la competencia.

---

### Módulos a desarrollar en Fase 2

#### Chat médico-paciente en tiempo real
- Nueva entidad `Mensaje.java`
- Reutiliza la infraestructura WebSocket ya instalada en el proyecto (teleconsulta)
- Vista de chat integrada en panel del médico y en panel del paciente
- Historial de mensajes guardado en base de datos

#### Notificaciones push
- Extensión del `service-worker.js` creado en Fase 1 con Push API
- Alertas cuando: el médico deja una nota, una cita está próxima, resultado de consulta disponible
- Configuración de preferencias de notificación desde el perfil

#### Sistema de calificaciones de médicos
- Nueva entidad `Calificacion.java` (1–5 estrellas + comentario + consulta asociada)
- Paciente califica al médico después de cada consulta
- Perfil público del médico muestra calificación promedio y número de consultas atendidas

#### Notas SOAP estructuradas para médicos
- Reemplaza el textarea libre del médico por 4 campos clínicos: Subjetivo / Objetivo / Evaluación / Plan
- Formato estándar clínico internacional
- Exportable en el PDF de historial del paciente

#### Perfil de salud completo del paciente
- Ampliar `PerfilPaciente.java` con: alergias conocidas, medicamentos actuales, enfermedades crónicas, grupo sanguíneo, antecedentes familiares
- La IA consume este contexto automáticamente para análisis más precisos y personalizados

#### Autenticación de dos factores (2FA)
- Código de 6 dígitos enviado por email al iniciar sesión
- Nuevos campos en `Usuario.java`: `otpCode`, `otpExpira`
- Aumenta seguridad para usuarios con datos de salud sensibles

#### Dashboard de estadísticas del médico
- Métricas propias en `PanelMedicoView.vue`: pacientes activos, distribución LEVE/MODERADO/GRAVE, calificación promedio, tiempo promedio de respuesta

#### Exportar historial del paciente en PDF
- Botón de descarga en `HistorialView.vue`
- Backend genera PDF con todas las consultas formateadas cronológicamente
- Útil para llevar a consulta presencial o compartir con otro médico

---

### Impacto de Fase 2 por usuario

**Paciente:** Chat directo con su médico, notificaciones en tiempo real, puede calificar al médico tras cada consulta, descarga su historial médico completo en PDF, el análisis de IA es más preciso porque conoce su perfil de salud.

**Médico:** Canal de comunicación directa con pacientes, notas clínicas estructuradas (formato SOAP estándar), estadísticas de su propio desempeño, acceso al perfil completo de salud del paciente antes de atender.

**Admin:** Dashboard con métricas globales de la plataforma, gestión de calificaciones y reputación de médicos, auditoría completa de accesos y actividad por IP.

---

## FASE 3 — REVOLUCIÓN Y ESCALA NACIONAL

**Objetivo:** Posicionar MediCheck como plataforma de referencia en salud digital en Colombia y el mundo hispanohablante.

---

### Módulos a desarrollar en Fase 3

#### IA con memoria longitudinal
- El análisis no evalúa solo la consulta actual, sino el historial completo del paciente
- Detección automática de patrones: "5 consultas por cefalea en 2 meses → recomendar evaluación neurológica"
- Servicio de alertas proactivas cuando se detectan patrones de riesgo

#### Módulo de salud preventiva
- Recordatorios de vacunas según esquema colombiano de vacunación y edad del paciente
- Alertas de chequeos anuales obligatorios según edad y sexo
- Consejos personalizados por perfil de riesgo (fumador, hipertenso, diabético, etc.)

#### Sistema de referidos a especialistas
- El médico de cabecera deriva formalmente al paciente a un especialista dentro de MediCheck
- El historial clínico se comparte automáticamente entre médicos autorizados
- Trazabilidad completa de la cadena de atención

#### Seguimiento de condiciones crónicas
- Panel dedicado para enfermedades crónicas: diabetes, hipertensión, asma, EPOC
- Registro periódico de valores: glucosa, presión arterial, oximetría, peso
- Gráficas de tendencias con alertas automáticas cuando los valores salen del rango seguro

#### Epidemiología en tiempo real
- Dashboard anonimizado de síntomas predominantes por ciudad y región de Colombia
- Detección temprana de posibles brotes locales
- Datos agregados anonimizados como fuente potencial de ingresos para Ministerio de Salud o aseguradoras (B2G)

#### Integración con EPS colombianas
- API de conexión con Sanitas, Compensar, Nueva EPS, Sura
- Afiliados de la EPS acceden a MediCheck como servicio complementario incluido en su plan
- Requiere negociación comercial directa con cada EPS — es el paso final del roadmap

#### Modo offline completo
- PWA extendida: registro de síntomas sin conexión a internet
- Sincronización automática al recuperar conectividad
- Crítico para zonas rurales de La Guajira y otras regiones con baja cobertura de datos

---

### Impacto de Fase 3 por usuario

**Paciente:** La IA lo conoce en profundidad y advierte proactivamente sobre patrones de riesgo. Recibe recordatorios preventivos personalizados. Puede usar MediCheck con conexión deficiente. Si tiene condición crónica, tiene seguimiento continuo y automatizado.

**Médico:** Recibe alertas proactivas basadas en patrones de cada paciente. Puede referir a especialistas dentro de la plataforma con traspaso de historial. Accede a contexto epidemiológico actualizado de su zona geográfica.

**Admin:** Mapa epidemiológico en tiempo real de todo el país. Gestión de contratos con EPS. Panel de métricas para reportes a entidades gubernamentales. Modelo de ingresos B2G habilitado.

---

## RESUMEN EJECUTIVO

### Cronograma estimado

| Fase | Estado | Duración estimada | Dependencias externas |
|---|---|---|---|
| Fase 0 | COMPLETADA | — | Revisión legal (recomendada) |
| Fase 1 | Lista para iniciar | 3–4 semanas | Cuenta PayU sandbox (gratis, 30 min) |
| Fase 2 | Planificada | 4–5 semanas | Ninguna |
| Fase 3 | Planificada | 6–8 semanas | Negociación con EPS (solo módulo final) |

### Arquitectura técnica actual del proyecto

| Componente | Tecnología |
|---|---|
| Backend | Spring Boot 3.5 + Java 23 + JPA/Hibernate |
| Frontend | Vue 3 + Vite + Vue Router |
| Base de datos | MySQL (JPA auto-schema) |
| IA local | llama3.2:3b via Ollama |
| Comunicación en tiempo real | WebRTC + WebSocket (STOMP) |
| Autenticación | JWT (Bearer token) |
| Mapas | Leaflet.js + OSRM para rutas |

### Recomendación de prioridad

**Prioridad 1 — Fase 1:** Sin modelo de negocio, ningún jurado de Enactus ni inversionista tomará en serio el proyecto, independientemente de su calidad técnica. La agenda de citas y el pago en línea son los cambios de mayor impacto percibido.

**Prioridad 2 — Fase 2 (chat + calificaciones):** Son los módulos que más visiblemente mejoran la experiencia del usuario y la credibilidad ante evaluadores. Se pueden implementar en paralelo con partes de la Fase 1 si hay tiempo.

**Fase 3** es el horizonte estratégico a 6–12 meses, no el objetivo inmediato.

---

## DECISIONES QUE EL EQUIPO DEBE TOMAR

1. **¿Aprobamos el texto legal actual de la Política de Privacidad?** (visible en `localhost:5173/privacidad`)
2. **¿Cuál es el modelo de negocio de la Fase 1?** (pago por consulta, suscripción mensual, o ambos)
3. **¿Confirmamos el precio por consulta?** (Se propone entre $5.000 y $15.000 COP)
4. **¿Creamos la cuenta en PayU para tener el sandbox listo?** (Paso previo obligatorio para Fase 1)
5. **¿Avanzamos con Fase 1?** Si el equipo está de acuerdo, la implementación comienza de inmediato.

---

*Este documento es de uso interno del equipo MediCheck.*
*La información técnica aquí descrita es propiedad intelectual de Leonardo Gómez — Universidad de La Guajira.*
*Prohibida su distribución sin autorización del titular del proyecto.*
