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

# --- Registro de Rafia en la base: cada medición se guarda en la hoja "Rafia" ---
# El webhook (Apps Script "Rafia base de datos") registra la medición en la hoja
# "Rafia" de la base de datos app calidad, sin tocar la hoja de tubos (Hoja 1).
# Pega aquí la URL de la aplicación web del script cuando esté creado.
RAFIA_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby4cUXL0QbfR7OBeDJRkK5mrtd05gvX_gFELRMADU7gVs1vtcSV8RgfikzuYJaqQgdx/exec"

def enviar_rafia(datos):
    try:
        if RAFIA_WEBHOOK_URL and RAFIA_WEBHOOK_URL != "TU_URL_DEL_SCRIPT_DE_RAFIA":
            requests.post(RAFIA_WEBHOOK_URL, json=datos, timeout=10)
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

st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
with col_img2:
    st.image("https://raw.githubusercontent.com/juandiegoruedajoc-dev/control-calidad-truper/main/logotipo%20de%20truper.png", width=180)

# --- Lógica de Equipos (Google Sheets) ---
@st.cache_data(ttl=60)
def cargar_equipos():
    url = "https://docs.google.com/spreadsheets/d/12wzscTu7K44OGYXzy1sjW77fPd2x7RmI/export?format=csv&gid=23729576"
    try:
        df = pd.read_csv(url, skiprows=13, header=None, encoding='utf-8')
        equipos = []
        for index, row in df.iterrows():
            codigo = str(row[1]).strip()
            if pd.isna(codigo) or codigo == 'nan' or not codigo:
                continue
                
            descripcion = str(row[2]).strip()
            fecha_str = str(row[7]).strip()
            ubicacion = str(row[10]).strip()
            status = str(row[13]).strip()
            
            try:
                fecha_obj = datetime.strptime(fecha_str, "%m/%d/%Y")
                fecha_formateada = fecha_obj.strftime("%Y-%m-%d")
            except:
                fecha_formateada = fecha_str
                
            equipos.append({
                "codigo": codigo,
                "descripcion": descripcion,
                "proxima_calibracion": fecha_formateada,
                "ubicacion": ubicacion,
                "status": status
            })
        return equipos
    except Exception as e:
        return []

if "app_iniciada" not in st.session_state:
    st.session_state["app_iniciada"] = True
    cargar_equipos.clear()

EQUIPMENT_DATA = cargar_equipos()

def verificar_equipos(dias_aviso=30):
    hoy = ahora_local().date()
    vencidos = []
    por_vencer = []
    
    for equipo in EQUIPMENT_DATA:
        if equipo.get("status") == "FUERA DE SERVICIO":
            continue
            
        try:
            fecha_cal = datetime.strptime(equipo["proxima_calibracion"], "%Y-%m-%d").date()
            dias_restantes = (fecha_cal - hoy).days
            
            if dias_restantes < 0:
                vencidos.append((equipo, dias_restantes))
            elif 0 <= dias_restantes <= dias_aviso:
                por_vencer.append((equipo, dias_restantes))
        except ValueError:
            pass
            
    return vencidos, por_vencer

st.title("Cálculos de tubos de perfileria")

equipos_global_vencidos, equipos_global_por_vencer = verificar_equipos(dias_aviso=7)
if equipos_global_vencidos or equipos_global_por_vencer:
    st.warning("⚠️ **ATENCIÓN:** Tienes equipos de medición vencidos o por vencer en los próximos 7 días. Revisa la pestaña de 'Equipos de medición'.")

REFERENCE_DATA_CPVC = {
    "CPVC-001": {"diam_min": 15.82, "diam_max": 15.98, "oval_max": 0.20, "esp_min": 1.40, "esp_max": 1.66},
    "CPVC-002": {"diam_min": 22.12, "diam_max": 22.28, "oval_max": 0.26, "esp_min": 1.65, "esp_max": 1.91},
    "CPVC-003": {"diam_min": 28.52, "diam_max": 28.68, "oval_max": 0.30, "esp_min": 2.12, "esp_max": 2.38},
    "CPVC-004": {"diam_min": 34.82, "diam_max": 34.98, "oval_max": 0.36, "esp_min": 3.18, "esp_max": 3.31},
    "CPVC-005": {"diam_min": 41.20, "diam_max": 41.40, "oval_max": 0.40, "esp_min": 3.76, "esp_max": 3.89},
    "CPVC-006": {"diam_min": 53.90, "diam_max": 54.10, "oval_max": 0.46, "esp_min": 4.90, "esp_max": 5.05},
}

REGLAS_TUBO = {
    "diam_min": 40.70, 
    "diam_max": 41.10, 
    "oval_max": 0.50, 
    "esp_min": 1.60, 
    "esp_max": 2.00
}

