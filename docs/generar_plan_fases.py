from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# ── Paleta limpia y legible ──────────────────────────────────────────────────
TEAL        = colors.HexColor('#00897B')   # verde teal principal
TEAL_LIGHT  = colors.HexColor('#E0F2F1')   # fondo teal suave
TEAL_MID    = colors.HexColor('#4DB6AC')   # teal medio
BLUE        = colors.HexColor('#1565C0')   # azul profundo
BLUE_LIGHT  = colors.HexColor('#E3F2FD')   # fondo azul suave
YELLOW      = colors.HexColor('#F57F17')   # ámbar oscuro (legible)
YELLOW_LIGHT= colors.HexColor('#FFF8E1')   # fondo ámbar
RED         = colors.HexColor('#C62828')   # rojo oscuro
RED_LIGHT   = colors.HexColor('#FFEBEE')   # fondo rojo
GREEN       = colors.HexColor('#2E7D32')   # verde completado
GREEN_LIGHT = colors.HexColor('#E8F5E9')   # fondo verde
GRAY_DARK   = colors.HexColor('#263238')   # texto principal
GRAY_MID    = colors.HexColor('#546E7A')   # texto secundario
GRAY_LIGHT  = colors.HexColor('#ECEFF1')   # fondo tabla alternado
GRAY_HEADER = colors.HexColor('#37474F')   # cabecera tabla
WHITE       = colors.white
BORDER      = colors.HexColor('#B0BEC5')   # bordes suaves

OUTPUT = r'L:\medicheck\docs\MediCheck_Plan_Fases_Desarrollo.pdf'

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2.5*cm,  bottomMargin=2.2*cm,
    title='MediCheck — Plan de Desarrollo por Fases',
    author='Leonardo Gómez — Universidad de La Guajira',
)

W = A4[0] - 4.4*cm

# ── Estilos de texto ─────────────────────────────────────────────────────────
def s(name, **kw):
    base = kw.pop('parent', 'Normal')
    p = ParagraphStyle(name, parent=getSampleStyleSheet()[base], **kw)
    return p

S_DOC_TITLE  = s('DocTitle',  fontSize=26, fontName='Helvetica-Bold',
                  textColor=TEAL,      alignment=TA_CENTER, spaceAfter=4, leading=30)
S_DOC_SUB    = s('DocSub',    fontSize=12, fontName='Helvetica',
                  textColor=GRAY_MID,  alignment=TA_CENTER, spaceAfter=3)
S_DOC_META   = s('DocMeta',   fontSize=9,  fontName='Helvetica',
                  textColor=GRAY_MID,  alignment=TA_CENTER, spaceAfter=2)

S_H1         = s('H1',  fontSize=13, fontName='Helvetica-Bold',
                  textColor=GRAY_DARK, spaceBefore=16, spaceAfter=4, leading=16)
S_H2         = s('H2',  fontSize=10.5, fontName='Helvetica-Bold',
                  textColor=GRAY_DARK, spaceBefore=10, spaceAfter=3, leading=13)
S_H3         = s('H3',  fontSize=9.5, fontName='Helvetica-Bold',
                  textColor=GRAY_MID,  spaceBefore=7,  spaceAfter=3, leading=12)

S_BODY       = s('Body', fontSize=9, fontName='Helvetica',
                  textColor=GRAY_MID,  leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
S_BULLET     = s('Bullet', fontSize=8.8, fontName='Helvetica',
                  textColor=GRAY_MID,  leading=13, leftIndent=14, spaceAfter=2)
S_NOTE       = s('Note', fontSize=8, fontName='Helvetica-Oblique',
                  textColor=GRAY_MID,  leading=11, spaceAfter=2)
S_LABEL      = s('Label', fontSize=7.5, fontName='Helvetica-Bold',
                  textColor=GRAY_MID,  spaceAfter=1)

def sp(h=6):
    return Spacer(1, h)

def hr(color=BORDER, thick=0.5, before=4, after=6):
    return HRFlowable(width='100%', thickness=thick, color=color,
                      spaceBefore=before, spaceAfter=after)

# ── Encabezado de sección con color lateral ───────────────────────────────────
def section_header(texto, color_bg, color_text=WHITE, color_accent=None):
    accent = color_accent or color_bg
    p = Paragraph(texto, s('sh', fontSize=11, fontName='Helvetica-Bold',
                            textColor=color_text, alignment=TA_LEFT))
    t = Table([[p]], colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), color_bg),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('RIGHTPADDING',  (0,0), (-1,-1), 14),
        ('LINEBEFORE',    (0,0), (0,-1),  5, WHITE if color_bg != WHITE else accent),
        ('ROUNDEDCORNERS',[4]),
    ]))
    return t

