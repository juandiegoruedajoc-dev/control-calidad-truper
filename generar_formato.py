# -*- coding: utf-8 -*-
"""
generar_formato.py — Genera el formato FO-ACP-090 Rev. 1 llenando la plantilla
Excel tal cual (sin mover nada del formato): solo edita las celdas de valores,
inserta las fotos de evidencia en su área y marca la casilla Conforme/No Conforme,
y después convierte el Excel a PDF con LibreOffice.

El llenado se hace editando directamente el XML del .xlsx (zip), de modo que se
conservan intactos el logo, los cuadros de texto (título y firmas), los estilos,
las celdas combinadas y todo lo demás del formato original.

Colores de valores (como en las hojas llenas aprobadas): texto en negro,
OK/CUMPLE en verde, NO OK/NO CUMPLE en rojo.
"""

import io
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from xml.sax.saxutils import escape

from PIL import Image

# Plantilla embebida (base64) como respaldo: si el .xlsx no está en el repo
# (p. ej. Streamlit Cloud sin el archivo binario), se usa esta copia exacta.
_PLANTILLA_B64 = (
    "UEsDBBQABgAIAAAAIQDYlSyykQEAAEMGAAATAAgCW0NvbnRlbnRfVHlwZXNdLnhtbCCiBAIooAACAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADEVcluwjAQvVfqP0S+VomBQ1VVBA5dji0S9ANMPEks"
    "Etuyh+3vOzFLqyqAIpB6yWJ73nvzJjMZjjd1Fa3AeWV0yvpJj0WgMyOVLlL2NXuPn1jkUWgpKqMhZVvwbDy6vxvOthZ8RNHap6xE"
    "tM+c+6yEWvjEWNC0kxtXC6RXV3ArsoUogA96vUeeGY2gMcYGg42Gr5CLZYXR24aWd0rmSrPoZXeuoUqZsLZSmUASylda/iGJTZ6r"
    "DKTJljVBJ946ENKXAFhXiXWKGN0UECkxzyLeSmp18YdU1Y3osN4e4qAiuC5C904kFBmS8aWy/oHsOqUqbJ1kOAR+UhGdkhBNhMMP"
    "UZNjfFPxtXGLuTGL5DxKV0ODsUktlD4qPyMgnPY83Po3VtIkGIC7Chn8lxCkJgEertebEWAupe5xW4G/9ScQQC9Sl8KBnCI1YHFz"
    "Bb+xLwmRTqwbDXz/cL31e6CzxDSPJs5YTyPPQfcCHGZFEx1bAgKHCn6mRVvPHSlpYF5dcmgmsgTZRs7DL2D0DQAA//8DAFBLAwQU"
    "AAYACAAAACEAlwhFmPQAAABPAgAACwAIAl9yZWxzLy5yZWxzIKIEAiigAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKySTU/DMAyG70j8h8j31d2QEEJLd0FIuyFUfoBJ3A+1jaMkG92/J1yASmNw"
    "4Oiv149febubp1EdOcRenIZ1UYJiZ8T2rtXwUj+u7kDFRM7SKI41nDjCrrq+2j7zSCkPxa73UWUVFzV0Kfl7xGg6nigW4tnlSiNh"
    "opTD0KInM1DLuCnLWwzfNaBaaKq91RD29gZUffJ58+/a0jS94Qcxh4ldOrMCeU7sLNuVD5ktpD5fo2oKLScNVsxTTkck74uMDQrP"
    "I23+jvTzuThxIkuJ0Ejgy0AfHReJ1v9p0tLGL3/mEd8kDK8iwycMLt6gegcAAP//AwBQSwMEFAAGAAgAAAAhAIcbZP+WAwAA5ggA"
    "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"
    "8eO+rPIPW3ruV2eYrzuvFf3n0v+erqbhrKbdZl2Vx/Kh7pHlvmwzf/xZf9bP1ydL/Pm/y4wz7FfFp414gWdT7tua5IxOttyzMe+N"
    "xsYnY0Kuav68ub/p/u9uEkxHE39yFdzdja+Gw8niajbyp1eTu4W/8l1n4IzHf3Rvr5t+8q66vT7kj8X7ov718K7qPGzqX8p3BKiv"
    "djv92+v+Kdv9hnqEUKFTFQ833YUzz7xZk6fJ8tumeDkqq+L3zvGpfAmrzX222RfUfanj1/mH98W2WNcFtZPMf6JsN11R/YI67sd3"
    "Qubipdv5vSx379f5tviH6Nxbyjug0if6XoyKLP9cPteiIpUsxsuHsvwoUEz2B+IRm9pEk/N1vflULIstWfMnNOT+2zyE+PX0kKKk"
    "fmDzaYJmiJE498VD/rytl+X235v7+klU3JuMnYkznYy6OvVf5UtUbB6fakom2vTf+f3nVXFc04CidvXozVOd63JLctHfnd1GzAw0"
    "IPLX5ueLMt6bDMeDmSdsr5+PdbnTterysiS9+6Yk/dQlnd7Q80bfLjpURemnKur2Bs5o7H6jSkpuqqSfl1ZJ0518Tnqjuuyw544m"
    "U+dbtTonjeiXS+t1SHVZMf1yetipO3Tl2/uawo6WWPxyejvTqfvFNvfl220Gxiqv89vrqnzp0ARELT8ecjGdu3PRJNFNJr2T3Kee"
    "85WOoyxRYWbJG/dmo4Hxh9orH+zrhj0aK2vRvIWwSq2UY79BS4VUrxW5Vhz5Ek2MggFHIUcRRzFHCUcpR5mF+iTUSXcSgqnljHrj"
    "S/URdlr6KGTqw5GvEP0QY1+oGHAUchRJNKGJirrKkV7Up1vHue5/oplqrSzF5zzaeKIQDTeNUo4yC1mC0ZTABBvROAWC1U+b9cdF"
    "KSY82G290al7Cast+RQy5ePIV8iUj6OQo4ijmKOEo5SjzEKWWiQLU8slNb5n8LkndYSVm65nveqJ/aqXKo/xXlcc+RwFHIUcRRzF"
    "HCUcpRxlCkkfwZKLhh0fjRPcu+ACqqcrYYgmUKriPDhGLcVknimtN3okrDjyFTLnL45CjiKOYokcekfnVs3sViWq5dSlTuOTo0xZ"
    "IiWFl2JOaMKHaS8ks97ZV/jWSqIVFHZoRFJFuh1LhYymrThqnCgqaOQKeK6Qo4ijmKOEo5SjTCHlxZn6iLCqrY/n9i4ek8IO9TB6"
    "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"
    "AAB4bC9tZWRpYS9pbWFnZTEucG5niVBORw0KGgoAAAANSUhEUgAAAbEAAAC+CAMAAACML8HiAAAAAXNSR0IArs4c6QAAAARnQU1B"
    "AACxjwv8YQUAAAH+UExURQAAAP8AAP9nIP5nHv1lH/1lH/9AAP5mH/9jHP5mH/9kIP8AAP1mHv1nHf9gFf9mAP9VAP5mH/9lHf8A"
    "AP9jGf5mHv5mH/5nH/9jGv5mHv1nHv5lHv9VAP5nH/1mH/5mHv9bEv9nHv5nHv9VDv9VDP9mGv1mH/xkHv9kH/5nH/5lIP5mHv9m"
    "Hf5mH/9mHf1lH/9mIP5kHv5oHf9kHP5mH/9mHP9mHv1nH/9gAP9hHP9mGv5nH/9fFv1mHv9nHv9lHf1lHv1mH/9eGv9nG/9iH/9k"
    "G/5mH/5lHvxiHP8rAP5mHf5kHv5mH/5mHv1lHv9jF/5lHv9jHf9jHP9gIP9lHf9nHP9lHv9kG/9kHv5mHv5nH/9mHv9ZGv9cFP5l"
    "H/9OAP9NAP1nHv5mHv1mHv5mHv9JAP1nHf5lHf1lIP9mHP1mH/9eHP5mHv5mH/9oIP1mHvxlHP1lHv5mHv5mH/9kGv1oHf5mH/5n"
    "Hf9oH/9oGP9lG/5mH/9kHP5jHf5nHv9kHP5nHv1lHf9mHf9iHv5mH/5jHv5mH/9lHP9mH/5lHv5lHP9mHP9lHP9kHP1lHv9mHv9m"
    "G/5mH/9mHv1oHf9gEP5lHf5mH/5lHv5kHP1mHv9jHP9jHv9mH/9mHf9pGv1nHv9aHv9dF/9fHv9lHP9nH/9jHv9mGv9mHv9lG/9n"
    "HzUhU2kAAACqdFJOUwAC/8GLgwT7NvZZAeyGJQUD/WIDH/T89THiiskG4d7fDmbSEhUojssp67r7adFGpoDGtkDxLX+eCDcK+iOP"
    "dzWk6h5DOULy3GUGrcH0+fMs1z4SCHIlbzhe7/xnFBmvDQqX1or4B6muoWSeG+DlIKhJ7bH+RYLerVsgJtt/tutj6Hx7POqx+Ft6"
    "wrQ3ZS6pPEH5gI4QzdnbvPQkVcBQJ4YRCzNRfDsUeDA5RE0G8AAAAAlwSFlzAAAh1QAAIdUBBJy0nQAADuJJREFUeF7t3fe/JEtZ"
    "B+AV9aKi4jUHFDBhThhRxBzBgAHMiGLOOUcw55wVs/+lMz3PWx2qeqaqp0+f5VLPL5z5fuut6pn6sHt3796zT7qu67qu67qu67qu"
    "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"
)

