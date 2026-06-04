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
    content: "";
    position: absolute;
    width: 0;
    height: 0;
    border-style: solid;
    opacity: .9;
}

.nutribot-hero::before {
    top: 0;
    right: 0;
    border-width: 0 34px 34px 0;
    border-color: transparent var(--nutri-purple) transparent transparent;
}

.nutribot-hero::after {
    left: 0;
    bottom: 0;
    border-width: 34px 0 0 34px;
    border-color: transparent transparent transparent var(--nutri-purple);
}

.nutribot-logo {
    width: 98px;
    height: 98px;
    object-fit: contain;
    border-radius: 50%;
    background: #fff;
    border: 1px solid var(--nutri-border);
    padding: 16px;
    box-shadow: 0 14px 40px rgba(91, 80, 126, .10);
}

.nutribot-kicker {
    margin: 0 0 4px;
    color: var(--nutri-purple);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: uppercase;
}

.nutribot-hero h1 {
    margin: 0;
    color: var(--nutri-ink);
    font-size: 58px;
    line-height: 1;
    letter-spacing: 0;
    font-weight: 800;
}

.nutribot-hero h1 span {
    color: var(--nutri-purple);
}

.nutribot-subtitle {
    max-width: 680px;
    margin: 12px 0 0;
    color: var(--nutri-muted);
    font-size: 16px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

.nutribot-note {
    margin: -8px 0 22px;
    padding: 12px 16px;
    border-left: 4px solid var(--nutri-purple);
    background: var(--nutri-purple-soft);
    color: #4f4965;
    border-radius: 6px;
    font-size: 14px;
}

.tab-nav,
.tabs,
[role="tablist"],
.tab-container {
    border-bottom-color: var(--nutri-border) !important;
}

.tab-nav,
[role="tablist"],
.tab-container {
    max-width: 100% !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    scrollbar-width: thin;
    display: flex !important;
    flex-wrap: nowrap !important;
}

.tab-nav button,
[role="tab"],
.tab-container button {
    flex: 0 0 auto !important;
    white-space: nowrap !important;
}

.gradio-container *,
.block,
.form,
.panel,
.wrap {
    box-sizing: border-box !important;
    min-width: 0 !important;
}

button,
.gr-button {
    border-radius: 6px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}

.gr-button-primary,
button.primary {
    background: var(--nutri-purple) !important;
    border-color: var(--nutri-purple) !important;
    color: #fff !important;
}

button:hover,
.gr-button:hover {
    border-color: var(--nutri-purple) !important;
}

input,
textarea,
select,
.wrap,
.block,
.form,
.panel {
    border-radius: 8px !important;
}

.block {
    border-color: var(--nutri-border) !important;
}

label,
.label-wrap span {
    color: var(--nutri-ink) !important;
    font-weight: 650 !important;
}

.markdown h2,
.markdown h3 {
    color: var(--nutri-purple) !important;
    letter-spacing: 0;
}

footer {
    opacity: .55;
}

.nutribot-splash {
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: grid;
    place-items: center;
    background: #fbfaff;
    animation: splash-hide 6.2s ease forwards;
}

.nutribot-splash-inner {
    display: grid;
    place-items: center;
    gap: 18px;
    animation: splash-logo 5.8s ease forwards;
}

.nutribot-splash img {
    width: min(76vw, 560px);
    height: auto;
}

@keyframes splash-logo {
    0% {
        opacity: 0;
        transform: scale(.96);
    }
    18%, 76% {
        opacity: 1;
        transform: scale(1);
    }
    100% {
        opacity: 0;
        transform: scale(1.03);
    }
}

@keyframes splash-hide {
    0%, 82% {
        opacity: 1;
        visibility: visible;
    }
    100% {
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
    }
}

@media (max-width: 900px) {
    .gradio-container {
        width: 100vw !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding-left: 14px !important;
        padding-right: 14px !important;
    }

    .nutribot-hero {
        grid-template-columns: auto 1fr;
        gap: 16px;
        padding: 24px 20px;
        margin-top: 10px;
    }

    .nutribot-logo {
        width: 82px;
        height: 82px;
        padding: 13px;
    }

    .nutribot-hero h1 {
        font-size: 44px;
    }

    .nutribot-subtitle {
        font-size: 15px;
        line-height: 1.5;
    }

    .nutribot-splash img {
        width: min(88vw, 440px);
    }
}

@media (max-width: 640px) {
    body {
        min-width: 0 !important;
    }

    .gradio-container {
        width: 100vw !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }

    .nutribot-hero {
        width: 100% !important;
        max-width: 100% !important;
        grid-template-columns: 1fr;
        gap: 14px;
        padding: 22px 18px;
        margin-bottom: 16px;
    }

    .nutribot-logo {
        width: 74px;
        height: 74px;
        padding: 12px;
    }

    .nutribot-hero h1 {
        font-size: 40px;
    }

    .nutribot-kicker {
        font-size: 12px;
    }

    .nutribot-subtitle {
        font-size: 14px;
    }

    .nutribot-note {
        margin: -4px 0 16px;
        padding: 11px 13px;
        font-size: 13px;
    }

    .tab-nav button {
        padding-left: 12px !important;
        padding-right: 12px !important;
        font-size: 14px !important;
    }

    [role="tablist"],
    .tab-container {
        width: 100% !important;
        max-width: 100% !important;
        height: 42px !important;
        min-height: 42px !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0 !important;
        overflow: hidden !important;
    }

    [role="tab"],
    .tab-container button {
        width: auto !important;
        min-height: 34px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
        font-size: 14px !important;
        border-radius: 0 !important;
        background: transparent !important;
    }

    button,
    .gr-button {
        width: 100% !important;
        min-height: 42px !important;
    }

    input,
    textarea,
    select {
        font-size: 16px !important;
    }
}

@media (max-width: 420px) {
    .gradio-container {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }

    .nutribot-hero {
        padding: 18px 14px;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    .nutribot-hero h1 {
        font-size: 34px;
    }

    .nutribot-logo {
        width: 66px;
        height: 66px;
        padding: 10px;
    }

    .markdown h2 {
        font-size: 24px !important;
    }

    .markdown h3 {
        font-size: 19px !important;
    }
}

/* Diseño experimental tipo app móvil */
:root {
    --app-lavender: #f4eefe;
    --app-lavender-2: #eadff9;
    --app-purple: #7d63c7;
    --app-purple-dark: #51408f;
    --app-ink: #171421;
    --app-muted: #6d6679;
    --app-card: rgba(255, 255, 255, .86);
}

body,
.gradio-container {
    background:
        radial-gradient(circle at 50% 0%, rgba(135, 103, 205, .16), transparent 34%),
        linear-gradient(180deg, #fbf8ff 0%, #f7f3fb 46%, #fff 100%) !important;
    color: var(--app-ink) !important;
}

.gradio-container {
    max-width: 980px !important;
}

.nutribot-hero {
    min-height: 410px;
    grid-template-columns: 1.1fr .9fr;
    gap: 22px;
    padding: 42px;
    border: 0;
    border-radius: 32px;
    background:
        radial-gradient(circle at 76% 22%, rgba(125, 99, 199, .22), transparent 32%),
        linear-gradient(145deg, #f7eefe 0%, #fff 58%, #fbf9ff 100%);
    box-shadow: 0 28px 70px rgba(64, 48, 105, .15);
}

.nutribot-hero::before,
.nutribot-hero::after {
    display: none;
}

.nutribot-app-copy {
    position: relative;
    z-index: 2;
}

.nutribot-app-mark {
    display: inline-flex;
    width: auto;
    height: 52px;
    align-items: center;
    justify-content: center;
    padding: 8px 18px;
    margin-bottom: 24px;
    border-radius: 22px;
    background: rgba(255, 255, 255, .72);
    color: var(--app-purple);
    font-size: 20px;
    font-weight: 800;
    box-shadow: 0 10px 28px rgba(87, 67, 145, .12);
}

.nutribot-app-mark img {
    width: 38px;
    height: 38px;
    object-fit: contain;
    display: block;
}

.nutribot-hero h1 {
    font-size: 58px;
    line-height: 1;
    margin: 0;
}

.nutribot-hero h1 span {
    color: var(--app-purple);
}

.nutribot-subtitle {
    max-width: 360px;
    font-size: 23px;
    line-height: 1.35;
    color: var(--app-ink);
}

.nutribot-tagline {
    margin: 14px 0 0;
    color: var(--app-purple-dark);
    font-size: 18px;
    font-weight: 750;
}

.nutribot-robot-wrap {
    position: relative;
    min-height: 250px;
    display: grid;
    place-items: center;
}

.nutribot-robot-img {
    width: min(380px, 82vw);
    max-height: 430px;
    object-fit: contain;
    filter: drop-shadow(0 30px 45px rgba(70, 52, 118, .22));
}

.hero-plans-popover {
    position: absolute;
    z-index: 8;
    left: 4px;
    top: 76px;
    width: min(270px, 72vw);
}

.hero-plans-popover summary {
    width: max-content;
    min-width: 106px;
    height: 44px;
    padding: 0 22px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,.78);
    background:
        linear-gradient(110deg, transparent 0%, rgba(255,255,255,.72) 42%, transparent 58%) -140px 0 / 120px 100% no-repeat,
        linear-gradient(135deg, #ffffff, #f1e9ff 48%, #d9caff);
    color: var(--app-purple-dark);
    font-weight: 900;
    line-height: 1;
    box-sizing: border-box;
    cursor: pointer;
    list-style: none;
    box-shadow: 0 18px 38px rgba(87, 67, 145, .20), inset 0 0 0 1px rgba(255,255,255,.75);
    animation: plan-shine 3.2s ease-in-out infinite;
}

.hero-plans-popover summary::-webkit-details-marker {
    display: none;
}

.hero-plans-popover[open] summary {
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 1003;
    width: 96px;
    min-width: 0;
    height: 42px;
    padding: 0;
    border-radius: 999px;
    border: 1px solid rgba(126, 99, 199, .16);
    background: rgba(255, 255, 255, .92);
    box-shadow: 0 12px 28px rgba(65, 48, 105, .14);
    animation: none;
}

.hero-plans-popover[open] summary {
    color: transparent;
    font-size: 0;
}

.hero-plans-popover[open] summary::before {
    content: "Cerrar";
    color: var(--app-purple-dark);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    line-height: 1;
    font-size: 14px;
    font-weight: 900;
}

.hero-plans-popover[open]::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 1000;
    background: rgba(31, 24, 51, .28);
    backdrop-filter: blur(12px);
    animation: plans-backdrop-in .28s ease both;
}

.hero-plans-card {
    margin-top: 12px;
    padding: 16px;
    border-radius: 22px;
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(126, 99, 199, .14);
    box-shadow: 0 18px 44px rgba(87, 67, 145, .16);
    backdrop-filter: blur(16px);
}

.hero-plans-popover[open] .hero-plans-card {
    position: fixed;
    inset: 22px;
    z-index: 1002;
    width: min(1100px, calc(100vw - 44px));
    max-height: calc(100vh - 44px);
    margin: auto;
    padding: 0;
    overflow: auto;
    border-radius: 30px;
    background: transparent;
    border: 0;
    box-shadow: 0 32px 90px rgba(32, 24, 54, .24);
    animation: plans-modal-in .46s cubic-bezier(.18, .9, .22, 1) both;
}

@keyframes plans-backdrop-in {
    from {
        opacity: 0;
        backdrop-filter: blur(0);
    }
    to {
        opacity: 1;
        backdrop-filter: blur(12px);
    }
}

@keyframes plans-modal-in {
    from {
        opacity: 0;
        transform: translateY(26px) scale(.965);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.hero-plans-card h3 {
    margin: 0 0 10px;
    color: var(--app-ink);
    font-size: 18px;
}

.hero-plan-row {
    padding: 11px 0;
    border-top: 1px solid rgba(126, 99, 199, .10);
}

.hero-plan-row strong {
    display: block;
    color: var(--app-ink);
    font-size: 15px;
}

.hero-plan-row span {
    display: block;
    margin-top: 3px;
    color: var(--app-purple-dark);
    font-weight: 850;
}

.hero-plan-note {
    margin: 10px 0 0;
    color: var(--app-muted);
    font-size: 12px;
    line-height: 1.35;
}

@keyframes plan-shine {
    0%, 45% { background-position: -150px 0, 0 0; }
    75%, 100% { background-position: 150px 0, 0 0; }
}

.plans-screen {
    border-radius: 28px;
    overflow: hidden;
    background: linear-gradient(180deg, #ffffff, #fbf9ff);
    border: 1px solid rgba(126, 99, 199, .12);
    box-shadow: 0 20px 54px rgba(87, 67, 145, .10);
    animation: plans-content-in .42s cubic-bezier(.18, .9, .22, 1) both;
}

@keyframes plans-content-in {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.plans-hero {
    padding: 28px;
    background:
        radial-gradient(circle at 88% 10%, rgba(125, 99, 199, .18), transparent 32%),
        linear-gradient(135deg, #f7f1ff, #ffffff 64%);
}

.plans-eyebrow {
    display: inline-flex;
    align-items: center;
    height: 34px;
    padding: 0 14px;
    border-radius: 999px;
    background: #ffffff;
    color: var(--app-purple);
    font-weight: 850;
    box-shadow: 0 10px 24px rgba(87, 67, 145, .10);
}

.plans-hero h2 {
    margin: 18px 0 8px;
    color: var(--app-ink);
    font-size: clamp(30px, 5vw, 46px);
    line-height: 1;
}

.plans-hero p {
    max-width: 620px;
    margin: 0;
    color: var(--app-muted);
    font-size: 17px;
    line-height: 1.55;
}

.plans-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    padding: 22px;
}

.plan-card {
    position: relative;
    display: flex;
    flex-direction: column;
    min-height: 315px;
    padding: 22px;
    border-radius: 24px;
    background: #ffffff;
    border: 1px solid rgba(126, 99, 199, .12);
    box-shadow: 0 16px 34px rgba(87, 67, 145, .08);
}

.plan-card.featured {
    background: linear-gradient(180deg, #fbf7ff, #ffffff);
    border-color: rgba(126, 99, 199, .26);
    box-shadow: 0 22px 48px rgba(87, 67, 145, .15);
}

.plan-badge {
    align-self: flex-start;
    padding: 7px 11px;
    border-radius: 999px;
    background: var(--app-lavender);
    color: var(--app-purple-dark);
    font-size: 12px;
    font-weight: 900;
}

.plan-card h3 {
    margin: 16px 0 8px;
    color: var(--app-ink);
    font-size: 22px;
}

.plan-price {
    color: var(--app-purple-dark);
    font-size: 28px;
    font-weight: 950;
}

.plan-price small {
    color: var(--app-muted);
    font-size: 13px;
    font-weight: 750;
}

.plan-card p {
    color: var(--app-muted);
    line-height: 1.45;
}

.plan-card ul {
    margin: 10px 0 0;
    padding-left: 18px;
    color: var(--app-ink);
    line-height: 1.65;
}

.plans-note-card {
    margin: 0 22px 24px;
    padding: 18px 20px;
    border-radius: 20px;
    background: #ffffff;
    border: 1px solid rgba(126, 99, 199, .10);
    color: var(--app-muted);
    line-height: 1.5;
}

.nutribot-robot {
    position: relative;
    width: min(245px, 66vw);
    height: 310px;
    border-radius: 110px 110px 92px 92px;
    background:
        radial-gradient(circle at 50% 66%, rgba(255,255,255,.95) 0 31%, transparent 32%),
        linear-gradient(180deg, #fff 0%, #eee7fb 58%, #d9cff4 100%);
    box-shadow: inset 0 -22px 36px rgba(118, 93, 193, .18), 0 30px 60px rgba(70, 52, 118, .22);
}

.nutribot-robot::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 25%;
    transform: translateX(-50%);
    width: 72%;
    height: 31%;
    border-radius: 42px;
    background: linear-gradient(180deg, #161337 0%, #080824 100%);
    box-shadow: inset 0 0 0 2px rgba(255, 255, 255, .1);
}

.nutribot-robot::after {
    content: "";
    position: absolute;
    left: 50%;
    top: -22px;
    width: 72px;
    height: 58px;
    transform: translateX(-50%);
    background: var(--robot-leaf);
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}

.nutribot-robot .ear {
    position: absolute;
    top: 33%;
    width: 34px;
    height: 70px;
    border-radius: 30px;
    background: linear-gradient(180deg, #d9cdf6, #9c84db);
    box-shadow: inset 0 0 0 4px rgba(255,255,255,.38);
}

.nutribot-robot .ear.left {
    left: -18px;
}

.nutribot-robot .ear.right {
    right: -18px;
}

.nutribot-robot .neck {
    position: absolute;
    left: 50%;
    bottom: 38px;
    transform: translateX(-50%);
    width: 66px;
    height: 38px;
    border-radius: 20px 20px 10px 10px;
    background: #d9cff4;
    box-shadow: inset 0 10px 14px rgba(99, 78, 164, .16);
}

.nutribot-robot .body {
    position: absolute;
    left: 50%;
    bottom: -10px;
    transform: translateX(-50%);
    width: 138px;
    height: 74px;
    border-radius: 46px 46px 24px 24px;
    background: linear-gradient(180deg, #fff, #e9e1fa);
    box-shadow: 0 18px 28px rgba(75, 57, 121, .12);
}

.nutribot-robot .button-dot {
    position: absolute;
    left: 50%;
    bottom: 28px;
    width: 8px;
    height: 8px;
    transform: translateX(-50%);
    border-radius: 50%;
    background: #c9b9ef;
}

.robot-eye {
    position: absolute;
    top: 36%;
    width: 19px;
    height: 42px;
    border-radius: 18px;
    background: #75e7ff;
    box-shadow: 0 0 18px rgba(117, 231, 255, .55);
    z-index: 3;
}

.robot-eye.left {
    left: 31%;
}

.robot-eye.right {
    right: 31%;
}

.robot-mouth {
    position: absolute;
    left: 50%;
    top: 51%;
    transform: translateX(-50%);
    width: 34px;
    height: 5px;
    border-radius: 999px;
    background: #d7c5ff;
    z-index: 3;
}

.phone-dashboard {
    margin-top: -92px;
    width: calc(100% - 24px);
    margin-left: auto;
    margin-right: auto;
    position: relative;
    z-index: 3;
    padding: 30px;
    background: var(--app-card);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(125, 99, 199, .10);
    border-radius: 30px;
    box-shadow: 0 26px 70px rgba(57, 43, 92, .14);
}

.phone-dashboard,
.phone-dashboard > *,
.phone-dashboard .form,
.phone-dashboard .block,
.phone-dashboard .wrap {
    box-sizing: border-box !important;
}

.phone-dashboard > .block,
.phone-dashboard .form,
.phone-dashboard .wrap,
.phone-dashboard .panel {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.phone-dashboard .gradio-row,
.phone-dashboard .feature-grid {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

.dash-title {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: start;
    margin-bottom: 20px;
    padding-right: 70px;
}

.dash-title h2 {
    margin: 0;
    font-size: 28px;
    color: var(--app-ink);
}

.dash-title p {
    margin: 6px 0 0;
    color: var(--app-muted);
    font-size: 16px;
}

.dash-arrow {
    display: none;
}

.food-register-toggle,
.food-register-toggle button {
    position: absolute !important;
    top: 30px;
    right: 30px;
    width: 46px !important;
    max-width: 46px !important;
    min-width: 46px !important;
    height: 46px !important;
    min-height: 46px !important;
    padding: 0 !important;
    border: 1px solid rgba(126, 99, 199, .20) !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,.78) !important;
    color: var(--app-purple) !important;
    box-shadow: 0 12px 28px rgba(87, 67, 145, .10) !important;
    font-size: 34px !important;
    font-weight: 850 !important;
    line-height: 1 !important;
    text-align: center !important;
    white-space: nowrap !important;
    z-index: 5;
}

.food-register-toggle::before {
    content: "";
    display: none;
}

.food-register-label {
    position: absolute;
    top: 30px;
    right: 88px;
    width: max-content;
    max-width: 190px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,.76);
    color: var(--app-purple-dark);
    border: 1px solid rgba(126, 99, 199, .12);
    box-shadow: 0 10px 26px rgba(87, 67, 145, .10);
    font-size: 13px;
    font-weight: 900;
    line-height: 1;
    pointer-events: none;
    z-index: 6;
}

@media (max-width: 760px) {
    .food-register-label {
        top: 26px;
        right: 82px;
        max-width: 170px;
        padding: 8px 11px;
        font-size: 12px;
    }
}

@media (max-width: 430px) {
    .food-register-label {
        top: 22px;
        right: 70px;
        max-width: 132px;
        padding: 7px 10px;
        font-size: 11px;
        line-height: 1.1;
        text-align: center;
    }
}

.food-register-toggle button::after {
    content: "";
}

.inline-food-panel {
    margin: -2px 0 24px;
    padding: 18px;
    border-radius: 30px;
    background: rgba(255,255,255,.92);
    border: 1px solid rgba(126, 99, 199, .10);
    box-shadow: 0 14px 38px rgba(87, 67, 145, .08);
    overflow: hidden;
    transform-origin: right center;
    animation: registro-panel-open .48s cubic-bezier(.18, .9, .22, 1) both;
}

.inline-food-guide {
    display: grid;
    grid-template-columns: 50px minmax(0, 1fr);
    gap: 14px;
    align-items: center;
    margin: 0 0 16px;
    padding: 0 2px 14px;
    border-bottom: 1px solid rgba(126, 99, 199, .10);
    background: transparent;
    color: var(--app-ink);
}

.inline-food-guide-icon {
    width: 50px;
    height: 50px;
    border-radius: 18px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #f4efff, #ffffff);
    color: var(--app-purple);
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 0;
    box-shadow: inset 0 0 0 1px rgba(126, 99, 199, .10);
}

.inline-food-guide h3 {
    margin: 0;
    font-size: 20px;
    color: var(--app-ink);
}

.inline-food-guide p {
    margin: 4px 0 0;
    color: var(--app-muted);
    font-size: 14px;
    line-height: 1.45;
}

@keyframes registro-panel-open {
    from {
        opacity: 0;
        transform: translateX(42px) scale(.98);
        max-height: 0;
        padding-top: 0;
        padding-bottom: 0;
    }
    to {
        opacity: 1;
        transform: translateX(0) scale(1);
        max-height: 980px;
        padding-top: 20px;
        padding-bottom: 20px;
    }
}

.inline-food-panel .block,
.inline-food-panel .form,
.inline-food-panel .wrap {
    background: transparent !important;
}

.inline-food-panel .gradio-radio {
    padding: 10px !important;
    border-radius: 20px !important;
    background: rgba(248, 246, 252, .72) !important;
    border: 1px solid rgba(126, 99, 199, .08) !important;
    box-shadow: none !important;
    margin-bottom: 14px !important;
}

.inline-food-panel .gradio-image {
    border-radius: 26px !important;
    overflow: hidden !important;
    background: #fff !important;
    border: 1px solid rgba(126, 99, 199, .10) !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.9), 0 14px 30px rgba(87, 67, 145, .07) !important;
    margin-bottom: 16px !important;
}

.inline-food-actions {
    display: grid !important;
    grid-template-columns: 1fr;
    gap: 10px !important;
    align-items: stretch !important;
}

.inline-food-primary button,
.inline-food-secondary button {
    min-height: 56px !important;
    border-radius: 20px !important;
    font-weight: 850 !important;
}

.inline-food-secondary button {
    background: #ffffff !important;
    color: var(--app-ink) !important;
    border: 1px solid rgba(126, 99, 199, .12) !important;
    box-shadow: 0 10px 24px rgba(87, 67, 145, .06) !important;
}

.inline-food-result,
.inline-food-history {
    margin-top: 12px;
    padding: 12px;
    border-radius: 22px;
    background: rgba(248, 246, 252, .58);
    border: 1px solid rgba(126, 99, 199, .08);
}

.meal-preview {
    height: 150px;
    border-radius: 20px;
    margin-bottom: 22px;
    background:
        radial-gradient(circle at 30% 40%, #f4b86f 0 12%, transparent 13%),
        radial-gradient(circle at 53% 36%, #76b36a 0 14%, transparent 15%),
        radial-gradient(circle at 63% 58%, #d86a42 0 20%, transparent 21%),
        radial-gradient(circle at 42% 62%, #f0d68a 0 16%, transparent 17%),
        linear-gradient(135deg, #fff3df, #f8faf0);
    box-shadow: inset 0 0 0 1px rgba(80, 62, 115, .08);
}

.feature-grid {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 24px;
    overflow: visible !important;
    scrollbar-width: none !important;
}

.feature-grid > * {
    min-width: 0 !important;
    overflow: visible !important;
}

.feature-grid::-webkit-scrollbar,
.feature-grid *::-webkit-scrollbar {
    width: 0 !important;
    height: 0 !important;
    display: none !important;
}

.feature-pill {
    display: grid;
    place-items: center;
    gap: 8px;
    min-height: 120px;
    border-radius: 24px;
    background: rgba(255,255,255,.72);
    box-shadow: 0 12px 32px rgba(87, 67, 145, .09);
    color: var(--app-ink);
    font-size: 17px;
    font-weight: 750;
    cursor: pointer;
}

button.feature-pill {
    width: 100%;
    border: 0;
    font-family: inherit;
}

button.feature-pill:hover {
    border-color: rgba(126, 99, 199, .28) !important;
    transform: translateY(-1px);
}

.meal-action-btn,
.meal-action-btn button {
    min-height: 112px !important;
    width: 100% !important;
    border-radius: 24px !important;
    background: rgba(255,255,255,.78) !important;
    border: 1px solid rgba(126, 99, 199, .12) !important;
    color: var(--app-ink) !important;
    box-shadow: 0 12px 32px rgba(87, 67, 145, .09) !important;
    font-size: 17px !important;
    font-weight: 780 !important;
    white-space: pre-line !important;
    line-height: 1.2 !important;
    padding: 12px 8px !important;
    display: grid !important;
    place-items: center !important;
    gap: 8px !important;
    cursor: pointer !important;
    touch-action: manipulation !important;
    user-select: none !important;
    overflow: visible !important;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease, background .16s ease !important;
}

.meal-action-btn:hover,
.meal-action-btn button:hover,
.meal-action-btn:focus-within,
.meal-action-btn button:focus-visible {
    transform: translateY(-2px) !important;
    background: #fff !important;
    border-color: rgba(126, 99, 199, .28) !important;
    box-shadow: 0 18px 42px rgba(87, 67, 145, .14) !important;
}

.meal-action-btn:active,
.meal-action-btn button:active {
    transform: translateY(0) scale(.99) !important;
}

#plan_desayuno_btn,
#plan_desayuno_btn button,
#plan_comida_btn,
#plan_comida_btn button,
#plan_cena_btn,
#plan_cena_btn button {
    font-size: 0 !important;
}

#plan_desayuno_btn::before,
#plan_desayuno_btn button::before,
#plan_comida_btn::before,
#plan_comida_btn button::before,
#plan_cena_btn::before,
#plan_cena_btn button::before {
    content: "";
    display: block;
    width: 54px;
    height: 54px;
    margin: 0 auto 8px;
    background: var(--app-purple);
}

#plan_desayuno_btn::before,
#plan_desayuno_btn button::before {
    -webkit-mask: url("data:image/svg+xml,%3Csvg%20viewBox%3D%270%200%2048%2048%27%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%3E%3Cg%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%273%27%20stroke-linecap%3D%27round%27%3E%3Ccircle%20cx%3D%2724%27%20cy%3D%2724%27%20r%3D%278%27/%3E%3Cpath%20d%3D%27M24%204v6M24%2038v6M4%2024h6M38%2024h6M9.9%209.9l4.2%204.2M33.9%2033.9l4.2%204.2M38.1%209.9l-4.2%204.2M14.1%2033.9l-4.2%204.2%27/%3E%3C/g%3E%3C/svg%3E") center / contain no-repeat;
    mask: url("data:image/svg+xml,%3Csvg%20viewBox%3D%270%200%2048%2048%27%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%3E%3Cg%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%273%27%20stroke-linecap%3D%27round%27%3E%3Ccircle%20cx%3D%2724%27%20cy%3D%2724%27%20r%3D%278%27/%3E%3Cpath%20d%3D%27M24%204v6M24%2038v6M4%2024h6M38%2024h6M9.9%209.9l4.2%204.2M33.9%2033.9l4.2%204.2M38.1%209.9l-4.2%204.2M14.1%2033.9l-4.2%204.2%27/%3E%3C/g%3E%3C/svg%3E") center / contain no-repeat;
}

#plan_comida_btn::before,
#plan_comida_btn button::before {
    -webkit-mask: url("data:image/svg+xml,%3Csvg%20viewBox%3D%270%200%2048%2048%27%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%3E%3Cg%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%273%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%3E%3Cpath%20d%3D%27M14%2028h20c0%206-4.5%2010-10%2010s-10-4-10-10Z%27/%3E%3Cpath%20d%3D%27M12%2028h24%27/%3E%3Cpath%20d%3D%27M18%2018c-2-3%202-4%200-7%27/%3E%3Cpath%20d%3D%27M25%2018c-2-3%202-4%200-7%27/%3E%3Cpath%20d%3D%27M32%2018c-2-3%202-4%200-7%27/%3E%3C/g%3E%3C/svg%3E") center / contain no-repeat;
    mask: url("data:image/svg+xml,%3Csvg%20viewBox%3D%270%200%2048%2048%27%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%3E%3Cg%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%273%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%3E%3Cpath%20d%3D%27M14%2028h20c0%206-4.5%2010-10%2010s-10-4-10-10Z%27/%3E%3Cpath%20d%3D%27M12%2028h24%27/%3E%3Cpath%20d%3D%27M18%2018c-2-3%202-4%200-7%27/%3E%3Cpath%20d%3D%27M25%2018c-2-3%202-4%200-7%27/%3E%3Cpath%20d%3D%27M32%2018c-2-3%202-4%200-7%27/%3E%3C/g%3E%3C/svg%3E") center / contain no-repeat;
}

#plan_cena_btn::before,
#plan_cena_btn button::before {
    -webkit-mask: url("data:image/svg+xml,%3Csvg%20viewBox%3D%270%200%2048%2048%27%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%3E%3Cpath%20d%3D%27M34%2037c-10%202-21-5-23-16C9%2012%2015%206%2023%205c-4%205-3%2013%202%2018%205%205%2013%206%2019%202-1%206-5%2010-10%2012Z%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%273%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27/%3E%3Cpath%20d%3D%27M35%2013l2%204%204%202-4%202-2%204-2-4-4-2%204-2%202-4Z%27%20fill%3D%27black%27/%3E%3C/svg%3E") center / contain no-repeat;
    mask: url("data:image/svg+xml,%3Csvg%20viewBox%3D%270%200%2048%2048%27%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%3E%3Cpath%20d%3D%27M34%2037c-10%202-21-5-23-16C9%2012%2015%206%2023%205c-4%205-3%2013%202%2018%205%205%2013%206%2019%202-1%206-5%2010-10%2012Z%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%273%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27/%3E%3Cpath%20d%3D%27M35%2013l2%204%204%202-4%202-2%204-2-4-4-2%204-2%202-4Z%27%20fill%3D%27black%27/%3E%3C/svg%3E") center / contain no-repeat;
}

#plan_desayuno_btn::after,
#plan_desayuno_btn button::after {
    content: "Desayuno";
}

#plan_comida_btn::after,
#plan_comida_btn button::after {
    content: "Comida";
}

#plan_cena_btn::after,
#plan_cena_btn button::after {
    content: "Cena";
}

#plan_desayuno_btn::after,
#plan_desayuno_btn button::after,
#plan_comida_btn::after,
#plan_comida_btn button::after,
#plan_cena_btn::after,
#plan_cena_btn button::after {
    display: block;
    color: var(--app-ink);
    font-size: 17px;
    font-weight: 780;
}

.meal-plan-output {
    margin: 0 0 20px;
    padding: 22px 24px;
    border-radius: 24px;
    background: rgba(255,255,255,.82);
    border: 1px solid rgba(126, 99, 199, .12);
    box-shadow: 0 12px 32px rgba(87, 67, 145, .07);
    color: var(--app-ink);
}

.meal-plan-output h2 {
    margin: 0 0 14px !important;
    font-size: 25px !important;
    color: var(--app-ink) !important;
}

.meal-plan-output h3 {
    margin: 18px 0 10px !important;
    color: var(--app-purple-dark) !important;
    font-size: 18px !important;
}

.meal-plan-output ol,
.meal-plan-output ul {
    display: grid;
    gap: 10px;
    padding-left: 22px !important;
}

.meal-plan-output li {
    margin: 0 !important;
    line-height: 1.55 !important;
}

.meal-plan-output p {
    line-height: 1.6 !important;
    margin: 8px 0 !important;
}

.meal-plan-output strong {
    color: var(--app-ink);
}

.meal-plan-output:empty {
    display: none !important;
}

.meal-icon-bowl {
    display: inline-grid;
    place-items: center;
    width: 34px;
    height: 34px;
    margin: 0 auto 8px;
    color: var(--app-purple);
}

.meal-icon-bowl svg {
    width: 34px;
    height: 34px;
    stroke: currentColor;
    stroke-width: 2.5;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
}

.feature-pill span {
    display: grid;
    place-items: center;
    width: 66px;
    height: 66px;
    border-radius: 50%;
    background: var(--app-lavender-2);
    color: var(--app-purple);
    font-size: 34px;
}

.feature-pill span svg {
    width: 38px;
    height: 38px;
    color: var(--app-purple);
    stroke: var(--app-purple);
    stroke-width: 2.4;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
}

.progress-card {
    padding: 22px;
    border-radius: 26px;
    background: #fff;
    box-shadow: 0 14px 38px rgba(87, 67, 145, .08);
}

.progress-card h3 {
    margin: 0 0 8px;
    font-size: 24px;
}

.progress-card p {
    margin: 0 0 18px;
    color: var(--app-muted);
}

.progress-detail-card {
    padding: 26px;
    border-radius: 28px;
    background: rgba(255,255,255,.88);
    border: 1px solid rgba(126, 99, 199, .12);
    box-shadow: 0 18px 48px rgba(87, 67, 145, .10);
}

.progress-detail-card h2 {
    margin: 0 0 6px;
    color: var(--app-ink);
    font-size: 28px;
}

.progress-detail-card .progress-lead {
    margin: 0 0 22px;
    color: var(--app-muted);
}

.progress-metric {
    margin: 18px 0;
}

.progress-metric-header {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: baseline;
    margin-bottom: 8px;
    font-weight: 800;
}

.progress-metric-header span {
    color: var(--app-muted);
    font-size: 14px;
    font-weight: 700;
}

.progress-detail-track {
    height: 16px;
    border-radius: 999px;
    background: #f0e9f8;
    overflow: hidden;
}

.progress-detail-track span {
    display: block;
    height: 100%;
    width: var(--value, 0%);
    border-radius: inherit;
    background: linear-gradient(90deg, #7d63c7, #b38be8);
}

.level-cta button {
    min-height: 54px;
    border-radius: 22px !important;
    background:
        linear-gradient(110deg, transparent 0%, rgba(255,255,255,.28) 42%, transparent 58%) -160px 0 / 140px 100% no-repeat,
        linear-gradient(135deg, #8b6ddd, #6f59bf) !important;
    color: #fff !important;
    border: 0 !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    box-shadow: 0 18px 42px rgba(87, 67, 145, .22) !important;
    animation: plan-shine 3.6s ease-in-out infinite;
}

.level-card {
    position: relative;
    overflow: hidden;
    padding: 28px;
    border-radius: 30px;
    background:
        radial-gradient(circle at 88% 10%, rgba(125, 99, 199, .20), transparent 34%),
        linear-gradient(145deg, rgba(255,255,255,.96), rgba(249,246,255,.92));
    border: 1px solid rgba(126, 99, 199, .14);
    box-shadow: 0 22px 54px rgba(87, 67, 145, .12);
}

.level-card small {
    display: inline-flex;
    padding: 7px 12px;
    border-radius: 999px;
    background: #efe8ff;
    color: var(--app-purple-dark);
    font-weight: 900;
}

.level-card h2 {
    margin: 16px 0 6px;
    font-size: 34px;
    color: var(--app-ink);
}

.level-card p {
    margin: 0 0 22px;
    color: var(--app-muted);
}

.level-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin: 18px 0;
}

.level-stat {
    padding: 16px;
    border-radius: 22px;
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(126, 99, 199, .10);
}

.level-stat span {
    display: block;
    color: var(--app-muted);
    font-size: 13px;
    font-weight: 750;
}

.level-stat strong {
    display: block;
    margin-top: 5px;
    color: var(--app-ink);
    font-size: 22px;
}

.level-track {
    height: 18px;
    border-radius: 999px;
    overflow: hidden;
    background: #eee7f8;
    box-shadow: inset 0 1px 3px rgba(70, 52, 118, .08);
}

.level-track span {
    display: block;
    height: 100%;
    width: var(--level-value, 0%);
    border-radius: inherit;
    background: linear-gradient(90deg, #7d63c7, #b486ee);
}

.level-foot {
    margin-top: 12px !important;
    font-size: 14px;
}

.challenge-cta button {
    min-height: 52px;
    border-radius: 22px !important;
    background: linear-gradient(135deg, #8b6ddd, #6f59bf) !important;
    color: #fff !important;
    border: 0 !important;
    font-weight: 900 !important;
    box-shadow: 0 18px 42px rgba(87, 67, 145, .20) !important;
}

.challenge-complete button {
    min-height: 50px;
    border-radius: 20px !important;
    font-weight: 900 !important;
}

.challenge-screen {
    padding: 28px;
    border-radius: 30px;
    background:
        radial-gradient(circle at 88% 8%, rgba(125, 99, 199, .18), transparent 34%),
        linear-gradient(145deg, rgba(255,255,255,.98), rgba(249,246,255,.92));
    border: 1px solid rgba(126, 99, 199, .14);
    box-shadow: 0 22px 54px rgba(87, 67, 145, .12);
}

.challenge-hero span {
    display: inline-flex;
    padding: 7px 12px;
    border-radius: 999px;
    background: #efe8ff;
    color: var(--app-purple-dark);
    font-weight: 900;
}

.challenge-hero h2 {
    margin: 16px 0 6px;
    color: var(--app-ink);
    font-size: 32px;
}

.challenge-hero p {
    margin: 0 0 22px;
    color: var(--app-muted);
}

.challenge-summary {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin: 18px 0 14px;
}

.challenge-summary div {
    padding: 16px;
    border-radius: 22px;
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(126, 99, 199, .10);
}

.challenge-summary small {
    display: block;
    color: var(--app-muted);
    font-size: 13px;
    font-weight: 750;
}

.challenge-summary strong {
    display: block;
    margin-top: 4px;
    color: var(--app-ink);
    font-size: 22px;
}

.challenge-track {
    height: 14px;
    border-radius: 999px;
    overflow: hidden;
    background: #eee7f8;
    margin-bottom: 22px;
}

.challenge-track span {
    display: block;
    width: var(--challenge-value, 0%);
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #7d63c7, #b486ee);
}

.challenge-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.challenge-card {
    padding: 18px;
    border-radius: 24px;
    background: rgba(255,255,255,.84);
    border: 1px solid rgba(126, 99, 199, .12);
    box-shadow: 0 12px 30px rgba(87, 67, 145, .08);
}

.challenge-card.done {
    background: linear-gradient(145deg, #f2fff8, #ffffff);
    border-color: rgba(78, 168, 119, .25);
}

.challenge-card-top,
.challenge-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.challenge-number,
.challenge-category {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    font-weight: 900;
}

.challenge-number {
    width: 34px;
    height: 34px;
    background: #efe8ff;
    color: var(--app-purple-dark);
}

.challenge-category {
    padding: 7px 10px;
    background: rgba(234, 223, 249, .60);
    color: var(--app-purple-dark);
    font-size: 12px;
}

.challenge-card h3 {
    margin: 14px 0 8px;
    color: var(--app-ink);
    font-size: 19px;
}

.challenge-card p {
    margin: 0 0 16px;
    color: var(--app-muted);
    line-height: 1.45;
}

.challenge-meta strong {
    color: var(--app-purple-dark);
}

.challenge-meta span {
    padding: 7px 10px;
    border-radius: 999px;
    background: #f6f2fd;
    color: var(--app-muted);
    font-size: 12px;
    font-weight: 900;
}

.challenge-card.done .challenge-meta span {
    background: #def7e8;
    color: #2d7d4d;
}

.challenge-badges {
    margin-top: 18px;
    padding: 18px;
    border-radius: 24px;
    background: rgba(255,255,255,.70);
    border: 1px solid rgba(126, 99, 199, .10);
}

.challenge-badges strong {
    display: block;
    margin-bottom: 10px;
}

.challenge-badges span {
    display: inline-flex;
    margin: 4px 6px 4px 0;
    padding: 7px 10px;
    border-radius: 999px;
    background: #efe8ff;
    color: var(--app-purple-dark);
    font-weight: 850;
    font-size: 13px;
}

.challenge-message {
    margin: 16px 0 0;
    padding: 14px 16px;
    border-radius: 18px;
    background: #f6f2fd;
    color: var(--app-purple-dark);
    font-weight: 850;
}

.challenge-message.success {
    background: #e8f8ef;
    color: #267347;
}

@media (max-width: 640px) {
    .level-card {
        padding: 22px;
        border-radius: 26px;
    }

    .level-card h2 {
        font-size: 30px;
    }

    .level-stats {
        grid-template-columns: 1fr;
    }

    .challenge-screen {
        padding: 22px;
        border-radius: 26px;
    }

    .challenge-summary,
    .challenge-grid {
        grid-template-columns: 1fr;
    }
}

.macro-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 22px 0;
}

.macro-tile {
    padding: 14px 12px;
    border-radius: 18px;
    background: rgba(234, 223, 249, .52);
    text-align: center;
}

.macro-tile strong {
    display: block;
    color: var(--app-purple-dark);
    font-size: 20px;
}

.macro-tile span {
    color: var(--app-muted);
    font-size: 13px;
}

.next-step-card {
    margin-top: 18px;
    padding: 16px 18px;
    border-radius: 20px;
    background: linear-gradient(135deg, #f6f0ff, #ffffff);
    border-left: 4px solid var(--app-purple);
    color: var(--app-ink);
}

.session-card {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 14px;
    align-items: center;
    margin: 18px 0 6px;
    padding: 18px 20px;
    border-radius: 24px;
    background: rgba(255,255,255,.90);
    border: 1px solid rgba(126, 99, 199, .14);
    box-shadow: 0 16px 42px rgba(87, 67, 145, .10);
}

.session-avatar {
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    border-radius: 18px;
    background: linear-gradient(135deg, #eadff9, #fff);
    color: var(--app-purple);
    font-size: 24px;
    font-weight: 900;
}

.session-card small {
    display: block;
    margin-bottom: 2px;
    color: var(--app-purple-dark);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .02em;
}

.session-card strong {
    display: block;
    color: var(--app-ink);
    font-size: 21px;
}

.session-card p {
    margin: 4px 0 0;
    color: var(--app-muted);
}

.progress-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 14px;
    align-items: center;
}

.progress-track {
    height: 18px;
    border-radius: 999px;
    background: #f0e9f8;
    overflow: hidden;
}

.progress-track span {
    display: block;
    width: var(--progress-width, 0%);
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #8569d4, #b088e7);
}

.nutribot-note,
.block,
.form,
.panel {
    border-radius: 24px !important;
    box-shadow: 0 12px 36px rgba(77, 60, 116, .08) !important;
}

button,
.gr-button {
    border-radius: 18px !important;
}

.gr-button-primary,
button.primary {
    background: linear-gradient(135deg, #8b6ddd, #6f59bf) !important;
    border: 0 !important;
}

[role="tablist"],
.tab-container {
    padding: 8px !important;
    border: 0 !important;
    border-radius: 24px !important;
    background: rgba(255,255,255,.72) !important;
    box-shadow: 0 12px 34px rgba(77, 60, 116, .09);
}

[role="tab"],
.tab-container button {
    border-radius: 16px !important;
    padding: 10px 16px !important;
}

[role="tab"][aria-selected="true"],
.tab-container button.selected {
    background: var(--app-lavender-2) !important;
    color: var(--app-purple-dark) !important;
}

.chatbot,
.message,
[data-testid="bot"],
[data-testid="user"] {
    border-radius: 24px !important;
}

.chatbot {
    min-height: 520px !important;
    background: linear-gradient(180deg, rgba(255,255,255,.92), rgba(250,247,255,.88)) !important;
    border: 1px solid rgba(126, 99, 199, .12) !important;
    box-shadow: 0 18px 46px rgba(77, 60, 116, .08) !important;
    padding: 18px !important;
    overflow: auto !important;
    scrollbar-width: thin !important;
}

.chatbot img {
    width: 58px !important;
    height: 58px !important;
    min-width: 58px !important;
    min-height: 58px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 2px solid rgba(255,255,255,.95) !important;
    box-shadow: 0 8px 20px rgba(77, 60, 116, .12) !important;
}

.chatbot .message,
.chatbot [data-testid="bot"],
.chatbot [data-testid="user"] {
    max-width: min(76%, 640px) !important;
    min-height: 0 !important;
    height: auto !important;
    padding: 14px 18px !important;
    line-height: 1.55 !important;
    font-size: 16px !important;
    white-space: normal !important;
    overflow: hidden !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
    box-sizing: border-box !important;
}

.chatbot .message *,
.chatbot [data-testid="bot"] *,
.chatbot [data-testid="user"] * {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    max-width: 100% !important;
}

.chatbot [data-testid="user"] {
    background: linear-gradient(135deg, #8d68e8, #6f58c4) !important;
    color: #fff !important;
    margin-left: auto !important;
}

.chatbot [data-testid="bot"] {
    background: #fff !important;
    color: var(--app-ink) !important;
    border: 1px solid rgba(126, 99, 199, .12) !important;
    margin-right: auto !important;
}

.chatbot .prose p {
    margin: 0 !important;
}

.chatbot [class*="avatar"] img {
    width: 60px !important;
    height: 60px !important;
    min-width: 60px !important;
    min-height: 60px !important;
}

.chatbot [class*="bubble"] {
    width: auto !important;
    max-width: 100% !important;
}

.chat-input-row textarea,
.chat-input-row input {
    border-radius: 22px !important;
    background: #fff !important;
    border-color: rgba(126, 99, 199, .16) !important;
}

.nuti-chat-shell {
    min-height: 520px;
    max-height: 620px;
    overflow-y: auto;
    padding: 22px;
    border-radius: 28px;
    background: linear-gradient(180deg, rgba(255,255,255,.94), rgba(250,247,255,.9));
    border: 1px solid rgba(126, 99, 199, .14);
    box-shadow: 0 18px 46px rgba(77, 60, 116, .08);
}

.chat-empty-state {
    min-height: 420px;
    display: grid;
    place-items: center;
    text-align: center;
    color: var(--app-muted);
    font-weight: 650;
}

.chat-row {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    margin: 16px 0;
}

.chat-row.user {
    justify-content: flex-end;
}

.chat-row.bot {
    justify-content: flex-start;
}

.chat-avatar {
    width: 62px;
    height: 62px;
    min-width: 62px;
    border-radius: 50%;
    object-fit: cover;
    background: #fff;
    border: 2px solid rgba(255,255,255,.95);
    box-shadow: 0 10px 24px rgba(77, 60, 116, .14);
}

.chat-bubble {
    max-width: min(72%, 640px);
    padding: 16px 18px;
    border-radius: 24px;
    font-size: 16px;
    line-height: 1.55;
    white-space: normal;
    overflow-wrap: anywhere;
    box-shadow: 0 12px 28px rgba(77, 60, 116, .08);
}

.chat-row.bot .chat-bubble {
    background: #fff;
    color: var(--app-ink);
    border: 1px solid rgba(126, 99, 199, .13);
    border-bottom-left-radius: 8px;
}

.chat-row.user .chat-bubble {
    background: linear-gradient(135deg, #8d68e8, #6f58c4);
    color: #fff;
    border-bottom-right-radius: 8px;
}

.chat-name {
    display: block;
    margin-bottom: 6px;
    color: var(--app-purple-dark);
    font-size: 13px;
    font-weight: 850;
}

.chat-row.user .chat-name {
    color: rgba(255,255,255,.9);
}

.chat-time {
    display: block;
    margin-top: 7px;
    font-size: 11px;
    font-weight: 700;
    text-align: right;
    color: rgba(91, 82, 115, .55);
}

.chat-row.user .chat-time {
    color: rgba(255,255,255,.76);
}

@media (max-width: 760px) {
    .gradio-container {
        padding: 12px !important;
    }

    .nutribot-hero {
        min-height: 500px;
        grid-template-columns: 1fr;
        padding: 34px 28px 92px;
        border-radius: 30px;
        margin-top: 8px;
    }

    .nutribot-app-mark {
        margin-bottom: 18px;
    }

    .nutribot-hero h1 {
        font-size: 44px;
    }

    .nutribot-subtitle {
        max-width: 260px;
        font-size: 25px;
    }

    .nutribot-robot-wrap {
        min-height: 120px;
        place-items: end center;
    }

    .nutribot-robot-img {
        width: min(265px, 54vw);
        max-height: 315px;
        position: absolute;
        right: -42px;
        bottom: -8px;
    }

    .hero-plans-popover {
        left: 0;
        top: 26px;
        width: min(255px, 76vw);
    }

    .hero-plans-popover[open] .hero-plans-card {
        inset: 12px;
        width: calc(100vw - 24px);
        max-height: calc(100vh - 24px);
        border-radius: 24px;
    }

    .hero-plans-popover[open] summary {
        top: 18px;
        right: 18px;
        width: 88px;
        height: 38px;
    }

    .hero-plans-popover summary {
        min-width: 96px;
        height: 40px;
        padding: 0 16px;
        font-size: 14px;
    }

    .phone-dashboard {
        margin-top: -138px;
        width: calc(100% - 24px);
        padding: 24px;
        border-radius: 28px;
    }

    .dash-title h2 {
        font-size: 27px;
    }

    .dash-title {
        padding-right: 64px;
    }

    .food-register-toggle,
    .food-register-toggle button {
        top: 25px;
        right: 24px;
        width: 44px !important;
        max-width: 44px !important;
        min-width: 44px !important;
        height: 44px !important;
        min-height: 44px !important;
        font-size: 32px !important;
    }

    .meal-preview {
        height: 130px;
    }

    .feature-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
    }

    .meal-action-btn,
    .meal-action-btn button {
        min-height: 108px !important;
        border-radius: 22px !important;
        padding: 10px 6px !important;
    }

    #plan_desayuno_btn::before,
    #plan_desayuno_btn button::before,
    #plan_comida_btn::before,
    #plan_comida_btn button::before,
    #plan_cena_btn::before,
    #plan_cena_btn button::before {
        width: 50px;
        height: 50px;
        margin-bottom: 7px;
    }

    .chatbot {
        min-height: 460px !important;
        padding: 14px !important;
    }

    .chatbot img {
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        min-height: 50px !important;
    }

    .chatbot .message,
    .chatbot [data-testid="bot"],
    .chatbot [data-testid="user"] {
        max-width: min(82%, 520px) !important;
        font-size: 15px !important;
        padding: 13px 15px !important;
    }

    .nuti-chat-shell {
        min-height: 460px;
        max-height: 560px;
        padding: 16px;
        border-radius: 24px;
    }

    .chat-avatar {
        width: 52px;
        height: 52px;
        min-width: 52px;
    }

    .chat-bubble {
        max-width: 78%;
        font-size: 15px;
        padding: 14px 16px;
    }

    .plans-grid {
        grid-template-columns: 1fr;
    }

    .plans-hero,
    .plans-grid {
        padding: 18px;
    }

    .plans-note-card {
        margin-left: 18px;
        margin-right: 18px;
    }

    .feature-pill {
        min-height: 106px;
        font-size: 15px;
        border-radius: 22px;
    }

    .feature-pill span {
        width: 58px;
        height: 58px;
        font-size: 29px;
    }
}

@media (max-width: 420px) {
    .nutribot-hero {
        min-height: 500px;
        padding: 28px 24px 86px;
    }

    .nutribot-hero h1 {
        font-size: 40px;
    }

    .nutribot-subtitle {
        font-size: 23px;
    }

    .nutribot-robot-img {
        width: min(225px, 56vw);
        right: -32px;
        bottom: -6px;
    }

    .hero-plans-popover {
        left: 0;
        top: 24px;
        width: min(238px, 82vw);
    }

    .hero-plans-popover[open] .hero-plans-card {
        inset: 10px;
        width: calc(100vw - 20px);
        max-height: calc(100vh - 20px);
    }

    .plan-card {
        min-height: 0;
    }

    .phone-dashboard {
        margin-top: -132px;
        width: calc(100% - 16px);
        padding: 20px;
    }

    .dash-title {
        padding-right: 58px;
        margin-bottom: 18px;
    }

    .food-register-toggle,
    .food-register-toggle button {
        top: 22px;
        left: auto;
        right: 20px;
        width: 42px !important;
        max-width: 42px !important;
        min-width: 42px !important;
        height: 42px !important;
        min-height: 42px !important;
        text-align: center !important;
        font-size: 30px !important;
    }

    .chatbot {
        min-height: 420px !important;
    }

    .chatbot .message,
    .chatbot [data-testid="bot"],
    .chatbot [data-testid="user"] {
        max-width: 86% !important;
    }

    .nuti-chat-shell {
        padding: 14px;
    }

    .chat-row {
        gap: 9px;
        margin: 14px 0;
    }

    .chat-avatar {
        width: 46px;
        height: 46px;
        min-width: 46px;
    }

    .chat-bubble {
        max-width: 80%;
        font-size: 14px;
        padding: 13px 14px;
        border-radius: 20px;
    }
}
"""


def logo_data_uri():
    logo_path = Path(__file__).parent / "assets" / "nutribot-logo.jpg"
    try:
        encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
    except OSError:
        return ""


def logo_titulo_data_uri():
    logo_path = Path(__file__).parent / "assets" / "nutribot-logo-titulo.png"
    try:
        encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except OSError:
        return ""


def planes_page_html():
    return """
    <section class="plans-screen">
        <div class="plans-hero">
            <span class="plans-eyebrow">Elige tu experiencia</span>
            <h2>Planes y precios</h2>
            <p>Opciones pensadas para distintos niveles de acompañamiento: desde una consulta puntual hasta una experiencia premium con seguimiento más completo.</p>
        </div>
        <div class="plans-grid">
            <article class="plan-card">
                <span class="plan-badge">Sesión individual</span>
                <h3>Consulta nutriólogo</h3>
                <div class="plan-price">$500 <small>MXN</small></div>
                <p>Orientación profesional en línea para resolver dudas, revisar metas y recibir recomendaciones personalizadas.</p>
                <ul>
                    <li>Consulta en línea</li>
                    <li>Revisión de objetivos y hábitos</li>
                    <li>Recomendaciones personalizadas</li>
                    <li>Ideal para apoyo puntual</li>
                </ul>
            </article>
            <article class="plan-card featured">
                <span class="plan-badge">Más accesible</span>
                <h3>Paquete mensual</h3>
                <div class="plan-price">$299 <small>MXN / mes</small></div>
                <p>Membresía para usar NutriBot como guía diaria de hábitos saludables, registro visual y seguimiento.</p>
                <ul>
                    <li>Registro de comida con foto</li>
                    <li>Planes de desayuno, comida y cena</li>
                    <li>Retos saludables y XP</li>
                    <li>Coach emocional y Nuti</li>
                </ul>
            </article>
            <article class="plan-card">
                <span class="plan-badge">Premium</span>
                <h3>Paquete Premium</h3>
                <div class="plan-price">$9,300 <small>MXN</small></div>
                <p>Plan completo para usuarios que buscan más beneficios, prioridad y una experiencia de seguimiento más avanzada.</p>
                <ul>
                    <li>Beneficios premium</li>
                    <li>Prioridad en servicios</li>
                    <li>Seguimiento más completo</li>
                    <li>Experiencia integral NutriBot</li>
                </ul>
            </article>
        </div>
        <div class="plans-note-card">
            Estos precios son de referencia para el prototipo NutriBot. La disponibilidad, beneficios y costos finales pueden ajustarse según el servicio, el seguimiento elegido y la validación con usuarios reales.
        </div>
    </section>
    """


def robot_data_uri(filename="nutribot-robot-3d.png"):
    robot_path = Path(__file__).parent / "assets" / filename
    try:
        encoded = base64.b64encode(robot_path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except OSError:
        return ""


def splash_html():
    logo_src = logo_titulo_data_uri()
    if not logo_src:
        return ""
    return f"""
    <div class="nutribot-splash" aria-hidden="true">
        <div class="nutribot-splash-inner">
            <img src="{logo_src}" alt="NutriBot">
        </div>
    </div>
    """


def dashboard_progreso_usuario():
    usuario = estado_app.get("usuario_actual")
    datos = obtener_datos_usuario(usuario) if usuario else None
    if not datos or not datos.get("perfil"):
        return {
            "porcentaje": 0,
            "texto": "Configura tu perfil para empezar.",
            "detalle": "0%"
        }

    total = int(datos.get("calorias_totales", 0) or 0)
    restante = int(datos.get("calorias_restantes", total) or 0)
    consumido = max(total - restante, 0)
    proteina_objetivo = int(datos.get("proteina_objetivo", 0) or 0)
    proteina_consumida = int(datos.get("proteina_consumida", 0) or 0)
    comidas = len(datos.get("historial_comidas", []))

    avance_calorias = (consumido / total) * 100 if total else 0
    avance_proteina = (proteina_consumida / proteina_objetivo) * 100 if proteina_objetivo else 0

    if comidas == 0:
        porcentaje = 0
    elif avance_proteina:
        porcentaje = round((avance_calorias * 0.65) + (avance_proteina * 0.35))
    else:
        porcentaje = round(avance_calorias)

    porcentaje = max(0, min(porcentaje, 100))

    if comidas == 0:
        texto = "Registra tu primera comida."
    elif porcentaje < 35:
        texto = "Apenas va empezando tu día."
    elif porcentaje < 80:
        texto = "Vas por buen camino."
    else:
        texto = "Cerca de completar tu meta."

    return {
        "porcentaje": porcentaje,
        "texto": texto,
        "detalle": f"{porcentaje}%"
    }


def hero_html():
    logo_src = logo_data_uri()
    robot_src = robot_data_uri("nutribot-robot-generated-hero.png")
    leaf_style = f' style="--robot-leaf: url({logo_src});"' if logo_src else ""
    robot = f'<img class="nutribot-robot-img" src="{robot_src}" alt="Robot Nutribot">' if robot_src else ""
    app_mark = f'<img src="{logo_src}" alt="Logo Nutribot">' if logo_src else "Nutribot"
    version_texto = texto_version_usuario()
    planes = f"""
        <details class="hero-plans-popover">
            <summary>Planes</summary>
            <div class="hero-plans-card">
                {planes_page_html()}
            </div>
        </details>
    """
    return f"""
    <section class="nutribot-hero"{leaf_style}>
        <div class="nutribot-app-copy">
            <div class="nutribot-app-mark">{app_mark}</div>
            <h1>¡Hola!</h1>
            <p class="nutribot-tagline">Comer sano, inteligente y divertido.</p>
            <p class="nutribot-subtitle">
                ¿{version_texto} para tu mejor versión hoy?
            </p>
        </div>
        <div class="nutribot-robot-wrap">
            {planes}
            {robot}
        </div>
    </section>
    """


def dashboard_intro_html(modo_registro=False):
    if modo_registro:
        return """
        <div class="dash-title dash-title-registro">
            <div>
                <h2>Registro de comida</h2>
                <p>Sube una foto para estimar calorías, proteína y nutrientes.</p>
            </div>
            <span class="dash-arrow">‹</span>
        </div>
        """

    return """
    <div class="dash-title">
        <div>
            <h2>Tu plan de hoy</h2>
            <p>Equilibrado y delicioso</p>
        </div>
        <span class="dash-arrow">›</span>
    </div>
    <div class="meal-preview" aria-hidden="true"></div>
    """


def texto_boton_registro_inicio(modo_registro=False):
    texto = "Plan diario" if modo_registro else "Registro de comida"
    return f'<div class="food-register-label">{texto}</div>'


def dashboard_progress_html():
    progreso = dashboard_progreso_usuario()
    return f"""
    <div class="progress-card">
        <h3>Tu progreso</h3>
        <p>{progreso["texto"]}</p>
        <div class="progress-row">
            <div class="progress-track"><span style="--progress-width: {progreso["porcentaje"]}%;"></span></div>
            <strong>{progreso["detalle"]}</strong>
        </div>
    </div>
    """


# =========================
# USUARIO ACTUAL
# =========================

def cargar_usuario_en_estado():
    usuario = estado_app.get("usuario_actual")
    estado_app["usuario_actual"] = usuario
    return usuario


def asegurar_usuario():
    usuario = estado_app.get("usuario_actual")

    if not usuario:
        return None, " Primero entra con tu nombre en la pestaña Inicio."

    datos = obtener_datos_usuario(usuario)

    if not datos:
        return None, " No se pudo cargar ese usuario."

    estado_app["usuario_actual"] = usuario
    return datos, None


def reiniciar_sesion_visual():
    estado_app["usuario_actual"] = None
    return None


def hero_actualizado():
    return hero_html()


def progreso_actualizado():
    return dashboard_progress_html()


def desbloquear_funciones():
    return [gr.update(interactive=True)] * 49


def texto_version_usuario():
    usuario = estado_app.get("usuario_actual")
    datos = obtener_datos_usuario(usuario) if usuario else None
    genero_usuario = ""

    if datos:
        genero_usuario = str(datos.get("perfil", {}).get("genero", "")).strip().lower()

    return "Lista" if genero_usuario == "mujer" else "Listo"


def actualizar_avatar_usuario(usuario):
    ruta = Path("assets") / "nutribot-user-chat-avatar.png"
    try:
        from PIL import Image, ImageDraw

        im = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.ellipse((8, 8, 312, 312), fill=(239, 232, 255, 255), outline=(128, 112, 199, 255), width=4)
        dr.ellipse((116, 70, 204, 158), fill=(128, 112, 199, 255))
        dr.rounded_rectangle((76, 176, 244, 268), radius=82, fill=(128, 112, 199, 255))
        dr.ellipse((116, 70, 204, 158), outline=(145, 126, 214, 255), width=2)
        dr.arc((78, 176, 242, 312), 190, 340, fill=(113, 92, 191, 255), width=4)
        im.save(ruta)
    except Exception:
        # Si Pillow no está disponible, conservamos el avatar anterior en lugar
        # de escribir un SVG con extensión PNG.
        return


# =========================
# XP / NIVEL
# =========================

def agregar_xp(cantidad):
    datos, error = asegurar_usuario()
    if error:
        return

    xp_actual = datos.get("xp", 0)
    nivel_actual = datos.get("nivel", 1)

    xp_actual += cantidad

    while xp_actual >= nivel_actual * 100:
        xp_actual -= nivel_actual * 100
        nivel_actual += 1

    datos["xp"] = xp_actual
    datos["nivel"] = nivel_actual
    actualizar_datos_usuario(datos)


def ver_nivel():
    datos, error = asegurar_usuario()
    if error:
        return f"""
        <section class="level-card">
            <small>Acceso requerido</small>
            <h2>Nivel bloqueado</h2>
            <p>{error}</p>
        </section>
        """

    nivel = datos.get("nivel", 1)
    xp = datos.get("xp", 0)
    meta_xp = nivel * 100

    porcentaje = int((xp / meta_xp) * 100) if meta_xp > 0 else 0
    porcentaje = min(porcentaje, 100)
    xp_restante = max(meta_xp - xp, 0)

    return f"""
    <section class="level-card">
        <small>Progreso de bienestar</small>
        <h2>Nivel {nivel}</h2>
        <p>Tu avance sube cuando registras comidas, completas retos y usas tus herramientas de NutriBot.</p>
        <div class="level-stats">
            <div class="level-stat">
                <span>XP actual</span>
                <strong>{xp}</strong>
            </div>
            <div class="level-stat">
                <span>Meta del nivel</span>
                <strong>{meta_xp}</strong>
            </div>
            <div class="level-stat">
                <span>Falta</span>
                <strong>{xp_restante}</strong>
            </div>
        </div>
        <div class="level-track" aria-label="Progreso de nivel">
            <span style="--level-value: {porcentaje}%"></span>
        </div>
        <p class="level-foot">{porcentaje}% completado para llegar al siguiente nivel.</p>
    </section>
    """


# =========================
# LOGIN SIMPLE
# =========================

def tarjeta_sesion(usuario, mensaje="Sesión activa"):
    if not usuario:
        return """
        <section class="session-card">
            <div class="session-avatar">?</div>
            <div>
                <small>Sin sesión</small>
                <strong>No hay usuario activo</strong>
                <p>Entra con tu nombre para desbloquear Nutribot.</p>
            </div>
        </section>
        """

    inicial = str(usuario).strip()[:1].upper() or "N"
    return f"""
    <section class="session-card">
        <div class="session-avatar">{inicial}</div>
        <div>
            <small>{mensaje}</small>
            <strong>Entraste como {usuario}</strong>
            <p>Tu perfil, progreso y planes se adaptarán a este usuario.</p>
        </div>
    </section>
    """


def entrar_usuario(nombre):
    mensaje = iniciar_o_crear_usuario(nombre)
    usuario = obtener_usuario_actual()
    estado_app["usuario_actual"] = usuario
    actualizar_avatar_usuario(usuario)
    return tarjeta_sesion(usuario, "Bienvenida")


def ver_usuario_actual():
    usuario = estado_app.get("usuario_actual")

    if not usuario:
        return tarjeta_sesion("")

    estado_app["usuario_actual"] = usuario
    return tarjeta_sesion(usuario, "Usuario actual")


def asset_data_uri(ruta_relativa):
    ruta = Path(ruta_relativa)
    if not ruta.exists():
        return ""

    mime = "image/png"
    if ruta.suffix.lower() in {".jpg", ".jpeg"}:
        mime = "image/jpeg"

    try:
        return f"data:{mime};base64,{base64.b64encode(ruta.read_bytes()).decode('ascii')}"
    except Exception:
        return ""


def formato_texto_chat(texto):
    texto = html.escape(str(texto or "").strip())
    texto = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", texto)
    texto = texto.replace("\n", "<br>")
    return texto


def limpiar_respuesta_chat(texto, max_palabras=115):
    texto = str(texto or "").strip()
    texto = re.sub(r"[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]+", "", texto)
    texto = re.sub(r"\s+:", ":", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    lineas = []
    vistas = set()
    for linea in texto.splitlines():
        limpia = linea.strip()
        if not limpia:
            if lineas and lineas[-1] != "":
                lineas.append("")
            continue
        firma = limpia.lower()
        if firma in vistas:
            continue
        vistas.add(firma)
        lineas.append(limpia)

    texto = "\n".join(lineas).strip()
    palabras = texto.split()
    if len(palabras) > max_palabras:
        texto = " ".join(palabras[:max_palabras]).rstrip(".,;:") + "."
    return texto


def hora_chat():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def hora_de_mensaje(item):
    return str(item.get("time") or item.get("hora") or "").strip()


def render_chat(historial, tipo="nuti"):
    historial = historial or []
    bot_nombre = "Nuti" if tipo == "nuti" else "Coach"
    usuario = estado_app.get("usuario_actual") or "Tú"
    user_avatar = asset_data_uri("assets/nutribot-user-chat-avatar.png")
    bot_avatar = asset_data_uri("assets/nutribot-robot-body-chat-avatar.png")

    if not historial:
        saludo = (
            "Hola. Entra con tu nombre y escríbeme para ayudarte con comida, hábitos o dudas de nutrición."
            if tipo == "nuti"
            else "Hola. Cuando quieras, cuéntame cómo te sientes y lo trabajamos paso a paso."
        )
        historial = [{"role": "assistant", "content": saludo, "time": hora_chat()}]

    filas = []
    for item in historial[-20:]:
        role = item.get("role", "assistant")
        contenido = formato_texto_chat(item.get("content", ""))
        hora = html.escape(hora_de_mensaje(item) or hora_chat())
        tiempo = f'<span class="chat-time">{hora}</span>'
        if role == "user":
            avatar = f'<img class="chat-avatar" src="{user_avatar}" alt="{html.escape(usuario)}">' if user_avatar else ""
            filas.append(
                '<div class="chat-row user">'
                f'<div class="chat-bubble"><span class="chat-name">{html.escape(usuario)}</span>{contenido}{tiempo}</div>'
                f'{avatar}'
                '</div>'
            )
        else:
            avatar = f'<img class="chat-avatar" src="{bot_avatar}" alt="{bot_nombre}">' if bot_avatar else ""
            filas.append(
                '<div class="chat-row bot">'
                f'{avatar}'
                f'<div class="chat-bubble"><span class="chat-name">{bot_nombre}</span>{contenido}{tiempo}</div>'
                '</div>'
            )

    return '<div class="nuti-chat-shell">' + "".join(filas) + "</div>"


def cargar_chats_usuario():
    datos, error = asegurar_usuario()
    if error:
        return render_chat([], "nuti"), render_chat([], "coach"), [], []
    memoria_nuti = datos.get("memoria_nuti", [])[-20:]
    memoria_coach = datos.get("memoria_coach", [])[-20:]
    return render_chat(memoria_nuti, "nuti"), render_chat(memoria_coach, "coach"), memoria_nuti, memoria_coach


def chat_inicial_nuti():
    return render_chat([], "nuti")


def chat_inicial_coach():
    return render_chat([], "coach")


def historial_inicial():
    return []




# =========================
# CARGAR DATOS EN FORMULARIO
# =========================

def cargar_formulario_usuario():
    datos, error = asegurar_usuario()
    if error:
        return (
            gr.update(value=None),  # edad
            gr.update(value=None),  # peso
            gr.update(value=None),  # altura
            gr.update(value=None),  # genero
            gr.update(value=None),  # actividad
            gr.update(value=None),  # meta
            gr.update(value=""),    # condicion
            gr.update(value=""),    # alergias
            gr.update(value=""),    # gustos
            gr.update(value=""),    # no_gusta
            gr.update(value=""),    # rutina
            gr.update(value=""),    # glucosa
            gr.update(value=""),    # colesterol
            gr.update(value=""),    # trigliceridos
            gr.update(value=""),    # hemoglobina
            gr.update(value=""),    # observaciones
            error
        )

    perfil = datos.get("perfil", {})
    labs = datos.get("labs", {})

    return (
        gr.update(value=perfil.get("edad", None)),
        gr.update(value=perfil.get("peso", None)),
        gr.update(value=perfil.get("altura", None)),
        gr.update(value=perfil.get("genero", None)),
        gr.update(value=perfil.get("actividad", None)),
        gr.update(value=perfil.get("meta", None)),
        gr.update(value=perfil.get("condicion", "")),
        gr.update(value=perfil.get("alergias", "")),
        gr.update(value=perfil.get("gustos", "")),
        gr.update(value=perfil.get("no_gusta", "")),
        gr.update(value=perfil.get("rutina", "")),
        gr.update(value=labs.get("glucosa", "")),
        gr.update(value=labs.get("colesterol", "")),
        gr.update(value=labs.get("trigliceridos", "")),
        gr.update(value=labs.get("hemoglobina", "")),
        gr.update(value=labs.get("observaciones", "")),
        " Datos cargados correctamente." if perfil else "Este usuario aún no tiene datos guardados."
    )


# =========================
# CHATBOT NUTI
# =========================

def conversar_nuti(mensaje, historial):
    datos, error = asegurar_usuario()
    if error:
        return render_chat(historial, "nuti"), error, historial or []

    if not mensaje or not mensaje.strip():
        return render_chat(historial, "nuti"), "", historial or []

    if historial is None:
        historial = []

    memoria_nuti = datos.get("memoria_nuti", [])
    ahora = hora_chat()
    memoria_nuti.append({"role": "user", "content": mensaje, "time": ahora})
    historial.append({"role": "user", "content": mensaje, "time": ahora})

    mensaje_nuti = (
        f"{mensaje}\n\n"
        "Responde como Nuti, asistente nutricional: directo, claro, práctico y específico. "
        "Contesta en español natural, sin repetir frases y sin mezclar otros idiomas. "
        "Por defecto responde corto: máximo 4 líneas o 90 palabras. "
        "Si recomiendas comida, da 1 o 2 opciones concretas con porción aproximada, kcal y proteína. "
        "Solo da 3 opciones si el usuario pide varias opciones. "
        "No respondas como coach emocional salvo que el usuario pida apoyo emocional."
    )
    respuesta = limpiar_respuesta_chat(buscar_respuesta(mensaje_nuti, memoria_nuti), max_palabras=115)

    hora_respuesta = hora_chat()
    memoria_nuti.append({"role": "assistant", "content": respuesta, "time": hora_respuesta})
    historial.append({"role": "assistant", "content": respuesta, "time": hora_respuesta})

    datos["memoria_nuti"] = memoria_nuti[-20:]
    actualizar_datos_usuario(datos)

    historial = historial[-20:]
    return render_chat(historial, "nuti"), "", historial


# =========================
# COACH EMOCIONAL
# =========================

def conversar_coach(mensaje, historial):
    datos, error = asegurar_usuario()
    if error:
        return render_chat(historial, "coach"), error, historial or []

    if not mensaje or not mensaje.strip():
        return render_chat(historial, "coach"), "", historial or []

    if historial is None:
        historial = []

    memoria_coach = datos.get("memoria_coach", [])
    ahora = hora_chat()
    memoria_coach.append({"role": "user", "content": mensaje, "time": ahora})
    historial.append({"role": "user", "content": mensaje, "time": ahora})

    mensaje_coach = (
        f"{mensaje}\n\n"
        "Responde como Coach emocional de Nutribot: humano, suave, empático y cercano. "
        "Contesta en español natural, sin repetir frases y sin mezclar otros idiomas. "
        "Mantén la respuesta breve: máximo 4 líneas o 95 palabras. "
        "Haz una pregunta breve si ayuda, valida lo que siente la persona y da un paso pequeño y realista. "
        "No hagas planes nutricionales detallados salvo que la emoción esté ligada a comida."
    )
    respuesta = limpiar_respuesta_chat(coach_emocional_inteligente(mensaje_coach, memoria_coach), max_palabras=105)

    hora_respuesta = hora_chat()
    memoria_coach.append({"role": "assistant", "content": respuesta, "time": hora_respuesta})
    historial.append({"role": "assistant", "content": respuesta, "time": hora_respuesta})

    datos["memoria_coach"] = memoria_coach[-20:]
    actualizar_datos_usuario(datos)

    historial = historial[-20:]
    return render_chat(historial, "coach"), "", historial


# =========================
# IA INTERNA DE LA APP
# =========================

MODEL_TEXTO_IA = "Qwen/Qwen2.5-7B-Instruct"


def llamar_ia_texto(system_prompt, user_prompt, temperature=0.55, max_tokens=520):
    token = obtener_hf_token()
    if not token:
        return None

    try:
        client = InferenceClient(provider="auto", token=token, timeout=25)
        completion = client.chat.completions.create(
            model=MODEL_TEXTO_IA,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        respuesta = completion.choices[0].message.content.strip()
        return respuesta or None
    except Exception:
        return None


def contexto_usuario_para_ia(datos):
    perfil = datos.get("perfil", {}) if datos else {}
    historial = datos.get("historial_comidas", []) if datos else []
    recientes = []
    for item in historial[-5:]:
        recientes.append(
            f"{item.get('comida', 'comida')} ({item.get('calorias', 0)} kcal, "
            f"{item.get('proteina', 0)} g proteína)"
        )

    return {
        "nombre": estado_app.get("usuario_actual") or "Usuario",
        "perfil": perfil,
        "calorias_totales": datos.get("calorias_totales", 0),
        "calorias_restantes": datos.get("calorias_restantes", 0),
        "proteina_objetivo": datos.get("proteina_objetivo", 0),
        "proteina_consumida": datos.get("proteina_consumida", 0),
        "comidas_recientes": ", ".join(recientes) if recientes else "Sin comidas registradas hoy."
    }


def prompt_base_nutricion():
    return """
Eres la IA nutricional de Nutribot.
Responde en español mexicano claro, profesional y cálido.
Cuida ortografía, acentos y puntuación.
Da orientación práctica, no diagnósticos médicos.
Respeta alergias, condiciones, alimentos que no gustan y meta del usuario.
Evita repetir la misma comida dentro de una respuesta.
Si faltan datos, haz una recomendación razonable y aclara que es orientativa.
Cuando recomiendes comidas, sé específico: nombra alimentos reales, porciones aproximadas, calorías y proteína estimadas.
Evita frases genéricas como "proteína con carbohidrato"; di ejemplos concretos como pollo con arroz, huevo con tortilla, yogurt con avena, atún con tostadas, etc.
Si el usuario pregunta qué comer, ofrece 3 opciones claras y diferentes.
No uses emojis.
""".strip()


def limpiar_markdown_ia(texto):
    texto = (texto or "").strip()
    if texto.startswith("```"):
        texto = texto.strip("`").strip()
        if texto.lower().startswith("markdown"):
            texto = texto[8:].strip()
    return texto


# =========================
# CÁLCULOS NUTRICIONALES
# =========================

def calcular_calorias_y_proteina(edad, peso, altura, genero, actividad, meta):
    if any(valor is None for valor in [edad, peso, altura]) or not all([genero, actividad, meta]):
        return None, None, " Completa todos los datos para calcular tus metas."

    try:
        edad = int(edad)
        peso = float(peso)
        altura = float(altura)
    except (TypeError, ValueError):
        return None, None, " Edad, peso y altura deben ser números válidos."

    if not 5 <= edad <= 100:
        return None, None, " Revisa la edad. Debe estar entre 5 y 100 años."
    if not 20 <= peso <= 300:
        return None, None, " Revisa el peso. Debe estar entre 20 y 300 kg."
    if not 80 <= altura <= 230:
        return None, None, " Revisa la altura. Debe estar entre 80 y 230 cm."

    if str(genero).lower() == "mujer":
        bmr = 655 + (9.6 * peso) + (1.8 * altura) - (4.7 * edad)
    else:
        bmr = 66 + (13.7 * peso) + (5 * altura) - (6.8 * edad)

    factores = {
        "sedentario": 1.2,
        "ligero": 1.375,
        "moderado": 1.55,
        "activo": 1.725,
        "muy activo": 1.9
    }

    calorias_base = bmr * factores.get(str(actividad).lower(), 1.55)

    meta_lower = str(meta).lower()

    if meta_lower == "bajar de peso":
        calorias_totales = round(calorias_base * 0.8)
        proteina_objetivo = round(peso * 1.6)
    elif meta_lower == "subir de peso":
        calorias_totales = round(calorias_base * 1.15)
        proteina_objetivo = round(peso * 1.8)
    else:
        calorias_totales = round(calorias_base)
        proteina_objetivo = round(peso * 1.4)

    mensaje = (
        f" Tu meta es **{meta_lower}**.\n"
        f" Puedes consumir aproximadamente **{calorias_totales} calorías por día**.\n"
        f" Tu objetivo aproximado de proteína es **{proteina_objetivo} g al día**."
    )

    return calorias_totales, proteina_objetivo, mensaje


def sugerencia_por_hora():
    hora = datetime.now().hour

    if 6 <= hora < 11:
        return " Es buena hora para un desayuno completo y con proteína."
    elif 11 <= hora < 16:
        return " Ahorita es el mejor momento para tu comida fuerte del día."
    elif 16 <= hora < 19:
        return " Esta hora funciona mejor para algo intermedio o una comida moderada."
    else:
        return " Ya es tarde; te conviene una cena más ligera y con buena proteína."


def evaluar_tipo_comida_por_hora(tipo_comida):
    hora = datetime.now().hour

    if 11 <= hora < 16:
        if tipo_comida == "fuerte":
            return " Por la hora, esta comida sí puede funcionar como plato fuerte."
        return " Por la hora, esta opción también encaja bien."
    elif 19 <= hora <= 23:
        if tipo_comida == "fuerte":
            return " Por la hora, esta comida está algo pesada. Te convendría algo más ligero."
        return " Por la hora, esta opción ligera encaja mejor."
    else:
        if tipo_comida == "fuerte":
            return "Puede funcionar, pero depende de cuánto hayas comido hoy."
        return " Esta opción se ve razonable para esta hora."


# =========================
# DATOS PERSONALES
# =========================

def guardar_informacion(
    edad,
    peso,
    altura,
    genero,
    actividad,
    meta,
    condicion,
    alergias,
    gustos,
    no_gusta,
    rutina,
    glucosa,
    colesterol,
    trigliceridos,
    hemoglobina,
    observaciones
):
    datos, error = asegurar_usuario()
    if error:
        return error

    usuario = obtener_usuario_actual()

    perfil = {
        "nombre": usuario,
        "edad": edad,
        "peso": peso,
        "altura": altura,
        "genero": genero,
        "actividad": actividad,
        "meta": meta,
        "condicion": condicion,
        "alergias": alergias,
        "gustos": gustos,
        "no_gusta": no_gusta,
        "rutina": rutina
    }

    labs = {
        "glucosa": glucosa,
        "colesterol": colesterol,
        "trigliceridos": trigliceridos,
        "hemoglobina": hemoglobina,
        "observaciones": observaciones
    }

    calorias_totales, proteina_objetivo, mensaje_nutricional = calcular_calorias_y_proteina(
        edad, peso, altura, genero, actividad, meta
    )

    datos["perfil"] = perfil
    datos["labs"] = labs

    if calorias_totales is not None:
        datos["calorias_totales"] = calorias_totales
        datos["calorias_restantes"] = calorias_totales

    if proteina_objetivo is not None:
        datos["proteina_objetivo"] = proteina_objetivo
        datos["proteina_consumida"] = 0

    actualizar_datos_usuario(datos)
    agregar_xp(20)

    return (
        f" Información guardada.\n"
        f"**Usuario:** {usuario}\n"
        f"**Condición:** {condicion or 'ninguna'}\n"
        f"**Alergias:** {alergias or 'ninguna'}\n\n"
        f"**Gustos:** {gustos or 'sin registrar'}\n"
        f"**Rutina:** {rutina or 'sin registrar'}\n\n"
        f"{mensaje_nutricional}\n\n"
        f"{sugerencia_por_hora()}\n\n"
        f" Ganaste **20 XP**"
    )


def ver_resumen():
    datos, error = asegurar_usuario()
    if error:
        return error

    perfil = datos.get("perfil", {})
    labs = datos.get("labs", {})

    if not perfil:
        return " Aún no has guardado tus datos personales."

    texto = (
        f" **Resumen del usuario**\n\n"
        f"**Nombre:** {perfil.get('nombre', 'Usuario')}\n"
        f"**Meta:** {perfil.get('meta', 'No definida')}\n"
        f"**Actividad:** {perfil.get('actividad', 'No definida')}\n"
        f"**Condición:** {perfil.get('condicion', 'ninguna') or 'ninguna'}\n"
        f"**Alergias:** {perfil.get('alergias', 'ninguna') or 'ninguna'}\n"
        f"**Gustos:** {perfil.get('gustos', 'sin registrar') or 'sin registrar'}\n"
        f"**No le gusta / evita:** {perfil.get('no_gusta', 'sin registrar') or 'sin registrar'}\n"
        f"**Rutina:** {perfil.get('rutina', 'sin registrar') or 'sin registrar'}\n"
        f"**Calorías objetivo:** {datos.get('calorias_totales', 0)} kcal\n"
        f"**Calorías restantes:** {datos.get('calorias_restantes', 0)} kcal\n"
        f"**Proteína objetivo:** {datos.get('proteina_objetivo', 0)} g\n"
        f"**Proteína consumida:** {datos.get('proteina_consumida', 0)} g\n"
        f"**Nivel:** {datos.get('nivel', 1)}\n"
        f"**XP:** {datos.get('xp', 0)}"
    )

    if any(str(v).strip() for v in labs.values()):
        texto += (
            f"\n\n **Laboratorios / estudios (opcional)**\n"
            f"Glucosa: {labs.get('glucosa', '') or '—'}\n"
            f"Colesterol: {labs.get('colesterol', '') or '—'}\n"
            f"Triglicéridos: {labs.get('trigliceridos', '') or '—'}\n"
            f"Hemoglobina: {labs.get('hemoglobina', '') or '—'}\n"
            f"Observaciones: {labs.get('observaciones', '') or '—'}"
        )

    return texto


# =========================
# PROGRESO VISUAL
# =========================

def ver_progreso():
    datos, error = asegurar_usuario()
    if error:
        return error

    total = datos.get("calorias_totales", 0)
    restante = datos.get("calorias_restantes", 0)
    consumido = max(total - restante, 0)

    proteina_objetivo = datos.get("proteina_objetivo", 0)
    proteina_consumida = datos.get("proteina_consumida", 0)

    if total == 0:
        return " Primero guarda tus datos personales."

    porcentaje_cal = int((consumido / total) * 100) if total > 0 else 0
    porcentaje_cal = min(porcentaje_cal, 100)

    porcentaje_prot = int((proteina_consumida / proteina_objetivo) * 100) if proteina_objetivo > 0 else 0
    porcentaje_prot = min(porcentaje_prot, 100)

    historial = datos.get("historial_comidas", [])
    comidas_hoy = len(historial)
    carbohidratos = sum(int(item.get("carbohidratos", 0) or 0) for item in historial)
    grasas = sum(int(item.get("grasas", 0) or 0) for item in historial)
    fibra = sum(int(item.get("fibra", 0) or 0) for item in historial)
    azucar = sum(int(item.get("azucar", 0) or 0) for item in historial)

    if porcentaje_cal < 35:
        siguiente_paso = "Te falta energía para el día. Considera una comida completa con proteína."
    elif porcentaje_cal <= 85:
        siguiente_paso = "Vas en buen ritmo. Mantén porciones equilibradas y toma agua."
    else:
        siguiente_paso = "Ya estás cerca de tu meta calórica. Elige algo ligero si tienes hambre."

    return f"""
    <section class="progress-detail-card">
        <h2>Progreso diario</h2>
        <p class="progress-lead">Resumen de tus metas de hoy según lo que has registrado.</p>

        <div class="progress-metric">
            <div class="progress-metric-header">
                <strong>Calorías</strong>
                <span>{consumido} / {total} kcal · {porcentaje_cal}%</span>
            </div>
            <div class="progress-detail-track"><span style="--value: {porcentaje_cal}%;"></span></div>
        </div>

        <div class="progress-metric">
            <div class="progress-metric-header">
                <strong>Proteína</strong>
                <span>{proteina_consumida} / {proteina_objetivo} g · {porcentaje_prot}%</span>
            </div>
            <div class="progress-detail-track"><span style="--value: {porcentaje_prot}%;"></span></div>
        </div>

        <div class="macro-grid">
            <div class="macro-tile"><strong>{carbohidratos} g</strong><span>Carbohidratos</span></div>
            <div class="macro-tile"><strong>{grasas} g</strong><span>Grasas</span></div>
            <div class="macro-tile"><strong>{fibra} g</strong><span>Fibra</span></div>
            <div class="macro-tile"><strong>{azucar} g</strong><span>Azúcar aprox.</span></div>
        </div>

        <div class="next-step-card">
            <strong>Comidas registradas:</strong> {comidas_hoy}<br>
            <strong>Siguiente paso:</strong> {siguiente_paso}
        </div>
    </section>
    """


# =========================
# PLAN PERSONALIZADO
# =========================

def generar_plan_personalizado():
    datos, error = asegurar_usuario()
    if error:
        return error

    perfil = datos.get("perfil", {})
    if not perfil:
        return " Primero guarda tus datos personales para generar tu plan."

    contexto = contexto_usuario_para_ia(datos)
    respuesta_ia = llamar_ia_texto(
        prompt_base_nutricion(),
        f"""
Genera un plan personalizado de alimentación para hoy.
Debe incluir:
- 3 opciones de desayuno.
- 3 opciones de comida.
- 3 opciones de cena.
- 2 snacks o postres opcionales, saludables y realistas.
- Ajustes importantes por alergias, condición o gustos.
- Meta aproximada del día.

Datos del usuario:
{json.dumps(contexto, ensure_ascii=False, indent=2)}

Formato:
## Plan personalizado sugerido para hoy
### Desayuno
1. ...
2. ...
3. ...
### Comida
1. ...
2. ...
3. ...
### Cena
1. ...
2. ...
3. ...
### Snacks o postres opcionales
1. ...
2. ...
### Meta de hoy
...
### Ajustes importantes
...
""".strip(),
        temperature=0.58,
        max_tokens=720,
    )
    if respuesta_ia:
        return limpiar_markdown_ia(respuesta_ia)

    meta = str(perfil.get("meta", "")).lower()
    condicion = str(perfil.get("condicion", "")).lower()
    alergias = str(perfil.get("alergias", "")).lower()
    gustos = str(perfil.get("gustos", "")).strip()
    no_gusta = str(perfil.get("no_gusta", "")).strip()
    rutina = str(perfil.get("rutina", "")).strip()
    proteina_objetivo = datos.get("proteina_objetivo", 0)

    desayuno = " **Desayuno:** yogurt natural con fruta y avena."
    comida = " **Comida:** pollo a la plancha con arroz y verduras."
    cena = " **Cena:** ensalada con proteína ligera y una tostada o pan integral."
    snack = " **Snack:** fruta, nueces o yogurt."

    if "bajar" in meta:
        desayuno = " **Desayuno:** huevo con verduras y una porción pequeña de avena."
        comida = " **Comida:** pollo, atún o carne magra con ensalada y arroz moderado."
        cena = " **Cena:** ensalada grande con proteína ligera."
        snack = " **Snack:** pepino, manzana o yogurt griego."
    elif "subir" in meta:
        desayuno = " **Desayuno:** huevos, pan integral, fruta y yogurt."
        comida = " **Comida:** pollo o carne con arroz, aguacate y verduras."
        cena = " **Cena:** sándwich o bowl completo con proteína."
        snack = " **Snack:** plátano con crema de cacahuate o yogurt con granola."
    elif "mantener" in meta:
        desayuno = " **Desayuno:** yogurt con fruta y avena o huevos con pan integral."
        comida = " **Comida:** plato equilibrado con proteína, arroz o pasta y verduras."
        cena = " **Cena:** opción ligera pero completa con proteína."
        snack = " **Snack:** fruta, nueces o yogurt."

    ajustes = []

    if "lactosa" in condicion:
        ajustes.append(" Ajuste: usa productos sin lactosa o bebidas vegetales.")
    if "gluten" in condicion or "celia" in condicion:
        ajustes.append(" Ajuste: evita pan o avena con gluten; usa arroz, quinoa o tortilla de maíz.")
    if "diabet" in condicion:
        ajustes.append(" Ajuste: prioriza fibra y controla porciones de carbohidratos simples.")
    if "hipertens" in condicion:
        ajustes.append(" Ajuste: reduce sal y ultraprocesados.")
    if alergias:
        ajustes.append(f" Alergias a considerar: {alergias}.")
    if gustos:
        ajustes.append(f" Personalización por gustos: intenta incluir opciones que sí disfrutas, como {gustos}.")
    if no_gusta:
        ajustes.append(f" Evita o cambia lo que no te gusta: {no_gusta}.")
    if rutina:
        ajustes.append(f" Rutina registrada: {rutina}. Ajusta horarios y porciones para que el plan sea realista.")

    texto = (
        f" **Plan personalizado sugerido para hoy**\n\n"
        f"Basado en tu meta, gustos y rutina.\n\n"
        f"{desayuno}\n\n"
        f"{comida}\n\n"
        f"{cena}\n\n"
        f"{snack}\n\n"
        f" Tu meta aproximada de proteína hoy es **{proteina_objetivo} g**.\n\n"
        f"{sugerencia_por_hora()}"
    )

    if ajustes:
        texto += "\n\n" + "\n".join(ajustes)

    return texto


def generar_plan_de_comida(tipo_comida):
    datos, error = asegurar_usuario()
    if error:
        return error

    perfil = datos.get("perfil", {})
    if not perfil:
        return "Primero guarda tus datos personales en Perfil para que Nutribot pueda hacer un plan real para ti."

    meta = str(perfil.get("meta", "")).lower()
    condicion = str(perfil.get("condicion", "")).lower()
    alergias = str(perfil.get("alergias", "")).strip()
    gustos = str(perfil.get("gustos", "")).strip()
    no_gusta = str(perfil.get("no_gusta", "")).strip()
    rutina = str(perfil.get("rutina", "")).strip()

    calorias_totales = int(datos.get("calorias_totales", 0) or 0)
    calorias_restantes = int(datos.get("calorias_restantes", calorias_totales) or 0)
    proteina_objetivo = int(datos.get("proteina_objetivo", 0) or 0)
    proteina_consumida = int(datos.get("proteina_consumida", 0) or 0)
    proteina_restante = max(proteina_objetivo - proteina_consumida, 0)

    distribucion = {
        "Desayuno": (0.25, 0.25),
        "Comida": (0.40, 0.40),
        "Cena": (0.25, 0.25),
    }
    porc_cal, porc_prot = distribucion.get(tipo_comida, (0.30, 0.30))
    kcal_objetivo = round(calorias_totales * porc_cal) if calorias_totales else 0
    prot_objetivo = round(proteina_objetivo * porc_prot) if proteina_objetivo else 0

    respuesta_ia = None
    if os.getenv("NUTRIBOT_PLAN_IA", "").strip().lower() in {"1", "true", "yes", "si", "sí"}:
        contexto = contexto_usuario_para_ia(datos)
        respuesta_ia = llamar_ia_texto(
            prompt_base_nutricion(),
            f"""
Genera recomendaciones para la comida: {tipo_comida}.

Necesito que regreses al menos 3 opciones distintas y no repetidas.
Cada opción debe tener:
- Nombre corto.
- Ingredientes principales.
- Porción aproximada.
- Calorías aproximadas.
- Proteína aproximada.
- Por qué le conviene al usuario.

Si es Desayuno o Comida, agrega también 2 opciones de postre o antojo saludable.
Si es Cena, agrega 2 opciones ligeras si la persona no tiene mucha hambre.

Datos del usuario:
{json.dumps(contexto, ensure_ascii=False, indent=2)}

Objetivo para esta comida:
- Calorías aproximadas: {kcal_objetivo} kcal.
- Proteína aproximada: {prot_objetivo} g.
- Calorías restantes del día: {calorias_restantes} kcal.
- Proteína restante del día: {proteina_restante} g.

Formato exacto:
## Plan de {tipo_comida.lower()}
### Opciones recomendadas
1. **Nombre**: ingredientes. Porción: ... Calorías: ... Proteína: ... Motivo: ...
2. **Nombre**: ...
3. **Nombre**: ...
### Extra opcional
1. ...
2. ...
### Meta para esta comida
...
### Ajustes importantes
...
""".strip(),
            temperature=0.62,
            max_tokens=720,
        )
    if respuesta_ia:
        return limpiar_markdown_ia(respuesta_ia)

    planes = {
        "Desayuno": {
            "base": [
                ("Avena cremosa con fruta", "Avena con yogurt natural, fresas o plátano y nueces.", "350-430 kcal", "18-25 g"),
                ("Huevos con tortilla y fruta", "Huevos con verduras, tortilla de maíz y fruta fresca.", "330-420 kcal", "20-28 g"),
                ("Yogurt alto en proteína", "Yogurt griego con granola moderada, fruta y semillas.", "300-390 kcal", "20-30 g"),
                ("Mollete ligero", "Bolillo integral o pan tostado con frijoles, queso panela y pico de gallo.", "360-460 kcal", "18-26 g"),
                ("Smoothie completo", "Leche o bebida vegetal, plátano, avena, yogurt griego y canela.", "380-500 kcal", "20-30 g"),
            ],
            "bajar": [
                ("Huevos con verduras", "Huevos con espinaca o calabacita, tortilla de maíz y fruta.", "300-380 kcal", "20-26 g"),
                ("Yogurt con frutos rojos", "Yogurt natural sin azúcar con fresas y chía.", "260-340 kcal", "18-25 g"),
                ("Tostada ligera", "Tostada horneada con aguacate, huevo y pico de gallo.", "320-400 kcal", "18-24 g"),
                ("Avena chica con proteína", "1/3 taza de avena con yogurt natural, fresas y canela.", "280-360 kcal", "18-24 g"),
                ("Tacos de huevo", "2 tortillas de maíz con huevo revuelto, nopales o espinaca y salsa.", "310-390 kcal", "20-28 g"),
            ],
            "subir": [
                ("Desayuno completo", "Huevos, pan integral, yogurt con fruta y crema de cacahuate.", "520-680 kcal", "28-40 g"),
                ("Avena energética", "Avena con leche, plátano, nueces y yogurt griego.", "500-650 kcal", "25-35 g"),
                ("Sándwich mañanero", "Pan integral con huevo, queso o pavo, fruta y yogurt.", "520-700 kcal", "30-42 g"),
                ("Hotcakes de avena", "Hotcakes de avena con huevo, plátano, yogurt griego y nueces.", "520-680 kcal", "25-38 g"),
                ("Burrito de desayuno", "Tortilla grande con huevo, frijoles, queso panela, aguacate y salsa.", "560-720 kcal", "30-42 g"),
            ],
            "mantener": [
                ("Yogurt con avena", "Yogurt natural con fruta, avena y semillas.", "350-450 kcal", "20-30 g"),
                ("Huevos con pan integral", "Huevos con verduras y una rebanada de pan integral.", "360-460 kcal", "22-30 g"),
                ("Licuado equilibrado", "Leche o bebida vegetal, fruta, avena y proteína natural como yogurt.", "380-500 kcal", "18-28 g"),
                ("Tostadas de aguacate y huevo", "2 tostadas horneadas con aguacate, huevo cocido, tomate y salsa.", "360-470 kcal", "20-30 g"),
                ("Quesadilla con fruta", "2 tortillas de maíz con queso panela, pico de gallo y una fruta.", "350-460 kcal", "18-28 g"),
            ],
            "ligero": "Si tienes poca hambre: yogurt griego con fruta y semillas.",
        },
        "Comida": {
            "base": [
                ("Bowl equilibrado", "Pollo, arroz o pasta, verduras y aguacate.", "550-750 kcal", "35-50 g"),
                ("Tacos completos", "Tortillas de maíz con carne magra, frijoles, verduras y salsa.", "520-720 kcal", "32-48 g"),
                ("Ensalada fuerte", "Ensalada con atún, pollo o huevo, garbanzos y aceite de oliva moderado.", "480-650 kcal", "30-45 g"),
                ("Pasta con pollo", "Pasta integral con pollo, calabacita, tomate y un poco de queso.", "560-740 kcal", "35-50 g"),
                ("Tostadas de atún", "2 o 3 tostadas horneadas con atún, aguacate, verduras y salsa.", "480-650 kcal", "32-46 g"),
            ],
            "bajar": [
                ("Plato magro", "Proteína magra, ensalada grande, arroz moderado y agua natural.", "430-600 kcal", "35-50 g"),
                ("Tazón fresco", "Atún o pollo con verduras, frijoles y aguacate moderado.", "450-620 kcal", "32-46 g"),
                ("Fajitas ligeras", "Fajitas de pollo con verduras y tortillas de maíz.", "460-620 kcal", "35-48 g"),
                ("Ensalada de atún completa", "Atún en agua, lechuga, pepino, tomate, 1/2 taza de frijoles y tostada horneada.", "420-560 kcal", "34-46 g"),
                ("Pollo con nopales", "120 g de pollo, nopales, pico de gallo, 2 tortillas y aguacate moderado.", "440-600 kcal", "36-50 g"),
            ],
            "subir": [
                ("Comida completa", "Pollo o carne con arroz, frijoles, aguacate y verduras.", "700-900 kcal", "45-65 g"),
                ("Bowl alto en energía", "Arroz, pollo, frijoles, queso moderado, aguacate y verduras.", "750-950 kcal", "45-65 g"),
                ("Pasta con proteína", "Pasta con pollo o atún, verduras y aceite de oliva moderado.", "700-900 kcal", "40-58 g"),
                ("Burrito completo", "Tortilla grande con carne o pollo, arroz, frijoles, queso, aguacate y verduras.", "760-980 kcal", "45-65 g"),
                ("Papa rellena", "Papa grande con pollo, queso panela, frijoles y verduras.", "700-900 kcal", "40-58 g"),
            ],
            "mantener": [
                ("Bowl de pollo con arroz", "120 g de pechuga de pollo, 3/4 taza de arroz, calabacita, zanahoria y 1/4 de aguacate.", "560-680 kcal", "38-48 g"),
                ("Plato mexicano balanceado", "2 tortillas de maíz, 1/2 taza de frijoles, 100 g de pollo o 2 huevos, ensalada de lechuga con pico de gallo.", "520-660 kcal", "32-44 g"),
                ("Wrap integral de pollo", "Tortilla integral grande con 100 g de pollo, espinaca, pepino, tomate, aguacate y aderezo de yogurt natural.", "500-640 kcal", "34-45 g"),
                ("Tacos de carne asada balanceados", "3 tortillas de maíz con carne magra, pico de gallo, guacamole moderado y frijoles.", "560-700 kcal", "35-50 g"),
                ("Bowl de atún y garbanzos", "Atún, 1/2 taza de garbanzos, pepino, tomate, arroz moderado y limón.", "500-660 kcal", "34-48 g"),
            ],
            "ligero": "Si quieres algo más ligero: ensalada completa con atún, pollo o huevo.",
        },
        "Cena": {
            "base": [
                ("Cena ligera completa", "100 g de pollo, atún o queso panela con verduras salteadas y 1 tortilla o 1/2 taza de arroz.", "350-520 kcal", "25-38 g"),
                ("Omelette con verduras", "Huevo con verduras y una tostada o tortilla.", "320-470 kcal", "22-34 g"),
                ("Bowl pequeño", "Pollo, atún o tofu con verduras y arroz moderado.", "380-540 kcal", "28-40 g"),
                ("Tostadas de pollo", "2 tostadas horneadas con pollo deshebrado, lechuga, salsa y aguacate moderado.", "360-500 kcal", "28-40 g"),
                ("Sopa con quesadilla", "Sopa de verduras con una quesadilla de queso panela o pollo.", "350-520 kcal", "22-35 g"),
            ],
            "bajar": [
                ("Ensalada con proteína", "Ensalada grande con pollo, atún o huevo y tostada horneada.", "320-460 kcal", "28-40 g"),
                ("Sopa con proteína", "Sopa de verduras con pollo o queso panela.", "280-420 kcal", "22-34 g"),
                ("Tacos ligeros", "Tacos de lechuga o maíz con pollo y verduras.", "330-470 kcal", "28-38 g"),
                ("Omelette ligero", "2 huevos o 1 huevo con claras, champiñones, espinaca y salsa.", "280-400 kcal", "22-34 g"),
                ("Atún con pepino", "Atún con pepino, tomate, limón, aguacate moderado y 1 tostada horneada.", "300-440 kcal", "28-38 g"),
            ],
            "subir": [
                ("Sándwich integral", "2 panes integrales con pavo o pollo, queso panela, aguacate, lechuga y tomate, más yogurt o fruta.", "480-650 kcal", "28-42 g"),
                ("Bowl nocturno", "Arroz o papa con pollo, verduras y aguacate.", "520-700 kcal", "35-50 g"),
                ("Quesadilla completa", "Tortillas con queso, pollo o frijoles y pico de gallo.", "480-650 kcal", "28-40 g"),
                ("Tacos de pollo con frijoles", "3 tortillas con pollo, frijoles, queso panela y salsa.", "500-680 kcal", "34-48 g"),
                ("Avena nocturna", "Avena con leche, yogurt griego, plátano y nueces en porción moderada.", "480-650 kcal", "24-36 g"),
            ],
            "mantener": [
                ("Omelette con verduras", "2 huevos con champiñones, espinaca y tomate, más 1 tortilla de maíz o tostada horneada.", "350-520 kcal", "25-38 g"),
                ("Tostadas saludables", "Tostadas horneadas con atún, aguacate moderado y verduras.", "380-540 kcal", "28-40 g"),
                ("Yogurt salado o dulce", "Yogurt griego con fruta si quieres algo ligero, o con pepino y tostada.", "300-460 kcal", "20-32 g"),
                ("Quesadillas ligeras", "2 tortillas de maíz con queso panela, champiñones y pico de gallo.", "360-500 kcal", "22-34 g"),
                ("Sopa de pollo", "Caldo de pollo con verduras, pollo deshebrado y 1 tortilla o arroz moderado.", "350-520 kcal", "28-42 g"),
            ],
            "ligero": "Si ya comiste suficiente: sopa de verduras con proteína ligera.",
        },
    }

    opciones = planes.get(tipo_comida, planes["Comida"])
    if "bajar" in meta:
        recomendaciones = opciones["bajar"]
    elif "subir" in meta:
        recomendaciones = opciones["subir"]
    elif "mantener" in meta:
        recomendaciones = opciones["mantener"]
    else:
        recomendaciones = opciones["base"]

    recomendaciones = recomendaciones[:]
    random.shuffle(recomendaciones)
    recomendaciones = recomendaciones[:3]

    extra_dulce = ""
    extra_titulo = ""
    extra_rango = ""
    if tipo_comida == "Desayuno":
        extra_titulo = "Opción dulce"
        extra_rango = "80 a 150 kcal"
        if "diabet" in condicion:
            extra_dulce = "Fresas con yogurt natural sin azúcar, o manzana con canela."
        elif "lactosa" in condicion:
            extra_dulce = "Fruta fresca con nueces, o pan integral con un toque de crema de cacahuate."
        elif "bajar" in meta:
            extra_dulce = "Fruta fresca, yogurt griego natural o avena con canela."
        elif "subir" in meta:
            extra_dulce = "Plátano con crema de cacahuate, yogurt con granola o pan integral con miel."
        else:
            extra_dulce = "Fruta con yogurt, avena con canela o un mini hotcake de avena."
    elif tipo_comida == "Comida":
        extra_titulo = "Postre opcional"
        extra_rango = "100 a 180 kcal"
        if "diabet" in condicion:
            extra_dulce = "Yogurt natural sin azúcar con fresas, o una manzana con canela."
        elif "lactosa" in condicion:
            extra_dulce = "Fruta fresca con crema de cacahuate o yogurt sin lactosa."
        elif "bajar" in meta:
            extra_dulce = "Fruta fresca, gelatina sin azúcar o yogurt griego natural."
        elif "subir" in meta:
            extra_dulce = "Plátano con crema de cacahuate, yogurt con granola o arroz con leche en porción pequeña."
        else:
            extra_dulce = "Fresas con yogurt, fruta con nueces o un postre casero en porción pequeña."

    ajustes = []
    condicion_l = condicion.lower()
    if "lactosa" in condicion_l:
        ajustes.append("Usa opción sin lactosa o bebida vegetal.")
    if "gluten" in condicion_l or "celia" in condicion_l:
        ajustes.append("Evita pan/avena con gluten; usa maíz, arroz o quinoa.")
    if "diabet" in condicion_l:
        ajustes.append("Prioriza fibra y evita bebidas azucaradas.")
    if "hipertens" in condicion_l:
        ajustes.append("Cuida la sal y evita ultraprocesados.")
    if alergias:
        ajustes.append(f"Evita tus alergias registradas: {alergias}.")
    if no_gusta:
        ajustes.append(f"Si incluye algo que no te gusta, cámbialo por algo equivalente. Evitar: {no_gusta}.")

    personal = []
    if gustos:
        personal.append(f"Puede adaptarse con alimentos que te gustan: {gustos}.")
    if rutina:
        personal.append(f"Toma en cuenta tu rutina: {rutina}.")

    progreso = dashboard_progreso_usuario()
    extra_texto = (
        f"**{extra_titulo}:** {extra_dulce}\n\n"
        f"Para que siga dentro de tu meta, procura que sea una porción pequeña de **{extra_rango}**.\n\n"
        if extra_dulce else ""
    )
    extra_bloque = f"### Extra opcional\n{extra_texto}" if extra_texto else ""
    opciones_txt = ""
    for i, (nombre, desc, kcal, prot) in enumerate(recomendaciones, 1):
        opciones_txt += (
            f"{i}. **{nombre}**\n"
            f"   - Ingredientes: {desc}\n"
            f"   - Estimación: {kcal} y {prot} de proteína.\n"
        )

    return (
        f"## Plan de {tipo_comida.lower()}\n\n"
        f"### Opciones recomendadas\n"
        f"{opciones_txt}\n"
        f"{extra_bloque}"
        f"### Meta para esta comida\n"
        f"Aproximadamente **{kcal_objetivo} kcal** y **{prot_objetivo} g de proteína**.\n\n"
        f"### Tu avance de hoy\n"
        f"- Meta diaria: **{calorias_totales} kcal** y **{proteina_objetivo} g de proteína**.\n"
        f"- Te queda: **{calorias_restantes} kcal** y **{proteina_restante} g de proteína**.\n"
        f"- Progreso: **{progreso['detalle']}** - {progreso['texto']}\n\n"
        + ("### Personalización\n" + "\n".join(f"- {item}" for item in personal) + "\n\n" if personal else "")
        + ("### Ajustes importantes\n" + "\n".join(f"- {item}" for item in ajustes) if ajustes else "Este plan es orientativo y puedes ajustar porciones según tu hambre.")
    )


def mostrar_plan_de_comida(tipo_comida):
    return gr.update(value=generar_plan_de_comida(tipo_comida), visible=True)


def alternar_plan_de_comida(tipo_comida, plan_actual):
    if plan_actual == tipo_comida:
        return gr.update(value="", visible=False), ""

    return gr.update(value=generar_plan_de_comida(tipo_comida), visible=True), tipo_comida


def alternar_registro_inicio(abierto):
    nuevo_estado = not bool(abierto)
    return (
        dashboard_intro_html(nuevo_estado),
        texto_boton_registro_inicio(nuevo_estado),
        gr.update(value="‹" if nuevo_estado else "›"),
        gr.update(visible=nuevo_estado),
        gr.update(visible=not nuevo_estado),
        nuevo_estado,
    )


# =========================
# COMIDAS
# =========================

ALIMENTOS_FOTO = [
    {
        "label": "banana",
        "nombre": "Plátano",
        "aliases": ["banana", "bananas", "plantain", "plantains", "platano", "plátano", "platanos", "plátanos"],
        "calorias": 105,
        "proteina": 1,
        "tipo": "ligera",
        "porcion": "1 pieza mediana"
    },
    {
        "label": "apple",
        "nombre": "Manzana",
        "aliases": ["apple", "manzana"],
        "calorias": 95,
        "proteina": 0,
        "tipo": "ligera",
        "porcion": "1 pieza mediana"
    },
    {
        "label": "fruit salad",
        "nombre": "Fruta",
        "aliases": ["fruit", "fruta", "fruit salad", "frutas"],
        "calorias": 180,
        "proteina": 2,
        "tipo": "ligera",
        "porcion": "1 taza"
    },
    {
        "label": "yogurt",
        "nombre": "Yogurt con fruta",
        "aliases": ["yogurt", "yoghurt", "yogur"],
        "calorias": 220,
        "proteina": 12,
        "tipo": "ligera",
        "porcion": "1 bowl"
    },
    {
        "label": "chicken salad",
        "nombre": "Ensalada de pollo",
        "aliases": ["chicken salad", "salad", "ensalada", "ensalada de pollo"],
        "calorias": 350,
        "proteina": 30,
        "tipo": "ligera",
        "porcion": "1 plato"
    },
    {
        "label": "rice with chicken",
        "nombre": "Pollo con arroz",
        "aliases": ["rice with chicken", "chicken and rice", "pollo con arroz", "arroz con pollo"],
        "calorias": 520,
        "proteina": 35,
        "tipo": "fuerte",
        "porcion": "1 plato"
    },
    {
        "label": "taco",
        "nombre": "Taco",
        "aliases": ["taco", "tacos"],
        "calorias": 250,
        "proteina": 15,
        "tipo": "moderada",
        "porcion": "1 taco"
    },
    {
        "label": "pizza",
        "nombre": "Pizza",
        "aliases": ["pizza"],
        "calorias": 285,
        "proteina": 12,
        "tipo": "fuerte",
        "porcion": "1 rebanada"
    },
    {
        "label": "hamburger and fries",
        "nombre": "Hamburguesa con papas",
        "aliases": ["hamburger", "burger", "fries", "papas", "hamburguesa"],
        "calorias": 800,
        "proteina": 28,
        "tipo": "fuerte",
        "porcion": "1 combo"
    },
    {
        "label": "pasta",
        "nombre": "Pasta",
        "aliases": ["pasta", "spaghetti", "espagueti"],
        "calorias": 420,
        "proteina": 14,
        "tipo": "fuerte",
        "porcion": "1 plato"
    },
    {
        "label": "sushi",
        "nombre": "Sushi",
        "aliases": ["sushi"],
        "calorias": 450,
        "proteina": 18,
        "tipo": "moderada",
        "porcion": "1 rollo"
    },
    {
        "label": "eggs",
        "nombre": "Huevo",
        "aliases": ["egg", "eggs", "huevo", "huevos"],
        "calorias": 155,
        "proteina": 13,
        "tipo": "moderada",
        "porcion": "2 huevos"
    },
    {
        "label": "sandwich",
        "nombre": "Sándwich",
        "aliases": ["sandwich", "sándwich", "torta"],
        "calorias": 380,
        "proteina": 18,
        "tipo": "moderada",
        "porcion": "1 pieza"
    },
    {
        "label": "soup",
        "nombre": "Sopa",
        "aliases": ["soup", "sopa", "caldo"],
        "calorias": 220,
        "proteina": 10,
        "tipo": "ligera",
        "porcion": "1 plato"
    },
    {
        "label": "beans",
        "nombre": "Frijoles",
        "aliases": ["beans", "frijoles"],
        "calorias": 240,
        "proteina": 15,
        "tipo": "moderada",
        "porcion": "1 taza"
    },
    {
        "label": "fish",
        "nombre": "Pescado",
        "aliases": ["fish", "pescado"],
        "calorias": 280,
        "proteina": 32,
        "tipo": "moderada",
        "porcion": "1 filete"
    },
    {
        "label": "rice",
        "nombre": "Arroz",
        "aliases": ["rice", "arroz"],
        "calorias": 205,
        "proteina": 4,
        "tipo": "moderada",
        "porcion": "1 taza cocida"
    },
    {
        "label": "bread",
        "nombre": "Pan",
        "aliases": ["bread", "pan", "toast", "tostada"],
        "calorias": 80,
        "proteina": 3,
        "tipo": "ligera",
        "porcion": "1 rebanada"
    },
    {
        "label": "tortilla",
        "nombre": "Tortilla",
        "aliases": ["tortilla", "tortillas"],
        "calorias": 65,
        "proteina": 2,
        "tipo": "ligera",
        "porcion": "1 pieza"
    },
    {
        "label": "avocado",
        "nombre": "Aguacate",
        "aliases": ["avocado", "aguacate"],
        "calorias": 120,
        "proteina": 2,
        "tipo": "moderada",
        "porcion": "1/2 pieza"
    },
    {
        "label": "cheese",
        "nombre": "Queso",
        "aliases": ["cheese", "queso"],
        "calorias": 110,
        "proteina": 7,
        "tipo": "moderada",
        "porcion": "30 g"
    },
    {
        "label": "milk",
        "nombre": "Leche",
        "aliases": ["milk", "leche"],
        "calorias": 120,
        "proteina": 8,
        "tipo": "ligera",
        "porcion": "1 vaso"
    },
    {
        "label": "beef",
        "nombre": "Carne de res",
        "aliases": ["beef", "steak", "carne", "res"],
        "calorias": 300,
        "proteina": 28,
        "tipo": "fuerte",
        "porcion": "120 g"
    },
    {
        "label": "potato",
        "nombre": "Papa",
        "aliases": ["potato", "potatoes", "papa", "papas"],
        "calorias": 160,
        "proteina": 4,
        "tipo": "moderada",
        "porcion": "1 pieza mediana"
    },
    {
        "label": "vegetables",
        "nombre": "Verduras",
        "aliases": ["vegetables", "vegetable", "verduras", "vegetales"],
        "calorias": 80,
        "proteina": 3,
        "tipo": "ligera",
        "porcion": "1 taza"
    },
    {
        "label": "orange",
        "nombre": "Naranja",
        "aliases": ["orange", "naranja"],
        "calorias": 62,
        "proteina": 1,
        "tipo": "ligera",
        "porcion": "1 pieza"
    },
    {
        "label": "strawberries",
        "nombre": "Fresas",
        "aliases": ["strawberry", "strawberries", "fresas", "fresa"],
        "calorias": 50,
        "proteina": 1,
        "tipo": "ligera",
        "porcion": "1 taza"
    }
]


NUTRIENTES_EXTRA = {
    "banana": {"carbohidratos": 27, "grasas": 0, "fibra": 3, "azucar": 14, "ingredientes": "plátano"},
    "apple": {"carbohidratos": 25, "grasas": 0, "fibra": 4, "azucar": 19, "ingredientes": "manzana"},
    "fruit salad": {"carbohidratos": 45, "grasas": 1, "fibra": 5, "azucar": 32, "ingredientes": "fruta variada"},
    "yogurt": {"carbohidratos": 26, "grasas": 4, "fibra": 2, "azucar": 18, "ingredientes": "yogurt y fruta"},
    "chicken salad": {"carbohidratos": 14, "grasas": 16, "fibra": 5, "azucar": 5, "ingredientes": "pollo, verduras y aderezo"},
    "rice with chicken": {"carbohidratos": 55, "grasas": 12, "fibra": 3, "azucar": 2, "ingredientes": "pollo, arroz y verduras"},
    "taco": {"carbohidratos": 24, "grasas": 10, "fibra": 3, "azucar": 2, "ingredientes": "tortilla, carne o guiso y salsa"},
    "pizza": {"carbohidratos": 36, "grasas": 10, "fibra": 2, "azucar": 4, "ingredientes": "masa, queso, salsa y toppings"},
    "hamburger and fries": {"carbohidratos": 85, "grasas": 35, "fibra": 7, "azucar": 9, "ingredientes": "pan, carne, papas y salsas"},
    "pasta": {"carbohidratos": 75, "grasas": 8, "fibra": 4, "azucar": 5, "ingredientes": "pasta y salsa"},
    "sushi": {"carbohidratos": 60, "grasas": 8, "fibra": 3, "azucar": 8, "ingredientes": "arroz, alga, pescado o vegetales"},
    "eggs": {"carbohidratos": 1, "grasas": 11, "fibra": 0, "azucar": 1, "ingredientes": "huevo"},
    "sandwich": {"carbohidratos": 42, "grasas": 14, "fibra": 4, "azucar": 6, "ingredientes": "pan, proteína, verduras y aderezo"},
    "soup": {"carbohidratos": 22, "grasas": 7, "fibra": 4, "azucar": 4, "ingredientes": "caldo, verduras y proteína variable"},
    "beans": {"carbohidratos": 44, "grasas": 1, "fibra": 15, "azucar": 1, "ingredientes": "frijoles"},
    "fish": {"carbohidratos": 0, "grasas": 12, "fibra": 0, "azucar": 0, "ingredientes": "pescado"},
    "rice": {"carbohidratos": 45, "grasas": 0, "fibra": 1, "azucar": 0, "ingredientes": "arroz"},
    "bread": {"carbohidratos": 15, "grasas": 1, "fibra": 1, "azucar": 2, "ingredientes": "pan"},
    "tortilla": {"carbohidratos": 13, "grasas": 1, "fibra": 2, "azucar": 0, "ingredientes": "maíz o harina"},
    "avocado": {"carbohidratos": 6, "grasas": 11, "fibra": 5, "azucar": 0, "ingredientes": "aguacate"},
    "cheese": {"carbohidratos": 1, "grasas": 9, "fibra": 0, "azucar": 0, "ingredientes": "queso"},
    "milk": {"carbohidratos": 12, "grasas": 5, "fibra": 0, "azucar": 12, "ingredientes": "leche"},
    "beef": {"carbohidratos": 0, "grasas": 20, "fibra": 0, "azucar": 0, "ingredientes": "carne de res"},
    "potato": {"carbohidratos": 37, "grasas": 0, "fibra": 4, "azucar": 2, "ingredientes": "papa"},
    "vegetables": {"carbohidratos": 16, "grasas": 1, "fibra": 6, "azucar": 5, "ingredientes": "verduras variadas"},
    "orange": {"carbohidratos": 15, "grasas": 0, "fibra": 3, "azucar": 12, "ingredientes": "naranja"},
    "strawberries": {"carbohidratos": 12, "grasas": 0, "fibra": 3, "azucar": 7, "ingredientes": "fresas"},
}


def buscar_alimento_por_texto(texto):
    texto = (texto or "").lower()
    for alimento in ALIMENTOS_FOTO:
        if any(alias in texto for alias in alimento["aliases"]):
            return alimento
    return None


def nutrientes_extra(alimento, cantidad):
    base = NUTRIENTES_EXTRA.get(alimento["label"], {})
    return {
        "carbohidratos": int(base.get("carbohidratos", 0) * cantidad),
        "grasas": int(base.get("grasas", 0) * cantidad),
        "fibra": int(base.get("fibra", 0) * cantidad),
        "azucar": int(base.get("azucar", 0) * cantidad),
        "ingredientes": base.get("ingredientes", alimento["nombre"].lower()),
    }


def imagen_a_data_url(imagen):
    path = Path(imagen)
    mime = "image/png"
    if path.suffix.lower() in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif path.suffix.lower() == ".webp":
        mime = "image/webp"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def limpiar_json_respuesta(texto):
    texto = (texto or "").strip()
    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.lower().startswith("json"):
            texto = texto[4:].strip()
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio != -1 and fin != -1 and fin > inicio:
        texto = texto[inicio:fin + 1]
    return json.loads(texto)


def numero_seguro(valor, default=0):
    try:
        return int(round(float(valor)))
    except (TypeError, ValueError):
        return default


def etiqueta_seguridad(valor):
    confianza = numero_seguro(valor, 65)
    if confianza <= 0:
        return "Estimación visual aproximada"
    if confianza < 45:
        return "Estimación visual con seguridad baja"
    if confianza < 75:
        return "Estimación visual con seguridad media"
    return "Estimación visual con seguridad alta"


def normalizar_tipo(tipo):
    tipo = str(tipo or "moderada").lower().strip()
    if tipo not in ["ligera", "moderada", "fuerte"]:
        return "moderada"
    return tipo


def analizar_comida_con_ia_avanzada(imagen):
    token = obtener_hf_token()
    if not token:
        return None, "No hay token de Hugging Face configurado para usar la IA visual avanzada."

    prompt = """
Analiza la foto de comida como nutriólogo visual especializado en alimentos caseros y mexicanos.
Primero identifica lo visible: fruta, verduras, carnes, lácteos, pan, tortillas, arroz, pasta, frijoles, salsas, cremas, bebidas, postres, congelados, toppings y forma de preparación.
No fuerces un platillo común si la imagen solo muestra ingredientes simples. Por ejemplo: si ves plátanos, fresas con crema, fruta congelada o un licuado, nómbralo así y no lo cambies por ensalada, pollo o comida salada.
Si hay dudas entre varias comidas, elige la más probable y explica brevemente la incertidumbre en notas.
No inventes ingredientes invisibles. Solo agrega ingredientes "posibles" cuando sean muy probables por la preparación.
Estima porciones y nutrientes aproximados para la comida completa.
Usa rangos razonables mentalmente, pero responde con un solo estimado central realista.
La confianza debe reflejar la calidad de la foto: 80-95 si se ve muy claro, 55-79 si se ve razonable, 25-54 si está borroso, cortado o con ingredientes ocultos.
Responde SOLO en JSON válido, sin markdown, con esta estructura:
{
  "nombre": "nombre breve de la comida",
  "ingredientes": ["ingrediente 1", "ingrediente 2"],
  "preparacion": "crudo|cocido|frito|horneado|licuado|con crema|congelado|desconocida",
  "porcion": "porción estimada",
  "calorias": 0,
  "proteina": 0,
  "carbohidratos": 0,
  "grasas": 0,
  "fibra": 0,
  "azucar": 0,
  "tipo": "ligera|moderada|fuerte",
  "confianza": 0,
  "notas": "breve nota sobre incertidumbre o factores que pueden cambiar los nutrientes"
}
Todos los nutrientes son gramos excepto calorías. Responde en español.
""".strip()

    try:
        client = InferenceClient(provider="auto", token=token, timeout=30)
        completion = client.chat.completions.create(
            model="CohereLabs/aya-vision-32b:cohere",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": imagen_a_data_url(imagen)}},
                    ],
                }
            ],
            temperature=0.2,
            max_tokens=420,
        )
        contenido = completion.choices[0].message.content
        datos = limpiar_json_respuesta(contenido)

        nombre = str(datos.get("nombre") or "Comida detectada").strip()
        ingredientes = datos.get("ingredientes") or []
        if isinstance(ingredientes, str):
            ingredientes = [ingredientes]
        ingredientes = [str(i).strip() for i in ingredientes if str(i).strip()]

        calorias = numero_seguro(datos.get("calorias"))
        proteina = numero_seguro(datos.get("proteina"))
        carbohidratos = numero_seguro(datos.get("carbohidratos"))
        grasas = numero_seguro(datos.get("grasas"))
        fibra = numero_seguro(datos.get("fibra"))
        azucar = numero_seguro(datos.get("azucar"))
        confianza = max(0, min(100, numero_seguro(datos.get("confianza"), 65)))
        tipo = normalizar_tipo(datos.get("tipo"))

        if calorias <= 0:
            return None, "La IA visual no pudo estimar calorías con seguridad."

        ingredientes_txt = ", ".join(ingredientes) if ingredientes else "ingredientes visibles en la foto"
        porcion = str(datos.get("porcion") or "porción aproximada").strip()
        preparacion = str(datos.get("preparacion") or "").strip()
        notas = str(datos.get("notas") or "Estimación visual aproximada.").strip()
        seguridad = etiqueta_seguridad(confianza)
        preparacion_linea = f"**Preparación detectada:** {preparacion}\n" if preparacion else ""

        return {
            "mensaje": (
                f"Parece que la foto muestra **{nombre}**.\n\n"
                f"**Ingredientes detectados:** {ingredientes_txt}\n"
                f"{preparacion_linea}"
                f"**Porción estimada:** {porcion}\n"
                f"**Nivel de seguridad:** {seguridad}\n\n"
                f"{notas}"
            ),
            "calorias": calorias,
            "proteina": proteina,
            "carbohidratos": carbohidratos,
            "grasas": grasas,
            "fibra": fibra,
            "azucar": azucar,
            "ingredientes": ingredientes_txt,
            "tipo": tipo,
            "nombre": nombre
        }, None
    except Exception as e:
        return None, str(e)


def estimar_cantidad(alimento, descripcion):
    descripcion = (descripcion or "").lower()
    nombre = alimento["nombre"].lower()
    if "plátano" in nombre or "platano" in nombre:
        if any(palabra in descripcion for palabra in ["bunch", "several", "many", "varios", "manojo"]):
            return 3
        return 1
    if any(palabra in descripcion for palabra in ["two", "dos", "2"]):
        return 2
    if any(palabra in descripcion for palabra in ["three", "tres", "3"]):
        return 3
    return 1


def reconocer_comida_con_ia(imagen):
    token = obtener_hf_token()
    if not token:
        return None, "No hay token de Hugging Face configurado para usar reconocimiento visual."

    client = InferenceClient(provider="auto", token=token, timeout=25)
    labels = [alimento["label"] for alimento in ALIMENTOS_FOTO]

    descripcion = ""
    try:
        caption = client.image_to_text(imagen, model="Salesforce/blip-image-captioning-base")
        descripcion = getattr(caption, "generated_text", "") or str(caption)
    except Exception:
        descripcion = ""

    try:
        resultados = client.zero_shot_image_classification(
            imagen,
            candidate_labels=labels,
            model="openai/clip-vit-large-patch14"
        )
        if resultados:
            mejor = max(resultados, key=lambda item: float(getattr(item, "score", 0)))
            etiqueta = getattr(mejor, "label", "")
            confianza = float(getattr(mejor, "score", 0))
            alimento = next((a for a in ALIMENTOS_FOTO if a["label"] == etiqueta), None)
            if alimento and confianza >= 0.12:
                return {
                    "alimento": alimento,
                    "confianza": confianza,
                    "descripcion": descripcion
                }, None
    except Exception as e:
        alimento = buscar_alimento_por_texto(descripcion)
        if alimento:
            return {
                "alimento": alimento,
                "confianza": 0.55,
                "descripcion": descripcion
            }, None
        return None, str(e)

    alimento = buscar_alimento_por_texto(descripcion)
    if alimento:
        return {
            "alimento": alimento,
            "confianza": 0.55,
            "descripcion": descripcion
        }, None
    return None, None


def analizar_foto(imagen):
    if imagen is None:
        return {
            "mensaje": "Sube o toma una foto de tu comida.",
            "calorias": 0,
            "proteina": 0,
            "tipo": "ligera",
            "nombre": ""
        }

    resultado_avanzado, error_avanzado = analizar_comida_con_ia_avanzada(imagen)
    if resultado_avanzado:
        return resultado_avanzado

    resultado_ia, error_ia = reconocer_comida_con_ia(imagen)
    if not resultado_ia:
        detalle_error = error_avanzado or error_ia
        detalle = f"\n\nDetalle: {detalle_error}" if detalle_error else ""
        return {
            "mensaje": (
                "No pude reconocer con seguridad la comida en la foto. "
                "Intenta tomarla con más luz, más cerca del plato y sin tantos objetos alrededor."
                f"{detalle}"
            ),
            "calorias": 0,
            "proteina": 0,
            "tipo": "ligera",
            "nombre": ""
        }

    alimento = resultado_ia["alimento"]
    cantidad = estimar_cantidad(alimento, resultado_ia.get("descripcion", ""))
    calorias = int(alimento["calorias"] * cantidad)
    proteina = int(alimento["proteina"] * cantidad)
    extra = nutrientes_extra(alimento, cantidad)
    porcion = alimento["porcion"] if cantidad == 1 else f"{cantidad} porciones aproximadas"
    confianza = int(resultado_ia["confianza"] * 100)
    seguridad = etiqueta_seguridad(confianza)

    return {
        "mensaje": (
            f"Parece que la foto muestra **{alimento['nombre']}**.\n\n"
            f"**Porción estimada:** {porcion}\n"
            f"**Ingredientes o base detectada:** {extra['ingredientes']}\n"
            f"**Nivel de seguridad:** {seguridad}\n\n"
            "La estimación puede variar según tamaño, preparación e ingredientes."
        ),
        "calorias": calorias,
        "proteina": proteina,
        "carbohidratos": extra["carbohidratos"],
        "grasas": extra["grasas"],
        "fibra": extra["fibra"],
        "azucar": extra["azucar"],
        "ingredientes": extra["ingredientes"],
        "tipo": alimento["tipo"],
        "nombre": alimento["nombre"]
    }


def registrar_comida(imagen):
    datos, error = asegurar_usuario()
    if error:
        return error

    resultado = analizar_foto(imagen)

    calorias = resultado["calorias"]
    proteina = resultado["proteina"]
    carbohidratos = resultado.get("carbohidratos", 0)
    grasas = resultado.get("grasas", 0)
    fibra = resultado.get("fibra", 0)
    azucar = resultado.get("azucar", 0)
    tipo = resultado["tipo"]

    if calorias == 0:
        return resultado["mensaje"]

    datos["calorias_restantes"] = max(datos.get("calorias_restantes", 0) - calorias, 0)
    datos["proteina_consumida"] = datos.get("proteina_consumida", 0) + proteina

    historial = datos.get("historial_comidas", [])
    historial.append({
        "fecha": str(datetime.now()),
        "comida": resultado["nombre"],
        "calorias": calorias,
        "proteina": proteina,
        "carbohidratos": carbohidratos,
        "grasas": grasas,
        "fibra": fibra,
        "azucar": azucar,
        "ingredientes": resultado.get("ingredientes", ""),
        "tipo": tipo
    })

    datos["historial_comidas"] = historial[-20:]
    actualizar_datos_usuario(datos)
    agregar_xp(10)

    recomendacion_hora = evaluar_tipo_comida_por_hora(tipo)

    return (
        f"{resultado['mensaje']}\n\n"
        f"**Calorías:** {calorias} kcal\n"
        f"**Proteína:** {proteina} g\n"
        f"**Carbohidratos:** {carbohidratos} g\n"
        f"**Grasas:** {grasas} g\n"
        f"**Fibra:** {fibra} g\n"
        f"**Azúcar natural/aprox.:** {azucar} g\n\n"
        f"{recomendacion_hora}\n\n"
        f" Calorías restantes: **{datos['calorias_restantes']} kcal**\n"
        f" Proteína acumulada: **{datos['proteina_consumida']} g**\n\n"
        f" Ganaste **10 XP**"
    )


def imagen_disponible(valor):
    if valor is None:
        return False
    if isinstance(valor, str):
        return bool(valor.strip())
    return True


def registrar_comida_desde_opciones(imagen_trasera, imagen_frontal, imagen_archivo):
    imagen_elegida = None
    for candidata in (imagen_trasera, imagen_frontal, imagen_archivo):
        if imagen_disponible(candidata):
            imagen_elegida = candidata
            break
    return registrar_comida(imagen_elegida)


def cambiar_modo_foto(modo):
    return (
        gr.update(visible=modo == "Cámara trasera"),
        gr.update(visible=modo == "Cámara frontal"),
        gr.update(visible=modo == "Subir archivo"),
    )


def mostrar_historial():
    datos, error = asegurar_usuario()
    if error:
        return error

    historial = datos.get("historial_comidas", [])

    if not historial:
        return " Aún no has registrado comidas."

    texto = " **Historial de comidas:**\n\n"
    for i, item in enumerate(historial[-10:], 1):
        texto += (
            f"{i}. {item['comida']} - "
            f"{item['calorias']} kcal - "
            f"{item.get('proteina', 0)} g proteína - "
            f"{item.get('carbohidratos', 0)} g carbohidratos - "
            f"{item.get('grasas', 0)} g grasas\n"
        )

    texto += (
        f"\n Te quedan **{datos.get('calorias_restantes', 0)} kcal**"
        f"\n Llevas **{datos.get('proteina_consumida', 0)} g de proteína**"
    )
    return texto


# =========================
# RECETAS
# =========================

RECETAS_BASE = [
    {
        "nombre": "Avena con fresas y yogurt",
        "descripcion": "Avena, yogurt natural o griego, fresas y un poco de canela. Buena para desayuno rápido."
    },
    {
        "nombre": "Bowl de pollo con arroz y verduras",
        "descripcion": "Pollo a la plancha, arroz, verduras y aguacate. Opción completa para comida."
    },
    {
        "nombre": "Tostadas saludables",
        "descripcion": "Tostadas horneadas con frijoles, pollo o atún, lechuga, tomate y salsa casera."
    },
    {
        "nombre": "Snack de fruta con crema de cacahuate",
        "descripcion": "Manzana o plátano con una porción pequeña de crema de cacahuate. Útil si necesitas energía."
    }
]


def subir_receta(nombre, descripcion, imagen):
    datos, error = asegurar_usuario()
    if error:
        return error

    if not nombre or not descripcion:
        return " Ingresa nombre y descripción."

    recetas = datos.get("recetas", [])
    recetas.append({
        "nombre": nombre,
        "descripcion": descripcion,
        "imagen": str(imagen) if imagen is not None else None
    })

    datos["recetas"] = recetas[-20:]
    actualizar_datos_usuario(datos)

    return f" Receta '{nombre}' añadida correctamente."


def mostrar_recetas():
    datos, error = asegurar_usuario()
    if error:
        return error

    recetas = datos.get("recetas", [])
    contexto = contexto_usuario_para_ia(datos)

    recetas_ia = llamar_ia_texto(
        prompt_base_nutricion(),
        f"""
Genera 5 recetas saludables y realistas para este usuario.
Cada receta debe ser distinta, fácil de hacer y adaptada a su meta, gustos, alergias y rutina.
Incluye desayuno, comida, cena, snack o postre si aplica.

Datos del usuario:
{json.dumps(contexto, ensure_ascii=False, indent=2)}

Formato:
## Recetas personalizadas por IA
### 1. Nombre
Ingredientes: ...
Preparación: ...
Nutrición aproximada: ... kcal, ... g proteína
Por qué te conviene: ...
""".strip(),
        temperature=0.62,
        max_tokens=780,
    )

    texto = ""
    if recetas_ia:
        texto += recetas_ia.strip() + "\n\n"

    texto += "**Recetas base de Nutribot:**\n\n"
    recetas_mostrar = RECETAS_BASE + recetas[-10:]
    for receta in recetas_mostrar:
        texto += f"**{receta['nombre']}**\n{receta['descripcion']}\n\n"

    return texto


# =========================
# PLANES / MODELO DE NEGOCIO
# =========================

PLANES_NUTRIBOT = {
    "Paquete mensual": {
        "precio": "$299 MXN / mes",
        "descripcion": "Seguimiento visual, retos diarios, recetas saludables y uso del coach virtual.",
        "ideal": "Usuarios que quieren crear hábitos saludables con una guía sencilla y constante."
    },
    "Consulta nutriólogo": {
        "precio": "$500 MXN",
        "descripcion": "Sesión en línea con orientación profesional para revisar metas, dudas y avances.",
        "ideal": "Usuarios que necesitan acompañamiento puntual de un especialista."
    },
    "Paquete Premium": {
        "precio": "$9,300 MXN",
        "descripcion": "Experiencia premium con seguimiento completo, beneficios avanzados y prioridad en servicios.",
        "ideal": "Usuarios que buscan una experiencia integral con acompañamiento más completo."
    }
}


def ver_planes_precios():
    return planes_page_html()


def seleccionar_plan(plan):
    datos, error = asegurar_usuario()
    if error:
        return error

    if not plan or plan not in PLANES_NUTRIBOT:
        return "Selecciona un plan."

    datos["plan_seleccionado"] = {
        "nombre": plan,
        "precio": PLANES_NUTRIBOT[plan]["precio"],
        "fecha": str(datetime.now())
    }
    actualizar_datos_usuario(datos)
    agregar_xp(10)

    return (
        f"Seleccionaste **{plan}**.\n\n"
        f"**Precio:** {PLANES_NUTRIBOT[plan]['precio']}\n\n"
        "Tu elección quedó guardada en tu perfil.\n\n"
        "Ganaste **10 XP** por avanzar en tu plan de bienestar."
    )


def solicitar_consulta(motivo, modalidad):
    datos, error = asegurar_usuario()
    if error:
        return error

    motivo = (motivo or "").strip()
    modalidad = modalidad or "En línea"

    if not motivo:
        return "Escribe brevemente por qué quieres la consulta."

    consultas = datos.get("consultas_nutriologo", [])
    contexto = contexto_usuario_para_ia(datos)
    orientacion_ia = llamar_ia_texto(
        prompt_base_nutricion(),
        f"""
Prepara una orientación previa para una consulta nutricional.
No diagnostiques. Ayuda al usuario a entender qué temas llevar a consulta.

Motivo del usuario: {motivo}
Modalidad: {modalidad}
Datos del usuario:
{json.dumps(contexto, ensure_ascii=False, indent=2)}

Incluye:
1. Resumen breve del motivo.
2. Preguntas importantes para hacerle al nutriólogo.
3. Datos que debería tener listos.
4. Recomendación orientativa segura mientras espera la consulta.
5. Recordatorio de que esto no sustituye consulta profesional.
""".strip(),
        temperature=0.45,
        max_tokens=620,
    )

    consultas.append({
        "fecha": str(datetime.now()),
        "motivo": motivo,
        "modalidad": modalidad,
        "estado": "Solicitada",
        "precio_referencia": PLANES_NUTRIBOT["Consulta nutriólogo"]["precio"],
        "orientacion_ia": orientacion_ia or ""
    })

    datos["consultas_nutriologo"] = consultas[-10:]
    actualizar_datos_usuario(datos)
    agregar_xp(15)

    texto = (
        "Consulta solicitada.\n\n"
        f"**Modalidad:** {modalidad}\n"
        f"**Precio de referencia:** {PLANES_NUTRIBOT['Consulta nutriólogo']['precio']}\n"
        f"**Motivo:** {motivo}\n\n"
        "Un nutriólogo puede revisar tu caso y darte orientación personalizada.\n\n"
    )
    if orientacion_ia:
        texto += f"## Preparación para tu consulta\n\n{orientacion_ia}\n\n"
    else:
        texto += (
            "Antes de la consulta, ten listos tus horarios, alimentos frecuentes, alergias, "
            "medicamentos o estudios recientes si los tienes.\n\n"
        )
    texto += "Ganaste **15 XP**"
    return texto


# =========================
# NUTRIÓLOGOS
# =========================

def buscar_nutriologos(estado, ciudad):
    recomendaciones = [
        {
            "nombre": "Lic. Alondra Nuñez Ron",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutrióloga clínica en Nutritivia",
            "redes": "Instagram, TikTok y Facebook disponibles desde Doctoralia",
            "contacto": "Nutritivia, Fernando Montes de Oca #23, Col. La Huerta. Teléfono mostrado en Doctoralia.",
            "fuente": "https://www.doctoralia.com.mx/clinicas/nutritivia"
        },
        {
            "nombre": "Mtra. Rocío Echave Cota",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutrióloga clínica y especialista en obesidad y delgadez",
            "redes": "Perfil profesional en Doctoralia",
            "contacto": "Nutritivia, Fernando Montes de Oca #23, Col. La Huerta.",
            "fuente": "https://www.doctoralia.com.mx/rocio-echave-cota/nutriologo-clinico-especialista-en-obesidad-y-delgadez/sonora"
        },
        {
            "nombre": "Lic. Marina Piña",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutricionista y nutrióloga clínica, hábitos nutricionales y control de peso",
            "redes": "Perfil profesional en Doctoralia",
            "contacto": "Consulta nutricional en Boulevard Solidaridad 408, Hermosillo.",
            "fuente": "https://www.doctoralia.com.mx/marina-pina/nutricionista/sonora"
        },
        {
            "nombre": "Lic. Kenia Itzel Álvarez Méndez",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutricionista, planes adaptados a hábitos y metas",
            "redes": "Perfil profesional en Doctoralia",
            "contacto": "Nutrikenia, Villa de Seris 67, Hermosillo.",
            "fuente": "https://www.doctoralia.com.mx/kenia-itzel-alvarez-mendez/nutricionista/sonora"
        },
        {
            "nombre": "Lic. Areli Solís Larios",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutricionista, educación en diabetes y hábitos",
            "redes": "Perfil profesional en Doctoralia",
            "contacto": "Consulta nutricional individualizada online en Hermosillo.",
            "fuente": "https://www.doctoralia.com.mx/areli-solis-larios/nutricionista/sonora"
        },
        {
            "nombre": "Mtra. Anaid Eugenia Rodríguez López",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutrióloga clínica, nutricionista y especialista en obesidad y delgadez",
            "redes": "Perfil profesional en Doctoralia",
            "contacto": "Consultorio Nutrióloga Anaid E. Rodríguez López, Hermosillo.",
            "fuente": "https://www.doctoralia.com.mx/nutriologo-clinico/hermosillo/modelo"
        },
        {
            "nombre": "Mónica Torres",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutrición clínica, infantil y dieta keto",
            "redes": "Instagram: @nutriologa_monica_torres",
            "contacto": "Sitio: https://www.monicatorres.mx/",
            "fuente": "https://www.monicatorres.mx/"
        },
        {
            "nombre": "Yeraldí López",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutrición deportiva, consultas presenciales y online",
            "redes": "Instagram y Facebook disponibles en su perfil público",
            "contacto": "Teléfono: 662 187 2670",
            "fuente": "https://www.allbiz.mx/nutri%C3%B3loga-yerald%C3%AD-l%C3%B3pez-662-187-2670"
        },
        {
            "nombre": "Bibiana Paz G",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutrición clínica, alimentación emocional, pediatría y control de peso",
            "redes": "Instagram y Facebook disponibles en su perfil público",
            "contacto": "Teléfono: 662 298 6018",
            "fuente": "https://www.allbiz.mx/nutriologa-bibiana-paz-g-662-298-6018"
        },
        {
            "nombre": "Mayda González Nogales",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Nutrición clínica y educación en diabetes",
            "redes": "Sitio y contacto profesional",
            "contacto": "Teléfono: 662 291 9717",
            "fuente": "https://www.mgnutricionclinica.com/"
        },
        {
            "nombre": "Nutritivia",
            "estado": "Sonora",
            "ciudad": "Hermosillo",
            "especialidad": "Clínica de nutrición integral",
            "redes": "Instagram, TikTok y Facebook disponibles en Doctoralia",
            "contacto": "Doctoralia: agenda y mensajes",
            "fuente": "https://www.doctoralia.com.mx/clinicas/nutritivia"
        },
        {
            "nombre": "Lety Huerta",
            "estado": "Ciudad de México",
            "ciudad": "Ciudad de México",
            "especialidad": "Cambio de hábitos y nutrición personalizada",
            "redes": "Instagram, YouTube y sitio profesional disponibles en su perfil público",
            "contacto": "Teléfono: 55 5652 4064",
            "fuente": "https://www.allbiz.mx/nutriologa-lety-huerta-55-5652-4064"
        },
        {
            "nombre": "Montserrat González",
            "estado": "Ciudad de México",
            "ciudad": "Ciudad de México",
            "especialidad": "Nutrición clínica funcional, psiconutrición y salud digestiva",
            "redes": "Sitio profesional: Nutmmga",
            "contacto": "Sitio: https://www.nutmmga.com/",
            "fuente": "https://www.nutmmga.com/"
        },
        {
            "nombre": "Martha Mtz",
            "estado": "Nuevo León",
            "ciudad": "Monterrey",
            "especialidad": "Nutrición clínica con enfoque en salud hormonal",
            "redes": "Instagram disponible en Linktree",
            "contacto": "Linktree: https://linktr.ee/nutrihormonal",
            "fuente": "https://linktr.ee/nutrihormonal"
        },
        {
            "nombre": "Nutrióloga Lore",
            "estado": "Nuevo León",
            "ciudad": "Monterrey",
            "especialidad": "Nutrición, ejercicio y hábitos",
            "redes": "Instagram y Facebook disponibles en Linktree",
            "contacto": "Linktree: https://linktr.ee/nutriologalore",
            "fuente": "https://linktr.ee/nutriologalore"
        },
        {
            "nombre": "Patricia Barajas",
            "estado": "Jalisco",
            "ciudad": "Guadalajara",
            "especialidad": "Nutrición personalizada, deportiva, control de peso y bienestar integral",
            "redes": "Sitio profesional y agenda en línea",
            "contacto": "Sitio: https://www.clinicadepaty.com/",
            "fuente": "https://www.clinicadepaty.com/"
        },
        {
            "nombre": "Melissa Pineda",
            "estado": "Jalisco",
            "ciudad": "Guadalajara",
            "especialidad": "Salud hormonal, nutrición deportiva y hábitos saludables",
            "redes": "Instagram, WhatsApp y TikTok disponibles en Linktree",
            "contacto": "Linktree: https://linktr.ee/pinedanutricion",
            "fuente": "https://linktr.ee/pinedanutricion"
        },
        {
            "nombre": "María Ceballos",
            "estado": "Jalisco",
            "ciudad": "Guadalajara",
            "especialidad": "Nutrición clínica",
            "redes": "Sitio profesional",
            "contacto": "Sitio: https://www.mncmariaceballos.com/",
            "fuente": "https://www.mncmariaceballos.com/"
        },
        {
            "nombre": "Andrea Austria González",
            "estado": "Querétaro",
            "ciudad": "Santiago de Querétaro",
            "especialidad": "Nutrición clínica y geriátrica",
            "redes": "Instagram disponible en su sitio profesional",
            "contacto": "Teléfono: 442 709 1206",
            "fuente": "https://www.nutriologaenqueretaro.com/"
        },
        {
            "nombre": "Karen Correa",
            "estado": "Querétaro",
            "ciudad": "Santiago de Querétaro",
            "especialidad": "Nutrición clínica, deportiva y cardiovascular",
            "redes": "Instagram, TikTok y LinkedIn disponibles en Linktree",
            "contacto": "Linktree: https://linktr.ee/nutri.karencorrea",
            "fuente": "https://linktr.ee/nutri.karencorrea"
        },
        {
            "nombre": "Nutri Tijuana",
            "estado": "Baja California",
            "ciudad": "Tijuana",
            "especialidad": "Nutrición clínica, deportiva y enfermedades metabólicas",
            "redes": "Sitio profesional",
            "contacto": "Sitio: https://nutritijuana.com/",
            "fuente": "https://nutritijuana.com/"
        },
        {
            "nombre": "Berenice García",
            "estado": "Baja California",
            "ciudad": "Tijuana",
            "especialidad": "Planes alimenticios personalizados",
            "redes": "Instagram: nutriberegr",
            "contacto": "Teléfono: 664 605 0339",
            "fuente": "https://www.waze.com/live-map/directions/mexico/baja-california/tijuana/nutriologa-berenice-garcia-planes-alimenticios-personalizados?to=place.ChIJaXEPqnhJ2YARnGo5akVevEU"
        }
    ]

    estado = (estado or "").strip().lower()
    ciudad = (ciudad or "").strip().lower()
    alias_ciudad = {
        "hmo": "hermosillo",
        "hermosillo sonora": "hermosillo",
        "hermosillo son": "hermosillo",
    }
    alias_estado = {
        "son": "sonora",
        "son mx": "sonora",
        "sonora mx": "sonora",
    }
    ciudad = alias_ciudad.get(ciudad, ciudad)
    estado = alias_estado.get(estado, estado)

    resultados = [
        n for n in recomendaciones
        if (estado and estado in n["estado"].lower())
        or (ciudad and ciudad in n["ciudad"].lower())
    ]

    if not resultados:
        estados = sorted({n["estado"] for n in recomendaciones})
        ciudades = sorted({n["ciudad"] for n in recomendaciones})
        return (
            "No encontré recomendaciones verificadas para esa ubicación en la base actual.\n\n"
            f"Prueba con estos estados: {', '.join(estados)}.\n\n"
            f"O con estas ciudades: {', '.join(ciudades)}."
        )

    texto = (
        "## Nutriólogos recomendados\n\n"
        "Referencias públicas encontradas en sitios profesionales o directorios como Doctoralia y sitios oficiales. "
        "Antes de agendar, verifica disponibilidad, costos, cédula profesional y pide apoyo de un adulto si eres menor de edad.\n\n"
    )

    resumen_ia = llamar_ia_texto(
        prompt_base_nutricion(),
        f"""
Resume esta lista de nutriólogos reales para un usuario que busca apoyo en {ciudad or estado}.
No inventes datos nuevos. Solo ordena y explica cómo elegir.
Lista:
{json.dumps(resultados[:8], ensure_ascii=False, indent=2)}

Hazlo breve, profesional y útil.
""".strip(),
        temperature=0.35,
        max_tokens=360,
    )
    if resumen_ia:
        texto += resumen_ia.strip() + "\n\n"

    for n in resultados:
        texto += (
            f"### {n['nombre']}\n"
            f"**Especialidad:** {n['especialidad']}\n\n"
            f"**Ubicación:** {n['ciudad']}, {n['estado']}, México\n\n"
            f"**Redes:** {n['redes']}\n\n"
            f"**Contacto:** {n['contacto']}\n\n"
            f"**Fuente:** {n['fuente']}\n\n"
        )
    return texto


# =========================
# INTERFAZ
# =========================

with gr.Blocks(
    title="NutriBot | Salud y Bienestar",
    theme=gr.themes.Soft(primary_hue="violet", neutral_hue="slate"),
    css=APP_CSS,
) as app:
    gr.HTML(splash_html())
    hero_panel = gr.HTML(hero_html())
    with gr.Column(elem_classes=["phone-dashboard"]):
        dashboard_intro_panel = gr.HTML(dashboard_intro_html())
        food_register_label = gr.HTML(texto_boton_registro_inicio(False))
        boton_registro_inicio_toggle = gr.Button("›", elem_classes=["food-register-toggle"], interactive=False)
        registro_inicio_abierto = gr.State(False)
        with gr.Column(elem_classes=["inline-food-panel"], visible=False) as panel_registro_inicio:
            gr.HTML(
                """
                <div class="inline-food-guide">
                    <div class="inline-food-guide-icon">Foto</div>
                    <div>
                        <h3>Captura tu comida</h3>
                        <p>Usa buena luz y encuadra el plato completo para obtener una mejor estimación.</p>
                    </div>
                </div>
                """
            )
            modo_foto_inicio = gr.Radio(
                ["Cámara trasera", "Cámara frontal", "Subir archivo"],
                label="Modo de foto",
                value="Cámara trasera",
                interactive=False,
                elem_classes=["inline-food-mode"],
            )
            imagen_trasera_inicio = gr.Image(
                label="Foto de tu comida - cámara trasera",
                type="filepath",
                sources=["webcam"],
                interactive=False,
                elem_classes=["inline-food-camera"],
                webcam_options=gr.WebcamOptions(
                    mirror=False,
                    constraints={"video": {"facingMode": {"ideal": "environment"}}},
                ),
            )
            imagen_frontal_inicio = gr.Image(
                label="Foto de tu comida - cámara frontal",
                type="filepath",
                sources=["webcam"],
                visible=False,
                interactive=False,
                elem_classes=["inline-food-camera"],
                webcam_options=gr.WebcamOptions(
                    mirror=True,
                    constraints={"video": {"facingMode": {"ideal": "user"}}},
                ),
            )
            imagen_archivo_inicio = gr.Image(
                label="Subir foto de comida",
                type="filepath",
                sources=["upload", "clipboard"],
                visible=False,
                interactive=False,
                elem_classes=["inline-food-camera"],
            )
            with gr.Row(elem_classes=["inline-food-actions"]):
                boton_registrar_inicio = gr.Button("Registrar comida", variant="primary", interactive=False, elem_classes=["inline-food-primary"])
                boton_historial_inicio = gr.Button("Ver historial", interactive=False, elem_classes=["inline-food-secondary"])
            salida_foto_inicio = gr.Markdown(elem_classes=["inline-food-result"])
            salida_historial_inicio = gr.Markdown(elem_classes=["inline-food-history"])
        with gr.Column() as plan_inicio_panel:
            with gr.Row(elem_classes=["feature-grid"]):
                plan_desayuno_btn = gr.Button("☼\nDesayuno", elem_id="plan_desayuno_btn", elem_classes=["meal-action-btn"], interactive=False)
                plan_comida_btn = gr.Button("Comida", elem_id="plan_comida_btn", elem_classes=["meal-action-btn"], interactive=False)
                plan_cena_btn = gr.Button("☾\nCena", elem_id="plan_cena_btn", elem_classes=["meal-action-btn"], interactive=False)
            salida_plan_rapido = gr.Markdown(elem_classes=["meal-plan-output"], visible=False)
            plan_rapido_actual = gr.State("")
            progress_panel = gr.HTML(dashboard_progress_html())
    gr.HTML(
        '<div class="nutribot-note">Las recomendaciones son orientativas y no sustituyen la consulta con un profesional de salud.</div>'
    )

    with gr.Tab("Inicio"):
        gr.Markdown("## Acceso")
        nombre_login = gr.Textbox(label="Nombre")
        boton_login = gr.Button("Entrar", variant="primary")
        salida_login = gr.HTML()
        boton_ver_usuario = gr.Button("Ver usuario actual")
        salida_usuario = gr.HTML()

    with gr.Tab("Perfil"):
        with gr.Row():
            edad = gr.Number(label="Edad", interactive=False)
            peso = gr.Number(label="Peso (kg)", interactive=False)
            altura = gr.Number(label="Altura (cm)", interactive=False)

        genero = gr.Radio(["Hombre", "Mujer"], label="Género", interactive=False)
        actividad = gr.Dropdown(
            ["Sedentario", "Ligero", "Moderado", "Activo", "Muy activo"],
            label="Nivel de actividad física",
            interactive=False
        )
        meta = gr.Radio(
            ["Bajar de peso", "Mantener peso", "Subir de peso"],
            label="Meta personal",
            interactive=False
        )

        condicion = gr.Textbox(
            label="Condición alimenticia o enfermedad (opcional)",
            placeholder="Ejemplo: diabetes, hipertensión, intolerancia a la lactosa...",
            interactive=False
        )

        alergias = gr.Textbox(
            label="Alergias alimenticias (opcional)",
            placeholder="Ejemplo: maní, gluten, mariscos...",
            interactive=False
        )

        gr.Markdown("### Gustos y rutina")
        gustos = gr.Textbox(
            label="Alimentos que te gustan",
            placeholder="Ejemplo: pollo, fresas, avena, tacos, yogurt...",
            interactive=False
        )
        no_gusta = gr.Textbox(
            label="Alimentos que no te gustan o prefieres evitar",
            placeholder="Ejemplo: pescado, brócoli, leche, picante...",
            interactive=False
        )
        rutina = gr.Textbox(
            label="Rutina diaria",
            placeholder="Ejemplo: escuela de 7 a 2, entreno en la tarde, duermo tarde...",
            interactive=False
        )

        gr.Markdown("### Estudios / laboratorio (opcional)")
        glucosa = gr.Textbox(label="Glucosa", interactive=False)
        colesterol = gr.Textbox(label="Colesterol", interactive=False)
        trigliceridos = gr.Textbox(label="Triglicéridos", interactive=False)
        hemoglobina = gr.Textbox(label="Hemoglobina", interactive=False)
        observaciones = gr.Textbox(label="Observaciones adicionales", interactive=False)

        guardar_datos = gr.Button("Guardar información", variant="primary", interactive=False)
        salida_datos = gr.Markdown()

        boton_cargar = gr.Button("Cargar mis datos", interactive=False)
        salida_carga = gr.Markdown()

        boton_resumen = gr.Button("Ver resumen", interactive=False)
        salida_resumen = gr.Markdown()

    with gr.Tab("Progreso"):
        boton_progreso = gr.Button("Ver progreso", variant="primary", interactive=False)
        salida_progreso = gr.HTML()

    with gr.Tab("Consulta"):
        gr.Markdown("Solicita una consulta de orientación nutricional en línea.")
        motivo_consulta = gr.Textbox(
            label="Motivo de consulta",
            placeholder="Ejemplo: quiero mejorar mis hábitos, tengo dudas sobre mi alimentación...",
            interactive=False
        )
        modalidad_consulta = gr.Radio(
            ["En línea", "Seguimiento por chat"],
            label="Modalidad",
            value="En línea",
            interactive=False
        )
        boton_consulta = gr.Button("Solicitar consulta", variant="primary", interactive=False)
        salida_consulta = gr.Markdown()

    with gr.Tab("Nivel"):
        boton_nivel = gr.Button("Ver mi nivel", interactive=False, elem_classes=["level-cta"])
        salida_nivel = gr.HTML()

    with gr.Tab("Nuti"):
        gr.Markdown("### Nuti - guía de nutrición")
        chat_nuti = gr.HTML(chat_inicial_nuti())
        chat_nuti_state = gr.State([])
        entrada_nuti = gr.Textbox(label="Escribe algo para Nuti...", lines=2, max_lines=4, interactive=False, elem_classes=["chat-input-row"])
        boton_nuti = gr.Button("Enviar", variant="primary", interactive=False)

    with gr.Tab("Coach"):
        gr.Markdown("### Coach emocional")
        chat_coach = gr.HTML(chat_inicial_coach())
        chat_coach_state = gr.State([])
        entrada_coach = gr.Textbox(label="Cuéntame cómo te sientes hoy...", lines=2, max_lines=4, interactive=False, elem_classes=["chat-input-row"])
        boton_coach = gr.Button("Enviar", variant="primary", interactive=False)

    with gr.Tab("Recetas"):
        nombre_rec = gr.Textbox(label="Nombre de la receta", interactive=False)
        descripcion = gr.Textbox(label="Descripción o ingredientes", interactive=False)
        imagen_receta = gr.Image(label="Imagen (opcional)", type="filepath", interactive=False)
        boton_subir = gr.Button("Subir receta", variant="primary", interactive=False)
        salida_subir = gr.Textbox(label="Estado")
        boton_ver = gr.Button("Ver recetas disponibles", interactive=False)
        salida_recetas = gr.Markdown()

    with gr.Tab("Retos"):
        boton_ver_retos = gr.Button("Ver mis retos de hoy", interactive=False, elem_classes=["challenge-cta"])
        salida_retos = gr.HTML()
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