# ── Caja de información ───────────────────────────────────────────────────────
def info_box(texto, color_border, color_bg):
    p = Paragraph(texto, s('ib', fontSize=8.8, fontName='Helvetica',
                            textColor=GRAY_DARK, leading=13))
    t = Table([[p]], colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), color_bg),
        ('LINEBEFORE',    (0,0), (0,-1),  4, color_border),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('BOX',           (0,0), (-1,-1), 0.5, BORDER),
        ('ROUNDEDCORNERS',[3]),
    ]))
    return t

# ── Tabla estándar legible (fondo blanco) ─────────────────────────────────────
def mk_table(data, col_widths, accent=TEAL):
    rows = len(data)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        # Cabecera
        ('BACKGROUND',    (0,0), (-1,0),  accent),
        ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),  8.5),
        ('TOPPADDING',    (0,0), (-1,0),  7),
        ('BOTTOMPADDING', (0,0), (-1,0),  7),
        # Filas alternas
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('TEXTCOLOR',     (0,1), (-1,-1), GRAY_DARK),
        ('TOPPADDING',    (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
        ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
    ]
    # Filas alternas blanco / gris suave
    for i in range(1, rows):
        bg = WHITE if i % 2 == 1 else GRAY_LIGHT
        style.append(('BACKGROUND', (0,i), (-1,i), bg))
    t.setStyle(TableStyle(style))
    return t

# ── Tabla de impacto por usuario ──────────────────────────────────────────────
def impact_table(data, accent):
    t = Table(data, colWidths=[W/3]*3)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  accent),
        ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8.5),
        ('BACKGROUND',    (0,1), (-1,-1), WHITE),
        ('TEXTCOLOR',     (0,1), (-1,-1), GRAY_DARK),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

# ── Encabezado y pie de página ────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Franja verde en top
    canvas.setFillColor(TEAL)
    canvas.rect(0, A4[1]-1*cm, A4[0], 1*cm, fill=1, stroke=0)
    # Texto en franja
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(WHITE)
    canvas.drawString(2.2*cm, A4[1]-0.65*cm, 'MediCheck IA — Plan de Desarrollo por Fases')
    canvas.drawRightString(A4[0]-2.2*cm, A4[1]-0.65*cm, 'Mayo 2026 · Uso interno del equipo')
    # Footer
    canvas.setFillColor(GRAY_LIGHT)
    canvas.rect(0, 0, A4[0], 1.2*cm, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(0, 1.2*cm, A4[0], 1.2*cm)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_MID)
    canvas.drawString(2.2*cm, 0.45*cm,
        'Leonardo Gómez · Universidad de La Guajira · Ingeniería de Sistemas · LG358356@gmail.com')
    canvas.drawRightString(A4[0]-2.2*cm, 0.45*cm, f'Página {doc.page}')
    canvas.restoreState()

# ══════════════════════════════════════════════════════════════════════════════
# CONTENIDO
# ══════════════════════════════════════════════════════════════════════════════
story = []

# ── PORTADA ───────────────────────────────────────────────────────────────────
story.append(sp(35))

# Logo / nombre
logo_data = [[
    Paragraph('🩺', s('logo_ico', fontSize=38, alignment=TA_CENTER)),
    Paragraph('MediCheck <font color="#00897B">IA</font>',
              s('logo_txt', fontSize=34, fontName='Helvetica-Bold',
                textColor=GRAY_DARK, leading=38))
]]
logo_t = Table(logo_data, colWidths=[2.5*cm, W-2.5*cm])
logo_t.setStyle(TableStyle([
    ('VALIGN',       (0,0),(-1,-1),'MIDDLE'),
    ('LEFTPADDING',  (0,0),(-1,-1), 0),
    ('RIGHTPADDING', (0,0),(-1,-1), 0),
    ('TOPPADDING',   (0,0),(-1,-1), 0),
    ('BOTTOMPADDING',(0,0),(-1,-1), 0),
]))
story.append(logo_t)
story.append(sp(16))

story.append(Paragraph(
    'Plan de Desarrollo por Fases',
    s('cvr_sub', fontSize=18, fontName='Helvetica-Bold',
      textColor=GRAY_MID, alignment=TA_CENTER)))
story.append(sp(6))

# Línea divisoria teal
story.append(HRFlowable(width='60%', thickness=3, color=TEAL,
                         spaceBefore=4, spaceAfter=10,
                         hAlign='CENTER'))

story.append(Paragraph(
    'Documento para revisión interna del equipo · Mayo 2026',
    s('cvr_meta', fontSize=10, fontName='Helvetica',
      textColor=GRAY_MID, alignment=TA_CENTER)))
