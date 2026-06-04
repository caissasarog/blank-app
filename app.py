import gradio as gr
import random
import base64
import os
import json
import html
import re
from datetime import datetime
from pathlib import Path

from huggingface_hub import InferenceClient

from chatbot_nuti import buscar_respuesta
from coach_emocional import coach_emocional_inteligente
from hf_config import obtener_hf_token
from retos_saludables import mostrar_retos, completar_reto
from usuarios import (
    iniciar_o_crear_usuario,
    obtener_usuario_actual,
    obtener_datos_usuario,
    actualizar_datos_usuario,
)

estado_app = {
    "usuario_actual": ""
}


APP_CSS = """
:root {
    --nutri-bg: #f7f7f9;
    --nutri-surface: #ffffff;
    --nutri-ink: #2d2b38;
    --nutri-muted: #6f6a7b;
    --nutri-border: #e7e3ef;
    --nutri-purple: #8070c7;
    --nutri-purple-soft: #f0edf9;
    --nutri-green: #7b9c85;
}

body,
.gradio-container {
    background: var(--nutri-bg) !important;
    color: var(--nutri-ink) !important;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

html,
body {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    overflow-x: hidden !important;
}

*::-webkit-scrollbar-button {
    width: 0 !important;
    height: 0 !important;
    display: none !important;
}

.gradio-container {
    width: 100% !important;
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding-left: 18px !important;
    padding-right: 18px !important;
    overflow-x: hidden !important;
}

#root,
.app,
.main,
.contain,
.wrap,
.block,
.form,
.panel {
    max-width: 100% !important;
    overflow-wrap: anywhere !important;
}

.nutribot-hero {
    position: relative;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 24px;
    align-items: center;
    width: 100%;
    max-width: 100%;
    padding: 34px 36px;
    margin: 14px 0 24px;
    background: linear-gradient(135deg, #ffffff 0%, #fbfaff 74%, #f1eef9 100%);
    border: 1px solid var(--nutri-border);
    border-radius: 8px;
    overflow: hidden;
}

.nutribot-hero::before,
.nutribot-hero::after {
