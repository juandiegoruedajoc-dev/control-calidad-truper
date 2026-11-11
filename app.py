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

def enviar_app_google_sheets(datos):
    try:
        if WEBHOOK_URL != "TU_LINK_AQUI":
            requests.post(WEBHOOK_URL, json=datos, timeout=5)
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
    hoy = datetime.now().date()
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
                "fecha": datetime.now().strftime("%d/%m/%Y"),
                "hora": datetime.now().strftime("%H:%M:%S"),
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
    
    col_raf_in, col_space = st.columns([1, 1])
    with col_raf_in:
        peso_rafia = st.number_input("Ingresar Peso (g)", value=None, format="%.2f", step=0.1, key="peso_rafia")
    
    col_btns1, col_btns2 = st.columns([3, 1])
    with col_btns1:
        evaluar_rafia_btn = st.button("🚀 CALCULAR", type="primary", use_container_width=True, key="btn_eval_rafia")
    with col_btns2:
        st.button("🧹 Limpiar Todo", on_click=limpiar_rafia, use_container_width=True, key="btn_clean_rafia")
    
    if evaluar_rafia_btn:
        if peso_rafia is not None and peso_rafia > 0:
            peso_por_metro = peso_rafia / 9
            denier = peso_por_metro * 9000
            
            st.divider()
            st.write("### 📝 Resultados Calculados")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div class='rafia-card'><div class='rafia-title'>Peso por metro (g/m)</div><div class='rafia-value'>{peso_por_metro:.2f}</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='rafia-card'><div class='rafia-title'>Denier</div><div class='rafia-value'>{denier:.0f}</div></div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Ingresa un peso válido para calcular.")

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

    es_lunes = datetime.now().weekday() == 0
    falta_enviar = "wa_enviado_hoy" not in st.session_state or st.session_state["wa_enviado_hoy"] != datetime.now().date()

    if es_lunes and falta_enviar:
        st.info("📅 **RECORDATORIO:** Es Lunes. No
