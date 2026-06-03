import html
import json
import os
import random
from datetime import datetime

from usuarios import obtener_usuario_actual, obtener_datos_usuario, actualizar_datos_usuario


RETOS_FILE = "retos_usuario.json"


RETOS_BASE = [
    {
        "titulo": "Hidratacion constante",
        "descripcion": "Bebe agua durante el dia hasta completar tu meta personal.",
        "categoria": "Hidratacion",
        "puntos": 10,
        "insignia": "Heroe del Agua",
    },
    {
        "titulo": "Fruta del dia",
        "descripcion": "Incluye una fruta fresca en una comida o colacion.",
        "categoria": "Nutricion",
        "puntos": 15,
        "insignia": "NutriNinja",
    },
    {
        "titulo": "Caminata ligera",
        "descripcion": "Camina 20 minutos a un ritmo comodo.",
        "categoria": "Movimiento",
        "puntos": 20,
        "insignia": "Caminante Saludable",
    },
    {
        "titulo": "Desayuno con proteina",
        "descripcion": "Agrega huevo, yogurt, pollo, queso, legumbres u otra proteina a tu desayuno.",
        "categoria": "Nutricion",
        "puntos": 15,
        "insignia": "Power Breakfast",
    },
    {
        "titulo": "Dia sin refresco",
        "descripcion": "Evita refrescos o bebidas azucaradas por hoy.",
        "categoria": "Habitos",
        "puntos": 20,
        "insignia": "Sin Azucar",
    },
    {
        "titulo": "Estiramiento breve",
        "descripcion": "Haz 10 minutos de estiramiento o movilidad suave.",
        "categoria": "Movimiento",
        "puntos": 10,
        "insignia": "Cuerpo en Movimiento",
    },
    {
        "titulo": "Cena balanceada",
        "descripcion": "Cena algo ligero con verduras, proteina y una porcion moderada de carbohidratos.",
        "categoria": "Nutricion",
        "puntos": 15,
        "insignia": "Cena Inteligente",
    },
    {
        "titulo": "Plato con color",
        "descripcion": "Agrega al menos dos colores de verduras o frutas a tu plato.",
        "categoria": "Nutricion",
        "puntos": 15,
        "insignia": "Plato Vivo",
    },
    {
        "titulo": "Pausa consciente",
        "descripcion": "Respira profundo durante 3 minutos antes de una comida.",
        "categoria": "Bienestar",
        "puntos": 10,
        "insignia": "Mente Presente",
    },
    {
        "titulo": "Registro completo",
        "descripcion": "Registra una comida con foto o descripcion para conocer mejor tus habitos.",
        "categoria": "Seguimiento",
        "puntos": 15,
        "insignia": "Registro Pro",
    },
    {
        "titulo": "Colacion inteligente",
        "descripcion": "Elige una colacion con fruta, yogurt, nueces, queso o verdura.",
        "categoria": "Habitos",
        "puntos": 15,
        "insignia": "Snack Inteligente",
    },
    {
        "titulo": "Sueno saludable",
        "descripcion": "Define una hora para dormir y evita pantallas 20 minutos antes.",
        "categoria": "Bienestar",
        "puntos": 20,
        "insignia": "Descanso Pro",
    },
]