REFERENCE_DATA_PVC = {
    "Código 43038 (PVC-001)": {"diam_min": 21.20, "diam_max": 21.40, "oval_max": 0.40, "esp_min": 2.60, "esp_max": 2.80},
    "Código 43039 (PVC-002)": {"diam_min": 26.60, "diam_max": 26.80, "oval_max": 0.50, "esp_min": 2.70, "esp_max": 2.90},
    "Código 43040 (PVC-003)": {"diam_min": 33.30, "diam_max": 33.50, "oval_max": 0.50, "esp_min": 3.20, "esp_max": 3.40},
    "Código 45520 (PVC-004)": {"diam_min": 42.00, "diam_max": 42.30, "oval_max": 0.60, "esp_min": 3.40, "esp_max": 3.60},
    "Código 45521 (PVC-005)": {"diam_min": 48.10, "diam_max": 48.40, "oval_max": 0.60, "esp_min": 3.50, "esp_max": 3.70},
    "Código 45522 (PVC-006)": {"diam_min": 60.10, "diam_max": 60.50, "oval_max": 0.60, "esp_min": 3.70, "esp_max": 3.90},
}

REFERENCE_DATA_PVC_RD = {
    "Código 40081 (PVC-101)": {"diam_min": 21.20, "diam_max": 21.40, "oval_max": 0.50, "esp_min": 0.80, "esp_max": 1.10},
    "Código 40082 (PVC-102)": {"diam_min": 26.60, "diam_max": 26.80, "oval_max": 0.50, "esp_min": 1.20, "esp_max": 1.50},
    "Código 40083 (PVC-103)": {"diam_min": 33.30, "diam_max": 33.50, "oval_max": 0.50, "esp_min": 1.20, "esp_max": 1.50},
    "Código 40084 (PVC-104)": {"diam_min": 42.10, "diam_max": 42.30, "oval_max": 0.50, "esp_min": 1.30, "esp_max": 1.60},
    "Código 40085 (PVC-105)": {"diam_min": 48.10, "diam_max": 48.50, "oval_max": 0.50, "esp_min": 1.60, "esp_max": 1.90},
    "Código 40086 (PVC-106)": {"diam_min": 60.10, "diam_max": 60.50, "oval_max": 0.50, "esp_min": 2.00, "esp_max": 2.30},
}

REFERENCE_DATA_PPR = {
    "Código 49897 (CV-001)": {"diam_min": 20.00, "diam_max": 20.30, "oval_max": 1.20, "esp_min": 2.80, "esp_max": 3.10},
    "Código 49898 (CV-002)": {"diam_min": 25.00, "diam_max": 25.30, "oval_max": 1.20, "esp_min": 3.50, "esp_max": 3.80},
    "Código 49899 (CV-003)": {"diam_min": 32.00, "diam_max": 32.30, "oval_max": 1.30, "esp_min": 4.40, "esp_max": 4.70},
    "Código 45444 (CV-004)": {"diam_min": 40.00, "diam_max": 40.40, "oval_max": 1.40, "esp_min": 5.50, "esp_max": 5.90},
    "Código 45445 (CV-005)": {"diam_min": 50.00, "diam_max": 50.50, "oval_max": 1.40, "esp_min": 6.90, "esp_max": 7.40},
    "Código 45446 (CV-006)": {"diam_min": 63.00, "diam_max": 63.60, "oval_max": 1.60, "esp_min": 8.60, "esp_max": 9.10},
}

REFERENCE_DATA_CESPOL = {
    'Céspol 1-1/4"': {"diam_min": 32.00, "diam_max": 32.40, "oval_max": 0.50, "esp_min": 1.20, "esp_max": 1.60},
    'Céspol 1-1/2"': {"diam_min": 37.20, "diam_max": 37.60, "oval_max": 0.50, "esp_min": 1.30, "esp_max": 1.70},
}

# --- Especificaciones de Rafia (documento QDoc Truper, págs. 1-2) ---
# Calibre: peso por metro (g/m) de la muestra de 9 m. Denier: g/9000 m.
# La especificación depende solo de la trazabilidad (calibre): todos los
# códigos 2.2 comparten la misma, sin importar si es blanco o de color.
ESPEC_RAFIA = {
    "Rafia 2.2": {"codigos": "44492, 45032, 45037, 45031, 45033", "claves": "RAF-290, RAF-250, RAF-245, RAF-290C, RAF-250C", "gm_min": 2.11, "gm_max": 2.28, "den_min": 19008, "den_max": 20592},
    "Rafia 3": {"codigos": "40053", "claves": "RAF-345", "gm_min": 2.88, "gm_max": 3.12, "den_min": 25920, "den_max": 28080},
    "Rafia 3.8": {"codigos": "45038", "claves": "RAF-445", "gm_min": 3.65, "gm_max": 3.95, "den_min": 32832, "den_max": 35568},
    "Rafia 6": {"codigos": "40054", "claves": "RAF-645", "gm_min": 5.76, "gm_max": 6.24, "den_min": 51840, "den_max": 56160},
    "Rafia 8": {"codigos": "40062", "claves": "RAF-845", "gm_min": 7.68, "gm_max": 8.32, "den_min": 69120, "den_max": 74880},
}