def _plantilla_efectiva(plantilla_path):
    """Devuelve la ruta de la plantilla; si no existe, decodifica la embebida."""
    if plantilla_path and os.path.exists(plantilla_path):
        return plantilla_path
    import base64 as _b64mod, tempfile as _tf2
    fd, ruta = _tf2.mkstemp(suffix=".xlsx", prefix="plantilla_")
    with os.fdopen(fd, "wb") as f:
        f.write(_b64mod.b64decode("".join(_PLANTILLA_B64)))
    return ruta

EMU_PX = 9525          # 1 px a 96 dpi = 9525 EMU
EMU_PT = 12700         # 1 pt = 12700 EMU
MDW = 7                # px por unidad de ancho de columna (Calibri 11)

# Área de evidencia en la plantilla: B24:L26 (combinada)
EV_COL_INI, EV_COL_FIN = 2, 12      # columnas 1-indexadas B..L
EV_FILA_INI, EV_FILA_FIN = 24, 26   # filas 1-indexadas

# Casillas de conclusión: formas roundRect en el dibujo.
# (columna 0-indexada, fila 0-indexada) del ancla "from"
CASILLA_CONFORME = (2, 28)       # C29
CASILLA_NO_CONFORME = (8, 28)    # I29


# ----------------------------------------------------------------------------
# Métricas de la hoja (para posicionar las fotos en EMU)
# ----------------------------------------------------------------------------

