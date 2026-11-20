# -*- coding: utf-8 -*-
"""Generador PDF del formato FO-ACP-090 Rev. 1 (pruebas mensuales).

Reproduce el layout aprobado en la muestra (título, Información general,
Producto a evaluar, Resultados, Evidencia centrada, Conclusión, Observaciones,
firmas según inspector y pie). Lo usa la pestaña "Pruebas mensuales" de app.py.
"""
import base64
import io

from PIL import Image, ImageDraw
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
    "07exZTVOVnoRU539Q9ltxiL3uVnsHFaqSyELeztfLDJ+a1N7WGR85HBFdrjsJmOPd5xZ6UXMDw/8Yt4Yodd9ySKXtdvplD5hilaH"
    "QiYtf2WsthGfXrdQ2qk5TfBsVdMk2UEicnY57fhanroIIZh8CNA95/+IRZx5hMXOY0XE5VN3sUw+RJ2z7QWDVNann+U/mzKdXWWQ"
    "CU4jySLm3LHFRvfsWCgk9m7XrvNi1lqavNEkUPus/zSJMwfx/hLrmHXu87rRfqZ6Y7a1sPjOmd2aIvsPPGQRB6uLUsTMrqxqt5+z"
    "Xni0n2muJyW/pupXj9XhtKL2M9XFnR+ximURp+r9Xitb3CtFjD/tZ+r6WbCOi2JEm3DFLn7Ti2Vw8Otr5rDY+Q3n/Z1FZLCexSzP"
    "MahaEZonH8sxMO/x0L0XvMu1NpndC7XePPK+99SLZaHzfxY+JMuTT64rj72dG1zL31VYLoORF+f4hl+gaPeJqerLxf221X4i5v0o"
    "quHb0RrfoBD0Hu/lg7nj9LtTPxjHG08rFsW1FnjtdfpO/L7is0IULX+X9rPiCtMGUMCKF30bmZjtF6WMT+OWn8TN+uHFI+fJPYee"
    "Lb3dithInzT9m5hz9ev/U7z80nb5u2e/GTuNuot6YYcG/UzM9nGM2YK4bfMzUdoFKogCVo6oRcwvjd8Xs/0ipLowx/qNTVVr8QN6"
    "qv0eU52PWZ3fW9VEv8S+Tp2d/Hv55sjkJtKNFDI/HLcs2kSakp8zqzk0KuU+VhwTvYg5V5OBrEeSH7hyvzPbaXsju52k3v+p5x9b"
    "cKE2F9mohsfks+67sfNokkoUMefSXghkMBIZHqrFwLXqBxG/Wa916/6WlWr/p5p3lbQGk18LGj4eO4+8NIRH/HDy1th5NE1liphz"
    "aS4IKea8FrP3tJBNo7RbktTyrbLWcPLbSR/Pwcj7pck7Y6fRRJUqYs6ltTCklOtGxbrQI5VjmkqeqUnxuMpgJNwPFk/liphzrw2K"
    "Cg/mqudXNbUqZLPpuyudXw2kMr9SybPukuiAqtwUaT1gq3Kz85lYHXvVcNgPJxvesLUqfa8aRn44udAsHjc7r1vodWciUpkP3E06"
    "9imItk3QRqwcNGUvak0fsDIYmezmLeK3zNu+c87pz7strpO9mjePedtHPCtvw5j1d97rXev9ZbavYfZpv3TgmjLbxPrVYoLOFrO7"
    "vHc35Aqi00UZHlw2SgklmfW6n/AiH84fKfRlMOGJzgnSG3ZcoFv9l0V8N1cc1UPi5XLZNxoZpQYAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAFRNt26mqbOxatDPtvVf1YxA03NsaTn6piNhV3/y46Pyq3vfOFXecU3jv63HGub248zLnW4+Umc9GzcL0Pe2lgw/EziOv"
    "JDYARhxe/Ae0n33gxF8MRp7nJjXHymITQni+tTR5U8x8YKvl2/+k/ezEf6e62TVFDOvXz4I651TD/X44uTp2OiiP937heFFLdbHD"
    "maXav5V5Rg/SIeLfW5dTQtg47WdK/9dXav1LEcPctJ9p6HVD7DwQR0oLHTZO+5nq3u0/FzuPtVDEkIuImDw0E2mi72uutflzodc5"
    "HDuNM6GIwQSLWXPR9/Um4jeHXncaO4/ToYjBDItZc9H39SYirdg5nA5FDIAJClm9VbV/KWIwVdWBDiC/Ks5vihjM6W7uP2yqKi5y"
    "qDeKGOztyo7GTgFAMUKv+2LsHFbiE3Oigsz+yCKOBH+9iFxoEQvlseh/Ufc2ca1rLPJZSfuZFrbvoobHiohbNVbz22vrFos4K4nI"
    "G61j5hGtiBUxyHOdyhC9XvaNP2WYTqFa+w78oVGoE3EsTwXpr35/Jvv+d2QVDycz7H/nnHO6eMHFzm963DJmEfxw8tbYOZSh6vO7"
    "SjidiBNkMBJVfdIkmG79hkkclEKWnnoitT3zsDGW/avXLWyzipUXRQwn8cPxRbFzQDwUsnoz699ztr1gEscARQynYCED6qtu85si"
    "BuAkFouc7t1xq0UuwFooYliVTmfJP/EV8ai3v+oRWA1FDKuSlrszdg5ImOj22CmgGShiWF3QnbFTQLrE+TfHzgHNQBHD6lrt5dgp"
    "IF3qwv/FzgHNQBEDcJLZ4s4/yBtDVP/KIhdgLRQxACfxvpV/S6vhgY9Z5AJ7ddu5g70TcYq6DXKsX9X7vsz86nY/laWg4c7YORxH"
    "EcNJrBYJnYWHLOKgPFUvYMhH9+xYcO32cxaxWsPJzRZxLFDE4JyzX8D88uQqy3gojt7UucJt8l+KnQeKU+cPKBSxGqjzAMXqqtzn"
    "nIazVeW+rgIu7KiDQ6OzY6ewkqo+EzsHAMWo2ocUilgNyGfdd2PnsJIfjt8SOwfEodNwf+wc6qZqRaNqKGI1UZWBPpuFR2PngHj8"
    "/snVsXOoo6rM76rksRJFrEaqMMDay5PLYueAOKow/uqM47s6iljNxBzoTLLmUtXDsXNAsao6vyliNaSqoew2qzrAUQ4/HG+NnUMT"
    "xJpnVZ7fFLEa8sNxq8z2qjzAUTz6v1xlH++q9y9FrKbKGnhVH+AoUJheT//Hwfx+HTc715gMRlLYjZKqvy/D8R8XEhuVx2mt+DSE"
    "L4n3P11E7JSOM0Ws5nQa7pe2f69ZvDD9R7908Bes4iEtKS1udeeXJldaf0hNsX8pYjXn90+uthroKQ5wGJiMtsoDjqsPK8jybEuq"
    "85si1gBWA137maY60OuGfsBxTZ/fXNjREFaDk81IgQrS6btMwizuWLSIUyaKWJPMpj9uEmaxc69FnKqiUCM1Mjz4sEkg3x6axCkR"
    "RaxBZPng1yzieO/fbxFnXhQZ4FRNPdtCEWuYpg709Qq97tOxcwDm1cT5TRFroDoM9KLaFpHziogLlKUO83sjKGJNNRiZ9H2dCplJ"
    "PA2F3HwKxKC9C94dO4e1UMQaSpxTVT1iEUt7nds2+pogs78wabufqd547rm5Y1jdazOc/KtFHCAPs0vlZdMXTOIUiPvEGswPx1tM"
    "Fm/xtzrnbtvIS1r7DnxE+9nNudt2zrkt535L++c6DbOv+qUDP7Hel6VyugSvq1KfVf2eqqbcP0YRa7g6DXTxrbdHPb2p+kSstoHV"
    "1Gl+nw6nExHth+CqTop5+eF4V+wcgO+lITxpESf0uqU/p3A9KGJwzjmns+nnTeJU6HRPmYKGl2PnAKzGL00usogjIqJ7dvyQRSxL"
    "FDE455zzywd/1iqW7ulcu95/W5dvY63h5JzYOQCnYzbP2u2vm8QxRBHDCXYD3f/9hv696hdN2o2kLoUY9VbX+8coYjhJjIEuw/Fu"
    "izajmB39ydgpAOums/eZhKlQIaOI4VT+yCUWYTZUyBL8NhNcuEOWn/pK7DyA9ZLhgc9YxQq97swqVh4UMZxC/vrQ41axalvIvhMW"
    "WoPJR2OnAWyU1TwTEa+/cv7ZFrHyoIhhVZYFRT/UWfcNyDIYiXt+tMWq7SLIYCRy9+RbsfMA5mU2v99w1ksmcXKgiOG0zAb6Vv/o"
    "htq9zx2RwUhUtVr3pYTpNUl9WwTO5PHRJoswsX8fo4jhjGJe0eSH49ax9vUWixzmJYORyGAksnTw0zHzACzJg25qFStmIavXtlPT"
    "cMXcr21NzX4HWrc8+ZbJKE/d07lc9k++vNHXyWB8u3Pu9hNxep3fdeLvsMhpVeHopbL01H8UFt+5dPq+CE14768e+S+3eUvl36cM"
    "RqJ7OpdbxJp3fgNYg/a7XAYPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAECD/D+xAnbx0wFnZgAAAABJRU5ErkJggg=="
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
# Claves = inspectores actuales (lista enviada por Juan el 2026-11-20).
FIRMAS = {
    "luis_trujillo": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "aaron_limon": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "alan_meyai": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "lizbeth_garcia": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "paola_luna": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "jesus_martinez": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "miguel_rodriguez": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "yesenia_hernandez": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "jorge_henkel": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "genaro_vega": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "juan": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
    "emir_navarro": ("Ing. Jose Antonio Hernandez del Valle", "Ing. Raúl Valdez Escamilla"),
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


def _casilla(marcada):
    """Casilla de verificación dibujada (cuadrado con X si está marcada).

    Se dibuja como imagen porque las fuentes base (Helvetica) no traen los
    glifos ☑/☐ y los renderizan como cuadros negros.
    """
    size = 72
    im = Image.new("RGB", (size, size), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([3, 3, size - 4, size - 4], outline="black", width=5)
    if marcada:
        d.line([16, 16, size - 16, size - 16], fill="black", width=6)
        d.line([size - 16, 16, 16, size - 16], fill="black", width=6)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    buf.seek(0)
    return RLImage(buf, width=13, height=13)


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
        [_campo("Responsable de evaluación:", datos.get("responsable", ""), est["valor"], w1, 150, est),
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
    concl = Table([
        [_casilla(conforme), Paragraph("Conforme", est["celda"]),
         _casilla(not conforme), Paragraph("No Conforme", est["celda"])],
        [Paragraph("En caso de obtener una evaluación con no cumplimiento aplicar plan de reacción declarado en PR-ACP-002", est["nota"]),
         Paragraph("", est["nota"]), Paragraph("", est["nota"]), Paragraph("", est["nota"])],
    ], colWidths=[26, ancho_util * 0.5 - 26, 26, ancho_util * 0.5 - 26])
    concl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("SPAN", (0, 1), (3, 1)),
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
