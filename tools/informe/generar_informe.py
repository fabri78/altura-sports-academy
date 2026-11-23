"""Genera el informe final a partir de la plantilla del docente.

Conserva la carátula, los estilos, el encabezado y el índice de la plantilla, y reemplaza
el cuerpo por el contenido del proyecto ALTURA Sports Academy.

Uso:
  python -I tools/informe/generar_informe.py "<plantilla.docx>" "<salida.docx>" <url_publicacion> <url_repositorio>
"""
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLA, SALIDA, URL_PUB, URL_REPO = sys.argv[1:5]

# --------------------------------------------------------------------------
# Utilidades de WordprocessingML
# --------------------------------------------------------------------------
RPR = '<w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:lang w:val="es-PE"/>'


def run(texto, negrita=False, cursiva=False, tam=None, color=None):
    extra = ("<w:b/><w:bCs/>" if negrita else "") + ("<w:i/>" if cursiva else "")
    if color:
        extra += f'<w:color w:val="{color}"/>'
    if tam:
        extra += f'<w:sz w:val="{tam}"/><w:szCs w:val="{tam}"/>'
    return f'<w:r><w:rPr>{RPR}{extra}</w:rPr><w:t xml:space="preserve">{escape(texto)}</w:t></w:r>'


def runs(texto, **kw):
    """Admite **negrita** dentro del texto."""
    partes = re.split(r"(\*\*[^*]+\*\*)", texto)
    return "".join(run(p[2:-2], negrita=True, **kw) if p.startswith("**") else run(p, **kw) for p in partes if p)


def p(texto, estilo="Textoindependiente", jc="both", ind='w:left="762" w:right="400"', antes=0, despues=120):
    return (f'<w:p><w:pPr><w:pStyle w:val="{estilo}"/><w:spacing w:before="{antes}" w:after="{despues}" w:line="276" w:lineRule="auto"/>'
            f'<w:ind {ind}/><w:jc w:val="{jc}"/><w:rPr>{RPR}</w:rPr></w:pPr>{runs(texto)}</w:p>')


def vineta(texto):
    return (f'<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="23"/></w:numPr>'
            f'<w:spacing w:after="60" w:line="276" w:lineRule="auto"/><w:ind w:left="1122" w:hanging="360"/><w:jc w:val="both"/>'
            f'<w:rPr>{RPR}<w:sz w:val="24"/></w:rPr></w:pPr>{runs(texto, tam=24)}</w:p>')


def salto_pagina():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def h2(texto):
    return (f'{salto_pagina()}<w:p><w:pPr><w:pStyle w:val="Ttulo2"/><w:spacing w:before="0" w:after="240"/><w:ind w:left="0"/>'
            f'<w:jc w:val="center"/><w:rPr>{RPR}</w:rPr></w:pPr>{run(texto, tam=28, negrita=True)}</w:p>')


def h3(texto):
    return (f'<w:p><w:pPr><w:pStyle w:val="Ttulo3"/><w:keepNext/><w:spacing w:before="240" w:after="120"/><w:ind w:left="402"/>'
            f'<w:jc w:val="both"/><w:rPr>{RPR}</w:rPr></w:pPr>{run(texto, negrita=True, tam=24)}</w:p>')


def h4(texto):
    return (f'<w:p><w:pPr><w:pStyle w:val="Ttulo4"/><w:keepNext/><w:spacing w:before="180" w:after="80"/><w:ind w:left="762"/>'
            f'<w:rPr>{RPR}</w:rPr></w:pPr>{run(texto, negrita=True, tam=24, color="1F3864")}</w:p>')


def titulo1(texto):
    return (f'{salto_pagina()}<w:p><w:pPr><w:pStyle w:val="Ttulo1"/><w:spacing w:after="240"/><w:rPr>{RPR}</w:rPr></w:pPr>'
            f'{run(texto, negrita=True, tam=32)}</w:p>')


def campo(instruccion, resultado="1"):
    return (f'<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> {instruccion} </w:instrText></w:r>'
            f'<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:rPr><w:noProof/></w:rPr><w:t>{resultado}</w:t></w:r>'
            f'<w:r><w:fldChar w:fldCharType="end"/></w:r>')


CONT = {"Ilustración": 0, "Tabla": 0}


def leyenda(tipo, texto):
    CONT[tipo] += 1
    return (f'<w:p><w:pPr><w:pStyle w:val="Descripcin"/><w:keepNext w:val="{1 if tipo == "Tabla" else 0}"/><w:jc w:val="center"/>'
            f'<w:rPr>{RPR}</w:rPr></w:pPr>{run(tipo + " ")}{campo(f"SEQ {tipo} \\* ARABIC", CONT[tipo])}{run(". " + texto)}</w:p>')


IMAGENES = []  # (rId, nombre_media, ruta)


def imagen(ruta, texto, ancho_cm=15.0, alto_max_cm=19.0):
    ruta = Path(ruta)
    n = len(IMAGENES) + 1
    rid = f"rIdAlt{n}"
    nombre = f"alt{n:02d}{ruta.suffix.lower().replace('.jpeg', '.jpg')}"
    IMAGENES.append((rid, nombre, ruta))
    w, h = Image.open(ruta).size
    cx = int(ancho_cm * 360000)
    cy = int(cx * h / w)
    if cy > alto_max_cm * 360000:
        cy = int(alto_max_cm * 360000)
        cx = int(cy * w / h)
    dibujo = (
        f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:docPr id="{1000 + n}" name="Imagen {n}" descr="{escape(texto)}"/>'
        f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{1000 + n}" name="{nombre}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:ln w="6350"><a:solidFill><a:srgbClr val="D2D2D7"/></a:solidFill></a:ln></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
    )
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/><w:jc w:val="center"/></w:pPr>{dibujo}</w:p>'
            + leyenda("Ilustración", texto))


