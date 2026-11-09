import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import threading
import requests
import json
import base64
import urllib.parse

# --- Configuración Base de Datos Invisible ---
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzKz2I-_NrWneexvxl6D78NELPu0An1YpDXsYgwsRf28L1LgLoycRFe8vB0d2RY6bTrug/exec"

def enviar_a_google_sheets(datos):
    try:
        if WEBHOOK_URL != "TU_LINK_AQUI":
            requests.post(WEBHOOK_URL, json=datos, timeout=5)
    except Exception:
        pass # Falla silenciosamente para no interrumpir al usuario

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

st.markdown(f"""
    <link rel="manifest" href="data:application/manifest+json;base64,{manifest_b64}">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/juandiegoruedajoc-dev/control-calidad-truper/main/logotipo%20de%20truper.png">
    <meta name="apple-mobile-web-app-title" content="Cálculos Truper">
    <meta name="application-name" content="Cálculos Truper">
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Permite el comportamiento nativo de "Pull to refresh" en móviles */
    body, html, .stApp {
        overscroll-behavior-y: auto !important;
    }
    .big-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0px !important;
    }
    .rafia-card {
        background-color: #f9f9f9;
        border: 2px solid #F0711B;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .rafia-title {
        font-size: 1.6rem;
        color: #555;
        margin-bottom: 15px;
    }
    .rafia-value {
        font-size: 3rem;
        font-weight: 900;
        color: #F0711B;
    }
    /* Botón flotante en el costado derecho (medio de la pantalla) */
    div:has(> button[key="btn_modal_flotante"]) {
        position: fixed !important;
        top: 50% !important;
        right: 0px !important;
        transform: translateY(-50%) !important;
        z-index: 99999 !important;
    }
    div:has(> button[key="btn_modal_flotante"]) button {
        background: linear-gradient(135deg, #F0711B, #d45f10) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px 0px 0px 25px !important;
        padding: 14px 20px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        box-shadow: -4px 4px 15px rgba(0,0,0,0.3) !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    div:has(> button[key="btn_modal_flotante"]) button:hover {
        padding-left: 2
