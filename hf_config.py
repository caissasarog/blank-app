import os
from pathlib import Path


def obtener_hf_token():
    for nombre in ("HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGING_FACE_HUB_TOKEN"):
        token = os.getenv(nombre, "").strip()
        if token:
            return token

    base = Path(__file__).parent
    for archivo in (".hf_token", "hf_token.txt", ".env"):
        ruta = base / archivo
        if not ruta.exists():
            continue

        try:
            contenido = ruta.read_text(encoding="utf-8").strip()
        except OSError:
            continue

        if not contenido:
            continue

        if archivo == ".env":
            for linea in contenido.splitlines():
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                clave, valor = linea.split("=", 1)
                if clave.strip() in {"HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGING_FACE_HUB_TOKEN"}:
                    valor = valor.strip().strip('"').strip("'")
                    if valor:
                        return valor
        else:
            return contenido

    return ""