story.append(sp(30))

# Cuadro de datos del equipo
team_data = [
    ['Proyecto', 'MediCheck — Orientación médica con Inteligencia Artificial'],
    ['Desarrollador', 'Leonardo Gómez'],
    ['Institución', 'Universidad de La Guajira · Ingeniería de Sistemas'],
    ['Contacto', 'LG358356@gmail.com · 300 279 3410'],
    ['Fecha', 'Mayo 2026'],
    ['Versión', '1.0 — Revisión estratégica de fases'],
]
td = Table(team_data, colWidths=[3.5*cm, W-3.5*cm])
td.setStyle(TableStyle([
    ('FONTNAME',      (0,0),(0,-1), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0),(-1,-1), 9),
    ('TEXTCOLOR',     (0,0),(0,-1), TEAL),
    ('TEXTCOLOR',     (1,0),(1,-1), GRAY_DARK),
    ('ROWBACKGROUNDS',(0,0),(-1,-1), [WHITE, GRAY_LIGHT]),
    ('GRID',          (0,0),(-1,-1), 0.4, BORDER),
    ('TOPPADDING',    (0,0),(-1,-1), 6),
    ('BOTTOMPADDING', (0,0),(-1,-1), 6),
    ('LEFTPADDING',   (0,0),(-1,-1), 10),
    ('RIGHTPADDING',  (0,0),(-1,-1), 10),
    ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
]))
story.append(td)

# ── NUEVA PÁGINA ──────────────────────────────────────────────────────────────
story.append(PageBreak())

# ── ESTADO ACTUAL ─────────────────────────────────────────────────────────────
story.append(section_header('📋  Estado Actual del Proyecto', GRAY_HEADER))
story.append(sp(8))
story.append(Paragraph(
    'MediCheck es un prototipo funcional completo con los siguientes módulos operativos '
    'disponibles en localhost al momento de este documento:',
    S_BODY))

modulos = [
    ['Autenticación JWT',       'Roles: Paciente, Médico, Administrador'],
    ['Triaje con IA',           'Modelo llama3.2:3b vía Ollama local'],
    ['Panel del médico',        'Gestión completa de consultas asignadas'],
    ['Videoconsulta',           'WebRTC + WebSocket (STOMP)'],
    ['Botón SOS',               'Geolocalización GPS + alerta por correo'],
    ['Mapa de pacientes',       'Leaflet.js + rutas OSRM'],
    ['Validación credenciales', 'Verificación de licencias médicas'],
    ['Alertas de emergencia',   'Notificación por correo electrónico'],
]
story.append(mk_table(
    [['Módulo', 'Descripción']] + modulos,
    [5*cm, W-5*cm], accent=GRAY_HEADER))
story.append(sp(8))
story.append(info_box(
    '<b>Stack tecnológico:</b>  Spring Boot 3.5 + Java 23  ·  Vue 3 + Vite  ·  MySQL  ·  '
    'llama3.2:3b (Ollama)  ·  WebRTC + WebSocket  ·  JWT  ·  Leaflet.js + OSRM',
    TEAL, TEAL_LIGHT))

# ══════════════════════════════════════════════════════════════════════════════
# FASE 0
# ══════════════════════════════════════════════════════════════════════════════
story.append(sp(16))
story.append(section_header('✅  Fase 0 — Blindaje Legal y Seguridad  ·  COMPLETADA', GREEN))
story.append(sp(8))

story.append(Paragraph(
    'Se preparó el proyecto para mostrarse a usuarios reales cumpliendo la '
    '<b>Ley 1581 de 2012</b> (protección de datos sensibles) y la '
    '<b>Resolución 2654 de 2019</b> (telemedicina en Colombia).',
    S_BODY))

story.append(sp(4))
story.append(Paragraph('Archivos modificados y creados', S_H2))

f0 = [
    ['Archivo', 'Cambio realizado'],
    ['NuevaConsultaView.vue',     'Aviso clínico obligatorio + checkbox de confirmación + contador de consultas'],
    ['ConsultaCard.vue',          'Disclaimer legal debajo de cada resultado de IA'],
    ['RegisterView.vue',          'Checkbox de consentimiento + modal de Términos de Uso'],
    ['PrivacidadView.vue',        'Página pública nueva — Política de Privacidad (10 secciones, Ley 1581)'],
    ['router/index.js',           'Ruta /privacidad habilitada sin autenticación'],
    ['Usuario.java',              'Campos nuevos: consentimientoAceptado + fechaConsentimiento'],
    ['Consulta.java',             'Trazabilidad: ipOrigen (IP del usuario) + versionIa (modelo usado)'],
    ['AuthController.java',       'Rechaza registro si consentimientoAceptado = false'],
    ['RateLimiterService.java',   'NUEVO — Máximo 10 consultas por hora por usuario (thread-safe)'],
    ['ConsultaController.java',   'Rate limiting + captura de IP + endpoint GET /api/consultas/limite'],
    ['ConsultaService.java',      'Guarda IP y versión de IA en cada consulta creada'],
    ['BackendApplication.java',   '@EntityScan + @EnableJpaRepositories (fix crítico de compatibilidad JPA)'],
]
story.append(mk_table(f0, [4.8*cm, W-4.8*cm], accent=GREEN))

