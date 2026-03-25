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

# Datos de referencia para CPVC
REFERENCE_DATA_CPVC = {
    "CPVC-001": {"diam_min": 15.82, "diam_max": 15.98, "oval_max": 0.20, "esp_min": 1.40, "esp_max": 1.66},
    "CPVC-002": {"diam_min": 22.12, "diam_max": 22.28, "oval_max": 0.26, "esp_min": 1.65, "esp_max": 1.91},
    "CPVC-003": {"diam_min": 28.52, "diam_max": 28.68, "oval_max": 0.30, "esp_min": 2.12, "esp_max": 2.38},
    "CPVC-004": {"diam_min": 34.82, "diam_max": 34.98, "oval_max": 0.36, "esp_min": 3.18, "esp_max": 3.31},
    "CPVC-005": {"diam_min": 41.20, "diam_max": 41.40, "oval_max": 0.40, "esp_min": 3.76, "esp_max": 3.89},
    "CPVC-006": {"diam_min": 53.90, "diam_max": 54.10, "oval_max": 0.46, "esp_min": 4.90, "esp_max": 5.05},
}

# Datos fijos para Tubo de Estante
REGLAS_TUBO = {
    "diam_min": 40.70, 
    "diam_max": 41.10, 
    "oval_max": 0.50, 
    "esp_min": 1.60, 
    "esp_max": 2.00
}

# Datos de referencia para PVC Cédula 40
REFERENCE_DATA_PVC = {
    "Código 43038 (PVC-001)": {"diam_min": 21.20, "diam_max": 21.40, "oval_max": 0.40, "esp_min": 2.50, "esp_max": 2.80},
    "Código 43039 (PVC-002)": {"diam_min": 26.60, "diam_max": 26.80, "oval_max": 0.50, "esp_min": 2.60, "esp_max": 2.90},
    "Código 43040 (PVC-003)": {"diam_min": 33.30, "diam_max": 33.50, "oval_max": 0.50, "esp_min": 3.10, "esp_max": 3.40},
    "Código 45520 (PVC-004)": {"diam_min": 42.00, "diam_max": 42.30, "oval_max": 0.60, "esp_min": 3.30, "esp_max": 3.60},
    "Código 45521 (PVC-005)": {"diam_min": 48.10, "diam_max": 48.40, "oval_max": 0.60, "esp_min": 3.40, "esp_max": 3.70},
    "Código 45522 (PVC-006)": {"diam_min": 60.10, "diam_max": 60.50, "oval_max": 0.60, "esp_min": 3.60, "esp_max": 3.90},
}

# Datos de referencia para PVC RD
REFERENCE_DATA_PVC_RD = {
    "Código 40081 (PVC-101)": {"diam_min": 21.20, "diam_max": 21.40, "oval_max": 0.50, "esp_min": 0.80, "esp_max": 1.10},
    "Código 40082 (PVC-102)": {"diam_min": 26.60, "diam_max": 26.80, "oval_max": 0.50, "esp_min": 1.20, "esp_max": 1.50},
    "Código 40083 (PVC-103)": {"diam_min": 33.30, "diam_max": 33.50, "oval_max": 0.50, "esp_min": 1.20, "esp_max": 1.50},
    "Código 40084 (PVC-104)": {"diam_min": 42.10, "diam_max": 42.30, "oval_max": 0.50, "esp_min": 1.30, "esp_max": 1.60},
    "Código 40085 (PVC-105)": {"diam_min": 48.10, "diam_max": 48.50, "oval_max": 0.50, "esp_min": 1.60, "esp_max": 1.90},
    "Código 40086 (PVC-106)": {"diam_min": 60.10, "diam_max": 60.50, "oval_max": 0.50, "esp_min": 2.00, "esp_max": 2.30},
}

# Datos de referencia para PPR
REFERENCE_DATA_PPR = {
    "Código 49897 (CV-001)": {"diam_min": 20.00, "diam_max": 20.30, "oval_max": 1.20, "esp_min": 2.80, "esp_max": 3.10},
    "Código 49898 (CV-002)": {"diam_min": 25.00, "diam_max": 25.30, "oval_max": 1.20, "esp_min": 3.50, "esp_max": 3.80},
    "Código 49899 (CV-003)": {"diam_min": 32.00, "diam_max": 32.30, "oval_max": 1.30, "esp_min": 4.40, "esp_max": 4.70},
    "Código 45444 (CV-004)": {"diam_min": 40.00, "diam_max": 40.40, "oval_max": 1.40, "esp_min": 5.50, "esp_max": 5.90},
    "Código 45445 (CV-005)": {"diam_min": 50.00, "diam_max": 50.50, "oval_max": 1.40, "esp_min": 6.90, "esp_max": 7.40},
    "Código 45446 (CV-006)": {"diam_min": 63.00, "diam_max": 63.60, "oval_max": 1.60, "esp_min": 8.60, "esp_max": 9.10},
}

# Datos de referencia para Tubo de Céspol
REFERENCE_DATA_CESPOL = {
    'Céspol 1-1/4"': {"diam_min": 32.00, "diam_max": 32.40, "oval_max": 0.50, "esp_min": 1.20, "esp_max": 1.60},
    'Céspol 1-1/2"': {"diam_min": 37.20, "diam_max": 37.60, "oval_max": 0.50, "esp_min": 1.30, "esp_max": 1.70},
}

def limpiar_campos(tab_key):
    for key in ["d1", "d2", "d3", "d4", "e1", "e2", "e3", "e4"]:
        full_key = f"{key}_{tab_key}"
        if full_key in st.session_state:
            st.session_state[full_key] = None

def render_tab(reglas, tab_key, validar_espesor_individual=True):
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
            
            # Evaluar Diámetros
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
                        
            # Evaluar Espesores
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
tab_cpvc, tab_estante, tab_pvc, tab_pvc_rd, tab_ppr, tab_cespol = st.tabs(["CPVC", "Tubo de Estante", "PVC Cédula 40", "PVC RD", "PPR", "Tubo de Céspol"])

with tab_cpvc:
    clave = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_CPVC.keys()), key="sel_cpvc")
    st.divider()
    render_tab(REFERENCE_DATA_CPVC[clave], "cpvc")

with tab_estante:
    st.markdown("#### 📌 Especificaciones Fijas: Tubo de Estante")
    st.divider()
    render_tab(REGLAS_TUBO, "tubo")

with tab_pvc:
    clave_pvc = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_PVC.keys()), key="sel_pvc")
    st.divider()
    render_tab(REFERENCE_DATA_PVC[clave_pvc], "pvc")

with tab_pvc_rd:
    clave_pvc_rd = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_PVC_RD.keys()), key="sel_pvc_rd")
    st.divider()
    render_tab(REFERENCE_DATA_PVC_RD[clave_pvc_rd], "pvc_rd")

with tab_ppr:
    clave_ppr = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_PPR.keys()), key="sel_ppr")
    st.divider()
    # PPR no valida cada espesor individual
    render_tab(REFERENCE_DATA_PPR[clave_ppr], "ppr", validar_espesor_individual=False)

with tab_cespol:
    clave_cespol = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA_CESPOL.keys()), key="sel_cespol")
    st.divider()
    render_tab(REFERENCE_DATA_CESPOL[clave_cespol], "cespol")