def limpiar_campos(tab_key):
    keys_to_clear = []
    for key in ["d1", "d2", "d3", "d4", "e1", "e2", "e3", "e4"]:
        keys_to_clear.extend([key, f"int_{key}", f"man_{key}", f"chk_{key}"])
    for i in range(3):
        keys_to_clear.extend([f"ai_{i}", f"af_{i}", f"esp1_{i}", f"esp2_{i}"])
        
    for k in keys_to_clear:
        full_key = f"{k}_{tab_key}"
        if full_key in st.session_state:
            if full_key.startswith("chk_"):
                st.session_state[full_key] = False
            else:
                st.session_state[full_key] = None

def limpiar_rafia():
    if "peso_rafia" in st.session_state:
        st.session_state["peso_rafia"] = None
    if "trazabilidad_rafia" in st.session_state:
        st.session_state["trazabilidad_rafia"] = list(ESPEC_RAFIA.keys())[0]

def render_tab(reglas, tab_key, validar_espesor_individual=True, min_aplastamiento=None, nombre_tubo="Desconocido"):
    base_diam = int(reglas['diam_min'])
    base_esp = int(reglas['esp_min'])
    
    def create_input_card(label_str, id_str, base_val):
        val = None
        with st.container(border=True):
            modo_manual = st.checkbox(f"📏 **{label_str}** — Modo Libre", key=f"chk_{id_str}_{tab_key}")
                
            if not modo_manual:
                input_val = st.number_input(
                    f"🟢 Base: **{base_val}.**", 
                    value=None, 
                    format="%d", 
                    step=1, 
                    key=f"int_{id_str}_{tab_key}"
                )
                if input_val is not None:
                    val = base_val + (input_val / 100.0)
            else:
                input_val = st.number_input(
                    f"Lectura completa (Flotante)", 
                    value=None, 
                    format="%.2f", 
                    step=0.01, 
                    key=f"man_{id_str}_{tab_key}"
                )
                if input_val is not None:
                    val = input_val
        return val

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### Diámetros (Norma: {reglas['diam_min']:.2f} - {reglas['diam_max']:.2f} mm)")
            
        d1 = create_input_card("D1", "d1", base_diam)
        d2 = create_input_card("D2", "d2", base_diam)
        d3 = create_input_card("D3", "d3", base_diam)
        d4 = create_input_card("D4", "d4", base_diam)
        st.caption(f"Límite de Ovalidad: {reglas['oval_max']:.2f} mm")

    with col2:
        st.markdown(f"#### Espesores (Norma: {reglas['esp_min']:.2f} - {reglas['esp_max']:.2f} mm)")
            
        e1 = create_input_card("E1", "e1", base_esp)
        e2 = create_input_card("E2", "e2", base_esp)
        e3 = create_input_card("E3", "e3", base_esp)
        e4 = create_input_card("E4", "e4", base_esp)

    st.divider()
    
    aplastamiento_inputs = []
    if min_aplastamiento is not None:
        with st.expander(f"💥 Prueba de Aplastamiento (Mínimo requerido: > {min_aplastamiento}%)"):
            col_a1, col_a2, col_a3 = st.columns(3)
            for i, col in enumerate([col_a1, col_a2, col_a3]):
                with col:
                    with st.container(border=True):
                        st.markdown(f"**Probeta {i+1}**")
                        ai = st.number_input("Ai (Inicial)", value=None, format="%.2f", step=0.1, key=f"ai_{i}_{tab_key}")
                        af = st.number_input("AF (Final)", value=None, format="%.2f", step=0.1, key=f"af_{i}_{tab_key}")
                        esp1 = st.number_input("Esp1", value=None, format="%.2f", step=0.1, key=f"esp1_{i}_{tab_key}")
                        esp2 = st.number_input("Esp2", value=None, format="%.2f", step=0.1, key=f"esp2_{i}_{tab_key}")
                        if all(x is not None for x in [ai, af, esp1, esp2]) and ai > 0:
                            x_val = (af - esp1 - esp2) / ai
                            pct = (1 - x_val) * 100
                            aplastamiento_inputs.append(pct)
                            st.info(f"Resultado: {pct:.1f}%")
        st.divider()

    col_btns1, col_btns2 = st.columns([3, 1])
    with col_btns1:
        evaluar_btn = st.button("🚀 EVALUAR MEDIDAS", type="primary", use_container_width=True, key=f"btn_eval_{tab_key}")
    with col_btns2:
        st.button("🧹 Limpiar Todo", on_click=limpiar_campos, args=(tab_key,), use_container_width=True, key=f"btn_clean_{tab_key}")

    if evaluar_btn:
        diams_raw = [d1, d2, d3, d4]
        esps_raw = [e1, e2, e3, e4]
        
        diams_filled = [d for d in diams_raw if d is not None]
        esps_filled = [e for e in esps_raw if e is not None]
        
        hay_datos_principales = len(diams_filled) > 0 or len(esps_filled) > 0
        hay_aplastamiento = len(aplastamiento_inputs) > 0
        
        if not hay_datos_principales and not hay_aplastamiento:
            st.warning("⚠️ No has ingresado ninguna medición para evaluar.")
        else:
            fallos = []
            prom_diam = None
            ovalidad = None
            prom_esp = None
            
            if len(diams_filled) > 0:
                if len(diams_filled) < 4:
                    fallos.append("⚠️ Faltan datos de Diámetro para realizar la evaluación de diámetros.")
                else:
                    prom_diam = sum(diams_filled) / len(diams_filled)
                    min_diam = min(diams_filled)
                    max_diam = max(diams_filled)
                    ovalidad = max(abs(max_diam - prom_diam), abs(min_diam - prom_diam))
                    
                    if not (reglas["diam_min"] <= prom_diam <= reglas["diam_max"]):
                        fallos.append(f"**Diámetro Promedio** ({prom_diam:.2f} mm) fuera de rango ({reglas['diam_min']:.2f} a {reglas['diam_max']:.2f})")
                    if ovalidad > reglas["oval_max"]:
                        fallos.append(f"**Ovalidad** ({ovalidad:.2f} mm) excede límite ({reglas['oval_max']:.2f} mm)")
                        
            if len(esps_filled) > 0:
                if len(esps_filled) < 4:
                    fallos.append("⚠️ Faltan datos de Espesor para realizar la evaluación de espesores.")
                else:
                    prom_esp = sum(esps_filled) / len(esps_filled)
                    
                    if not (reglas["esp_min"] <= prom_esp <= reglas["esp_max"]):
                        fallos.append(f"**Espesor Promedio** ({prom_esp:.2f} mm) fuera de rango ({reglas['esp_min']:.2f} a {reglas['esp_max']:.2f})")
                        
                    if validar_espesor_individual:
                        for i, esp in enumerate(esps_filled):
                            if not (reglas["esp_min"] <= esp <= reglas["esp_max"]):
                                fallos.append(f"**Espesor {i+1} individual** ({esp:.2f} mm) crítico fuera de rango ({reglas['esp_min']:.2f} a {reglas['esp_max']:.2f})")
                                
            prom_aplastamiento = None
            if min_aplastamiento is not None:
                if len(aplastamiento_inputs) > 0:
                    if len(aplastamiento_inputs) < 3:
                        fallos.append("⚠️ Faltan datos en la prueba de Aplastamiento (requiere 3 probetas).")
                    else:
                        prom_aplastamiento = sum(aplastamiento_inputs) / len(aplastamiento_inputs)
                        if prom_aplastamiento <= min_aplastamiento:
                            fallos.append(f"**Aplastamiento Promedio** ({prom_aplastamiento:.1f}%) no cumple el mínimo requerido (> {min_aplastamiento}%).")
                        for i, pct in enumerate(aplastamiento_inputs):
                            if pct <= min_aplastamiento:
                                fallos.append(f"**Aplastamiento Probeta {i+1}** ({pct:.1f}%) no cumple el mínimo requerido (> {min_aplastamiento}%).")
                            
            st.divider()
            st.write("### 📝 Datos Calculados")
            
            cols = st.columns(4)
            if prom_diam is not None:
                cols[0].metric("Diámetro Promedio", f"{prom_diam:.2f} mm")
                cols[1].metric("Ovalidad Calculada", f"{ovalidad:.2f} mm")
            if prom_esp is not None:
                cols[2].metric("Espesor Promedio", f"{prom_esp:.2f} mm")
            if prom_aplastamiento is not None:
                cols[3].metric("Aplastamiento Prom.", f"{prom_aplastamiento:.1f}%")

            dictamen_final = "RECHAZADO" if fallos else "PASADO"
            if fallos:
                st.error("<div class='big-title'>RECHAZADO</div>", icon="🚫")
                st.error("#### Motivos de Falla:")
                for fallo in fallos:
                    st.markdown(f"- ❌ {fallo}")
            else:
                st.success("<div class='big-title'>PASADO</div>", icon="✅")
                st.success("✨ ¡Excelente! Las mediciones evaluadas cumplen con la norma.")
                
            datos_registro = {
                "fecha": ahora_local().strftime("%d/%m/%Y"),
                "hora": ahora_local().strftime("%H:%M:%S"),
                "tipo": tab_key.upper(),
                "clave": nombre_tubo,
                "prom_diam": f"{prom_diam:.2f}" if prom_diam is not None else "NA",
                "ovalidad": f"{ovalidad:.2f}" if ovalidad is not None else "NA",
                "prom_esp": f"{prom_esp:.2f}" if prom_esp is not None else "NA",
                "aplastamiento": f"{prom_aplastamiento:.1f}%" if prom_aplastamiento is not None else "NA",
                "resultado": dictamen_final,
                "motivos": " | ".join(fallos).replace("**", "") if fallos else "Ninguno"
            }
            threading.Thread(target=enviar_app_google_sheets, args=(datos_registro,)).start()

