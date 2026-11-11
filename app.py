import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# Hora local (Ciudad de México, UTC-6 fijo, sin horario de verano desde 2022).
# La app corre en un servidor con hora UTC; sin esto, las horas salían 6 horas adelante.
ZONA_MEXICO = timezone(timedelta(hours=-6))

def ahora_local():
    return datetime.now(ZONA_MEXICO)
import threading
import requests
import json
import base64
import urllib.parse

# --- Configuración Base de Datos Invisible ---
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzKz2I-_NrWneexvxl6D78NELPu0An1YpDXsYgwsRf28L1LgLoycRFe8vB0d2RY6bTrug/exec"

def enviar_app_google_sheets(datos):
    try:
        if WEBHOOK_URL != "TU_LINK_AQUI":
            requests.post(WEBHOOK_URL, json=datos, timeout=5)
    except Exception:
        pass

# --- Fotos de la entrega de turno: se comprimen y se mandan al segundo webhook ---
# El segundo webhook (Apps Script "Fotos entrega de turno") guarda las fotos en
# Drive y registra la entrega completa; un proceso aparte las pasa a la base Excel.
# Pega aquí la URL de la aplicación web del script cuando esté creado.
FOTOS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz7Y0-vqtQzHoEtdI1DPFx53JbYr5I6BSHHK9WfewbVl9YOONTDcicbFdQHCFQ1ExS-Sw/exec"

def foto_a_base64(archivo):
    """Comprime una foto a 1024 px JPEG calidad 70 y la devuelve en base64. Un PDF se envía tal cual."""
    if archivo is None:
        return None
    try:
        datos = archivo.getvalue()
    except Exception:
        return None
    nombre = getattr(archivo, "name", "foto.jpg")
    if nombre.lower().endswith(".pdf"):
        return {"nombre": nombre, "tipo": "application/pdf", "datos": base64.b64encode(datos).decode("utf-8")}
    try:
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(datos)).convert("RGB")
        img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=70, optimize=True)
        return {"nombre": nombre.rsplit(".", 1)[0] + ".jpg", "tipo": "image/jpeg", "datos": base64.b64encode(buf.getvalue()).decode("utf-8")}
    except Exception:
        return {"nombre": nombre, "tipo": "image/jpeg", "datos": base64.b64encode(datos).decode("utf-8")}

def enviar_fotos_entrega(datos):
    try:
        if FOTOS_WEBHOOK_URL and FOTOS_WEBHOOK_URL != "TU_URL_DEL_SCRIPT_DE_FOTOS":
            requests.post(FOTOS_WEBHOOK_URL, json=datos, timeout=30)
    except Exception:
        pass

# Configuración de la página
st.set_page_config(
    page_title='Cálculos de tubos de perfileria', 
    page_icon='https://raw.githubusercontent.com/juandiegoruedajoc-dev/control-calidad-truper/main/logotipo%20de%20truper.png', 
    layout='wide', 
    initial_sidebar_state='collapsed'
)

manifest_json = """
{
  "name": "Cálculos de tubos de perfileria",
  "short_name": "Cálculos Truper",
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone",
  "icons": [
    {
      "src": "https://raw.githubusercontent.com/juandiegoruedajoc-dev/control-calidad-truper/main/logotipo%20de%20truper.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "https://raw.githubusercontent.com/juandiegoruedajoc-dev/control-calidad-truper/main/logotipo%20de%20truper.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""
manifest_b64 = base64.b64encode(manifest_json.encode('utf-8')).decode('utf-8')

st.markdown(
    f'<link rel="manifest" href="data:application/manifest+json;base64,{manifest_b64}">'
    '<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/juandiegoruedajoc-dev/control-calidad-truper/main/logotipo%20de%20truper.png">'
    '<meta name="apple-mobile-web-app-title" content="Cálculos Truper">'
    '<meta name="application-name" content="Cálculos Truper">',
    unsafe_allow_html=True
)