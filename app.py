import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(page_title='Control de Calidad Truper', layout='wide', initial_sidebar_state='collapsed')

if "scroll_to_top" in st.session_state and st.session_state.scroll_to_top:
    components.html(
        """
        <script>
            window.parent.scrollTo(0,0);
            window.parent.document.querySelector('.main').scrollTo(0,0);
        </script>
        """, height=0
    )
    st.session_state.scroll_to_top = False

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stMarkdown, p, h1, h2, h3, label { color: #000000 !important; }
    div[data-testid='stMetricValue'] { color: #F0711B !important; }
    button[kind="primary"] { background-color: #F0711B !important; border-color: #F0711B !important; color: white !important; }
    div[data-testid="stAlert"] {
        padding: 20px;
    }
    .big-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0px !important;
    }
    /* Estilos nuevos para inputs y modo Rafia */
    div[data-baseweb="input"] > div {
        min-height: 60px !important;
        font-size: 1.2rem !important;
    }
    input[type="number"] {
        font-size: 1.2rem !important;
        height: 100% !important;
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
    /* Estilos para Toggles activos */
    div[data-testid="stToggle"] > label > div[data-checked="true"] > div {
        background-color: #F0711B !important;
    }
    div[data-testid="stToggle"] label[data-checked="true"] div[data-baseweb="checkbox"] > div {
        background-color: #F0711B !important;
    }
    /* El selector oficial suele ser la div que funciona como track */
    /* Fix Fila Protegida Obligatorio */
    div[data-testid='column'] { 
        width: unset !important; 
        flex: 1 1 auto !important; 
        min-width: 0px !important; 
    }
    div[data-testid='stHorizontalBlock'] { 
        flex-wrap: nowrap !important; 
        align-items: center !important; 
    }
    .stNumberInput {
        max-width: 100px !important;
    }
    .stNumberInput input { 
        font-size: 20px !important; 
        padding: 5px !important; 
    }
    </style>
""", unsafe_allow_html=True)

col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
with col_img2:
    st.image("https://raw.githubusercontent.com/juandiegoruedajoc-dev/control-calidad-truper/main/logotipo%20de%20truper.png", width=180)

st.title("Sistema de Control de Calidad - Laboratorio de Extrusión")
st.subheader("Uso exclusivo para Laboratorio de Extrusión - Grupo Truper")

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
        chk_key = f"chk_entero_{key}_{tab_key}"
        if chk_key in st.session_state:
            st.session_state[chk_key] = False
        
    st.session_state.scroll_to_top = True

def limpiar_rafia():
    if "peso_rafia" in st.session_state:
        st.session_state["peso_rafia"] = None
    st.session_state.scroll_to_top = True

def render_tab(reglas, tab_key, validar_espesor_individual=True):
    base_diam = int(reglas['diam_min'])
    base_esp = int(reglas['esp_min'])
    
    col1, col2 = st.columns(2)

    def create_input(label, key_suffix, base):
        toggle_key = f"chk_entero_{key_suffix}_{tab_key}"
        modo_manual = st.session_state.get(toggle_key, False)
        
        valor_final_retorno = None
        
        if not modo_manual:
            # 3 Columnas: [ D1 + 15. ] | [ Input ] | [ Switch ]
            ci_1, ci_2, ci_3 = st.columns([1.5, 1.2, 0.8], vertical_alignment="center")
            
            with ci_1:
                st.markdown(f"<span style='font-weight: bold; font-size: 1.1rem; min-width: 30px; display: inline-block;'>{label}</span><span style='font-size: 1.4rem; font-weight: 900; color: #000; margin-left:10px;'>{base}.</span>", unsafe_allow_html=True)
            with ci_2:
                val = st.number_input(label, value=None, format="%d", step=1, label_visibility="collapsed", key=f"int_{key_suffix}_{tab_key}")
            with ci_3:
                st.toggle("Man", key=toggle_key)
                
            if val is not None:
                valor_final_retorno = base + (val / 100)
                
        else:
            # Vista Manual Abierta
            ci_1, ci_2, ci_3 = st.columns([1.5, 2, 0.8], vertical_alignment="center")
            
            with ci_1:
                st.markdown(f"<span style='font-size: 1.1rem; font-weight: bold; color: #F0711B;'>{label}</span>", unsafe_allow_html=True)
            with ci_2:
                val = st.number_input(label, value=None, format="%.2f", step=0.01, label_visibility="collapsed", key=f"man_{key_suffix}_{tab_key}")
            with ci_3:
                st.toggle("Man", key=toggle_key)
                
            if val is not None:
                valor_final_retorno = val
                
        return valor_final_retorno

    with col1:
        st.markdown(f"#### Diámetros (Norma: {reglas['diam_min']:.2f} - {reglas['diam_max']:.2f} mm)")
            
        d1 = create_input("D1", "d1", base_diam)
        d2 = create_input("D2", "d2", base_diam)
        d3 = create_input("D3", "d3", base_diam)
        d4 = create_input("D4", "d4", base_diam)
        st.caption(f"Límite de Ovalidad: {reglas['oval_max']:.2f} mm")

    with col2:
        st.markdown(f"#### Espesores (Norma: {reglas['esp_min']:.2f} - {reglas['esp_max']:.2f} mm)")
            
        e1 = create_input("E1", "e1", base_esp)
        e2 = create_input("E2", "e2", base_esp)
        e3 = create_input("E3", "e3", base_esp)
        e4 = create_input("E4", "e4", base_esp)

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
tab_cpvc, tab_estante, tab_pvc, tab_pvc_rd, tab_ppr, tab_cespol, tab_rafia = st.tabs(["CPVC", "Tubo de Estante", "PVC Cédula 40", "PVC RD", "PPR", "Tubo de Céspol", "Rafia"])

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

with tab_rafia:
    st.markdown("#### 📌 Especificaciones de Rafia")
    st.divider()
    
    col_raf_in, col_space = st.columns([1, 1])
    with col_raf_in:
        peso_rafia = st.number_input("Ingresar Peso (g)", value=None, format="%.2f", step=0.1, key="peso_rafia")
    
    col_btns1, col_btns2 = st.columns([3, 1])
    with col_btns2:
        st.button("🧹 Limpiar Todo", on_click=limpiar_rafia, use_container_width=True, key="btn_clean_rafia")
    
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