# --- Tab Layout ---
tab_cpvc, tab_estante, tab_pvc, tab_pvc_rd, tab_ppr, tab_cespol, tab_rafia, tab_equipos, tab_entrega_turno = st.tabs([
    "CPVC", "Tubo de Estante", "PVC Cédula 40", "PVC RD", "PPR", "Tubo de Céspol", "Rafia", "Equipos de medición", "📝 Entrega de Turno"
])

with tab_cpvc:
    clave = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_CPVC.keys()), key="sel_cpvc")
    st.divider()
    render_tab(REFERENCE_DATA_CPVC[clave], "cpvc", min_aplastamiento=80, nombre_tubo=clave)

with tab_estante:
    st.markdown("#### 📌 Especificaciones Fijas: Tubo de Estante")
    st.divider()
    render_tab(REGLAS_TUBO, "tubo", nombre_tubo="Tubo de Estante")

with tab_pvc:
    clave_pvc = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_PVC.keys()), key="sel_pvc")
    st.divider()
    render_tab(REFERENCE_DATA_PVC[clave_pvc], "pvc", min_aplastamiento=60, nombre_tubo=clave_pvc)

with tab_pvc_rd:
    clave_pvc_rd = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_PVC_RD.keys()), key="sel_pvc_rd")
    st.divider()
    render_tab(REFERENCE_DATA_PVC_RD[clave_pvc_rd], "pvc_rd", min_aplastamiento=80, nombre_tubo=clave_pvc_rd)

