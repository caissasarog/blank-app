        numero_reto = gr.Number(label="Numero de reto completado", minimum=1, maximum=6, step=1, interactive=False)
        boton_completar = gr.Button("Marcar reto completado", variant="primary", interactive=False, elem_classes=["challenge-complete"])

    with gr.Tab("Nutriólogos"):
        estado = gr.Textbox(label="Estado", interactive=False)
        ciudad = gr.Textbox(label="Ciudad", interactive=False)
        boton_buscar = gr.Button("Buscar nutriólogos", variant="primary", interactive=False)
        salida_nutri = gr.Markdown()

    componentes_bloqueados = [
        boton_registro_inicio_toggle,
        modo_foto_inicio, imagen_trasera_inicio, imagen_frontal_inicio, imagen_archivo_inicio,
        boton_registrar_inicio, boton_historial_inicio,
        plan_desayuno_btn, plan_comida_btn, plan_cena_btn,
        edad, peso, altura, genero, actividad, meta,
        condicion, alergias, gustos, no_gusta, rutina,
        glucosa, colesterol, trigliceridos, hemoglobina, observaciones,
        guardar_datos, boton_cargar, boton_resumen,
        boton_progreso,
        motivo_consulta, modalidad_consulta, boton_consulta,
        boton_nivel,
        entrada_nuti, boton_nuti,
        entrada_coach, boton_coach,
        nombre_rec, descripcion, imagen_receta, boton_subir, boton_ver,
        boton_ver_retos, numero_reto, boton_completar,
        estado, ciudad, boton_buscar,
    ]

    # EVENTOS
    boton_login.click(
        entrar_usuario,
        inputs=nombre_login,
        outputs=salida_login
    ).then(
        cargar_formulario_usuario,
        outputs=[
            edad, peso, altura, genero, actividad, meta,
            condicion, alergias, gustos, no_gusta, rutina,
            glucosa, colesterol, trigliceridos, hemoglobina, observaciones,
            salida_carga
        ]
    ).then(
        desbloquear_funciones,
        outputs=componentes_bloqueados
    ).then(
        hero_actualizado,
        outputs=hero_panel
    ).then(
        progreso_actualizado,
        outputs=progress_panel
    ).then(
        cargar_chats_usuario,
        outputs=[chat_nuti, chat_coach, chat_nuti_state, chat_coach_state]
    )

    boton_ver_usuario.click(ver_usuario_actual, outputs=salida_usuario)

    guardar_datos.click(
        guardar_informacion,
        inputs=[
            edad, peso, altura, genero, actividad, meta,
            condicion, alergias, gustos, no_gusta, rutina,
            glucosa, colesterol, trigliceridos, hemoglobina, observaciones
        ],
        outputs=salida_datos
    ).then(
        hero_actualizado,
        outputs=hero_panel
    ).then(
        progreso_actualizado,
        outputs=progress_panel
    )

    boton_cargar.click(
        cargar_formulario_usuario,
        outputs=[
            edad, peso, altura, genero, actividad, meta,
            condicion, alergias, gustos, no_gusta, rutina,
            glucosa, colesterol, trigliceridos, hemoglobina, observaciones,
            salida_carga
        ]
    )

    boton_resumen.click(ver_resumen, outputs=salida_resumen)
    boton_progreso.click(ver_progreso, outputs=salida_progreso)
    boton_registro_inicio_toggle.click(
        alternar_registro_inicio,
        inputs=registro_inicio_abierto,
        outputs=[dashboard_intro_panel, food_register_label, boton_registro_inicio_toggle, panel_registro_inicio, plan_inicio_panel, registro_inicio_abierto]
    )
    modo_foto_inicio.change(
        cambiar_modo_foto,
        inputs=modo_foto_inicio,
        outputs=[imagen_trasera_inicio, imagen_frontal_inicio, imagen_archivo_inicio]
    )
    boton_registrar_inicio.click(
        registrar_comida_desde_opciones,
        inputs=[imagen_trasera_inicio, imagen_frontal_inicio, imagen_archivo_inicio],
        outputs=salida_foto_inicio
    ).then(
        hero_actualizado,
        outputs=hero_panel
    ).then(
        progreso_actualizado,
        outputs=progress_panel
    )
    boton_historial_inicio.click(mostrar_historial, outputs=salida_historial_inicio)
    plan_desayuno_btn.click(
        lambda actual: alternar_plan_de_comida("Desayuno", actual),
        inputs=plan_rapido_actual,
        outputs=[salida_plan_rapido, plan_rapido_actual],
        queue=False,
        show_progress="hidden",
    )
    plan_comida_btn.click(
        lambda actual: alternar_plan_de_comida("Comida", actual),
        inputs=plan_rapido_actual,
        outputs=[salida_plan_rapido, plan_rapido_actual],
        queue=False,
        show_progress="hidden",
    )
    plan_cena_btn.click(
        lambda actual: alternar_plan_de_comida("Cena", actual),
        inputs=plan_rapido_actual,
        outputs=[salida_plan_rapido, plan_rapido_actual],
        queue=False,
        show_progress="hidden",
    )
    boton_consulta.click(
        solicitar_consulta,
        inputs=[motivo_consulta, modalidad_consulta],
        outputs=salida_consulta
    )
    boton_nivel.click(ver_nivel, outputs=salida_nivel)

    boton_nuti.click(
        conversar_nuti,
        inputs=[entrada_nuti, chat_nuti_state],
        outputs=[chat_nuti, entrada_nuti, chat_nuti_state]
    )

    boton_coach.click(
        conversar_coach,
        inputs=[entrada_coach, chat_coach_state],
        outputs=[chat_coach, entrada_coach, chat_coach_state]
    )

    boton_subir.click(
        subir_receta,
        inputs=[nombre_rec, descripcion, imagen_receta],
        outputs=salida_subir
    )

    boton_ver.click(mostrar_recetas, outputs=salida_recetas)

    boton_ver_retos.click(mostrar_retos, outputs=salida_retos)
    boton_completar.click(completar_reto, inputs=numero_reto, outputs=salida_retos)

    boton_buscar.click(
        buscar_nutriologos,
        inputs=[estado, ciudad],
        outputs=salida_nutri
    )

if __name__ == "__main__":
    reiniciar_sesion_visual()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        share=os.getenv("NUTRIBOT_SHARE", "").strip().lower() in {"1", "true", "yes", "si", "sí"},
        ssr_mode=False,
        favicon_path="assets/nutribot-logo.jpg",
        pwa=True,
    )