def _col_emu(unidades):
    """Ancho de columna (unidades Excel) -> EMU."""
    if unidades <= 0:
        return 0
    return (int(unidades * MDW) + 5) * EMU_PX


def _leer_metricas(sheet_xml):
    """Devuelve (prefijos de columna, prefijos de fila) en EMU.

    prefijos_col[k] = borde izquierdo (EMU) de la columna 0-indexada k.
    prefijos_fila[k] = borde superior (EMU) de la fila 0-indexada k.
    """
    m = re.search(r'<sheetFormatPr[^>]*>', sheet_xml)
    def_col_w, def_row_h = 8.43, 15.0
    if m:
        dm = re.search(r'defaultColWidth="([\d.]+)"', m.group(0))
        if dm:
            def_col_w = float(dm.group(1))
        rm = re.search(r'defaultRowHeight="([\d.]+)"', m.group(0))
        if rm:
            def_row_h = float(rm.group(1))

    col_w = {}
    for cm in re.finditer(r'<col\s+min="(\d+)"\s+max="(\d+)"\s+width="([\d.]+)"', sheet_xml):
        a, b, w = int(cm.group(1)), int(cm.group(2)), float(cm.group(3))
        for c in range(a, b + 1):
            col_w[c] = w

    row_h = {}
    for rm in re.finditer(r'<row\s+r="(\d+)"[^>]*>', sheet_xml):
        tag = rm.group(0)
        hm = re.search(r'\sht="([\d.]+)"', tag)
        if hm:
            row_h[int(rm.group(1))] = float(hm.group(1))

    max_col, max_row = 20, 45
    pref_col = [0]
    for c in range(1, max_col + 1):
        pref_col.append(pref_col[-1] + _col_emu(col_w.get(c, def_col_w)))
    pref_fila = [0]
    for f in range(1, max_row + 1):
        pref_fila.append(pref_fila[-1] + int(row_h.get(f, def_row_h) * EMU_PT))
    return pref_col, pref_fila


def _celda_de_punto(pref, x):
    """Índice 0-indexado de la celda que contiene la coordenada x (EMU)."""
    lo, hi = 0, len(pref) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if pref[mid] <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo


# ----------------------------------------------------------------------------
# Estilos de valores: negro para texto, verde para OK/CUMPLE, rojo para NO OK
# ----------------------------------------------------------------------------