with tab_ppr:
    clave_ppr = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_PPR.keys()), key="sel_ppr")
    st.divider()
    render_tab(REFERENCE_DATA_PPR[clave_ppr], "ppr", validar_espesor_individual=False, nombre_tubo=clave_ppr)

with tab_cespol:
    clave_cespol = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_CESPOL.keys()), key="sel_cespol")
    st.divider()
    render_tab(REFERENCE_DATA_CESPOL[clave_cespol], "cespol", nombre_tubo=clave_cespol)

with tab_rafia:
    st.markdown("#### 📌 Especificaciones de Rafia")
    st.divider()

    trazabilidad_rafia = st.selectbox("📌 Seleccione Trazabilidad:", list(ESPEC_RAFIA.keys()), key="trazabilidad_rafia")
    espec = ESPEC_RAFIA[trazabilidad_rafia]

    col_raf_in, col_space = st.columns([1, 1])
    with col_raf_in:
        peso_rafia = st.number_input("Ingresar Peso (g) — muestra de 9 m", value=None, format="%.2f", step=0.1, key="peso_rafia")

    col_btns1, col_btns2 = st.columns([3, 1])
    with col_btns1:
        evaluar_rafia_btn = st.button("🚀 CALCULAR", type="primary", use_container_width=True, key="btn_eval_rafia")
    with col_btns2:
        st.button("🧹 Limpiar Todo", on_click=limpiar_rafia, use_container_width=True, key="btn_clean_rafia")

    if evaluar_rafia_btn:
        if peso_rafia is not None and peso_rafia > 0:
            peso_por_metro = peso_rafia / 9
            denier = peso_por_metro * 9000

            gm_ok = espec["gm_min"] <= peso_por_metro <= espec["gm_max"]
            den_ok = espec["den_min"] <= denier <= espec["den_max"]
            resultado_rafia = "PASADO" if (gm_ok and den_ok) else "RECHAZADO"
            motivos_rafia = []
            if not gm_ok:
                motivos_rafia.append("calibre fuera de rango")
            if not den_ok:
                motivos_rafia.append("denier fuera de rango")

            # Registrar la medición en la base (hoja "Rafia"), como los tubos
            datos_rafia = {
                "fecha": ahora_local().strftime("%d/%m/%Y"),
                "hora": ahora_local().strftime("%H:%M:%S"),
                "trazabilidad": trazabilidad_rafia,
                "peso_muestra": f"{peso_rafia:.2f}",
                "peso_por_metro": f"{peso_por_metro:.2f}",
                "denier": f"{denier:.0f}",
                "resultado": resultado_rafia,
                "motivos": " | ".join(motivos_rafia) if motivos_rafia else "Ninguno"
            }
            threading.Thread(target=enviar_rafia, args=(datos_rafia,)).start()

            st.divider()
            st.write("### 📝 Resultados Calculados")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div class='rafia-card'><div class='rafia-title'>Peso por metro (g/m)</div><div class='rafia-value'>{peso_por_metro:.2f}</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='rafia-card'><div class='rafia-title'>Denier</div><div class='rafia-value'>{denier:.0f}</div></div>", unsafe_allow_html=True)

            st.write(f"**Calibre:** {peso_por_metro:.2f} g/m — Especificación {espec['gm_min']:.2f} – {espec['gm_max']:.2f} g/m {'✅' if gm_ok else '❌'}")
            st.write(f"**Denier:** {denier:,.0f} — Especificación {espec['den_min']:,} – {espec['den_max']:,} g/9000 m {'✅' if den_ok else '❌'}")

            if resultado_rafia == "PASADO":
                st.success(f"✅ **{trazabilidad_rafia} — PASADO**")
            else:
                st.error(f"❌ **{trazabilidad_rafia} — RECHAZADO** ({', '.join(motivos_rafia)})")
        else:
            st.warning("⚠️ Ingresa un peso válido para calcular.")

    with st.expander("📋 Ver tabla completa de especificaciones"):
        st.dataframe(
            pd.DataFrame([
                {"Trazabilidad": k, "Códigos": v["codigos"], "Claves": v["claves"],
                 "Calibre (g/m)": f"{v['gm_min']:.2f} – {v['gm_max']:.2f}",
                 "Denier (g/9000 m)": f"{v['den_min']:,} – {v['den_max']:,}"}
                for k, v in ESPEC_RAFIA.items()
            ]),
            use_container_width=True, hide_index=True,
        )

