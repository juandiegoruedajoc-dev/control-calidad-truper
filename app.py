import streamlit as st
import pandas as pd

# Configuración de la página (para que se vea bien en móviles)
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

# CSS para inyectar algunos estilos, como centrar los cuadros de resultado
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

# Selector de clave
clave = st.selectbox("📌 Seleccione Clave:", list(REFERENCE_DATA.keys()))

# Mostrar tabla de límites
reglas = REFERENCE_DATA[clave]
st.write("### 📊 Límites de Referencia")

# Crear el DataFrame para mostrar la tablita requerida
limites_df = pd.DataFrame({
    "Característica": ["Diámetro (mm)", "Ovalidad Máx (mm)", "Espesor (mm)"],
    "Mínimo": [f"{reglas['diam_min']:.2f}", "-", f"{reglas['esp_min']:.2f}"],
    "Máximo": [f"{reglas['diam_max']:.2f}", f"{reglas['oval_max']:.2f}", f"{reglas['esp_max']:.2f}"]
})
# Renderizar la tabla sin índice
st.dataframe(limites_df, hide_index=True, use_container_width=True)

st.divider()
st.write("### 📏 Ingrese las Mediciones")

# Campos de entrada en columnas para organizar espacio
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Diámetros (mm)")
    d1 = st.number_input("D1", value=0.00, format="%.2f", step=0.01)
    d2 = st.number_input("D2", value=0.00, format="%.2f", step=0.01)
    d3 = st.number_input("D3", value=0.00, format="%.2f", step=0.01)
    d4 = st.number_input("D4", value=0.00, format="%.2f", step=0.01)

with col2:
    st.markdown("#### Espesores (mm)")
    e1 = st.number_input("E1", value=0.00, format="%.2f", step=0.01)
    e2 = st.number_input("E2", value=0.00, format="%.2f", step=0.01)
    e3 = st.number_input("E3", value=0.00, format="%.2f", step=0.01)
    e4 = st.number_input("E4", value=0.00, format="%.2f", step=0.01)

st.divider()

# Botón grande (use_container_width=True ayuda mucho a pantallas móviles)
if st.button("🚀 EVALUAR MEDIDAS", type="primary", use_container_width=True):
    diams = [d1, d2, d3, d4]
    esps = [e1, e2, e3, e4]
    
    # Validar que los campos no se hayan dejado en 0.0 cuando se esperan mediciones de CPVC
    # Como en estos límites un tubo real no usaría 0.0, prevenimos evaluaciones vacías.
    if all(d == 0.0 for d in diams) or all(e == 0.0 for e in esps):
        st.warning("⚠️ Por favor ingresa los valores reales de medición. Parecen estar en 0.0")
    else:
        fallos = []
        
        # Cálculos de Diámetro
        prom_diam = sum(diams) / len(diams)
        min_diam = min(diams)
        max_diam = max(diams)
        
        # Nueva lógica de ovalidad: mayor diferencia contra el promedio
        ovalidad = max(abs(max_diam - prom_diam), abs(min_diam - prom_diam))
        
        if not (reglas["diam_min"] <= prom_diam <= reglas["diam_max"]):
            fallos.append(f"**Promedio de Diámetro** ({prom_diam:.3f} mm) fuera de rango ({reglas['diam_min']} a {reglas['diam_max']})")
            
        if ovalidad > reglas["oval_max"]:
            fallos.append(f"**Ovalidad** ({ovalidad:.3f} mm) excede el límite permitido ({reglas['oval_max']} mm)")
            
        # Cálculos de Espesor
        for i, esp in enumerate(esps):
            if not (reglas["esp_min"] <= esp <= reglas["esp_max"]):
                fallos.append(f"**Espesor {i+1}** ({esp:.2f} mm) fuera de rango ({reglas['esp_min']} a {reglas['esp_max']})")
                
        st.divider()
        st.write("### 📝 Datos Calculados")
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Diámetro Promedio", f"{prom_diam:.3f} mm")
        col_res2.metric("Ovalidad Calculada", f"{ovalidad:.3f} mm")
        col_res3.metric("Espesor Mínimo", f"{min(esps):.2f} mm")

        # Mostrar los cuadros GRANDE en base al resultado
        if fallos:
            st.error("<div class='big-title'>RECHAZADO</div>", icon="🚫")
            st.error("#### Motivos de Falla:")
            for fallo in fallos:
                st.markdown(f"- ❌ {fallo}")
        else:
            st.success("<div class='big-title'>PASADO</div>", icon="✅")
            st.success("✨ ¡Excelente! Todas las mediciones cumplen estrictamente con los límites de la tabla de tolerancias.")