def _preparar_estilos(styles_xml):
    """Agrega fuentes y estilos para las celdas de valores.

    Devuelve (nuevo_styles_xml, mapa) con los índices de los nuevos estilos:
    J3, B18, F18, B33, K12, I8, G12, M_OK, M_NO, J_OK, J_NO, K_OK, K_NO.
    """
    # --- Fuentes nuevas ---
    fuentes_nuevas = [
        '<font><sz val="11" /><color rgb="FF000000" /><name val="Calibri" />'
        '<family val="2" /><scheme val="minor" /></font>',                       # 0: negro Calibri 11
        '<font><b /><sz val="11" /><color rgb="FF00B050" /><name val="Calibri" />'
        '<family val="2" /><scheme val="minor" /></font>',                       # 1: verde negrita
        '<font><b /><sz val="11" /><color rgb="FFFF0000" /><name val="Calibri" />'
        '<family val="2" /><scheme val="minor" /></font>',                       # 2: rojo negrita
        '<font><b /><sz val="16" /><color rgb="FF000000" /><name val="Calibri" />'
        '<family val="2" /><scheme val="minor" /></font>',                       # 3: negro negrita 16 (fecha)
        '<font><sz val="10" /><color rgb="FF000000" /><name val="Lora" /></font>',  # 4: negro Lora 10
    ]
    m_fonts = re.search(r'(<fonts count=")(\d+)("[^>]*>)', styles_xml)
    n_fonts = int(m_fonts.group(2))
    idx = {nombre: n_fonts + i for i, nombre in
           enumerate(['NEGRO', 'VERDE', 'ROJO', 'FECHA', 'LORA_NEGRO'])}
    styles_xml = (styles_xml[:m_fonts.start()] +
                  m_fonts.group(1) + str(n_fonts + len(fuentes_nuevas)) + m_fonts.group(3) +
                  styles_xml[m_fonts.end():])
    styles_xml = styles_xml.replace('</fonts>', ''.join(fuentes_nuevas) + '</fonts>', 1)

    # --- Estilos de celda nuevos (copias de los originales con otra fuente) ---
    m_xfs = re.search(r'(<cellXfs count=")(\d+)("[^>]*>)', styles_xml)
    n_xfs = int(m_xfs.group(2))
    cuerpo_xfs = styles_xml[m_xfs.end():styles_xml.index('</cellXfs>')]
    lista_xfs = re.findall(r'<xf [^>]*?(?:/>|>.*?</xf>)', cuerpo_xfs, re.S)

    def copia(indice, nueva_fuente=None, con_wrap=False):
        xf = lista_xfs[indice]
        if nueva_fuente is not None:
            xf = re.sub(r'fontId="\d+"', f'fontId="{nueva_fuente}"', xf, count=1)
        if con_wrap and 'wrapText' not in xf:
            def _wrap(m):
                attrs = m.group(1)
                if 'vertical=' not in attrs:
                    attrs += ' vertical="center"'
                return f'<alignment{attrs} wrapText="1" />'
            xf = re.sub(r'<alignment([^>]*?)\s*/>', _wrap, xf, count=1)
        return xf

    def nuevo(border_id, fuente):
        return (f'<xf numFmtId="0" fontId="{fuente}" fillId="0" borderId="{border_id}" '
                f'xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">'
                f'<alignment horizontal="center" vertical="center" /></xf>')

    nuevos_xfs = [
        copia(78, idx['FECHA']),                    # J3 fecha (negro negrita 16)
        copia(64, idx['NEGRO'], con_wrap=True),     # B18 característica (negro, con ajuste)
        copia(66, idx['NEGRO']),                    # F18 especificación (negro)
        copia(40, idx['NEGRO']),                    # B33 observaciones (negro)
        nuevo(7, idx['VERDE']),                     # M1/M2 OK (verde)
        nuevo(7, idx['ROJO']),                      # M1/M2 NO OK (rojo)
        copia(6, idx['VERDE']),                     # J18 M3 OK (verde)
        copia(6, idx['ROJO']),                      # J18 M3 NO OK (rojo)
        copia(67, idx['VERDE']),                    # K18 CUMPLE (verde)
        copia(67, idx['ROJO']),                     # K18 NO CUMPLE (rojo)
        copia(21, idx['LORA_NEGRO']),               # K12 cantidad (negro Lora)
        copia(24, con_wrap=True),                   # I8 prueba (con ajuste de texto)
        copia(25, con_wrap=True),                   # G12 clave (con ajuste de texto)
    ]
    mapa = {
        'J3': n_xfs + 0, 'B18': n_xfs + 1, 'F18': n_xfs + 2, 'B33': n_xfs + 3,
        'M_OK': n_xfs + 4, 'M_NO': n_xfs + 5,
        'J_OK': n_xfs + 6, 'J_NO': n_xfs + 7,
        'K_OK': n_xfs + 8, 'K_NO': n_xfs + 9,
        'K12': n_xfs + 10, 'I8': n_xfs + 11, 'G12': n_xfs + 12,
    }
    styles_xml = (styles_xml[:m_xfs.start()] +
                  m_xfs.group(1) + str(n_xfs + len(nuevos_xfs)) + m_xfs.group(3) +
                  styles_xml[m_xfs.end():])
    styles_xml = styles_xml.replace('</cellXfs>', ''.join(nuevos_xfs) + '</cellXfs>', 1)
    return styles_xml, mapa


def _es_ok(valor):
    v = str(valor or '').strip().upper()
    return v.startswith('OK') and not v.startswith('NO')


def _es_cumple(valor):
    v = str(valor or '').strip().upper()
    return 'CUMPLE' in v and 'NO' not in v


# ----------------------------------------------------------------------------
# Edición de celdas (inlineStr, conservando o sustituyendo el estilo s=...)
# ----------------------------------------------------------------------------

def _poner_valor(sheet_xml, ref, valor, s_nuevo=None):
    """Escribe `valor` en la celda `ref` como inlineStr."""
    patron = re.compile(r'<c r="' + re.escape(ref) + r'"([^>]*?)(?:/>|>(?:.*?)</c>)', re.S)
    m = patron.search(sheet_xml)
    if not m:
        return sheet_xml, False
    if s_nuevo is None:
        sm = re.search(r'\ss="(\d+)"', m.group(1))
        s_attr = f' s="{sm.group(1)}"' if sm else ''
    else:
        s_attr = f' s="{s_nuevo}"'
    esc = escape(str(valor))
    nuevo = f'<c r="{ref}"{s_attr} t="inlineStr"><is><t xml:space="preserve">{esc}</t></is></c>'
    return sheet_xml[:m.start()] + nuevo + sheet_xml[m.end():], True


def _altura_fila_actual(sheet_xml, fila):
    """Altura actual (pt) de una fila en el XML de la hoja."""
    m = re.search(r'<row\s+r="' + str(fila) + r'"[^>]*>', sheet_xml)
    if not m:
        return 15.0
    hm = re.search(r'\sht="([\d.]+)"', m.group(0))
    return float(hm.group(1)) if hm else 15.0