story.append(sp(8))
story.append(Paragraph('Qué ve cada usuario después de Fase 0', S_H2))

story.append(impact_table(
    [
        ['👤  Paciente', '👨‍⚕️  Médico', '🔧  Admin'],
        [
            'Al registrarse debe aceptar Términos de Uso y Política de Privacidad. '
            'Antes de consultar ve advertencias clínicas y confirma con checkbox. '
            'Cada análisis de IA incluye aviso legal. Ve cuántas consultas le quedan.',
            'Sin cambios visibles en su panel de trabajo.',
            'Puede auditar en base de datos la IP de origen y el modelo de IA utilizado '
            'en cada consulta generada por los pacientes.',
        ]
    ], GREEN))

story.append(sp(8))
story.append(info_box(
    '⚠  <b>Pendiente del equipo:</b>  ¿Está aprobado el texto de la Política de Privacidad '
    'en /privacidad? Se recomienda revisión con el asesor jurídico de la universidad antes '
    'de presentar el proyecto a usuarios reales.',
    YELLOW, YELLOW_LIGHT))

# ══════════════════════════════════════════════════════════════════════════════
# FASE 1
# ══════════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(section_header('🔵  Fase 1 — MVP Comercialmente Viable', BLUE))
story.append(sp(8))

story.append(Paragraph(
    '<b>Objetivo:</b>  Convertir MediCheck de prototipo técnico en un producto con modelo de '
    'negocio real, agenda profesional y receta médica digital. '
    'Sin esta fase, ningún evaluador de Enactus ni inversionista considerará el proyecto viable, '
    'sin importar su calidad tecnológica.',
    S_BODY))
story.append(info_box(
    '📅  <b>Duración estimada:</b>  3 a 4 semanas de desarrollo  '
    '·  <b>Dependencia externa:</b>  Cuenta gratuita en payulatam.com (30 min)',
    BLUE, BLUE_LIGHT))

story.append(sp(10))

# 1.1 Pagos
story.append(Paragraph('1.1  Sistema de Pagos — PayU Colombia', S_H2))
story.append(Paragraph(
    'PayU es el procesador de pagos líder en Colombia. Acepta PSE, tarjetas de crédito/débito, '
    'Nequi y Daviplata. El entorno de pruebas (sandbox) es completamente gratuito.',
    S_BODY))
f1_pago = [
    ['Archivo', 'Tipo', 'Descripción'],
    ['model/Pago.java',                'NUEVO',     'Entidad: monto, estado, referencia PayU, fecha, consulta asociada'],
    ['repository/PagoRepository.java', 'NUEVO',     'Repositorio JPA estándar'],
    ['service/PagoService.java',       'NUEVO',     'Crea órdenes de pago y procesa confirmaciones del webhook PayU'],
    ['controller/PagoController.java', 'NUEVO',     'POST /api/pagos/iniciar  ·  POST /api/pagos/confirmacion'],
    ['views/PagoView.vue',             'NUEVO',     'Pantalla de pago antes de enviar la consulta'],
    ['NuevaConsultaView.vue',          'MODIFICAR', 'Añade paso de pago previo al análisis de IA'],
    ['AdminView.vue',                  'MODIFICAR', 'Nueva pestaña "Facturación" con historial de transacciones'],
]
story.append(mk_table(f1_pago, [4.8*cm, 2*cm, W-6.8*cm], accent=BLUE))

story.append(sp(6))
story.append(Paragraph('Modelos de negocio disponibles con este módulo:', S_H3))
precios = [
    ['Modelo',                          'Precio sugerido'],
    ['Pago por consulta',               '$5.000 – $15.000 COP por consulta'],
    ['Suscripción mensual (paciente)',   '$30.000 – $50.000 COP por mes'],
    ['Plan empresarial B2B',            'Tarifa negociada por empleado / mes'],
]
story.append(mk_table(precios, [7*cm, W-7*cm], accent=BLUE))

