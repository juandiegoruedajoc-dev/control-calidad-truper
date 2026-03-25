import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Control de Calidad: CPVC", layout="centered", initial_sidebar_state="collapsed")

# Datos de referencia
REFERENCE_DATA = {
    "CPVC-001": {"diam_min": 15.82, "diam_max": 15.98, "oval_max": 0.20, "esp_min": 1.40, "esp_max": 1.66},
    "CPVC-002": {"diam_min": 22.12, "diam_max": 22.28, "oval_max": 0.26, "esp_min": 1.65, "esp_max": 1.91},
    "CPVC-003": {"diam_min": 28.52, "diam_max": 28.68, "oval_max": 0.30, "esp_min": 2.12, "esp_max": 2.38},
    "CPVC-004": {"diam_min": 34.82, "diam_max": 34.98, "oval_max": 0.36, "esp_min": 3.18, "esp_max": 3.31},
    "CPVC-005": {"diam_min": 41.20, "diam_max": 41.40, "oval_max": 0.40, "esp_min": 3.76, "esp_max": 3.89},
    "CPVC-006": {"diam_min": 53.90, "diam_max": 54.10, "oval_max": 0.46, "esp_min": 4.90, "esp_max": 5.05},
}

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

st.title("Control de Calidad: CPVC")

# Manejo de estado para el botón de Limpiar Todo
if "limpiar_trigger" not in st.session_state:
    st.session_state.limpiar_trigger = False

def limpiar_campos():
    for key in ["d1", "d2", "d3", "d4", "e1", "e2", "e3", "e4"]:
        if key in st.session_state:
            st.session_state[key] = None

# Selector de clave
clave = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA.keys()))
reglas = REFERENCE_DATA[clave]

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### Diámetros (Norma: {reglas['diam_min']:.2f} - {reglas['diam_max']:.2f} mm)")
    st.caption(f"Límite de Ovalidad: {reglas['oval_max']:.2f} mm")
    d1 = st.number_input("D1", value=None, format="%.2f", step=0.01, key="d1")
    d2 = st.number_input("D2", value=None, format="%.2f", step=0.01, key="d2")
    d3 = st.number_input("D3", value=None, format="%.2f", step=0.01, key="d3")
    d4 = st.number_input("D4", value=None, format="%.2f", step=0.01, key="d4")

with col2:
    st.markdown(f"#### Espesores (Mín: {reglas['esp_min']:.2f} mm)")
    e1 = st.number_input("E1", value=None, format="%.2f", step=0.01, key="e1")
    e2 = st.number_input("E2", value=None, format="%.2f", step=0.01, key="e2")
    e3 = st.number_input("E3", value=None, format="%.2f", step=0.01, key="e3")
    e4 = st.number_input("E4", value=None, format="%.2f", step=0.01, key="e4")

st.divider()

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    evaluar_btn = st.button("🚀 EVALUAR MEDIDAS", type="primary", use_container_width=True)
with col_btn2:
    st.button("🧹 Limpiar Todo", on_click=limpiar_campos, use_container_width=True)


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
                    fallos.append(f"**Diámetro Promedio** ({prom_diam:.3f} mm) fuera de rango ({reglas['diam_min']} a {reglas['diam_max']})")
                if ovalidad > reglas["oval_max"]:
                    fallos.append(f"**Ovalidad** ({ovalidad:.3f} mm) excede límite ({reglas['oval_max']} mm)")
                    
        # Evaluar Espesores (independiente)
        if len(esps_filled) > 0:
            if len(esps_filled) < 4:
                fallos.append("⚠️ Faltan datos de Espesor para realizar la evaluación de espesores.")
            else:
                prom_esp = sum(esps_filled) / len(esps_filled)
                
                if not (reglas["esp_min"] <= prom_esp <= reglas["esp_max"]):
                    fallos.append(f"**Espesor Promedio** ({prom_esp:.2f} mm) fuera de rango ({reglas['esp_min']} a {reglas['esp_max']})")
                    
                for i, esp in enumerate(esps_filled):
                    if not (reglas["esp_min"] <= esp <= reglas["esp_max"]):
                        fallos.append(f"**Espesor {i+1} individual** ({esp:.2f} mm) crítico fuera de rango ({reglas['esp_min']} a {reglas['esp_max']})")
                        
        st.divider()
        st.write("### 📝 Datos Calculados")
        
        cols = st.columns(3)
        if prom_diam is not None:
            cols[0].metric("Diámetro Promedio", f"{prom_diam:.3f} mm")
            cols[1].metric("Ovalidad Calculada", f"{ovalidad:.3f} mm")
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