def cargar_datos_retos():
    if os.path.exists(RETOS_FILE):
        try:
            with open(RETOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def guardar_datos_retos(datos):
    with open(RETOS_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def obtener_perfil_usuario():
    usuario = obtener_usuario_actual()
    if not usuario:
        return {"nombre": "Usuario", "meta": "", "actividad": "", "edad": ""}

    datos = obtener_datos_usuario(usuario)
    if not datos:
        return {"nombre": usuario, "meta": "", "actividad": "", "edad": ""}

    perfil = datos.get("perfil", {})
    return {
        "nombre": perfil.get("nombre", usuario) or usuario,
        "meta": str(perfil.get("meta", "")).lower(),
        "actividad": str(perfil.get("actividad", "")).lower(),
        "edad": perfil.get("edad", ""),
    }


def generar_retos_personalizados(perfil):
    retos = [reto.copy() for reto in RETOS_BASE]
    meta = perfil.get("meta", "")
    actividad = perfil.get("actividad", "")
    extras = []

    if "bajar" in meta:
        extras.extend([
            {
                "titulo": "Cambio inteligente",
                "descripcion": "Elige una colacion saludable en vez de comida chatarra.",
                "categoria": "Habitos",
                "puntos": 20,
                "insignia": "Eleccion Inteligente",
            },
            {
                "titulo": "Movimiento extra",
                "descripcion": "Haz 25 minutos de caminata, baile, bici o movimiento suave.",
                "categoria": "Movimiento",
                "puntos": 25,
                "insignia": "Paso Ligero",
            },
        ])
    elif "subir" in meta:
        extras.extend([
            {
                "titulo": "Energia nutritiva",
                "descripcion": "Agrega una comida nutritiva extra hoy.",
                "categoria": "Nutricion",
                "puntos": 20,
                "insignia": "Energia Extra",
            },
            {
                "titulo": "Proteina doble",
                "descripcion": "Incluye proteina en 2 comidas del dia.",
                "categoria": "Nutricion",
                "puntos": 25,
                "insignia": "Construccion Saludable",
            },
        ])
    elif "mantener" in meta:
        extras.append({
            "titulo": "Rutina estable",
            "descripcion": "Manten horarios regulares de comida hoy.",
            "categoria": "Habitos",
            "puntos": 20,
            "insignia": "Equilibrio Diario",
        })

    if "sedentario" in actividad:
        extras.append({
            "titulo": "Activacion rapida",
            "descripcion": "Levantate y muevete 5 minutos, 3 veces hoy.",
            "categoria": "Movimiento",
            "puntos": 20,
            "insignia": "Activacion Total",
        })

    if "activo" in actividad or "muy activo" in actividad:
        extras.append({
            "titulo": "Recuperacion",
            "descripcion": "Haz un estiramiento completo despues de entrenar o moverte.",
            "categoria": "Movimiento",
            "puntos": 15,
            "insignia": "Recuperacion Pro",
        })

    retos.extend(extras)
    random.shuffle(retos)
    retos_finales = retos[:6]

    for reto in retos_finales:
        reto["completado"] = False

    return retos_finales


def obtener_fecha_hoy():
    return datetime.now().strftime("%Y-%m-%d")


def obtener_datos_retos_usuario():
    perfil = obtener_perfil_usuario()
    nombre = perfil["nombre"]
    fecha_hoy = obtener_fecha_hoy()
    datos = cargar_datos_retos()

    if nombre not in datos:
        datos[nombre] = {
            "fecha": fecha_hoy,
            "retos": generar_retos_personalizados(perfil),
            "puntos": 0,
            "insignias": [],
        }
    elif datos[nombre].get("fecha") != fecha_hoy:
        datos[nombre]["fecha"] = fecha_hoy
        datos[nombre]["retos"] = generar_retos_personalizados(perfil)

    guardar_datos_retos(datos)
    return datos, nombre


def _pantalla_bloqueada():
    return """
    <section class="challenge-screen">
        <div class="challenge-hero">
            <span>Retos saludables</span>
            <h2>Inicia sesion para ver tus retos</h2>
            <p>Entra con tu nombre para activar tus misiones personalizadas del dia.</p>
        </div>
    </section>
    """


def mostrar_retos():
    usuario_actual = obtener_usuario_actual()
    if not usuario_actual:
        return _pantalla_bloqueada()

    datos, nombre = obtener_datos_retos_usuario()
    usuario = datos[nombre]
    retos = usuario.get("retos", [])
    completados = sum(1 for reto in retos if reto.get("completado"))
    total = len(retos)
    porcentaje = int((completados / total) * 100) if total else 0

    cards = ""
    for i, reto in enumerate(retos, 1):
        estado = "Completado" if reto.get("completado") else "Pendiente"
        estado_clase = "done" if reto.get("completado") else "pending"
        cards += f"""
        <article class="challenge-card {estado_clase}">
            <div class="challenge-card-top">
                <span class="challenge-number">{i}</span>
                <span class="challenge-category">{html.escape(reto.get("categoria", "Reto"))}</span>
            </div>
            <h3>{html.escape(reto.get("titulo", "Reto saludable"))}</h3>
            <p>{html.escape(reto.get("descripcion", ""))}</p>
            <div class="challenge-meta">
                <strong>{reto.get("puntos", 0)} pts</strong>
                <span>{estado}</span>
            </div>
        </article>
        """

    insignias = usuario.get("insignias", [])
    insignias_html = "".join(f"<span>{html.escape(insignia)}</span>" for insignia in insignias)
    if not insignias_html:
        insignias_html = "<span>Aun sin insignias</span>"

    return f"""
    <section class="challenge-screen">
        <div class="challenge-hero">
            <span>Retos saludables</span>
            <h2>Misiones de hoy</h2>
            <p>Elige un reto, completalo y marca su numero abajo para sumar puntos y XP.</p>
        </div>
        <div class="challenge-summary">
            <div><small>Avance diario</small><strong>{completados}/{total}</strong></div>
            <div><small>Puntos</small><strong>{usuario.get("puntos", 0)}</strong></div>
            <div><small>Progreso</small><strong>{porcentaje}%</strong></div>
        </div>
        <div class="challenge-track"><span style="--challenge-value: {porcentaje}%"></span></div>
        <div class="challenge-grid">{cards}</div>
        <div class="challenge-badges">
            <strong>Insignias</strong>
            <div>{insignias_html}</div>
        </div>
    </section>
    """


def completar_reto(numero):
    usuario_actual = obtener_usuario_actual()
    if not usuario_actual:
        return _pantalla_bloqueada()

    if numero is None:
        return mostrar_retos() + "<p class='challenge-message'>Ingresa el numero del reto que completaste.</p>"

    try:
        index = int(numero) - 1
    except ValueError:
        return mostrar_retos() + "<p class='challenge-message'>Ingresa un numero valido.</p>"

    datos_retos, nombre = obtener_datos_retos_usuario()
    usuario_retos = datos_retos[nombre]
    retos = usuario_retos["retos"]

    if 0 <= index < len(retos):
        if not retos[index]["completado"]:
            retos[index]["completado"] = True
            usuario_retos["puntos"] += retos[index]["puntos"]

            insignia = retos[index]["insignia"]
            if insignia not in usuario_retos["insignias"]:
                usuario_retos["insignias"].append(insignia)

            guardar_datos_retos(datos_retos)

            datos_usuario = obtener_datos_usuario(usuario_actual)
            if datos_usuario:
                xp_actual = datos_usuario.get("xp", 0) + 10
                nivel_actual = datos_usuario.get("nivel", 1)

                while xp_actual >= nivel_actual * 100:
                    xp_actual -= nivel_actual * 100
                    nivel_actual += 1

                datos_usuario["xp"] = xp_actual
                datos_usuario["nivel"] = nivel_actual
                actualizar_datos_usuario(datos_usuario, usuario_actual)

            return mostrar_retos() + f"""
            <p class="challenge-message success">
                Reto completado. Ganaste {retos[index]["puntos"]} puntos, la insignia "{html.escape(insignia)}" y 10 XP.
            </p>
            """
        return mostrar_retos() + "<p class='challenge-message'>Este reto ya fue completado.</p>"

    return mostrar_retos() + "<p class='challenge-message'>Numero de reto invalido.</p>"
