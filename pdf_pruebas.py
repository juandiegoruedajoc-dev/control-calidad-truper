# -*- coding: utf-8 -*-
"""Generador PDF del formato FO-ACP-090 Rev. 1 (pruebas mensuales).

Reproduce el layout aprobado en la muestra (título, Información general,
Producto a evaluar, Resultados, Evidencia centrada, Conclusión, Observaciones,
firmas según inspector y pie). Lo usa la pestaña "Pruebas mensuales" de app.py.
"""
import base64
import io

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

LOGO_B64 = (
    "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"
    "B4uzyClOTNjKAAAAAElFTkSuQmCC"
)

VERDE = colors.HexColor("#00B050")
ROJO = colors.HexColor("#FF0000")
GRIS_TITULO = colors.HexColor("#A6A6A6")
NEGRO = colors.black

# --- Tipografías: registra DejaVu/Liberation si existen, si no Helvetica ---
def _registrar_fuentes():
    import os
    candidatos = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVu"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVu-Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", "DejaVu-Oblique"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "Liberation"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "Liberation-Bold"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", "Liberation-Italic"),
    ]
    fuentes = {}
    for ruta, nombre in candidatos:
        if os.path.exists(ruta):
            try:
                pdfmetrics.registerFont(TTFont(nombre, ruta))
                fuentes[nombre] = True
            except Exception:
                pass
    return fuentes

_F = _registrar_fuentes()
F_NORMAL = "DejaVu" if _F.get("DejaVu") else ("Liberation" if _F.get("Liberation") else "Helvetica")
F_BOLD = "DejaVu-Bold" if _F.get("DejaVu-Bold") else ("Liberation-Bold" if _F.get("Liberation-Bold") else "Helvetica-Bold")
F_OBLIQUE = "DejaVu-Oblique" if _F.get("DejaVu-Oblique") else ("Liberation-Italic" if _F.get("Liberation-Italic") else "Helvetica-Oblique")

# Firmas (elaboró = inspector; aprueban jefe y gerente).
# Juan (2026-11-20): solo José Antonio Hernández (jefe) y Raúl Valdez (gerente)
# para todos los inspectores; ya no se usan Hilario Martínez ni Luz Iliana.
FIRMAS = {
    "lizeth": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "dilan": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "juan": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "jose_israel": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "daniel": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "judith": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
}


def _estilos():
    return {
        "titulo": ParagraphStyle("titulo", fontName=F_BOLD, fontSize=13, leading=16, alignment=TA_CENTER),
        "fecha": ParagraphStyle("fecha", fontName=F_NORMAL, fontSize=11, leading=14, alignment=TA_RIGHT),
        "fecha_valor": ParagraphStyle("fecha_valor", fontName=F_BOLD, fontSize=14, leading=17, alignment=TA_RIGHT),
        "seccion": ParagraphStyle("seccion", fontName=F_BOLD, fontSize=11, leading=14, alignment=TA_CENTER),
        "etiqueta": ParagraphStyle("etiqueta", fontName=F_NORMAL, fontSize=10, leading=13, alignment=TA_LEFT),
        "valor": ParagraphStyle("valor", fontName=F_NORMAL, fontSize=10, leading=13, alignment=TA_CENTER),
        "celda": ParagraphStyle("celda", fontName=F_NORMAL, fontSize=10, leading=13, alignment=TA_CENTER),
        "celda_b": ParagraphStyle("celda_b", fontName=F_BOLD, fontSize=10, leading=13, alignment=TA_CENTER),
        "ok": ParagraphStyle("ok", fontName=F_BOLD, fontSize=11, leading=14, alignment=TA_CENTER, textColor=VERDE),
        "no_ok": ParagraphStyle("no_ok", fontName=F_BOLD, fontSize=11, leading=14, alignment=TA_CENTER, textColor=ROJO),
        "subtitulo": ParagraphStyle("subtitulo", fontName=F_NORMAL, fontSize=9, leading=11, alignment=TA_CENTER),
        "obs": ParagraphStyle("obs", fontName=F_NORMAL, fontSize=10, leading=13, alignment=TA_CENTER),
        "nota": ParagraphStyle("nota", fontName=F_NORMAL, fontSize=8, leading=10, alignment=TA_CENTER),
        "firma_rol": ParagraphStyle("firma_rol", fontName=F_NORMAL, fontSize=9, leading=11, alignment=TA_CENTER),
        "firma_nombre": ParagraphStyle("firma_nombre", fontName=F_BOLD, fontSize=9, leading=11, alignment=TA_CENTER),
        "firma_hint": ParagraphStyle("firma_hint", fontName=F_OBLIQUE, fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.HexColor("#808080")),
        "pie": ParagraphStyle("pie", fontName=F_NORMAL, fontSize=8, leading=10, alignment=TA_LEFT),
        "pie_c": ParagraphStyle("pie_c", fontName=F_NORMAL, fontSize=8, leading=10, alignment=TA_CENTER),
        "pie_r": ParagraphStyle("pie_r", fontName=F_NORMAL, fontSize=8, leading=10, alignment=TA_RIGHT),
    }