def _ajustar_altura_fila(sheet_xml, fila, altura_pt):
    """Fija la altura (pt) de una fila sin tocar nada más."""
    patron = re.compile(r'(<row\s+r="' + str(fila) + r'"[^>]*>)')
    m = patron.search(sheet_xml)
    if not m:
        return sheet_xml, False
    tag = m.group(1)
    if re.search(r'\sht="[\d.]+"', tag):
        nuevo_tag = re.sub(r'\sht="[\d.]+"', f' ht="{altura_pt}"', tag)
    else:
        nuevo_tag = tag[:-1] + f' ht="{altura_pt}">'
    return sheet_xml[:m.start(1)] + nuevo_tag + sheet_xml[m.end(1):], True


def _altura_para_texto(texto, ancho_px, tam_pt=11.0, margen_pt=8.0):
    """Altura (pt) necesaria para que `texto` quepa con ajuste en `ancho_px`."""
    if not texto:
        return 21.0
    font_px = tam_pt * 96.0 / 72.0
    char_px = 0.52 * font_px          # ancho medio de carácter (Calibri)
    usable = max(40.0, ancho_px - 10.0)
    chars_linea = max(8.0, usable / char_px)
    lineas = 0
    for parrafo in str(texto).split('\n'):
        lineas += max(1, int((len(parrafo) + chars_linea - 1) // chars_linea))
    alto_linea = tam_pt * 1.35
    return lineas * alto_linea + margen_pt


# ----------------------------------------------------------------------------
# Casillas Conforme / No Conforme (formas roundRect del dibujo)
# ----------------------------------------------------------------------------

def _marcar_casilla(drawing_xml, col0, row0):
    """Rellena de negro la casilla (forma) anclada en (col0, row0)."""
    patron = re.compile(
        r'(<xdr:twoCellAnchor>(?:(?!</xdr:twoCellAnchor>).)*?'
        r'<xdr:from><xdr:col>' + str(col0) + r'</xdr:col><xdr:colOff>\d+</xdr:colOff>'
        r'<xdr:row>' + str(row0) + r'</xdr:row>.*?</xdr:twoCellAnchor>)',
        re.S)
    m = patron.search(drawing_xml)
    if not m:
        return drawing_xml, False
    bloque = m.group(1)
    if 'roundRect' not in bloque:
        return drawing_xml, False
    nuevo = re.sub(
        r'<a:solidFill><a:sysClr[^>]*/></a:solidFill>',
        '<a:solidFill><a:srgbClr val="000000" /></a:solidFill>',
        bloque, count=1)
    if nuevo == bloque:
        return drawing_xml, False
    return drawing_xml[:m.start(1)] + nuevo + drawing_xml[m.end(1):], True


# ----------------------------------------------------------------------------
# Fotos: preparación y distribución en el área de evidencia
# ----------------------------------------------------------------------------

def _preparar_foto(bytes_foto, max_w_px, max_h_px):
    """Redimensiona la foto para caber en (max_w_px, max_h_px) sin ampliar.

    Devuelve (jpeg_bytes, w_px, h_px). Si la foto no se puede leer, (None, 0, 0).
    """
    try:
        img = Image.open(io.BytesIO(bytes_foto))
        try:
            img.draft("RGB", (max_w_px, max_h_px))
        except Exception:
            pass
        img = img.convert("RGB")
        w, h = img.size
        escala = min(1.0, max_w_px / w, max_h_px / h)
        nw, nh = max(1, int(w * escala)), max(1, int(h * escala))
        if (nw, nh) != (w, h):
            img = img.resize((nw, nh), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=82, optimize=True)
        return buf.getvalue(), nw, nh
    except Exception:
        return None, 0, 0


def _layout_fotos(aspectos, area_w, area_h):
    """Distribuye las fotos en una rejilla dentro del área (EMU).

    aspectos: lista de (w/h) de cada foto.
    Devuelve lista de rectángulos (x, y, w, h) en EMU relativos al origen del área.
    """
    n = len(aspectos)
    mejor = None
    for cols in range(n, 0, -1):
        rows = (n + cols - 1) // cols
        cw, ch = area_w / cols, area_h / rows
        rects, total = [], 0.0
        for asp in aspectos:
            if cw / ch >= asp:
                h, w = ch, ch * asp
            else:
                w, h = cw, cw / asp
            rects.append((w, h))
            total += w * h
        vacios = cols * rows - n
        clave = (total, -vacios, -rows)
        if mejor is None or clave > mejor[0]:
            mejor = (clave, cols, rows, rects)
    _, cols, rows, rects = mejor
    cw, ch = area_w / cols, area_h / rows
    resultado = []
    for i, (w, h) in enumerate(rects):
        cx = (i % cols) * cw
        cy = (i // cols) * ch
        resultado.append((cx + (cw - w) / 2, cy + (ch - h) / 2, w, h))
    return resultado


def _ancla_foto(col, col_off, row, row_off, x_abs, y_abs, w_emu, h_emu, rid, img_id, nombre):
    """XML de un ancla oneCellAnchor para una foto."""
    return (
        f'<xdr:oneCellAnchor>'
        f'<xdr:from><xdr:col>{col}</xdr:col><xdr:colOff>{col_off}</xdr:colOff>'
        f'<xdr:row>{row}</xdr:row><xdr:rowOff>{row_off}</xdr:rowOff></xdr:from>'
        f'<xdr:ext cx="{int(w_emu)}" cy="{int(h_emu)}"/>'
        f'<xdr:pic>'
        f'<xdr:nvPicPr><xdr:cNvPr id="{img_id}" name="{escape(nombre)}"/>'
        f'<xdr:cNvPicPr><a:picLocks noChangeAspect="1"/></xdr:cNvPicPr></xdr:nvPicPr>'
        f'<xdr:blipFill>'
        f'<a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        f'r:embed="{rid}" cstate="print"/>'
        f'<a:stretch><a:fillRect/></a:stretch></xdr:blipFill>'
        f'<xdr:spPr><a:xfrm><a:off x="{int(x_abs)}" y="{int(y_abs)}"/>'
        f'<a:ext cx="{int(w_emu)}" cy="{int(h_emu)}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr>'
        f'</xdr:pic><xdr:clientData/></xdr:oneCellAnchor>'
    )


# ----------------------------------------------------------------------------
# Generación principal
# ----------------------------------------------------------------------------

def generar_formato(datos, plantilla_path, fotos_bytes, carpeta_salida=None):
    """Llena la plantilla FO-ACP-090 y devuelve (ruta_xlsx, ruta_pdf, n_fotos).

    datos: dict con fecha, responsable, planta, periodicidad, prueba, codigo,
           clave, cantidad, caracteristica, especificacion, m1, m2, m3,
           resultado, conforme (bool), observaciones.
    fotos_bytes: lista de bytes de imágenes de evidencia.
    """
    plantilla_path = _plantilla_efectiva(plantilla_path)
    tmp = tempfile.mkdtemp(prefix='formato_')
    try:
        # 1) Descomprimir la plantilla
        with zipfile.ZipFile(plantilla_path) as z:
            z.extractall(tmp)

        ruta_sheet = os.path.join(tmp, 'xl', 'worksheets', 'sheet1.xml')
        ruta_styles = os.path.join(tmp, 'xl', 'styles.xml')
        ruta_drawing = os.path.join(tmp, 'xl', 'drawings', 'drawing1.xml')
        ruta_rels = os.path.join(tmp, 'xl', 'drawings', '_rels', 'drawing1.xml.rels')
        ruta_ct = os.path.join(tmp, '[Content_Types].xml')

        with open(ruta_sheet, encoding='utf-8') as f:
            sheet_xml = f.read()

        # 2) Estilos de valores (negro / verde OK / rojo NO OK)
        with open(ruta_styles, encoding='utf-8') as f:
            styles_xml = f.read()
        styles_xml, mapa_xf = _preparar_estilos(styles_xml)
        with open(ruta_styles, 'w', encoding='utf-8') as f:
            f.write(styles_xml)

        # 3) Corrección de la palabra "Responsable" (la plantilla trae "Reponsable")
        sheet_xml, _ = _poner_valor(sheet_xml, 'B6', 'Responsable de evaluación:')

        # 4) Llenar celdas de valores
        mapa = {
            'J3': (datos.get('fecha', ''), mapa_xf['J3']),
            'E6': (datos.get('responsable', ''), None),
            'J6': (datos.get('planta', ''), None),
            'E8': (datos.get('periodicidad', ''), None),
            'I8': (datos.get('prueba', ''), mapa_xf['I8']),
            'C12': (datos.get('codigo', ''), None),
            'G12': (datos.get('clave', ''), mapa_xf['G12']),
            'K12': (datos.get('cantidad', ''), mapa_xf['K12']),
            'B18': (datos.get('caracteristica', ''), mapa_xf['B18']),
            'F18': (datos.get('especificacion', ''), mapa_xf['F18']),
            'B33': (((datos.get('observaciones') or '').strip() or 'NA'), mapa_xf['B33']),
        }
        for ref, (valor, s_nuevo) in mapa.items():
            if valor is not None and str(valor).strip() != '':
                sheet_xml, _ = _poner_valor(sheet_xml, ref, str(valor), s_nuevo)

        # M1/M2/M3 y resultado: verde si OK/CUMPLE, rojo si NO OK/NO CUMPLE
        for ref, clave, ok_key, no_key in [
                ('H18', 'm1', 'M_OK', 'M_NO'),
                ('I18', 'm2', 'M_OK', 'M_NO'),
                ('J18', 'm3', 'J_OK', 'J_NO')]:
            valor = datos.get(clave, '')
            if valor is not None and str(valor).strip() != '':
                s_nuevo = mapa_xf[ok_key] if _es_ok(valor) else mapa_xf[no_key]
                sheet_xml, _ = _poner_valor(sheet_xml, ref, str(valor), s_nuevo)

        resultado = datos.get('resultado', '')
        if resultado is not None and str(resultado).strip() != '':
            s_nuevo = mapa_xf['K_OK'] if _es_cumple(resultado) else mapa_xf['K_NO']
            sheet_xml, _ = _poner_valor(sheet_xml, 'K18', str(resultado), s_nuevo)

        # 4b) Eliminar el espacio en blanco de RESULTADOS: ocultar las filas
        # vacías 19-22 (la app solo llena la fila 18) y pasar el borde grueso
        # inferior de la tabla a la fila 18.
        def _ocultar_fila(xml, n):
            xml = re.sub(rf'(<row\s+r="{n}"[^>]*?)\sht="[\d.]+"',
                         r'\1 ht="0"', xml, count=1)
            return re.sub(rf'(<row\s+r="{n}"[^>]*?)>',
                          r'\1 hidden="1">', xml, count=1)
        sheet_xml = _ocultar_fila(sheet_xml, 19)
        sheet_xml = _ocultar_fila(sheet_xml, 20)
        sheet_xml = _ocultar_fila(sheet_xml, 21)
        sheet_xml = re.sub(r'(<row\s+r="22"[^>]*?)\s+thickBot="1"',
                           r'\1', sheet_xml, count=1)
        sheet_xml = _ocultar_fila(sheet_xml, 22)
        sheet_xml = re.sub(r'(<row\s+r="18"[^>]*?)>',
                           r'\1 thickBot="1">', sheet_xml, count=1)

        # 5) Altura de la fila de resultados para que la especificación no se corte
        pref_col_tmp, _ = _leer_metricas(sheet_xml)
        ancho_fg_px = 0
        for c in (6, 7):
            ancho_fg_px += (pref_col_tmp[c] - pref_col_tmp[c - 1]) // EMU_PX
        altura_necesaria = _altura_para_texto(datos.get('especificacion', ''), ancho_fg_px)
        altura_necesaria = max(21.0, min(altura_necesaria, 180.0))
        sheet_xml, _ = _ajustar_altura_fila(sheet_xml, 18, round(altura_necesaria, 2))

        # 5b) Filas de Prueba (8) y Clave (12): altura si el texto largo no cabe
        ancho_i8_px = (pref_col_tmp[11] - pref_col_tmp[8]) // EMU_PX
        necesaria8 = _altura_para_texto(datos.get('prueba', ''), ancho_i8_px, tam_pt=10.0)
        sheet_xml, _ = _ajustar_altura_fila(
            sheet_xml, 8, round(max(_altura_fila_actual(sheet_xml, 8), necesaria8), 2))
        ancho_g12_px = (pref_col_tmp[8] - pref_col_tmp[6]) // EMU_PX
        necesaria12 = _altura_para_texto(datos.get('clave', ''), ancho_g12_px, tam_pt=10.0)
        sheet_xml, _ = _ajustar_altura_fila(
            sheet_xml, 12, round(max(_altura_fila_actual(sheet_xml, 12), necesaria12), 2))

        with open(ruta_sheet, 'w', encoding='utf-8') as f:
            f.write(sheet_xml)

        # 6) Dibujo: casilla + fotos
        with open(ruta_drawing, encoding='utf-8') as f:
            drawing_xml = f.read()

        casilla = CASILLA_CONFORME if datos.get('conforme', True) else CASILLA_NO_CONFORME
        drawing_xml, _ = _marcar_casilla(drawing_xml, casilla[0], casilla[1])

        fotos_insertadas = 0
        if fotos_bytes:
            pref_col, pref_fila = _leer_metricas(sheet_xml)
            # Área de evidencia B24:L26 en EMU absolutos
            x0 = pref_col[EV_COL_INI - 1]          # borde izquierdo de B
            x1 = pref_col[EV_COL_FIN]              # borde derecho de L
            y0 = pref_fila[EV_FILA_INI - 1]        # borde superior de fila 24
            y1 = pref_fila[EV_FILA_FIN]            # borde inferior de fila 26
            area_w, area_h = x1 - x0, y1 - y0
            margen = int(min(area_w, area_h) * 0.02)
            area_w -= 2 * margen
            area_h -= 2 * margen
            x0 += margen
            y0 += margen

            # Preparar fotos (tamaño natural para el layout)
            preparadas = []
            for fb in fotos_bytes:
                try:
                    img = Image.open(io.BytesIO(fb))
                    w, h = img.size
                    preparadas.append((fb, w / h if h else 1.0))
                except Exception:
                    continue

            if preparadas:
                aspectos = [a for _, a in preparadas]
                rects = _layout_fotos(aspectos, area_w, area_h)

                with open(ruta_rels, encoding='utf-8') as f:
                    rels_xml = f.read()
                rids_existentes = [int(x) for x in re.findall(r'Id="rId(\d+)"', rels_xml)]
                prox_rid = (max(rids_existentes) + 1) if rids_existentes else 2

                anclas = []
                nuevos_rels = []
                for i, ((fb, _), (rx, ry, rw, rh)) in enumerate(zip(preparadas, rects)):
                    max_w_px = max(1, int(rw / EMU_PX))
                    max_h_px = max(1, int(rh / EMU_PX))
                    jpeg, nw, nh = _preparar_foto(fb, max_w_px, max_h_px)
                    if jpeg is None:
                        continue
                    # Centrar dentro del rectángulo si la foto es más pequeña
                    w_emu, h_emu = nw * EMU_PX, nh * EMU_PX
                    x_abs = x0 + rx + (rw - w_emu) / 2
                    y_abs = y0 + ry + (rh - h_emu) / 2
                    col = _celda_de_punto(pref_col, int(x_abs))
                    row = _celda_de_punto(pref_fila, int(y_abs))
                    col_off = int(x_abs) - pref_col[col]
                    row_off = int(y_abs) - pref_fila[row]

                    rid = f'rId{prox_rid}'
                    prox_rid += 1
                    nombre_media = f'image{i + 2}.jpg'
                    ruta_media = os.path.join(tmp, 'xl', 'media', nombre_media)
                    os.makedirs(os.path.dirname(ruta_media), exist_ok=True)
                    with open(ruta_media, 'wb') as f:
                        f.write(jpeg)
                    nuevos_rels.append(
                        f'<Relationship Id="{rid}" '
                        f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                        f'Target="../media/{nombre_media}"/>')
                    anclas.append(_ancla_foto(
                        col, col_off, row, row_off, x_abs, y_abs, w_emu, h_emu,
                        rid, 100 + i, f'Evidencia {i + 1}'))
                    fotos_insertadas += 1

                if anclas:
                    # Insertar anclas antes de </xdr:wsDr>
                    drawing_xml = drawing_xml.replace('</xdr:wsDr>', ''.join(anclas) + '</xdr:wsDr>')
                    rels_xml = rels_xml.replace('</Relationships>', ''.join(nuevos_rels) + '</Relationships>')
                    with open(ruta_rels, 'w', encoding='utf-8') as f:
                        f.write(rels_xml)
                    # Asegurar tipo de contenido jpg
                    with open(ruta_ct, encoding='utf-8') as f:
                        ct_xml = f.read()
                    if 'Extension="jpg"' not in ct_xml:
                        ct_xml = ct_xml.replace(
                            '</Types>',
                            '<Default Extension="jpg" ContentType="image/jpeg"/></Types>')
                        with open(ruta_ct, 'w', encoding='utf-8') as f:
                            f.write(ct_xml)

        with open(ruta_drawing, 'w', encoding='utf-8') as f:
            f.write(drawing_xml)

        # 7) Reempaquetar el xlsx
        if carpeta_salida:
            os.makedirs(carpeta_salida, exist_ok=True)
            base = carpeta_salida
        else:
            base = tempfile.mkdtemp(prefix='formato_salida_')
        ruta_xlsx = os.path.join(base, 'formato_lleno.xlsx')
        with zipfile.ZipFile(ruta_xlsx, 'w', zipfile.ZIP_DEFLATED) as z:
            for raiz, _, archivos in os.walk(tmp):
                for nombre in archivos:
                    ruta_completa = os.path.join(raiz, nombre)
                    arcname = os.path.relpath(ruta_completa, tmp)
                    if arcname == 'formato_lleno.xlsx':
                        continue
                    z.write(ruta_completa, arcname)

        # 8) Convertir a PDF con LibreOffice
        perfil = os.path.join(tmp, 'lo_perfil')
        os.makedirs(perfil, exist_ok=True)
        cmd = [
            'soffice', '--headless', '--norestore', '--invisible',
            f'-env:UserInstallation=file://{perfil}',
            '--convert-to', 'pdf', '--outdir', base, ruta_xlsx,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        ruta_pdf = os.path.join(base, 'formato_lleno.pdf')
        if not os.path.exists(ruta_pdf):
            raise RuntimeError(f'LibreOffice no generó el PDF: {r.stdout} {r.stderr}')

        return ruta_xlsx, ruta_pdf, fotos_insertadas
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    import sys
    # Prueba rápida: python generar_formato.py <plantilla> <salida>
    plantilla = sys.argv[1] if len(sys.argv) > 1 else 'plantilla_fo_acp_090.xlsx'
    salida = sys.argv[2] if len(sys.argv) > 2 else '/tmp/prueba_formato'
    datos_prueba = {
        'fecha': '20/11/2026',
        'responsable': 'Ing. Paola Citlalli Luna Arteaga',
        'planta': '17 Perfileria',
        'periodicidad': 'Mensual',
        'prueba': 'PRUEBA DE TERMOFUSIÓN',
        'codigo': '49899',
        'clave': 'CV-003 TUBO DE PPR DE 1"',
        'cantidad': '3 probetas',
        'caracteristica': 'Prueba de termofusión',
        'especificacion': 'El tubo de PPR se debe de termofusionar con cualquier conector. Posterior a la termofusión no debe de existir ni movimiento ni desprendimiento en el ensamble.',
        'm1': 'OK', 'm2': 'OK', 'm3': 'OK',
        'resultado': 'CUMPLE',
        'conforme': True,
        'observaciones': '',
    }
    fotos = []
    for p in ['/home/hatch/workspace/test_formato/fotos/foto-002.png',
              '/home/hatch/workspace/test_formato/fotos/foto-003.png',
              '/home/hatch/workspace/test_formato/fotos/foto-004.png']:
        if os.path.exists(p):
            with open(p, 'rb') as f:
                fotos.append(f.read())
    xlsx, pdf, n = generar_formato(datos_prueba, plantilla, fotos, carpeta_salida=salida)
    print(f'XLSX: {xlsx}')
    print(f'PDF: {pdf}')
    print(f'Fotos insertadas: {n}')
