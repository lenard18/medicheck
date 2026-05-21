from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUTPUT = r'L:\medicheck\docs\MediCheck_Solicitud_Mentoria_CesarFletcher.pdf'

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2.5*cm,
    leftMargin=2.5*cm,
    topMargin=2.5*cm,
    bottomMargin=2.5*cm
)

TEAL      = colors.HexColor('#00d4aa')
DARK_BLUE = colors.HexColor('#0d1520')
MUTED     = colors.HexColor('#5a7399')
TEXT      = colors.HexColor('#1a2840')
WHITE     = colors.white

body = ParagraphStyle('body',
    fontName='Helvetica', fontSize=10,
    textColor=TEXT, spaceAfter=6,
    leading=16, alignment=TA_JUSTIFY)

section_title = ParagraphStyle('section_title',
    fontName='Helvetica-Bold', fontSize=13,
    textColor=TEAL, spaceBefore=14, spaceAfter=6, leading=16)

subsection_title = ParagraphStyle('subsection_title',
    fontName='Helvetica-Bold', fontSize=10.5,
    textColor=DARK_BLUE, spaceBefore=8, spaceAfter=4, leading=14)

bullet_style = ParagraphStyle('bullet',
    fontName='Helvetica', fontSize=10,
    textColor=TEXT, leftIndent=16,
    spaceAfter=4, leading=15)

note_style = ParagraphStyle('note',
    fontName='Helvetica-Oblique', fontSize=9,
    textColor=MUTED, leftIndent=12, rightIndent=12,
    spaceAfter=6, leading=13)

footer_style = ParagraphStyle('footer',
    fontName='Helvetica-Oblique', fontSize=8,
    textColor=MUTED, alignment=TA_CENTER, leading=11)

story = []

# ── CABECERA ──────────────────────────────────────────────────────────────────
header_data = [[
    Paragraph('<font color="#ffffff"><b>MediCheck</b></font>',
        ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=26, textColor=WHITE, leading=30)),
    Paragraph(
        '<font color="#00d4aa">Enactus Colombia</font><br/>'
        '<font color="#aaccdd" size="9">Laboratorio de IA &amp; Tecnologia</font>',
        ParagraphStyle('h2', fontName='Helvetica', fontSize=10, textColor=WHITE, leading=14, alignment=1))
]]
header_table = Table(header_data, colWidths=[10*cm, 6*cm])
header_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), DARK_BLUE),
    ('ROWPADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ('LINEBELOW', (0,0), (-1,-1), 3, TEAL),
]))
story.append(header_table)
story.append(Spacer(1, 18))

# ── META DATOS ────────────────────────────────────────────────────────────────
meta_data = [
    ['Para:', 'Cesar Andres Fletcher'],
    ['Email:', 'cesarflet@gmail.com'],
    ['Asunto:', 'Solicitud de mentoria - Proyecto de impacto en salud con IA'],
    ['Fecha:', 'Mayo de 2026'],
]
mt = Table(meta_data, colWidths=[2.2*cm, 13.8*cm])
mt.setStyle(TableStyle([
    ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE', (0,0), (-1,-1), 9.5),
    ('TEXTCOLOR', (0,0), (0,-1), TEAL),
    ('TEXTCOLOR', (1,0), (1,-1), TEXT),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.HexColor('#1a2840')),
]))
story.append(mt)
story.append(Spacer(1, 18))

# ── SALUDO ────────────────────────────────────────────────────────────────────
story.append(Paragraph('Estimado Cesar,',
    ParagraphStyle('saludo', fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BLUE, spaceAfter=8)))

story.append(Paragraph(
    'Mi nombre es <b>Leonardo Gomez</b>, estudiante de <b>Ingenieria de Sistemas</b> en la '
    '<b>Universidad de La Guajira</b> y lider del proyecto <b>MediCheck</b>, desarrollado bajo '
    'el marco de <b>Enactus Colombia</b>.', body))

story.append(Paragraph(
    'Nos comunicamos contigo porque, al revisar el Directorio de Mentores de Enactus Colombia, '
    'tu perfil destaco de manera particular: tu experiencia construyendo productos tecnologicos '
    'reales, tu trayectoria en el ecosistema de emprendimiento e IA aplicada, y tu comprension '
    'de lo que significa convertir una solucion tecnologica en un negocio de impacto sostenible, '
    'son exactamente lo que nuestro equipo necesita en esta etapa del proyecto.', body))

story.append(Paragraph(
    'Por eso, <b>te extendemos una invitacion formal a ser nuestro mentor.</b>', body))

# ── SECCION 1 ─────────────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1.5, color=TEAL, spaceAfter=6))
story.append(Paragraph('Que es MediCheck?', section_title))