def _campo(etiqueta, valor, estilo_valor, ancho_total, ancho_etiqueta, estilos):
    """Campo 'etiqueta: __valor__' dentro de un ancho_total dado."""
    ancho_valor = max(40, ancho_total - ancho_etiqueta - 4)
    t = Table([
        [Paragraph(etiqueta, estilos["etiqueta"]),
         Paragraph(f'<u>{valor}</u>' if valor else '<u>&nbsp;</u>', estilo_valor)]
    ], colWidths=[ancho_etiqueta, ancho_valor])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def _fotos_a_imagenes(fotos_bytes, ancho_max, alto_max=100, alto_min=55, gap=8):
    """Escala las fotos para que quepan en una sola fila centrada si es posible.

    Calcula el alto que hace que la fila completa quepa en ancho_max; si ese
    alto queda por debajo de alto_min, usa alto_min y deja que _filas_fotos
    reparta las fotos en varias filas.
    """
    pil_imgs = []
    for datos in fotos_bytes or []:
        try:
            pil_imgs.append(Image.open(io.BytesIO(datos)).convert("RGB"))
        except Exception:
            continue
    if not pil_imgs:
        return []

    n = len(pil_imgs)
    suma_aspectos = sum(img.size[0] / img.size[1] for img in pil_imgs)
    ancho_disponible = ancho_max - gap * (n - 1)
    alto_que_cabe = ancho_disponible / suma_aspectos if suma_aspectos > 0 else alto_max
    alto = min(alto_max, max(alto_min, alto_que_cabe))

    imagenes = []
    for img in pil_imgs:
        w, h = img.size
        escala = min(alto / h, ancho_max / w, 1.0)
        nw, nh = max(1, int(w * escala)), max(1, int(h * escala))
        buf = io.BytesIO()
        img.resize((nw, nh), Image.LANCZOS).save(buf, "JPEG", quality=85)
        buf.seek(0)
        imagenes.append(RLImage(buf, width=nw, height=nh))
    return imagenes


def _filas_fotos(imagenes, ancho_util, gap=8):
    """Acomoda las imágenes en filas centradas (como en la muestra aprobada)."""
    if not imagenes:
        return []
    filas = []
    fila = []
    ancho_fila = 0
    for im in imagenes:
        w = im.imageWidth
        if fila and ancho_fila + gap + w > ancho_util:
            filas.append(fila)
            fila, ancho_fila = [], 0
        if fila:
            ancho_fila += gap
        fila.append(im)
        ancho_fila += w
    if fila:
        filas.append(fila)
    tablas = []
    for f in filas:
        total = sum(im.imageWidth for im in f) + gap * (len(f) - 1)
        sobra = max(0, (ancho_util - total) / 2)
        celdas = [""] + list(f) + [""]
        t = Table([celdas], colWidths=[sobra] + [im.imageWidth for im in f] + [sobra])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        tablas.append(t)
    return tablas