# 1.2 IA
story.append(sp(10))
story.append(Paragraph('1.2  IA Médicamente Orientada', S_H2))
story.append(Paragraph(
    'El prompt actual genera respuestas genéricas. Con un prompt clínico estructurado, '
    'el análisis pasa de respuesta de chatbot a orientación con formato médico profesional. '
    'No se requiere cambiar el modelo — sigue siendo llama3.2:3b local.',
    S_BODY))
story.append(Paragraph('Archivo a modificar:  backend/service/OllamaService.java', S_H3))

ia_items = [
    ['1', 'Síntoma principal identificado por la IA'],
    ['2', 'Posibles causas diferenciales (3 a 5 opciones ordenadas por probabilidad)'],
    ['3', 'Signos de alarma específicos que el paciente debe vigilar'],
    ['4', 'Criterios concretos para acudir a urgencias'],
    ['5', 'Recomendación de seguimiento con el médico asignado'],
]
story.append(mk_table(
    [['#', 'El nuevo análisis de IA incluirá']] + ia_items,
    [1.2*cm, W-1.2*cm], accent=BLUE))

# 1.3 PWA
story.append(sp(10))
story.append(Paragraph('1.3  PWA — App Instalable sin App Store', S_H2))
story.append(Paragraph(
    'Permite instalar MediCheck desde el navegador directamente en el teléfono, '
    'sin necesidad de Play Store ni App Store. Crítico para el mercado objetivo '
    'con acceso limitado a tiendas de apps.',
    S_BODY))
f1_pwa = [
    ['Archivo', 'Tipo', 'Descripción'],
    ['public/manifest.json',     'NUEVO',     'Nombre, íconos y colores corporativos de MediCheck'],
    ['public/service-worker.js', 'NUEVO',     'Caché de pantallas principales para uso básico sin internet'],
    ['vite.config.js',           'MODIFICAR', 'Activar plugin vite-plugin-pwa en la configuración del proyecto'],
    ['index.html',               'MODIFICAR', 'Agregar meta tags PWA y theme-color corporativo'],
]
story.append(mk_table(f1_pwa, [4.8*cm, 2*cm, W-6.8*cm], accent=BLUE))
story.append(sp(4))
story.append(Paragraph(
    'Resultado visible: el navegador muestra un banner "Instalar MediCheck" en Android e iOS. '
    'El ícono queda en la pantalla de inicio como si fuera una app nativa.',
    S_NOTE))

# 1.4 Agenda
story.append(sp(10))
story.append(Paragraph('1.4  Agenda de Citas con Calendario', S_H2))
story.append(Paragraph(
    'El flujo actual es solo consulta de texto. Con agenda, el médico programa '
    'seguimientos y el paciente reserva citas — segundo canal de atención complementario.',
    S_BODY))
f1_agenda = [
    ['Archivo', 'Tipo', 'Descripción'],
    ['model/Cita.java',                'NUEVO',     'Entidad: fecha, hora, médico, paciente, estado'],
    ['repository/CitaRepository.java', 'NUEVO',     'Repositorio JPA'],
    ['service/CitaService.java',       'NUEVO',     'Lógica de reserva, confirmación y cancelación de citas'],
    ['controller/CitaController.java', 'NUEVO',     'GET /api/citas/disponibilidad/{id}  ·  POST /api/citas/reservar'],
    ['views/AgendaView.vue',           'NUEVO',     'Vista paciente: calendario con disponibilidad del médico'],
    ['PanelMedicoView.vue',            'MODIFICAR', 'Sección "Mi agenda" + configuración de horarios disponibles'],
    ['router/index.js',                'MODIFICAR', 'Nueva ruta /agenda'],
    ['Sidebar.vue',                    'MODIFICAR', 'Ítem "Agenda" en el menú lateral del paciente'],
]
story.append(mk_table(f1_agenda, [4.8*cm, 2*cm, W-6.8*cm], accent=BLUE))

# 1.5 Receta
story.append(sp(10))
story.append(Paragraph('1.5  Receta Médica Digital en PDF', S_H2))
story.append(Paragraph(
    'Una prescripción con número de licencia, firma del médico y código QR de verificación '
    'transforma MediCheck en una herramienta de trabajo real para el profesional de salud.',
    S_BODY))