with tab_equipos:
    st.header("Control de Equipos de Medición")
    
    vencidos_tot, por_vencer_tot = verificar_equipos(dias_aviso=30)
    msg = "*Reporte de Equipos - Control de Calidad*\n"
    if vencidos_tot:
        msg += "\n*🔴 Equipos Vencidos:*\n"
        for eq, _ in vencidos_tot:
            msg += f"- {eq['descripcion']} ({eq['codigo']}) - Venció: {eq['proxima_calibracion']}\n"
    if por_vencer_tot:
        msg += "\n*🟡 Equipos por Vencer:*\n"
        for eq, _ in por_vencer_tot:
            msg += f"- {eq['descripcion']} ({eq['codigo']}) - Vence: {eq['proxima_calibracion']}\n"
    if not vencidos_tot and not por_vencer_tot:
        msg += "\n✅ Todos los equipos están al día."
        
    numero_jefe = "525570708905"
    wa_link = f"https://wa.me/{numero_jefe}?text={urllib.parse.quote(msg)}"

    es_lunes = ahora_local().weekday() == 0
    falta_enviar = "wa_enviado_hoy" not in st.session_state or st.session_state["wa_enviado_hoy"] != ahora_local().date()

    if es_lunes and falta_enviar:
        st.info("📅 **RECORDATORIO:** Es Lunes. No olvides enviar el reporte de equipos de esta semana.")
        col_wa1, col_wa2 = st.columns([2, 1])
        with col_wa1:
            st.markdown(f'<a href="{wa_link}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #25D366; color: white; text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px; font-weight: bold; width: 100%;">📲 Abrir WhatsApp y Enviar Reporte</a>', unsafe_allow_html=True)
        with col_wa2:
            if st.button("✅ Marcar como Enviado", use_container_width=True):
                st.session_state["wa_enviado_hoy"] = ahora_local().date()
                st.rerun()
        st.markdown("---")
    else:
        st.markdown(f'<a href="{wa_link}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #128C7E; color: white; text-align: center; text-decoration: none; font-size: 14px; border-radius: 6px; font-weight: bold;">📤 Enviar Reporte Manualmente</a>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    vencidos, por_vencer = verificar_equipos(dias_aviso=30)
    if vencidos or por_vencer:
        total_alertas = len(vencidos) + len(por_vencer)
        with st.container():
            st.subheader(f"🔔 Alertas ({total_alertas})")
            if vencidos:
                for eq, dias in vencidos:
                    st.error(f"🔴 **VENCIDO ({abs(dias)} días):** {eq['descripcion']} ({eq['codigo']}) - Venció el {eq['proxima_calibracion']}")
            if por_vencer:
                for eq, dias in por_vencer:
                    st.warning(f"🟡 **POR VENCER (en {dias} días):** {eq['descripcion']} ({eq['codigo']}) - Vence el {eq['proxima_calibracion']}")
    else:
        st.success("✅ Todos los equipos activos están al día con su calibración.")
        
    st.markdown("---")
    st.subheader("Inventario de Equipos")
    
    df_equipos = pd.DataFrame(EQUIPMENT_DATA)
    if not df_equipos.empty:
        df_equipos.columns = ["Código", "Descripción", "Próxima Calibración", "Ubicación", "Status"]
    
    st.dataframe(df_equipos, use_container_width=True, hide_index=True)

# =============================================================
# PESTAÑA: ENTREGA DE TURNO (12 Puntos Oficiales)
# =============================================================
with tab_entrega_turno:
    st.header("📝 Cuestionario de Entrega de Turno")
    st.markdown("Completa **todos los campos obligatorios (\*)** antes de enviar. Los datos quedan registrados automáticamente.")
    st.divider()

    errores = []

    # ── 1. NOMBRE DE QUIÉN ENTREGA ────────────────────────────
    st.markdown("**1. Nombre de quién entrega \\***")
    nombre = st.radio(
        "Selecciona tu nombre",
        ["Aarón", "Alan", "Luis", "Jorge", "Paola", "Lizbeth", "Emir", "Yesenia", "Genaro", "Miguel", "Diego", "Jesús"],
        horizontal=True, index=None, key="et_nombre", label_visibility="collapsed"
    )
    if not nombre:
        errores.append("1. Nombre de quién entrega")

    st.divider()

    # ── 2. TURNO QUE SE ENTREGA ───────────────────────────────
    st.markdown("**2. Turno que se entrega \\***")
    turno = st.radio(
        "Selecciona el turno",
        ["Primer Turno", "Segundo Turno", "4D05", "4D06"],
        horizontal=True, index=None, key="et_turno", label_visibility="collapsed"
    )
    if not turno:
        errores.append("2. Turno que se entrega")

    st.divider()

    # ── 3. ÁREA O PROCESOS ────────────────────────────────────
    st.markdown("**3. Área o procesos \\***")
    area = st.radio(
        "Selecciona el área",
        ["CPVC / Estante / Carretes", "PPR / Rafia", "PVC / Canaleta / Trenzado"],
        horizontal=True, index=None, key="et_area", label_visibility="collapsed"
    )
    if not area:
        errores.append("3. Área o procesos")

    st.divider()

    # ── 4. CONDICIONADOS ABIERTOS ─────────────────────────────
    st.markdown("**4. Condicionados abiertos — Código y ubicación \\***")
    condicionados = st.text_input("Escriba su respuesta", placeholder="Ej: COND-045 — Área de cuarentena L2", key="et_condicionados")
    if not condicionados.strip():
        errores.append("4. Condicionados abiertos")

    st.divider()

    # ── 5. DESVIACIONES ACTIVAS ───────────────────────────────
    st.markdown("**5. Desviaciones activas** *(Semanal — solo aplica 1T)*")
    desviaciones = st.text_input("Escriba su respuesta", placeholder="Ej: DEV-012 activa desde el lunes", key="et_desviaciones")

    st.divider()

    # ── 6. INSTRUMENTOS DE MEDICIÓN ───────────────────────────
    st.markdown("**6. Instrumentos de medición \\*** *(Diario)*")
    df_instrumentos = pd.DataFrame({
        "Inspector": ["Inspector 1", "Inspector 2", "Inspector 3"],
        "Área Asignada": ["CPVC / Carretes / Estante", "PPR / Rafia", "PVC / Canaleta / Trenzado"],
        "Calibrador Vernier": ["IP-ACP17-068", "IP-ACP17-062", "IP-ACP17-001"],
        "Calibrador garganta": ["IP-ACP7E-051", "IP-ACP17-016", "IP-ACP17-050"],
        "Flexómetro": ["IP-ACP17-063", "IP-ACP17-066", "IP-ACP17-004"],
    })
    st.dataframe(df_instrumentos, use_container_width=True, hide_index=True)

    st.markdown("**¿Qué inspector entrega el turno?** *")
    inspector_entrega = st.radio(
        "Selecciona el inspector que entrega",
        ["Inspector 1", "Inspector 2", "Inspector 3"],
        horizontal=True, index=None, key="et_inspector_entrega", label_visibility="collapsed"
    )
    if not inspector_entrega:
        errores.append("6. Inspector que entrega el turno")

    st.markdown("**Estado general de los instrumentos del inspector que entrega** *")

    inspectores_data = {}
    inspectores_nombres = ["Inspector 1", "Inspector 2", "Inspector 3"]

    if inspector_entrega:
        estado_insp = st.radio(
            f"Estado para {inspector_entrega}",
            ["OK", "NOK", "Otras"],
            horizontal=True, index=None, key=f"et_estado_{inspector_entrega}"
        )

        obs_insp = ""
        archivo_insp = None

        if estado_insp in ["NOK", "Otras"]:
            obs_insp = st.text_input(f"Observaciones / Detalle para {inspector_entrega}", key=f"et_obs_{inspector_entrega}")
            archivo_insp = st.file_uploader(
                f"Cargar archivo / foto de evidencia para {inspector_entrega}",
                type=["png", "jpg", "jpeg", "pdf"],
                key=f"et_arch_{inspector_entrega}"
            )
            if archivo_insp:
                st.success(f"✔ Archivo cargado: {archivo_insp.name}")

        if not estado_insp:
            errores.append(f"6. Instrumentos de medición ({inspector_entrega})")

        inspectores_data[inspector_entrega] = {
            "estado": estado_insp,
            "observaciones": obs_insp,
            "archivo": archivo_insp
        }

    for insp in inspectores_nombres:
        if insp != inspector_entrega:
            inspectores_data[insp] = {
                "estado": "No aplica",
                "observaciones": "",
                "archivo": None
            }

    st.divider()

    # ── 7. CARGA DE ARCHIVO DE INSTRUMENTOS (SEMANAL 2T) ───────
    st.markdown("**7. Cargar archivo con etiquetas visibles y en buen estado de los instrumentos de medición** *(Semanal, APLICA SOLO 2T)*")
    archivo_instrumentos = st.file_uploader(
        "Subir archivo de instrumentos",
        type=["png", "jpg", "jpeg", "pdf"],
        key="et_arch_inst"
    )
    if archivo_instrumentos:
        st.success(f"✔ Archivo cargado: {archivo_instrumentos.name}")

    st.divider()

    # ── 8. MASTERS EN BUEN ESTADO ────────────────────────────
    st.markdown("**8. Masters en buen estado \\*** *(Semanal, APLICA SOLO 2T)*")
    masters = st.radio(
        "Estado de masters",
        ["OK", "NOK", "Otras"],
        horizontal=True, index=None, key="et_masters"
    )
    if not masters:
        errores.append("8. Masters en buen estado")
    masters_obs = ""
    if masters == "Otras":
        masters_obs = st.text_input("Especifique el estado de los masters", key="et_masters_obs")

    st.divider()

    # ── 9. TARIMAS PRELIBERADAS / SIN LIBERAR ────────────────
    st.markdown("**9. Número de tarimas preliberadas y/o sin liberar que se dejan pendientes \\***")
    tarimas = st.text_input("Escriba su respuesta", placeholder="Ej: 3 tarimas en L2", key="et_tarimas")
    if not tarimas.strip():
        errores.append("9. Número de tarimas pendientes")

    st.divider()

    # ── 10. SEGUIMIENTO 5'S ───────────────────────────────────
    st.markdown("**10. Seguimiento 5's (Cargar archivo del área libre de muestras y/o scrap) \\*** *(Diario)*")
    archivo_5s = st.file_uploader(
        "Subir archivo 5's",
        type=["png", "jpg", "jpeg", "pdf"],
        key="et_arch_5s"
    )
    if archivo_5s:
        st.success(f"✔ Archivo cargado: {archivo_5s.name}")

    st.divider()

    # ── 11. ÁREA DE CUARENTENA ────────────────────────────────
    st.markdown("**11. Área de cuarentena (Cargar archivo del área de cuarentena correspondiente libre de obstáculos) \\***")
    df_cuarentena = pd.DataFrame({
        "Inspector": ["Inspector 1 (CPVC / Carretes / Estante)", "Inspector 2 (PPR / Rafia)", "Inspector 3 (PVC / Canaleta / Trenzado)"],
        "Área Correspondiente": ["Área Estante", "Área Cuerda y Rafia", "Área Canaleta y Perfilería"]
    })
    st.dataframe(df_cuarentena, use_container_width=True, hide_index=True)

    archivo_cuarentena = st.file_uploader(
        "Subir archivo cuarentena",
        type=["png", "jpg", "jpeg", "pdf"],
        key="et_arch_cuarentena"
    )
    if archivo_cuarentena:
        st.success(f"✔ Archivo cargado: {archivo_cuarentena.name}")

    st.divider()

    # ── 12. OBSERVACIONES ─────────────────────────────────────
    st.markdown("**12. Observaciones \\***")
    observaciones = st.text_area("Escriba su respuesta", placeholder="Comentarios finales...", key="et_observaciones")
    if not observaciones.strip():
        errores.append("12. Observaciones")

    st.divider()

    # ── BOTÓN DE ENVÍO ────────────────────────────────────────
    if st.button("🚀 Enviar Cuestionario de Turno", type="primary", use_container_width=True):
        if errores:
            st.error("⚠️ Faltan los siguientes campos obligatorios por responder:")
            for err in set(errores):
                st.markdown(f"- ❌ {err}")
        else:
            datos_cuestionario = {
                "fecha": ahora_local().strftime("%d/%m/%Y"),
                "hora": ahora_local().strftime("%H:%M:%S"),
                "tipo": "ENTREGA_TURNO",
                "nombre": nombre,
                "turno": turno,
                "area": area,
                "condicionados": condicionados,
                "desviaciones": desviaciones,
                "instrumentos_inspector_1": f"{inspectores_data['Inspector 1']['estado']} - {inspectores_data['Inspector 1']['observaciones']}",
                "instrumentos_inspector_2": f"{inspectores_data['Inspector 2']['estado']} - {inspectores_data['Inspector 2']['observaciones']}",
                "instrumentos_inspector_3": f"{inspectores_data['Inspector 3']['estado']} - {inspectores_data['Inspector 3']['observaciones']}",
                "masters": masters if masters != "Otras" else f"Otras: {masters_obs}",
                "tarimas": tarimas,
                "observaciones": observaciones
            }
            threading.Thread(target=enviar_app_google_sheets, args=(datos_cuestionario,)).start()
            fotos = []
            archivo_insp_entrega = inspectores_data.get(inspector_entrega, {}).get("archivo") if inspector_entrega else None
            f = foto_a_base64(archivo_insp_entrega)
            if f:
                f["punto"] = "6. Instrumentos " + str(inspector_entrega)
                fotos.append(f)
            f = foto_a_base64(archivo_instrumentos)
            if f:
                f["punto"] = "7. Archivo de instrumentos"
                fotos.append(f)
            f = foto_a_base64(archivo_5s)
            if f:
                f["punto"] = "10. Seguimiento 5's"
                fotos.append(f)
            f = foto_a_base64(archivo_cuarentena)
            if f:
                f["punto"] = "11. Área de cuarentena"
                fotos.append(f)
            if fotos:
                datos_fotos = dict(datos_cuestionario)
                datos_fotos["inspector_entrega"] = inspector_entrega
                datos_fotos["fotos"] = fotos
                threading.Thread(target=enviar_fotos_entrega, args=(datos_fotos,)).start()
            st.success("✨ ¡Cuestionario de Entrega de Turno enviado correctamente!")