story.append(Paragraph(
    'MediCheck es una <b>plataforma digital de salud</b> orientada a reducir una de las brechas '
    'mas persistentes del sistema sanitario colombiano: <b>la desconexion entre pacientes y '
    'profesionales de la salud</b>, especialmente en poblaciones con acceso limitado a servicios '
    'medicos presenciales oportunos.', body))

story.append(Paragraph(
    'La plataforma integra <b>inteligencia artificial, comunicacion medico-paciente en tiempo real '
    'y herramientas de seguimiento clinico</b>, permitiendo que personas que de otro modo no '
    'tendrian acceso a orientacion medica oportuna puedan recibir evaluacion, acompanamiento y '
    'derivacion adecuados desde cualquier lugar.', body))

story.append(Paragraph('El sistema esta disenado para tres actores principales:', body))
story.append(Paragraph('  -  <b>Pacientes:</b> acceso a orientacion medica asistida por IA y seguimiento por un medico asignado.', bullet_style))
story.append(Paragraph('  -  <b>Medicos:</b> herramientas digitales para gestionar y acompanar a sus pacientes de forma remota.', bullet_style))
story.append(Paragraph('  -  <b>Administradores:</b> visibilidad y control sobre la operacion del sistema.', bullet_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'Nota: Por integridad del proyecto y proteccion de la propiedad intelectual del equipo, '
    'los detalles tecnicos especificos seran compartidos en el contexto confidencial de la '
    'mentoria, bajo acuerdo mutuo de reserva de informacion.', note_style))

# ── SECCION 2 ─────────────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1.5, color=TEAL, spaceAfter=6))
story.append(Paragraph('En que etapa estamos?', section_title))

estado_data = [
    ['OK', 'Prototipo funcional completo', 'La plataforma opera end-to-end con modulos integrados.'],
    ['OK', 'Validacion tecnica interna', 'Flujos probados con usuarios de prueba controlados.'],
    ['OK', 'Propuesta de valor clara', 'Sabemos el problema que resolvemos y para quien.'],
    ['>>',  'Modelo de negocio', 'En construccion - sostenible y escalable.'],
    ['>>',  'Medicion de impacto', 'En construccion - metodologia con beneficiarios reales.'],
    ['>>',  'Narrativa de competencia', 'En construccion - alineada al Criterio Enactus.'],
    ['>>',  'Piloto en campo', 'Pendiente - despliegue con pacientes y medicos reales.'],
]
et = Table(estado_data, colWidths=[0.9*cm, 4.5*cm, 10.6*cm])
et.setStyle(TableStyle([
    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
    ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
    ('TEXTCOLOR', (0,0), (0,2), TEAL),
    ('TEXTCOLOR', (0,3), (0,-1), colors.HexColor('#ffbe0b')),
    ('TEXTCOLOR', (1,0), (-1,-1), TEXT),
    ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#f0fefa'), colors.white]),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#d0e8e0')),
]))
story.append(et)

# ── SECCION 3 ─────────────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1.5, color=TEAL, spaceAfter=6))
story.append(Paragraph('Por que necesitamos un mentor como tu?', section_title))

story.append(Paragraph(
    'Somos conscientes de que tener una tecnologia funcional no es suficiente para ganar una '
    'competencia Enactus, ni para generar impacto real. Lo que nos falta no es tecnico: '
    '<b>es la capa de impacto, sostenibilidad y narrativa.</b>', body))

areas = [
    ('1. Modelo de negocio con proposito',
     'Estructurar un modelo sostenible financieramente sin perder la esencia de impacto social. '
     'Fuentes de ingresos, segmentos de clientes y propuesta de valor economica para cada actor.'),
    ('2. Medicion de impacto real',
     'El Criterio Enactus evalua resultados obtenidos, no intenciones. Necesitamos una metodologia '
     'para medir el impacto directo en personas de forma verificable y creible ante jueces.'),
    ('3. Estrategia de piloto con usuarios reales',
     'Disenar e implementar un piloto controlado con pacientes y medicos reales, de manera etica, '
     'legal y con capacidad de generar datos de impacto documentados.'),
    ('4. Narrativa y posicionamiento para competencia',
     'Los jueces no evaluan la tecnologia, evaluan la historia de transformacion humana detras '
     'de ella. Necesitamos construir esa narrativa clara, honesta y convincente bajo el marco Enactus.'),
    ('5. Escalabilidad y vision de largo plazo',
     'Como pasa MediCheck de prototipo a solucion de impacto a escala nacional o regional.'),
]
for t_area, d_area in areas:
    story.append(Paragraph(t_area, subsection_title))
    story.append(Paragraph(d_area, body))