def tabla(titulo, encabezados, filas, anchos):
    """anchos en twips; suman como máximo 8600."""
    total = sum(anchos)
    borde = '<w:top w:val="single" w:sz="4" w:color="BFBFBF"/><w:left w:val="single" w:sz="4" w:color="BFBFBF"/><w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/><w:right w:val="single" w:sz="4" w:color="BFBFBF"/><w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/><w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/>'

    def celda(texto, ancho, cabecera=False):
        sombra = '<w:shd w:val="clear" w:color="auto" w:fill="1D1D1F"/>' if cabecera else ""
        color = "FFFFFF" if cabecera else None
        return (f'<w:tc><w:tcPr><w:tcW w:w="{ancho}" w:type="dxa"/>{sombra}<w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:pStyle w:val="TableParagraph"/><w:spacing w:before="40" w:after="40"/><w:ind w:left="60" w:right="60"/></w:pPr>'
                f'{runs(str(texto), tam=19, color=color) if not cabecera else run(str(texto), negrita=True, tam=19, color=color)}</w:p></w:tc>')

    xml = leyenda("Tabla", titulo)
    xml += (f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>{borde}</w:tblBorders>'
            f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid>{"".join(f"<w:gridCol w:w=\"{a}\"/>" for a in anchos)}</w:tblGrid>')
    xml += '<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' + "".join(celda(t, a, True) for t, a in zip(encabezados, anchos)) + "</w:tr>"
    for fila in filas:
        xml += '<w:tr><w:trPr><w:cantSplit/></w:trPr>' + "".join(celda(t, a) for t, a in zip(fila, anchos)) + "</w:tr>"
    return xml + '</w:tbl><w:p><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>'


def indice(tipo, titulo):
    return (f'{salto_pagina()}<w:p><w:pPr><w:pStyle w:val="Ttulo2"/><w:ind w:left="0"/><w:jc w:val="center"/><w:rPr>{RPR}</w:rPr></w:pPr>{run(titulo, negrita=True, tam=28)}</w:p>'
            f'<w:p><w:pPr><w:pStyle w:val="Tabladeilustraciones"/><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8600"/></w:tabs></w:pPr>'
            f'{campo(f"TOC \\h \\z \\c &quot;{tipo}&quot;", "Actualice el índice (clic derecho > Actualizar campo).")}</w:p>')


# --------------------------------------------------------------------------
# Datos del proyecto
# --------------------------------------------------------------------------
metricas = json.loads((RAIZ / "docs" / "metricas.json").read_text(encoding="utf-8"))
creditos = json.loads((RAIZ / "docs" / "creditos-multimedia.json").read_text(encoding="utf-8"))
CAP = RAIZ / "docs" / "capturas"
DIA = RAIZ / "docs" / "diagramas"

paginas = [
    ("inicio", "Inicio (index.html)", "Hero con el titular “Salta más alto.”, marquesina de avisos, galería horizontal de lo más destacado con flechas y puntos, cifras animadas, bento de academias, video con subtítulos, avance de la tienda, blog y llamado a la acción final."),
    ("nosotros", "Nosotros", "Historia en línea de tiempo, misión y visión en la rejilla de 12 columnas de Material Design, valores, organigrama y descripción de la sede."),
    ("academias", "Academias", "Tarjetas por disciplina con color propio generado con un bucle @each de SASS y tabla comparativa de programas con caption, thead, tbody y tfoot."),
    ("basquet", "Academia de Básquet", "Subnavegación local fija, hero con zoom ligado al scroll, sección fija con cuatro etapas del método, tabla de datos de Material Design e iframe de YouTube."),
    ("aerobicos", "Aeróbicos y fitness", "Clases, reproductor de audio con la pista original de 128 BPM, horario semanal incrustado en un iframe interno y planes alineados con subgrid."),
    ("natacion", "Natación", "Banner con video de fondo, niveles en la rejilla de Material Design, video con subtítulos y preguntas frecuentes con details y summary."),
    ("horarios", "Horarios y tarifas", "Calendario semanal hecho con CSS Grid y tablas completas con rowspan y colspan dentro de pestañas de Material Design."),
    ("entrenadores", "Entrenadores", "Tarjetas que giran en 3D (perspective, rotateY y backface-visibility) con la trayectoria de cada entrenador."),
    ("tienda", "Tienda", "Banner promocional, barra lateral con filtros por categoría (chips) y precio, orden por precio y catálogo de nueve productos con contador de carrito."),
    ("producto", "Ficha de producto", "Selector de color hecho solo con CSS (radio + combinador ~), tallas, botón de compra y tabla de especificaciones."),
    ("eventos", "Eventos y torneos", "Marquesina con resultados, calendario de eventos con estados, cinta de patrocinadores animada en CSS y tabla del formato del torneo."),
    ("galeria", "Galería multimedia", "Mosaico con grid denso y lightbox con :target, videos, audios, elemento picture con dirección de arte y créditos de licencias."),
    ("blog", "Blog", "Artículo destacado, rejilla de artículos, barra lateral con categorías, etiquetas y formulario de boletín."),
    ("articulo", "Artículo del blog", "Texto largo con capitular (::first-letter), cita, abreviaturas, lista, barra de progreso de lectura y botones para compartir."),
    ("matricula", "Matrícula (formulario de clientes)", "Formulario en tres pasos con campos de Material Design, tarjetas de opción, botones de opción, casilla de aceptación y validación HTML5."),
    ("contacto", "Contacto", "Formulario de contacto, tarjetas con información de contacto y mapa de OpenStreetMap en un iframe, organizado con grid-template-areas."),
    ("reclamos", "Libro de Reclamaciones", "Hoja de reclamación según la Ley N.° 29571 con identificación del consumidor, bien contratado, detalle y número asignado al enviar."),
]

# --------------------------------------------------------------------------
# Cuerpo del informe
# --------------------------------------------------------------------------
B = []
A = B.append

# Índices de figuras y tablas
B.append(indice("Ilustración", "ÍNDICE DE FIGURAS"))
B.append(indice("Tabla", "ÍNDICE DE TABLAS"))

# Historial de versiones
A(h2("HISTORIAL DE VERSIONES"))
A(tabla("Historial de versiones del proyecto", ["Fecha", "Versión", "Elaborado por", "Descripción", "Revisado por", "Fecha de revisión"], [
    ["23-11-2026", "1.0", "F. Quispe", "Alcance inicial: estructura, capas de estilo y 8 páginas (etiqueta v1.0).", "", ""],
    ["23-11-2026", "2.0", "F. Quispe", "Ampliación del alcance: 18 páginas, tienda, formularios y multimedia (v2.0).", "", ""],
    ["23-11-2026", "3.0", "F. Quispe", "Incremento: animaciones, responsive, marcos, Docker y métricas (v3.0).", "", ""],
    ["24-11-2026", "4.0", "F. Quispe", "Entrega final: publicación en GitHub Pages e informe (v4.0).", "", ""],
], [1150, 850, 1150, 3100, 1150, 1200]))
A(p("Cada versión del documento corresponde a una etiqueta (tag) del repositorio Git, de modo que el historial del informe y el del código coinciden."))

# Resumen
A(h2("RESUMEN"))
A(p("El presente trabajo desarrolla el sitio web frontend de **ALTURA Sports Academy**, una academia deportiva ficticia ubicada en Yanahuara, Arequipa, a 2 335 metros sobre el nivel del mar. La organización ofrece programas de básquet para niños y jóvenes, aeróbicos y fitness para adultos, natación para todas las edades y una tienda de artículos deportivos. Su rubro es el de servicios deportivos y venta minorista de implementos."))
A(p("La academia atiende matrículas, consultas y reclamos solo por WhatsApp y en recepción; publica horarios y tarifas como imágenes sueltas que quedan desactualizadas; no tiene un catálogo en línea de su tienda y carece de un canal formal para el Libro de Reclamaciones exigido por INDECOPI."))
A(p("Para resolverlo se construyó un sitio web de 17 páginas más una página de error 404, con HTML5 y hojas de estilo externas. Siguiendo los componentes asignados al Grupo 04, los estilos se escribieron con **CSS**, el preprocesador **LESS**, el preprocesador **SASS** y el framework **Material Design CSS (MDC Web 14)**, enlazado por CDN. El diseño visual toma como referencia la página del iPhone 18 Pro de Apple: secciones negras y gris carbón, tipografía grande, botones en píldora y animaciones suaves al hacer scroll. El código se versiona con Git, se aloja en GitHub y se publica con GitHub Pages."))
A(p("Los módulos principales son: academias (básquet, aeróbicos, natación y entrenadores), horarios y tarifas, tienda (catálogo y ficha de producto), comunidad (eventos, galería y blog) y atención al cliente (matrícula, contacto y Libro de Reclamaciones)."))

A(h2("ABSTRACT"))
A(p("This project delivers the front-end website of ALTURA Sports Academy, a fictional sports academy and sporting-goods store in Arequipa, Peru, located 2,335 meters above sea level. The academy currently handles enrollment, inquiries and complaints only through WhatsApp and its front desk, publishes schedules as loose images and has no online catalog. The solution is a 17-page website plus a 404 page built with HTML5 and external style sheets written in plain CSS, LESS, SASS and the Material Design CSS framework (MDC Web 14). Its visual style follows Apple’s iPhone 18 Pro product page: dark sections, large type, pill-shaped buttons and scroll-driven animations. The code is versioned with Git, hosted on GitHub and published with GitHub Pages. The main modules are academies, schedules and fees, the online store, community content (events, gallery and blog) and customer service (enrollment, contact and the complaints book)."))

# Capítulo 1
A(h2("CAPÍTULO 1 ASPECTOS GENERALES"))
A(h3("1.1 DEFINICIÓN DEL PROBLEMA"))
A(h3("1.1.1 DESCRIPCIÓN DEL PROBLEMA"))
A(p("ALTURA Sports Academy S.A.C. (RUC 20612345678, datos ficticios) funciona desde 2014 en la Av. Ejército 1020, Yanahuara, Arequipa. Atiende a 640 alumnos con 18 entrenadores y cuenta con un coliseo techado con cancha FIBA, una piscina semiolímpica temperada, un salón de aeróbicos y una tienda deportiva. Sus áreas son la Dirección deportiva (básquet, aeróbicos, natación y fisioterapia), Administración (matrículas, caja y reclamos), Tienda (ventas e inventario) y Marketing (redes, eventos y blog)."))
A(p("Los problemas identificados son:"))
for t in [
    "Las matrículas y consultas se atienden solo por WhatsApp y en recepción, lo que satura al personal administrativo en temporada alta.",
    "Los horarios y tarifas se publican como imágenes en redes sociales y quedan desactualizados.",
    "La tienda no tiene catálogo en línea, y los alumnos no saben qué equipo comprar para su nivel.",
    "No existe un Libro de Reclamaciones virtual, obligatorio para los proveedores según la Ley N.° 29571.",
    "La marca no tiene un sitio propio que transmita su propuesta de valor: entrenar en altura.",
]:
    A(vineta(t))
A(imagen(DIA / "organigrama.png", "Organigrama de ALTURA Sports Academy"))
A(h4("Visión:"))
A(p("Ser al 2030 la academia deportiva de referencia del sur del Perú, reconocida por convertir el entrenamiento en altura en una ventaja para sus alumnos."))
A(h4("Misión:"))
A(p("Formar deportistas y personas más saludables en Arequipa con programas de básquet, aeróbicos y natación guiados por entrenadores certificados, y ofrecer el equipo adecuado para cada nivel."))
A(h4("Entorno:"))
A(p("Arequipa cuenta con varios gimnasios y escuelas deportivas, pero pocas ofrecen varias disciplinas y una tienda especializada en un mismo lugar. El público objetivo son familias con hijos de 6 a 17 años y adultos de 18 a 55 años de los distritos de Yanahuara, Cayma y Cercado, que buscan información y se inscriben desde el celular."))

A(h3("1.2 DEFINICIÓN DE OBJETIVOS DEL PROYECTO"))
A(h3("1.2.1 OBJETIVO GENERAL"))
A(p("Construir el sitio web frontend de ALTURA Sports Academy, responsivo y publicado en la nube, que permita conocer las academias, consultar horarios y tarifas, explorar la tienda, matricularse, contactar y registrar reclamos en línea, aplicando CSS, LESS, SASS y el framework Material Design CSS."))
A(h3("1.2.2 OBJETIVOS ESPECÍFICOS"))
for t in [
    "Diseñar 17 páginas con estructura HTML5 completa (encabezado con menú, cuerpo y pie de página) y una página de error 404.",
    "Organizar los estilos en archivos externos con el reparto pedido: CSS 10 %, LESS 15 %, SASS 15 %, animaciones 20 %, media queries y multimedia 20 %, Flexbox y Grid 20 %.",
    "Implementar formularios de clientes (matrícula), contacto y reclamos con validación en el navegador.",
    "Lograr que el sitio se vea correctamente en celulares, tabletas y computadoras.",
    "Versionar el proyecto con Git en cuatro entregas y publicarlo con GitHub Pages.",
]:
    A(vineta(t))

A(h3("1.2.3 ALCANCES Y LIMITACIONES"))
A(h3("1.2.3.1 Dentro del Alcance"))
for t in [
    "**Academias:** páginas de básquet, aeróbicos y fitness, natación y entrenadores.",
    "**Horarios y tarifas:** calendario semanal y tablas de precios por disciplina.",
    "**Tienda:** catálogo con filtros y orden, ficha de producto con selector de color y talla, carrito de demostración.",
    "**Comunidad:** eventos y torneos, galería multimedia, blog y artículo.",
    "**Atención:** formularios de matrícula, contacto y Libro de Reclamaciones; información de contacto y mapa.",
    "**Institucional:** inicio, nosotros (historia, misión, visión, valores, organigrama) y página 404.",
]:
    A(vineta(t))
A(h3("1.2.3.2 Fuera del Alcance"))
for t in [
    "Backend, base de datos y envío real de formularios (los datos no se guardan en un servidor).",
    "Pasarela de pagos y procesamiento real del carrito de compras.",
    "Cuentas de usuario, inicio de sesión y panel administrativo.",
]:
    A(vineta(t))
A(h3("1.2.3.3 Limitaciones"))
for t in [
    "La empresa es ficticia, por lo que los precios, horarios y datos de contacto son de ejemplo.",
    "Las fotos provienen de Wikimedia Commons con licencias libres y los videos se generaron a partir de ellas; no hay sesión fotográfica ni filmación propia.",
    "El framework MDC Web está en modo de mantenimiento por Google, aunque es la versión oficial y estable de Material Design para la web.",
    "Las etiquetas marquee y frameset son obsoletas en HTML5; se incluyen porque los lineamientos las piden.",
]:
    A(vineta(t))

A(h3("1.2.4 JUSTIFICACIÓN"))
A(p("Hoy la mayoría de familias busca y compara academias desde el celular. Sin un sitio propio, ALTURA depende de mensajes uno a uno, pierde interesados fuera del horario de atención y no cumple con ofrecer un Libro de Reclamaciones virtual. El sitio reduce la carga de recepción, mantiene horarios y precios actualizados en un solo lugar, da a conocer la tienda y refuerza la marca. Si no se construye, la academia seguirá atendiendo de forma manual, con información dispersa y con riesgo de sanción por no contar con el canal de reclamos."))

A(h3("1.3 EQUIPO DE TRABAJO"))
A(tabla("Roles y responsabilidades del equipo", ["Integrante", "Rol", "Responsabilidades"], [
    ["Quispe Morales, Fabricio Oscar (U25316441)", "Líder del proyecto y desarrollador front-end", "Planificación, maquetación HTML, estilos CSS, LESS, SASS y Material Design, control de versiones y publicación."],
    ["Quispe Morales, Fabricio Oscar", "Diseño UX/UI y contenido", "Dirección visual, prototipos, textos, selección de multimedia e ilustraciones."],
    ["Quispe Morales, Fabricio Oscar", "QA y documentación", "Pruebas en navegador y dispositivos, métricas de código, informe y exposición."],
], [2600, 2300, 3700]))

A(h3("1.4 RECURSOS Y PRESUPUESTO"))
A(tabla("Recursos y presupuesto estimado del proyecto", ["Recurso", "Detalle", "Cantidad", "Costo (S/)"], [
    ["Hardware", "Laptop de desarrollo (depreciación del periodo)", "1", "150.00"],
    ["Software", "Visual Studio Code, Node.js, Git, navegadores", "—", "0.00 (libre)"],
    ["Frameworks", "LESS, SASS, MDC Web 14, Google Fonts, Material Symbols", "—", "0.00 (libre)"],
    ["Hosting", "GitHub y GitHub Pages", "1", "0.00"],
    ["Dominio (opcional)", "alturasports.pe por un año", "1", "120.00"],
    ["Servicios", "Internet y energía del periodo", "—", "60.00"],
    ["Recurso humano", "Horas de desarrollo y documentación", "30 h × S/ 25", "750.00"],
    ["", "**Total estimado**", "", "**1 080.00**"],
], [1700, 3900, 1400, 1600]))

A(h3("1.5 CRONOGRAMA DE ACTIVIDADES"))
A(tabla("Cronograma de actividades", ["Fase", "Actividad", "Inicio", "Fin"], [
    ["Inicio", "Análisis de lineamientos, plantilla del informe y referencia visual", "23-11-2026 08:00", "23-11-2026 10:00"],
    ["Planificación", "Plan de desarrollo, sistema de diseño y mapa del sitio", "23-11-2026 10:00", "23-11-2026 12:00"],
    ["Ejecución", "v1.0: estructura, capas de estilo y 8 páginas", "23-11-2026 12:00", "23-11-2026 14:00"],
    ["Ejecución", "v2.0: 10 páginas más, tienda, formularios y multimedia", "23-11-2026 14:00", "23-11-2026 16:00"],
    ["Ejecución", "v3.0: animaciones, responsive, marcos y ajuste de métricas", "23-11-2026 16:00", "23-11-2026 18:00"],
    ["Supervisión y control", "Verificación de enlaces, pruebas en navegador, capturas", "23-11-2026 18:00", "23-11-2026 19:00"],
    ["Cierre", "Informe, publicación en GitHub Pages y versión v4.0", "23-11-2026 19:00", "24-11-2026 07:00"],
], [1700, 3700, 1600, 1600]))
A(h3("1.6 CRONOGRAMA DE HITOS DEL PROYECTO"))
A(tabla("Hitos del proyecto", ["Hito", "Entregable", "Fecha"], [
    ["H1", "Plan de desarrollo aprobado", "23-11-2026"],
    ["H2", "Versión v1.0 (alcance inicial)", "23-11-2026"],
    ["H3", "Versión v2.0 (ampliación del alcance)", "23-11-2026"],
    ["H4", "Versión v3.0 (incremento de resultados)", "23-11-2026"],
    ["H5", "Versión v4.0 publicada e informe en PDF", "24-11-2026"],
    ["H6", "Entrega en UTP+CLASS y exposición", "24-11-2026"],
], [900, 5700, 2000]))

# Capítulo 2
A(h2("CAPÍTULO 2 MARCO TEÓRICO"))
A(h3("2.1 FUNDAMENTO TEÓRICO"))
A(imagen(DIA / "conceptual.png", "Mapa conceptual de las tecnologías del proyecto"))
for titulo, texto in [
    ("HTML5", "HTML (HyperText Markup Language) es el lenguaje de marcado que define la estructura y el significado del contenido web. HTML5 agrega elementos semánticos (header, nav, main, section, article, aside, footer), controles de formulario con validación nativa y soporte directo para audio y video (MDN Web Docs, 2024; WHATWG, 2024)."),
    ("CSS3", "Las Hojas de Estilo en Cascada (CSS) describen la presentación de un documento HTML. La cascada, la especificidad y la herencia determinan qué regla se aplica a cada elemento. Los estilos se escriben en archivos externos enlazados con link, lo que separa contenido y presentación (W3C, 2024)."),
    ("LESS", "LESS es un preprocesador que extiende CSS con variables, mixins con parámetros, guards (condiciones), anidamiento, operaciones y funciones de color. El código .less se compila a CSS estándar con lessc (Less.js, 2024)."),
    ("SASS", "SASS es un preprocesador con sintaxis SCSS que añade variables, mapas, funciones (@function), mixins con bloques de contenido (@content), bucles (@each), herencia con %placeholder y @extend, y un sistema de módulos con @use y @forward (Sass, 2024)."),
    ("Material Design y MDC Web", "Material Design es el sistema de diseño de Google. Material Components for the Web (MDC Web) es su implementación oficial en CSS y JavaScript: botones con efecto ripple, campos de texto, casillas, pestañas, tablas de datos, snackbar y una rejilla de 12, 8 y 4 columnas con puntos de corte en 600, 905 y 1240 px. Se personaliza con variables CSS como --mdc-theme-primary (Google, 2023)."),
    ("Diseño web responsivo", "Consiste en adaptar un sitio a cualquier tamaño de pantalla con unidades relativas, media queries, consultas de contenedor (@container) e imágenes y videos fluidos (Marcotte, 2011; MDN Web Docs, 2024)."),
    ("Flexbox y CSS Grid", "Flexbox distribuye elementos en una dimensión (fila o columna); CSS Grid organiza filas y columnas a la vez, con áreas con nombre (grid-template-areas), auto-fit y subgrid para alinear tarjetas hermanas (MDN Web Docs, 2024)."),
    ("Animaciones, transiciones y transformaciones", "Las transiciones animan el cambio entre dos estados; @keyframes define animaciones de varios pasos; transform traslada, escala y rota en 2D y 3D. Las animaciones ligadas al scroll (animation-timeline) permiten efectos que avanzan con el desplazamiento, como en la página de referencia de Apple (W3C, 2024)."),
    ("Git, GitHub y GitHub Pages", "Git es un sistema de control de versiones distribuido; GitHub aloja repositorios en la nube y GitHub Pages publica sitios estáticos desde un repositorio, en este caso mediante un flujo de GitHub Actions (Chacon y Straub, 2014; GitHub, 2024)."),
]:
    A(h4(titulo))
    A(p(texto))

# Capítulo 3
A(h2("CAPÍTULO 3 DESARROLLO DE LA SOLUCIÓN"))
A(h3("3.1 PROJECT CHARTER"))
A(h3("3.1.1 NOMBRE DEL PROYECTO"))
A(p("**ALTURA Sports Academy: sitio web de academia y tienda deportiva con LESS, SASS y Material Design.**"))
A(h3("3.1.2 DESCRIPCIÓN DEL PROYECTO"))
for t in [
    "**Para quién:** ALTURA Sports Academy, sus alumnos, padres de familia y clientes de la tienda.",
    "**Objetivo:** dar a la academia un sitio web responsivo para informar, matricular, vender y atender reclamos.",
    "**Quiénes lo realizan:** Grupo 04 del curso Hojas de Estilo en Cascada Avanzado (Quispe Morales, Fabricio Oscar).",
    "**Fechas:** del 23 al 24 de noviembre de 2026.",
]:
    A(vineta(t))
A(h3("3.2 DEFINICIÓN DEL PRODUCTO"))
A(h3("3.2.1 CARACTERÍSTICAS DEL SISTEMA"))
A(tabla("Características del sistema", ["ID", "Descripción", "Prioridad"], [
    ["CAR-01", "El sitio debe mostrar las academias, sus categorías, precios y horarios.", "Alta"],
    ["CAR-02", "El sitio debe permitir enviar una matrícula con validación de los campos obligatorios.", "Alta"],
    ["CAR-03", "El sitio debe ofrecer un Libro de Reclamaciones virtual según la Ley N.° 29571.", "Alta"],
    ["CAR-04", "El sitio debe verse correctamente en celulares (desde 360 px), tabletas y computadoras.", "Alta"],
    ["CAR-05", "La tienda debe permitir filtrar por categoría y precio y ordenar por precio.", "Media"],
    ["CAR-06", "La ficha de producto debe permitir elegir color y talla.", "Media"],
    ["CAR-07", "El sitio debe incluir video, audio, imágenes e iframes con controles accesibles.", "Media"],
    ["CAR-08", "Todos los estilos deben estar en archivos externos, sin estilos en línea.", "Alta"],
    ["CAR-09", "Las animaciones deben desactivarse si el usuario prefiere movimiento reducido.", "Media"],
    ["CAR-10", "El sitio debe publicarse en la nube desde el repositorio de GitHub.", "Alta"],
], [1100, 6300, 1200]))

A(h3("3.3 CONTEXTO DEL SISTEMA"))
A(p("Los siguientes diagramas describen los procesos que el sitio apoya, el modelo de datos que tendría un futuro backend y la arquitectura del frontend."))
A(imagen(DIA / "proceso-matricula.png", "Diagrama de proceso de matrícula"))
A(imagen(DIA / "proceso-compra.png", "Diagrama de proceso de compra en la tienda"))
A(imagen(DIA / "proceso-reclamo.png", "Diagrama de proceso de atención de reclamos"))
A(imagen(DIA / "clases.png", "Diagrama de clases del dominio", ancho_cm=13.5))
A(imagen(DIA / "er.png", "Diagrama entidad-relación"))
A(imagen(DIA / "mapa-sitio.png", "Mapa del sitio"))
A(imagen(DIA / "capas.png", "Diseño del sistema: capas de estilo, compilación y publicación"))
A(tabla("Páginas del sitio", ["N.°", "Archivo", "Contenido"], [[str(i + 1), ("index.html" if k == "inicio" else f"paginas/{k}.html"), d] for i, (k, _, d) in enumerate(paginas)], [600, 2300, 5700]))

A(h3("3.3.1 PROTOTIPOS UX/UI"))
A(p("Las vistas se diseñaron con la página del iPhone 18 Pro como referencia de color y movimiento. Se tomaron los valores computados de esa página: fondos #000000 y #1D1D1F, texto #F5F5F7, enlaces #2997FF, botón principal #0071E3 con radio de 980 px, titulares de 40 px con peso 600 y transiciones de 0,2 a 0,4 s con ease-out. Se añadió un degradado de marca (#FF6A2B a #8C1D2F). Todas las vistas son de tipo Web y responsivas."))
for i, (k, titulo, desc) in enumerate(paginas):
    A(h4(f"PÁGINA {i + 1:02d}. {titulo.upper()}, tipo: Web"))
    A(imagen(CAP / f"{k}.png", f"Página web {titulo}", ancho_cm=15))
    A(p(f"**Descripción:** {desc}"))
A(h4("VISTAS MÓVILES, tipo: Móvil"))
A(p("En pantallas menores a 905 px el menú se convierte en un panel desplegable que funciona sin JavaScript (checkbox y label) y las rejillas pasan a una o dos columnas."))
for k, t in [("movil-inicio", "Vista móvil del inicio"), ("movil-tienda", "Vista móvil de la tienda con filtros"), ("movil-matricula", "Vista móvil del formulario de matrícula")]:
    A(imagen(CAP / f"{k}.jpg", t, ancho_cm=7.5, alto_max_cm=16))

A(h3("3.3.2 DOCUMENTACIÓN DEL CÓDIGO FUENTE"))
A(h4("Organización de Paquetes y Ficheros."))
A(imagen(DIA / "arbol.png", "Organización de paquetes y ficheros"))
for t in [
    "**HTML:** index.html y 404.html en la raíz; las demás páginas en paginas/. Las fuentes están en src/html: parciales/ (head, cabecera, pie y el horario semanal) y paginas/ (el cuerpo de cada página). El script tools/ensamblar.mjs une ambas partes para que las 18 páginas compartan exactamente el mismo encabezado, menú y pie.",
    "**CSS:** assets/css/base.css (CSS puro), altura-less.css y altura-sass.css (compilados) y la carpeta framework/ con layout.css, responsive.css y animaciones.css, que trabajan sobre las clases de Material Design.",
    "**Contenido multimedia:** assets/img (logo, íconos SVG, fotos WebP por sección, ilustraciones de productos y entrenadores), assets/video (MP4, WebM, pósteres y subtítulos .vtt) y assets/audio (MP3 originales).",
    "**Otros:** assets/js/main.js, tools/ (ensamblador, métricas, verificación y scripts de multimedia), docs/ (plan, métricas, créditos, capturas e informe), package.json, Dockerfile y el flujo .github/workflows/pages.yml.",
]:
    A(vineta(t))
A(h4("Organización HTML."))
A(p("Cada página tiene la misma estructura: DOCTYPE, html con lang=\"es-PE\", head con meta charset, viewport, description, keywords, author, robots, theme-color y Open Graph, favicon SVG y las hojas de estilo; body con enlace para saltar al contenido, header con logo y menú, main con secciones y footer con mapa del sitio, redes sociales, datos de contacto y Libro de Reclamaciones. La página paginas/marcos.html demuestra frameset con DOCTYPE HTML 4.01 Frameset, y paginas/horario-semanal.html se muestra dentro de un iframe en Aeróbicos."))
A(h4("Organización CSS."))
A(p("El orden de carga en cada página es: Google Fonts, Material Symbols, MDC Web 14 (CDN), base.css, altura-less.css, altura-sass.css, layout.css, responsive.css y animaciones.css. Así las capas propias se aplican sobre el framework sin usar !important (salvo en impresión y movimiento reducido)."))
filas_m = [[f["punto"], f["nombre"], ", ".join(Path(a).name for a in f["archivos"]), str(f["lineas"]), f'{f["porcentaje"]:.1f} %', f'{f["meta"]} %'] for f in metricas["filas"]]
A(tabla("Reparto del código de estilos propio (líneas útiles)", ["Punto", "Categoría", "Archivos", "Líneas", "Real", "Meta"], filas_m, [700, 2400, 2900, 800, 900, 900]))
A(imagen(DIA / "metricas.png", "Reparto real del código de estilos frente a la meta"))
A(p(f"El total es de {metricas['total']} líneas útiles de estilos propios (sin líneas vacías ni comentarios). Todos los porcentajes quedan a menos de 1,5 puntos de la meta. El CSS del framework cargado por CDN no se cuenta porque no es código propio."))
A(tabla("Enlaces externos de frameworks y recursos", ["Recurso", "Enlace"], [
    ["MDC Web 14 (CSS)", "https://unpkg.com/material-components-web@14.0.0/dist/material-components-web.min.css"],
    ["MDC Web 14 (JS)", "https://unpkg.com/material-components-web@14.0.0/dist/material-components-web.min.js"],
    ["Tipografías Inter e Inter Tight", "https://fonts.googleapis.com/css2?family=Inter&family=Inter+Tight"],
    ["Íconos Material Symbols", "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded"],
    ["LESS 4.2 (compilador)", "https://lesscss.org"],
    ["Dart Sass 1.77 (compilador)", "https://sass-lang.com"],
], [2800, 5800]))
A(tabla("Técnicas de LESS y SASS aplicadas", ["Preprocesador", "Técnica", "Dónde se usa"], [
    ["LESS", "Variables (@negro, @accion, @radio-xl)", "_variables.less, en todo el proyecto"],
    ["LESS", "Mixins con parámetros: .vidrio(), .pildora(), .contenedor()", "Barra de navegación, submenú, botones"],
    ["LESS", "Guards: .texto-sobre(@fondo) when (lightness(@fondo) >= 60%)", "Color de texto de cada tema de sección"],
    ["LESS", "Bucle recursivo con extract() sobre @redes", "Color de cada botón de red social"],
    ["LESS", "Funciones fade(), lighten(), darken() y escape ~\"\"", "Transparencias y clamp()"],
    ["SASS", "Mapas $colores, $deportes, $radios y map.get()", "_tokens.scss"],
    ["SASS", "@function c(), rem(), texto-para() con @if/@else y @error", "_funciones.scss"],
    ["SASS", "@each sobre $deportes y $acabados", "Tarjetas por disciplina y selector de color"],
    ["SASS", "@mixin con @content, %placeholder y @extend", "Insignias, tarjetas, controles ocultos"],
    ["SASS", "@use y @forward (módulos)", "altura.scss"],
], [1400, 3900, 3300]))
A(h4("Organización Archivos Multimedia."))
A(p("Las fotos se descargaron de Wikimedia Commons con licencias CC0, CC BY, CC BY-SA o dominio público, se redimensionaron y se convirtieron a WebP con el script tools/media/descargar_commons.py. Los productos de la tienda, el logo, los íconos y los avatares de los entrenadores son ilustraciones SVG propias. Las dos pistas de audio son originales: se sintetizaron con Python y se codificaron a MP3. Los dos videos (12 s cada uno) se generaron con ffmpeg a partir de esas fotos, con acercamiento lento y fundidos (tools/media/generar_videos.py), en MP4 y WebM, con subtítulos en español en formato WebVTT."))
A(tabla("Archivos multimedia por carpeta", ["Carpeta", "Formato", "Contenido"], [
    ["assets/img/logo", "SVG", "Logotipo y favicon"],
    ["assets/img/iconos", "SVG", "Sprite de redes sociales, cancha FIBA, Libro de Reclamaciones"],
    ["assets/img/hero, academias, galeria, blog", "WebP", f"{sum(1 for c in creditos if c['archivo'].endswith('.webp'))} fotografías con licencia libre"],
    ["assets/img/tienda", "SVG", "12 ilustraciones de productos (4 colores de zapatilla)"],
    ["assets/img/equipo", "SVG", "6 avatares ilustrados de entrenadores"],
    ["assets/video", "MP4, WebM, VTT", "Clips de básquet y piscina (generados con las fotos), pósteres y subtítulos"],
    ["assets/audio", "MP3", "Ritmo de step (128 BPM) y jingle de la marca"],
], [3000, 1600, 4000]))

A(h3("3.4 MATRIZ DE CUMPLIMIENTO DE LOS LINEAMIENTOS"))
A(tabla("Cumplimiento de los puntos de los lineamientos", ["Punto", "Requisito", "Evidencia"], [
    ["a", "Mínimo 14 páginas", "17 páginas + 404"],
    ["b", "Estructura HTML, meta tags, textos, enlaces, br", "Plantilla común en src/html/parciales/head.html"],
    ["c", "Encabezado con menú, cuerpo y pie", "Todas las páginas"],
    ["d", "Formularios y multimedia", "Matrícula, contacto, reclamos, boletín; video, audio, imágenes"],
    ["e", "Selectores, atributos y valores", "base.css (elemento, clase, atributo, pseudoclases, pseudoelementos, combinadores)"],
    ["f", "Tablas, frames, iframes, marquees", "Horarios, producto, academias; marcos.html; YouTube, OpenStreetMap, horario semanal; inicio y eventos"],
    ["g", "Tipografía, archivos externos, imágenes, íconos, vectores", "Google Fonts, Material Symbols, SVG propios, WebP"],
    ["g.i–g.iii", "CSS 10 %, LESS 15 %, SASS 15 %", "Tabla de reparto del código"],
    ["h", "Animaciones con framework (20 %)", "animaciones.css sobre componentes MDC"],
    ["i", "Media queries y multimedia con framework (20 %)", "responsive.css con puntos de corte de Material Design"],
    ["j", "Flexbox y Grid con framework (20 %)", "layout.css y mdc-layout-grid"],
    ["k", "Ampliación del alcance e incremento", "Etiquetas v1.0, v2.0, v3.0 y v4.0 en Git; CHANGELOG.md"],
    ["l, m, n", "Repositorio, despliegue e integración en la nube", f"Repositorio: {URL_REPO}; publicación: {URL_PUB}; Dockerfile"],
    ["14", "Partes mínimas de la página", "Logo, encabezados, menú, botones, redes, imágenes, videos, banners, barras laterales, destacados, pie, inicio, CTA, blog, formularios, contacto, enlaces internos y externos"],
], [1000, 3300, 4300]))

A(h3("CONCLUSIONES"))
for t in [
    "Se construyó y publicó el sitio web de ALTURA Sports Academy con 17 páginas y una página 404, cumpliendo el objetivo general del proyecto.",
    "El reparto del código de estilos quedó cerca de lo pedido (10/15/15/20/20/20) y se puede verificar en cualquier momento con npm run metricas.",
    "LESS resultó práctico para componentes de estructura (encabezado, pie, banners) gracias a sus mixins y guards; SASS fue más potente para generar variantes con mapas y bucles y para re-tematizar Material Design.",
    "Material Design aportó componentes accesibles y una rejilla responsiva; al personalizarlo con SASS y variables CSS se logró una apariencia propia, cercana a la referencia de Apple.",
    "Los formularios de matrícula, contacto y reclamos ofrecen canales formales de atención que la academia no tenía, aunque todavía sin un servidor que guarde los datos.",
    "Versionar en cuatro entregas con etiquetas de Git permitió mostrar la ampliación del alcance y el incremento de resultados, y GitHub Pages publicó el sitio sin costo.",
]:
    A(vineta(t))
A(h3("RECOMENDACIONES"))
for t in [
    "Desarrollar un backend (por ejemplo con Node.js y una base de datos) que reciba las matrículas, los pedidos y los reclamos, siguiendo el diagrama entidad-relación propuesto.",
    "Integrar una pasarela de pagos para la tienda y un panel para que administración actualice horarios y precios sin editar código.",
    "Reemplazar las fotos de terceros por una sesión fotográfica propia de la academia.",
    "Evaluar la migración a Material Web (componentes web de Material Design 3), sucesor de MDC Web.",
    "Medir el uso del sitio con una herramienta de analítica para priorizar mejoras.",
]:
    A(vineta(t))

A(h3("BIBLIOGRAFÍA"))
for t in [
    "Chacon, S. y Straub, B. (2014). Pro Git (2.ª ed.). Apress. https://git-scm.com/book/es/v2",
    "GitHub. (2024). Documentación de GitHub Pages. https://docs.github.com/es/pages",
    "Google. (2023). Material Components for the Web. https://github.com/material-components/material-components-web",
    "Google. (2024). Material Design 3. https://m3.material.io",
    "Less.js. (2024). Getting started. https://lesscss.org",
    "Marcotte, E. (2011). Responsive web design. A Book Apart.",
    "MDN Web Docs. (2024). CSS: Hojas de estilo en cascada. Mozilla. https://developer.mozilla.org/es/docs/Web/CSS",
    "MDN Web Docs. (2024). HTML: Lenguaje de etiquetas de hipertexto. Mozilla. https://developer.mozilla.org/es/docs/Web/HTML",
    "Sass. (2024). Sass documentation. https://sass-lang.com/documentation",
    "W3C. (2024). CSS Animations Level 1 y Scroll-driven Animations. https://www.w3.org/TR/css-animations-1/",
    "WHATWG. (2024). HTML Living Standard. https://html.spec.whatwg.org",
    "Congreso de la República del Perú. (2010). Ley N.° 29571, Código de Protección y Defensa del Consumidor.",
    "Apple. (2026). iPhone 18 Pro (página de producto usada como referencia visual). https://www.apple.com/iphone-18-pro/",
]:
    A(p(t, ind='w:left="1122" w:hanging="720" w:right="400"'))

A(titulo1("ANEXOS"))
A(h3("ENCUESTA"))
A(p("Cuestionario propuesto para validar el sitio con alumnos y padres de familia. Se aplica con Google Forms; sus resultados se registrarán cuando la academia la difunda."))
A(tabla("Cuestionario de satisfacción del sitio web", ["N.°", "Pregunta", "Tipo de respuesta"], [
    ["1", "¿Desde qué dispositivo visitó el sitio?", "Celular / tableta / computadora"],
    ["2", "¿Encontró fácilmente los horarios y precios de la disciplina que buscaba?", "Escala de 1 a 5"],
    ["3", "¿Qué tan claro le pareció el formulario de matrícula?", "Escala de 1 a 5"],
    ["4", "¿Compraría o reservaría productos desde la tienda en línea?", "Sí / No / Tal vez"],
    ["5", "¿El diseño del sitio transmite una imagen profesional de la academia?", "Escala de 1 a 5"],
    ["6", "¿Qué información le faltó encontrar?", "Respuesta abierta"],
    ["7", "¿Recomendaría ALTURA a un familiar o amigo?", "Escala de 0 a 10"],
], [700, 5300, 2600]))
A(h3("CRÉDITOS MULTIMEDIA"))
vistos = set()
filas_c = []
for c in creditos:
    if c["archivo"] in vistos:
        continue
    vistos.add(c["archivo"])
    filas_c.append([Path(c["archivo"]).name, (c.get("autor") or "Autor desconocido")[:60], c.get("licencia") or "", c.get("pagina") or ""])
A(tabla("Créditos de las fotos (Wikimedia Commons)", ["Archivo", "Autor", "Licencia", "Fuente"], filas_c, [1900, 2400, 1300, 3000]))

CUERPO = "".join(B)

# --------------------------------------------------------------------------
# Armado del paquete .docx
# --------------------------------------------------------------------------
tmp = Path(tempfile.mkdtemp())
with zipfile.ZipFile(PLANTILLA) as z:
    z.extractall(tmp)
doc_path = tmp / "word" / "document.xml"
x = doc_path.read_text(encoding="utf-8")
ini = x.index("<w:body>") + len("<w:body>")
fin = x.index("<w:sectPr", x.rindex("</w:p>"))
cuerpo = x[ini:fin]
elementos = [m.group(0) for m in re.finditer(r"<(w:p|w:tbl|w:sdt)\b[^>]*>.*?</\1>", cuerpo, re.S)]


def cambiar_textos(xml, reemplazos):
    for a, b in reemplazos:
        xml = xml.replace(a, b)
    return xml


# Carátula
titulo_xml = elementos[11]
titulo_xml = re.sub(r"<w:t>\[Titulo del trabajo\]</w:t>", "<w:t>ALTURA Sports Academy: sitio web con LESS, SASS y Material Design</w:t>", titulo_xml)
elementos[11] = titulo_xml


def reemplazar_corchete(xml, nuevo):
    # el texto [enlace del trabajo] está partido en varios <w:t>; se deja el primero y se vacían los demás
    textos = list(re.finditer(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", xml))
    i_ini = next(i for i, m in enumerate(textos) if "[" in m.group(1))
    salida, ultimo = [], 0
    for i, m in enumerate(textos):
        if i < i_ini:
            continue
        salida.append(xml[ultimo:m.start()])
        salida.append(f'<w:t xml:space="preserve">{escape(nuevo) if i == i_ini else ""}</w:t>')
        ultimo = m.end()
    salida.append(xml[ultimo:])
    return "".join(salida)


elementos[13] = reemplazar_corchete(elementos[13], URL_PUB)
elementos[14] = reemplazar_corchete(elementos[14], URL_REPO)
elementos[16] = elementos[16].replace("<w:t>00</w:t>", "<w:t>06</w:t>")
elementos[17] = re.sub(r"\[Ordenado por Apellidos\]", "", elementos[17])

# Tabla de integrantes: fila 1 con los datos, se quitan las filas 2 y 3
tbl = elementos[18]
filas = re.findall(r"<w:tr\b.*?</w:tr>", tbl, re.S)
datos = ["1", "U25316441", "QUISPE MORALES", "FABRICIO OSCAR", "U25316441@utp.edu.pe"]
celdas = re.findall(r"<w:tc>.*?</w:tc>", filas[1], re.S)
nuevas = []
for c, d in zip(celdas, datos):
    c = re.sub(r"<w:r\b.*?</w:r>", "", c, flags=re.S)
    tam = "20" if "@" in d else "24"
    c = c.replace("</w:p>", f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="{tam}"/><w:lang w:val="es-PE"/></w:rPr><w:t>{escape(d)}</w:t></w:r></w:p>', 1)
    nuevas.append(c)
fila1 = filas[1]
for c, n in zip(celdas, nuevas):
    fila1 = fila1.replace(c, n, 1)
tbl = tbl.replace(filas[1], fila1).replace(filas[2], "").replace(filas[3], "")
elementos[18] = tbl

# Se conserva la carátula (0-24) y el índice general (25); el resto se reemplaza
nuevo_cuerpo = "".join(elementos[:26]) + CUERPO
x = x[:ini] + nuevo_cuerpo + x[fin:]
# márgenes inferiores más cómodos para el contenido
x = x.replace('w:bottom="280"', 'w:bottom="1200"')
doc_path.write_text(x, encoding="utf-8")

# Imágenes y relaciones
rels_path = tmp / "word" / "_rels" / "document.xml.rels"
rels = rels_path.read_text(encoding="utf-8")
media = tmp / "word" / "media"
for rid, nombre, ruta in IMAGENES:
    destino = media / nombre
    if ruta.suffix.lower() in (".png",):
        img = Image.open(ruta).convert("RGB")
        img.save(destino.with_suffix(".jpg"), "JPEG", quality=86)
        nombre = destino.with_suffix(".jpg").name
    else:
        shutil.copy(ruta, destino)
    rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{nombre}"/></Relationships>')
rels_path.write_text(rels, encoding="utf-8")
ct_path = tmp / "[Content_Types].xml"
ct = ct_path.read_text(encoding="utf-8")
if 'Extension="jpg"' not in ct:
    ct = ct.replace("<Types ", "<Types ", 1).replace("</Types>", '<Default Extension="jpg" ContentType="image/jpeg"/></Types>')
ct_path.write_text(ct, encoding="utf-8")

# Que Word actualice los campos (índices) al abrir
settings = tmp / "word" / "settings.xml"
s = settings.read_text(encoding="utf-8")
if "<w:updateFields" not in s:
    s = re.sub(r"(<w:settings\b[^>]*>)", r'\1<w:updateFields w:val="true"/>', s, count=1)
settings.write_text(s, encoding="utf-8")

Path(SALIDA).parent.mkdir(parents=True, exist_ok=True)
if Path(SALIDA).exists():
    Path(SALIDA).unlink()
with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(tmp.rglob("*")):
        if f.is_file():
            z.write(f, f.relative_to(tmp).as_posix())
shutil.rmtree(tmp, ignore_errors=True)
print("Informe generado:", SALIDA, "| ilustraciones:", CONT["Ilustración"], "| tablas:", CONT["Tabla"])
