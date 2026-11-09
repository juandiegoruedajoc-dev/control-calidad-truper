                "tipo": "ENTREGA_TURNO",
                "clave": f"{turno} — {area}",
                "prom_diam": nombre_inspector,
                "ovalidad": estado_microm,
                "prom_esp": f"NC: {producto_nc} | Cant: {cantidad_nc} | Disp: {disposicion}",
                "aplastamiento": f"5S: {'OK' if cinco_s_ok else 'Pendiente'} | Tarimas: {tarimas_pend}",
                "resultado": "ENTREGA DE TURNO",
                "motivos": notas_finales if notas_finales else "Sin notas"
                "fecha":        datetime.now().strftime("%d/%m/%Y"),
                "hora":         datetime.now().strftime("%H:%M:%S"),
                "tipo":         "ENTREGA_TURNO",
                "clave":        f"{turno} — {area}",
                "prom_diam":    nombre,
                "ovalidad":     estado_instrumentos,
                "prom_esp":     f"Condicionados: {condicionados} | Desviaciones: {desviaciones or 'N/A'}",
                "aplastamiento":f"Masters: {masters}{' — ' + masters_obs if masters_obs else ''} | Tarimas: {tarimas}",
                "resultado":    "ENTREGA DE TURNO",
                "motivos":      observaciones,
            }
            threading.Thread(target=enviar_a_google_sheets, args=(datos_turno,)).start()
            st.success(f"✅ Reporte enviado correctamente. ¡Buen descanso, {nombre_inspector.split()[0]}!")
            if foto_evidencia:
                st.image(foto_evidencia, caption="Evidencia fotográfica adjunta", use_container_width=True)
            st.success(f"✅ Cuestionario enviado correctamente. ¡Buen descanso, **{nombre}**!")
            # Muestra miniaturas de fotos capturadas
            fotos_tomadas = [(foto_instrumentos, "Instrumentos"), (foto_5s, "5'S"), (foto_cuarentena, "Cuarentena")]
            fotos_validas = [(f, lbl) for f, lbl in fotos_tomadas if f is not None]
            if fotos_validas:
                st.markdown("**Evidencias fotográficas registradas:**")
                cols_fotos = st.columns(len(fotos_validas))
                for col_f, (foto, lbl) in zip(cols_fotos, fotos_validas):
                    col_f.image(foto, caption=lbl, use_container_width=True)
# ── Botón flotante visible en toda la app ─────────────────────
st.markdown("""
    <style>
    /* Ancla el contenedor del botón flotante a la esquina inferior derecha */
    [data-testid="stBottom"] {
        position: fixed !important;
        bottom: 20px !important;
""", unsafe_allow_html=True)
with st.container():
    # st.bottom fija el contenedor al pie de la página (Streamlit >= 1.40)
    with st.bottom():
        if st.button("📋 Entrega de Turno", key="fab_turno", use_container_width=False):
        if st.button("📝 Entrega de Turno", key="fab_turno", use_container_width=False):
            dialogo_entrega_turno()