# ── SECCION 4 ─────────────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1.5, color=TEAL, spaceAfter=6))
story.append(Paragraph('Que te pedimos?', section_title))

story.append(Paragraph('No esperamos que resuelvas nuestros desafios por nosotros. Lo que buscamos es:', body))
pedidos = [
    'Sesiones periodicas de mentoria (frecuencia y formato conveniente para ti).',
    'Retroalimentacion honesta y directa sobre nuestras decisiones y brechas.',
    'Orientacion estrategica para priorizar lo que realmente importa en esta etapa.',
    'Tu red y perspectiva para identificar alianzas y oportunidades que no estamos viendo.',
]
for p in pedidos:
    story.append(Paragraph(f'  -  {p}', bullet_style))

story.append(Spacer(1, 6))
story.append(Paragraph(
    'Tenemos equipo, tecnologia y voluntad. Lo que nos falta es la guia de alguien que ya ha '
    'recorrido el camino de convertir una idea tecnologica en un producto de impacto real.', body))

# ── SECCION 5 ─────────────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1.5, color=TEAL, spaceAfter=6))
story.append(Paragraph('Por que tu?', section_title))

story.append(Paragraph(
    'Porque en el directorio de mentores de Enactus Colombia, eres el unico perfil que combina '
    'tres cosas que MediCheck necesita simultaneamente:', body))

story.append(Paragraph('  -  <b>Experiencia construyendo productos de IA reales</b> - no solo teoria academica.', bullet_style))
story.append(Paragraph('  -  <b>Vision emprendedora y de negocio</b> - 18+ anos en consultoria TI y creacion de startups propias.', bullet_style))
story.append(Paragraph('  -  <b>Trayectoria en mentoria de emprendimientos</b> - sabes acompanar equipos, no solo dar conferencias.', bullet_style))

story.append(Spacer(1, 8))
story.append(Paragraph(
    'Creemos que bajo tu guia, MediCheck puede convertirse en un proyecto que no solo gane una '
    'competencia universitaria, sino que <b>genere un cambio real en como las personas acceden '
    'a la salud en Colombia.</b>', body))

# ── PROXIMOS PASOS ────────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1.5, color=TEAL, spaceAfter=6))
story.append(Paragraph('Proximos pasos', section_title))

story.append(Paragraph(
    'Si estas dispuesto a conocernos, te proponemos una <b>primera llamada de 30 minutos</b> '
    '(virtual, sin compromiso) para presentarte el proyecto con mayor detalle, responder tus '
    'preguntas y evaluar juntos si existe afinidad para trabajar en equipo.', body))

story.append(Paragraph(
    'Quedamos atentos a tu respuesta y agradecemos profundamente tu tiempo y consideracion.', body))

# ── FIRMA ─────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 16))
story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#1a2840'), spaceAfter=12))

firma_data = [[
    Paragraph('Atentamente,',
        ParagraphStyle('at', fontName='Helvetica', fontSize=9, textColor=MUTED, spaceAfter=6)),
    ''
],[
    Paragraph('<b>Leonardo Gomez</b>',
        ParagraphStyle('fn', fontName='Helvetica-Bold', fontSize=12, textColor=DARK_BLUE)),
    Paragraph('<b>MediCheck</b>',
        ParagraphStyle('mc', fontName='Helvetica-Bold', fontSize=20, textColor=TEAL, alignment=2))
],[
    Paragraph(
        'Lider del Proyecto MediCheck<br/>'
        'Equipo Enactus - Universidad de La Guajira<br/>'
        'Email: LG358356@gmail.com<br/>'
        'Tel: 300 279 3410',
        ParagraphStyle('fi', fontName='Helvetica', fontSize=9.5, textColor=TEXT, leading=15)),
    Paragraph(
        '<font color="#5a7399" size="8">Proyecto de impacto en salud<br/>'
        'Laboratorio IA &amp; Tecnologia - Enactus Colombia</font>',
        ParagraphStyle('fi2', fontName='Helvetica', fontSize=8, textColor=MUTED, alignment=2, leading=12))
]]

ft = Table(firma_data, colWidths=[10*cm, 6*cm])
ft.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('TOPPADDING', (0,0), (-1,-1), 4),
]))
story.append(ft)

# ── FOOTER ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 20))
story.append(HRFlowable(width='100%', thickness=0.3, color=MUTED, spaceAfter=6))
story.append(Paragraph(
    'Este documento contiene informacion de caracter confidencial y esta dirigido exclusivamente '
    'a su destinatario. La informacion aqui descrita sobre el proyecto MediCheck es propiedad '
    'intelectual del equipo y no debe ser reproducida, distribuida ni utilizada sin autorizacion expresa.',
    footer_style))

doc.build(story)
print('PDF generado en:', OUTPUT)