f1_receta = [
    ['Archivo', 'Tipo', 'Descripción'],
    ['model/Receta.java',                 'NUEVO',     'Entidad: medicamentos, dosis, frecuencia, duración, médico firmante'],
    ['service/RecetaService.java',         'NUEVO',     'Generación del PDF con Apache PDFBox'],
    ['controller/RecetaController.java',   'NUEVO',     'POST /api/medico/receta  ·  GET /api/medico/receta/{id}/pdf'],
    ['PanelMedicoView.vue',               'MODIFICAR', 'Formulario de prescripción integrado en cada consulta'],
]
story.append(mk_table(f1_receta, [4.8*cm, 2*cm, W-6.8*cm], accent=BLUE))
story.append(sp(4))
story.append(Paragraph(
    'El PDF generado incluye: membrete MediCheck, datos del médico (nombre + licencia + especialidad), '
    'datos del paciente, lista de medicamentos con dosis, código QR de autenticidad y número único de receta.',
    S_NOTE))

story.append(sp(10))
story.append(Paragraph('Impacto de Fase 1 por usuario', S_H2))
story.append(impact_table([
    ['👤  Paciente', '👨‍⚕️  Médico', '🔧  Admin'],
    [
        'Paga con PSE, tarjeta o Nequi. Agenda citas en calendario. '
        'Instala MediCheck como app en su celular. Recibe receta en PDF.',
        'Recibe compensación económica. Gestiona su propia agenda. '
        'Emite prescripciones con nombre y licencia médica.',
        'Visualiza todos los pagos. Configura precios y modelos de cobro. '
        'Accede al historial de recetas.',
    ]
], BLUE))

# ══════════════════════════════════════════════════════════════════════════════
# FASE 2
# ══════════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(section_header('🟡  Fase 2 — Escalabilidad y Confianza', YELLOW))
story.append(sp(8))
story.append(Paragraph(
    '<b>Objetivo:</b>  Agregar los módulos que generan retención de usuarios a largo plazo, '
    'confianza médica y diferenciación frente a la competencia.',
    S_BODY))
story.append(info_box(
    '📅  <b>Duración estimada:</b>  4 a 5 semanas de desarrollo  ·  '
    '<b>Dependencias externas:</b>  Ninguna',
    YELLOW, YELLOW_LIGHT))
story.append(sp(8))

f2 = [
    ['Módulo', 'Archivos principales', 'Dep. ext.'],
    ['Chat médico-paciente\nen tiempo real',
     'Mensaje.java · Reutiliza WebSocket existente · ChatView.vue',
     'Ninguna'],
    ['Notificaciones push',
     'service-worker.js (Push API) · Preferencias en perfil de usuario',
     'Ninguna'],
    ['Calificaciones de médicos',
     'Calificacion.java · CalificacionController.java\nPerfil público con rating promedio',
     'Ninguna'],
    ['Notas SOAP estructuradas',
     'PanelMedicoView.vue — 4 campos clínicos:\nSubjetivo / Objetivo / Evaluación / Plan',
     'Ninguna'],
    ['Perfil de salud completo',
     'PerfilPaciente.java — alergias, medicamentos,\ncrónicas, grupo sanguíneo, antecedentes',
     'Ninguna'],
    ['Autenticación 2FA',
     'Usuario.java — otpCode, otpExpira\nCódigo de 6 dígitos por correo al iniciar sesión',
     'Ninguna'],
    ['Dashboard del médico',
     'PanelMedicoView.vue — pacientes activos,\ndistribución LEVE/MODERADO/GRAVE, rating',
     'Ninguna'],
    ['Exportar historial PDF',
     'HistorialView.vue — botón de descarga\nBackend genera PDF con todas las consultas',
     'PDFBox\n(ya en F1)'],
]
story.append(mk_table(f2, [3.6*cm, 9.8*cm, 2.6*cm], accent=YELLOW))

story.append(sp(10))
story.append(Paragraph('Impacto de Fase 2 por usuario', S_H2))
story.append(impact_table([
    ['👤  Paciente', '👨‍⚕️  Médico', '🔧  Admin'],
    [
        'Chat directo con médico. Notificaciones en tiempo real. '
        'Califica al médico tras cada consulta. '
        'Descarga su historial en PDF. IA más precisa con su perfil de salud.',
        'Canal directo con pacientes. Notas SOAP estándar. '
        'Estadísticas propias de desempeño. '
        'Accede al perfil completo de salud antes de atender.',
        'Métricas globales de la plataforma. '
        'Gestión de calificaciones y reputación de médicos. '
        'Auditoría de accesos y actividad.',
    ]
], YELLOW))

# ══════════════════════════════════════════════════════════════════════════════
# FASE 3
# ══════════════════════════════════════════════════════════════════════════════
story.append(sp(16))
story.append(section_header('🔴  Fase 3 — Revolución y Escala Nacional', RED))
story.append(sp(8))
story.append(Paragraph(
    '<b>Objetivo:</b>  Posicionar MediCheck como plataforma de referencia en salud digital '
    'en Colombia y el mercado hispanohablante, con integración a EPS y análisis epidemiológico.',
    S_BODY))