def generar_pdf(datos, logo_path=None):
    """Genera el PDF FO-ACP-090 Rev. 1 y devuelve los bytes.

    datos: dict con claves:
      fecha (str), responsable (str), planta (str), periodicidad (str),
      prueba (str), codigo (str), clave (str), cantidad (str),
      caracteristica (str), especificacion (str),
      valores (lista de 3 strings M1/M2/M3),
      resultado (str, CUMPLE/NO CUMPLE),
      conforme (bool),
      observaciones (str),
      fotos (lista de bytes JPEG),
      inspector_key (str, para firmas),
    """
    est = _estilos()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=36, rightMargin=36, topMargin=24, bottomMargin=24,
        title="FO-ACP-090 Rev. 1",
    )
    ancho_util = letter[0] - 72  # ~540 pt
    historia = []

    def seccion(titulo):
        t = Table([[Paragraph(titulo, est["seccion"])]], colWidths=[ancho_util])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GRIS_TITULO),
            ("BOX", (0, 0), (-1, -1), 1, NEGRO),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        return t

    # ── Encabezado: logo + título ──────────────────────────────
    if logo_path is None:
        try:
            logo_path = io.BytesIO(base64.b64decode(LOGO_B64))
        except Exception:
            logo_path = None
    if logo_path:
        try:
            logo = RLImage(logo_path, width=110, height=110 * 190 / 433)
            celda_logo = logo
        except Exception:
            celda_logo = Paragraph("", est["etiqueta"])
    else:
        celda_logo = Paragraph("", est["etiqueta"])
    enc = Table([
        [celda_logo,
         Paragraph("REGISTRO DE EVALUACIÓN PARA PRUEBAS PERIÓDICAS REALIZADAS EN PLANTA", est["titulo"])]
    ], colWidths=[120, ancho_util - 120])
    enc.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (1, 0), (1, 0), 1.2, NEGRO),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    historia.append(enc)
    historia.append(Spacer(1, 2))

    # ── Fecha de evaluación ────────────────────────────────────
    fecha_tabla = Table([
        [Paragraph("Fecha de evaluación:", est["fecha"]),
         Paragraph(f'<u>{datos.get("fecha", "")}</u>', est["fecha_valor"])]
    ], colWidths=[ancho_util - 150, 150])
    fecha_tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    historia.append(fecha_tabla)

    # ── INFORMACIÓN GENERAL ────────────────────────────────────
    historia.append(seccion("INFORMACIÓN GENERAL"))
    w1 = ancho_util * 0.64
    w2 = ancho_util - w1
    info = Table([
        [_campo("Reponsable de evaluación:", datos.get("responsable", ""), est["valor"], w1, 150, est),
         _campo("Planta:", datos.get("planta", ""), est["valor"], w2, 55, est)],
        [_campo("Periodicidad de la prueba:", datos.get("periodicidad", "Mensual"), est["valor"], w1, 150, est),
         _campo("Prueba:", datos.get("prueba", ""), est["valor"], w2, 55, est)],
    ], colWidths=[w1, w2])
    info.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#CCCCCC")),
    ]))
    historia.append(info)

    # ── PRODUCTO A EVALUAR ─────────────────────────────────────
    historia.append(seccion("PRODUCTO A EVALUAR"))
    p1, p2, p3 = 140, 150, ancho_util - 290
    prod = Table([
        [_campo("Código", datos.get("codigo", ""), est["valor"], p1, 55, est),
         _campo("Clave:", datos.get("clave", ""), est["valor"], p2, 50, est),
         _campo("Cantidad de muestras a evaluar:", datos.get("cantidad", ""), est["valor"], p3, 175, est)]
    ], colWidths=[p1, p2, p3])
    prod.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    historia.append(prod)

    # ── RESULTADOS ─────────────────────────────────────────────
    titulo_res = Table([
        [Paragraph("RESULTADOS DE LAS CARACTERISTICAS EVALUDAS", est["seccion"])],
        [Paragraph("(Indicar cada una de las caracteristicas evaluadas)", est["subtitulo"])],
    ], colWidths=[ancho_util])
    titulo_res.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRIS_TITULO),
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("TOPPADDING", (0, 1), (-1, 1), 1),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    historia.append(titulo_res)

    valores = list(datos.get("valores", ["", "", ""]))[:3]
    while len(valores) < 3:
        valores.append("")
    celdas_valor = []
    for v in valores:
        txt = str(v).strip()
        if not txt:
            celdas_valor.append(Paragraph("", est["celda"]))
        elif "NO" in txt.upper() and "OK" in txt.upper():
            celdas_valor.append(Paragraph(txt, est["no_ok"]))
        elif txt.upper().startswith("OK"):
            celdas_valor.append(Paragraph(txt, est["ok"]))
        else:
            celdas_valor.append(Paragraph(txt, est["celda_b"]))

    resultado = str(datos.get("resultado", "")).strip().upper()
    if resultado == "NO CUMPLE":
        celda_res = Paragraph("NO CUMPLE", est["no_ok"])
    elif resultado:
        celda_res = Paragraph(resultado, est["ok"])
    else:
        celda_res = Paragraph("", est["celda"])

    res = Table([
        [Paragraph("Característica", est["celda"]),
         Paragraph("Especificación", est["celda"]),
         Paragraph("Valor", est["celda"]),
         Paragraph("", est["celda"]),
         Paragraph("", est["celda"]),
         Paragraph("Resultado", est["celda"])],
        [Paragraph("", est["celda"]),
         Paragraph("", est["celda"]),
         Paragraph("M1", est["celda"]),
         Paragraph("M2", est["celda"]),
         Paragraph("M3", est["celda"]),
         Paragraph("", est["celda"])],
        [Paragraph(str(datos.get("caracteristica", "")), est["celda"]),
         Paragraph(str(datos.get("especificacion", "")), est["celda"]),
         celdas_valor[0], celdas_valor[1], celdas_valor[2],
         celda_res],
    ], colWidths=[ancho_util * 0.22, ancho_util * 0.28, ancho_util * 0.11, ancho_util * 0.11, ancho_util * 0.11, ancho_util * 0.17])
    res.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, NEGRO),
        ("SPAN", (2, 0), (4, 0)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 0), (-1, 1), [colors.HexColor("#F2F2F2"), colors.white]),
    ]))
    historia.append(res)

    # ── EVIDENCIA ──────────────────────────────────────────────
    historia.append(seccion("EVIDENCIA DE EVALUACIÓN"))
    imagenes = _fotos_a_imagenes(datos.get("fotos", []), ancho_util - 20)
    filas_fotos = _filas_fotos(imagenes, ancho_util - 20)
    if filas_fotos:
        contenido = filas_fotos
    else:
        contenido = [Paragraph("Sin evidencia fotográfica", est["nota"])]
    ev = Table([[contenido]], colWidths=[ancho_util])
    ev.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    historia.append(ev)

    # ── CONCLUSIÓN ─────────────────────────────────────────────
    historia.append(seccion("CONCLUSIÓN"))
    conforme = bool(datos.get("conforme", True))
    marca_conf = "☑" if conforme else "☐"
    marca_no = "☐" if conforme else "☑"
    concl = Table([
        [Paragraph(f"{marca_conf}&nbsp;&nbsp;Conforme", est["celda"]),
         Paragraph(f"{marca_no}&nbsp;&nbsp;No Conforme", est["celda"])],
        [Paragraph("En caso de obtener una evaluación con no cumplimiento aplicar plan de reacción declarado en PR-ACP-002", est["nota"]),
         Paragraph("", est["nota"])],
    ], colWidths=[ancho_util * 0.5, ancho_util * 0.5])
    concl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("SPAN", (0, 1), (1, 1)),
    ]))
    historia.append(concl)

    # ── OBSERVACIONES ──────────────────────────────────────────
    historia.append(seccion("OBSERVACIONES GENERALES"))
    obs_txt = str(datos.get("observaciones", "")).strip()
    obs = Table([
        [Paragraph(obs_txt if obs_txt else "&nbsp;", est["obs"])]
    ], colWidths=[ancho_util])
    obs.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    historia.append(obs)

    # ── Firmas ─────────────────────────────────────────────────
    inspector_key = str(datos.get("inspector_key", "juan")).lower()
    jefe, gerente = FIRMAS.get(inspector_key, FIRMAS["juan"])
    elaboro_nombre = str(datos.get("responsable", "")).strip()

    def bloque_firma(nombre, rol_linea1, rol_linea2):
        celda = [
            Paragraph("Nombre y firma", est["firma_hint"]),
            Spacer(1, 2),
            Paragraph('<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>', est["firma_nombre"]),
            Spacer(1, 2),
            Paragraph(nombre, est["firma_nombre"]),
            Spacer(1, 2),
            Paragraph(f"{rol_linea1}<br/>{rol_linea2}", est["firma_rol"]),
        ]
        return celda

    firmas = Table([
        [bloque_firma(elaboro_nombre, "ELABORÓ:", "INSPECTOR DE CALIDAD"),
         bloque_firma(jefe, "APROBÓ:", "JEFE DE CALIDAD"),
         bloque_firma(gerente, "APROBÓ:", "GERENTE DE CALIDAD")],
    ], colWidths=[ancho_util / 3.0] * 3)
    firmas.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    historia.append(firmas)

    # ── Pie ────────────────────────────────────────────────────
    pie = Table([
        [Paragraph("Sistema de Gestión de Calidad", est["pie"]),
         Paragraph("Vigente a partir de: 05/11/2026", est["pie_c"]),
         Paragraph("FO-ACP-090 Rev. 1", est["pie_r"])],
    ], colWidths=[ancho_util * 0.34, ancho_util * 0.36, ancho_util * 0.30])
    pie.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    historia.append(pie)

    doc.build(historia)
    return buf.getvalue()
