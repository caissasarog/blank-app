import os
import json

USUARIOS_FILE = "usuarios.json"
SESION_FILE = "sesion_actual.json"


# =========================
# UTILIDADES JSON
# =========================

def cargar_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default
    return default


def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# USUARIOS
# =========================

def cargar_usuarios():
    return cargar_json(USUARIOS_FILE, {})


def guardar_usuarios(data):
    guardar_json(USUARIOS_FILE, data)


# =========================
# SESIÓN ACTUAL
# =========================

def guardar_sesion(nombre):
    guardar_json(SESION_FILE, {"usuario_actual": nombre})


def obtener_usuario_actual():
    sesion = cargar_json(SESION_FILE, {})
    return sesion.get("usuario_actual", "")


# =========================
# LOGIN SIMPLE (NOMBRE)
# =========================

def iniciar_o_crear_usuario(nombre):
    nombre = (nombre or "").strip()

    if not nombre:
        return " Escribe tu nombre."

    usuarios = cargar_usuarios()

    if nombre not in usuarios:
        usuarios[nombre] = {
            "perfil": {},
            "historial_comidas": [],
            "recetas": [],
            "memoria_nuti": [],
            "memoria_coach": [],
            "calorias_totales": 0,
            "calorias_restantes": 0,
            "xp": 0,
            "nivel": 1
        }
        guardar_usuarios(usuarios)

    guardar_sesion(nombre)

    return f" Entraste como **{nombre}**."


# =========================
# OBTENER DATOS
# =========================

def obtener_datos_usuario(nombre=None):
    usuarios = cargar_usuarios()

    if not nombre:
        nombre = obtener_usuario_actual()

    if not nombre or nombre not in usuarios:
        return None

    return usuarios[nombre]


# =========================
# ACTUALIZAR DATOS
# =========================

def actualizar_datos_usuario(data, nombre=None):
    usuarios = cargar_usuarios()

    if not nombre:
        nombre = obtener_usuario_actual()

    if not nombre:
        return

    if nombre not in usuarios:
        usuarios[nombre] = {
            "perfil": {},
            "historial_comidas": [],
            "recetas": [],
            "memoria_nuti": [],
            "memoria_coach": [],
            "calorias_totales": 0,
            "calorias_restantes": 0,
            "xp": 0,
            "nivel": 1
        }

    usuarios[nombre] = data
    guardar_usuarios(usuarios)