story.append(info_box(
    '📅  <b>Duración estimada:</b>  6 a 8 semanas de desarrollo  ·  '
    '<b>Dependencia externa:</b>  Negociación comercial con EPS (solo módulo de integración EPS)',
    RED, RED_LIGHT))
story.append(sp(8))

f3 = [
    ['Módulo', 'Descripción', 'Dep. ext.'],
    ['IA con memoria\nlongitudinal',
     'Analiza historial completo del paciente. Detecta patrones.\n"5 consultas por cefalea → recomendar neurología"',
     'Ninguna'],
    ['Salud preventiva',
     'Recordatorios de vacunas (esquema colombiano). Chequeos\nanuales por edad. Consejos por perfil de riesgo.',
     'Ninguna'],
    ['Referidos a\nespecialistas',
     'Médico de cabecera deriva al paciente a un especialista\ndentro de MediCheck con traspaso automático del historial.',
     'Ninguna'],
    ['Seguimiento\ncrónicas',
     'Panel para diabetes, hipertensión, asma, EPOC.\nGráficas de tendencias con alertas automáticas.',
     'Ninguna'],
    ['Epidemiología\nen tiempo real',
     'Dashboard anonimizado de síntomas por ciudad / región.\nDetección de brotes. Fuente de ingresos B2G.',
     'Ninguna'],
    ['Integración EPS',
     'API con Sanitas, Compensar, Nueva EPS, Sura.\nAfiliados acceden a MediCheck como servicio complementario.',
     'Negociación\ncomercial EPS'],
    ['Modo offline\ncompleto',
     'PWA extendida: registro de síntomas sin internet.\nSincronización automática al recuperar conectividad.',
     'Ninguna'],
]
story.append(mk_table(f3, [3.4*cm, 10.4*cm, 2.2*cm], accent=RED))

story.append(sp(10))
story.append(Paragraph('Impacto de Fase 3 por usuario', S_H2))
story.append(impact_table([
    ['👤  Paciente', '👨‍⚕️  Médico', '🔧  Admin'],
    [
        'La IA lo conoce y le avisa proactivamente ante patrones de riesgo. '
        'Recordatorios preventivos personalizados. '
        'Usa MediCheck sin internet. Seguimiento automatizado si tiene condición crónica.',
        'Alertas proactivas por patrones del paciente. '
        'Puede referir a especialistas con traspaso de historial. '
        'Accede a contexto epidemiológico de su zona.',
        'Mapa epidemiológico nacional en tiempo real. '
        'Gestión de contratos EPS. '
        'Reportes para entidades gubernamentales. Modelo B2G habilitado.',
    ]
], RED))

# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN EJECUTIVO
# ══════════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(section_header('📊  Resumen Ejecutivo', GRAY_HEADER))
story.append(sp(10))

resumen = [
    ['Fase', 'Estado', 'Duración estimada', 'Dependencia externa', 'Impacto en el negocio'],
    ['Fase 0', '✅ Completada',   '—',            'Revisión legal\n(recomendada)',          'Blindaje legal mínimo'],
    ['Fase 1', '▶ Lista para\niniciar', '3–4 semanas', 'Cuenta PayU sandbox\n(gratis, ~30 min)', 'Genera ingresos reales'],
    ['Fase 2', '🕐 Planificada', '4–5 semanas', 'Ninguna',                               'Retención y confianza'],
    ['Fase 3', '🕐 Planificada', '6–8 semanas', 'Negociación EPS\n(módulo final)',        'Escala nacional'],
]
tr = Table(resumen, colWidths=[2*cm, 2.4*cm, 3*cm, 3.8*cm, W-11.2*cm])
tr.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0),  GRAY_HEADER),
    ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
    ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8.5),
    ('BACKGROUND',    (0,1), (-1,1),  GREEN_LIGHT),
    ('TEXTCOLOR',     (0,1), (-1,1),  GREEN),
    ('BACKGROUND',    (0,2), (-1,2),  BLUE_LIGHT),
    ('TEXTCOLOR',     (0,2), (-1,2),  BLUE),
    ('BACKGROUND',    (0,3), (-1,3),  YELLOW_LIGHT),
    ('TEXTCOLOR',     (0,3), (-1,3),  YELLOW),
    ('BACKGROUND',    (0,4), (-1,4),  RED_LIGHT),
    ('TEXTCOLOR',     (0,4), (-1,4),  RED),
    ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
    ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ('TOPPADDING',    (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('FONTNAME',      (0,1), (0,-1),  'Helvetica-Bold'),
]))
story.append(tr)

story.append(sp(14))
story.append(Paragraph('Recomendación de Prioridad', S_H1))
story.append(hr())

