import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Control de Calidad: Inspección", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    div[data-testid="stAlert"] {
        padding: 20px;
    }
    .big-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Control de Calidad")

# Reglas fijas por pestaña
REGLAS_CPVC = {
    "diam_min": 28.52, 
    "diam_max": 28.68, 
    "oval_max": 0.30, 
    "esp_min": 2.12, 
    "esp_max": 2.38
}

REGLAS_TUBO = {
    "diam_min": 40.70, 
    "diam_max": 41.10, 
    "oval_max": 0.50, 
    "esp_min": 1.60, 
    "esp_max": 2.00
}

def limpiar_campos(tab_key):
    for key in ["d1", "d2", "d3", "d4", "e1", "e2", "e3", "e4"]:
        full_key = f"{key}_{tab_key}"
        if full_key in st.session_state:
            st.session_state[full_key] = None

def render_tab(reglas, tab_key):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### Diámetros (Norma: {reglas['diam_min']:.2f} - {reglas['diam_max']:.2f} mm)")
        d1 = st.number_input("D1", value=None, format="%.2f", step=0.01, key=f"d1_{tab_key}")
        d2 = st.number_input("D2", value=None, format="%.2f", step=0.01, key=f"d2_{tab_key}")
        d3 = st.number_input("D3", value=None, format="%.2f", step=0.01, key=f"d3_{tab_key}")
        d4 = st.number_input("D4", value=None, format="%.2f", step=0.01, key=f"d4_{tab_key}")
        st.caption(f"Límite de Ovalidad: {reglas['oval_max']:.2f} mm")

    with col2:
        st.markdown(f"#### Espesores (Norma: {reglas['esp_min']:.2f} - {reglas['esp_max']:.2f} mm)")
        e1 = st.number_input("E1", value=None, format="%.2f", step=0.01, key=f"e1_{tab_key}")
        e2 = st.number_input("E2", value=None, format="%.2f", step=0.01, key=f"e2_{tab_key}")
        e3 = st.number_input("E3", value=None, format="%.2f", step=0.01, key=f"e3_{tab_key}")
        e4 = st.number_input("E4", value=None, format="%.2f", step=0.01, key=f"e4_{tab_key}")

    st.divider()

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        evaluar_btn = st.button("🚀 EVALUAR MEDIDAS", type="primary", use_container_width=True, key=f"btn_eval_{tab_key}")
    with col_btn2:
        st.button("🧹 Limpiar Todo", on_click=limpiar_campos, args=(tab_key,), use_container_width=True, key=f"btn_clean_{tab_key}")

    if evaluar_btn:
        diams_raw = [d1, d2, d3, d4]
        esps_raw = [e1, e2, e3, e4]
        
        diams_filled = [d for d in diams_raw if d is not None]
        esps_filled = [e for e in esps_raw if e is not None]
        
        if len(diams_filled) == 0 and len(esps_filled) == 0:
            st.warning("⚠️ No has ingresado ninguna medición para evaluar.")
        else:
            fallos = []
            prom_diam = None
            ovalidad = None
            prom_esp = None
            
            # Evaluar Diámetros (independiente)
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
                        
            # Evaluar Espesores (independiente)
            if len(esps_filled) > 0:
                if len(esps_filled) < 4:
                    fallos.append("⚠️ Faltan datos de Espesor para realizar la evaluación de espesores.")
                else:
                    prom_esp = sum(esps_filled) / len(esps_filled)
                    
                    if not (reglas["esp_min"] <= prom_esp <= reglas["esp_max"]):
                        fallos.append(f"**Espesor Promedio** ({prom_esp:.2f} mm) fuera de rango ({reglas['esp_min']:.2f} a {reglas['esp_max']:.2f})")
                        
                    for i, esp in enumerate(esps_filled):
                        if not (reglas["esp_min"] <= esp <= reglas["esp_max"]):
                            fallos.append(f"**Espesor {i+1} individual** ({esp:.2f} mm) crítico fuera de rango ({reglas['esp_min']:.2f} a {reglas['esp_max']:.2f})")
                            
            st.divider()
            st.write("### 📝 Datos Calculados")
            
            cols = st.columns(3)
            if prom_diam is not None:
                cols[0].metric("Diámetro Promedio", f"{prom_diam:.2f} mm")
                cols[1].metric("Ovalidad Calculada", f"{ovalidad:.2f} mm")
            if prom_esp is not None:
                cols[2].metric("Espesor Promedio", f"{prom_esp:.2f} mm")

            # Mostrar los cuadros GRANDE en base al resultado
            if fallos:
                st.error("<div class='big-title'>RECHAZADO</div>", icon="🚫")
                st.error("#### Motivos de Falla:")
                for fallo in fallos:
                    st.markdown(f"- ❌ {fallo}")
            else:
                st.success("<div class='big-title'>PASADO</div>", icon="✅")
                st.success("✨ ¡Excelente! Las mediciones evaluadas cumplen con la norma.")

# --- Tab Layout ---
tab_cpvc, tab_estante = st.tabs(["CPVC", "Tubo de Estante"])

with tab_cpvc:
    render_tab(REGLAS_CPVC, "cpvc")

with tab_estante:
    render_tab(REGLAS_TUBO, "tubo")