prio = [
    [Paragraph('🥇  Prioridad 1 — Fase 1', s('pt', fontSize=9.5, fontName='Helvetica-Bold',
               textColor=BLUE)),
     Paragraph(
        'Sin modelo de negocio, ningún evaluador de Enactus ni inversionista tomará '
        'en serio el proyecto, sin importar la calidad tecnológica. '
        'El pago en línea y la agenda de citas son los cambios de mayor impacto percibido.',
        s('pb', fontSize=8.8, fontName='Helvetica', textColor=GRAY_DARK, leading=13))],
    [Paragraph('🥈  Prioridad 2 — Fase 2\n(chat + calificaciones)', s('pt2', fontSize=9.5,
               fontName='Helvetica-Bold', textColor=YELLOW)),
     Paragraph(
        'Son los módulos que más visiblemente mejoran la experiencia del usuario '
        'y la credibilidad ante jurados. Pueden implementarse en paralelo con '
        'partes de la Fase 1 si hay tiempo disponible.',
        s('pb2', fontSize=8.8, fontName='Helvetica', textColor=GRAY_DARK, leading=13))],
    [Paragraph('🔭  Horizonte — Fase 3', s('pt3', fontSize=9.5, fontName='Helvetica-Bold',
               textColor=RED)),
     Paragraph(
        'Es la visión estratégica a 6–12 meses. No es el objetivo inmediato, '
        'pero debe comunicarse a los jurados como evidencia de escalabilidad.',
        s('pb3', fontSize=8.8, fontName='Helvetica', textColor=GRAY_DARK, leading=13))],
]
pt = Table(prio, colWidths=[4.2*cm, W-4.2*cm])
pt.setStyle(TableStyle([
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS',(0,0), (-1,-1), [WHITE, GRAY_LIGHT, WHITE]),
    ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
    ('TOPPADDING',    (0,0), (-1,-1), 9),
    ('BOTTOMPADDING', (0,0), (-1,-1), 9),
    ('LEFTPADDING',   (0,0), (-1,-1), 10),
    ('RIGHTPADDING',  (0,0), (-1,-1), 10),
    ('LINEBEFORE',    (0,0), (0,0),   4, BLUE),
    ('LINEBEFORE',    (0,1), (0,1),   4, YELLOW),
    ('LINEBEFORE',    (0,2), (0,2),   4, RED),
]))
story.append(pt)

# ── DECISIONES
story.append(sp(14))
story.append(Paragraph('Decisiones Pendientes del Equipo', S_H1))
story.append(hr())

decisiones = [
    ['#', 'Decisión requerida'],
    ['1', '¿Está aprobado el texto de la Política de Privacidad en /privacidad?'],
    ['2', '¿Cuál es el modelo de negocio de Fase 1? (pago por consulta, suscripción mensual o ambos)'],
    ['3', '¿Confirmamos el precio por consulta? (propuesta: entre $5.000 y $15.000 COP)'],
    ['4', '¿Creamos ya la cuenta gratuita en PayU para tener el sandbox listo? (~30 min)'],
    ['5', '¿Avanzamos con Fase 1? Si hay acuerdo del equipo, la implementación comienza de inmediato.'],
]
td2 = Table(decisiones, colWidths=[0.8*cm, W-0.8*cm])
td2.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0),  GRAY_HEADER),
    ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
    ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 9),
    ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
    ('TEXTCOLOR',     (0,1), (-1,-1), GRAY_DARK),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, GRAY_LIGHT]),
    ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
    ('FONTNAME',      (0,1), (0,-1),  'Helvetica-Bold'),
    ('TEXTCOLOR',     (0,1), (0,-1),  TEAL),
    ('ALIGN',         (0,0), (0,-1),  'CENTER'),
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ('LEFTPADDING',   (0,0), (-1,-1), 10),
    ('RIGHTPADDING',  (0,0), (-1,-1), 10),
    ('TOPPADDING',    (0,0), (-1,-1), 7),
    ('BOTTOMPADDING', (0,0), (-1,-1), 7),
]))
story.append(td2)

# ── PIE DE DOCUMENTO
story.append(sp(18))
story.append(hr(BORDER, 0.5))
story.append(Paragraph(
    'Documento de uso interno. La información técnica es propiedad intelectual de '
    'Leonardo Gómez — Universidad de La Guajira. '
    'Prohibida su distribución sin autorización del titular del proyecto.',
    s('footer_txt', fontSize=8, fontName='Helvetica-Oblique',
      textColor=GRAY_MID, alignment=TA_CENTER, leading=12)))

# ── BUILD
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print('PDF generado correctamente:', OUTPUT)
