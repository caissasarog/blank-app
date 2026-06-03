import os
import json
from huggingface_hub import InferenceClient
from hf_config import obtener_hf_token
from usuarios import obtener_usuario_actual, obtener_datos_usuario

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
MEMORIA_EMOCIONAL_FILE = "memoria_emocional.json"

def cargar_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default
    return default


def obtener_perfil():
    usuario = obtener_usuario_actual()
    datos = obtener_datos_usuario(usuario) if usuario else None
    perfil = datos.get("perfil", {}) if datos else {}

    return {
        "nombre": perfil.get("nombre", usuario or "Usuario"),
        "edad": perfil.get("edad", ""),
        "peso": perfil.get("peso", ""),
        "altura": perfil.get("altura", ""),
        "genero": perfil.get("genero", ""),
        "actividad": perfil.get("actividad", ""),
        "meta": perfil.get("meta", ""),
        "condicion": perfil.get("condicion", ""),
        "alergias": perfil.get("alergias", ""),
        "gustos": perfil.get("gustos", ""),
        "no_gusta": perfil.get("no_gusta", ""),
        "rutina": perfil.get("rutina", ""),
    }


def obtener_contexto_emocional(nombre):
    memoria = cargar_json(MEMORIA_EMOCIONAL_FILE, {})
    bloque = memoria.get(nombre, {})
    alertas = bloque.get("alertas_nutricion", [])
    if alertas:
        return alertas[-1]
    return None


def resumir_historial(historial, limite=6):
    if not historial:
        return "Sin historial reciente."
    partes = []
    for item in historial[-limite:]:
        if isinstance(item, dict):
            rol = item.get("role", "")
            content = item.get("content", "")
            if rol and content:
                partes.append(f"{rol}: {content}")
    return "\n".join(partes) if partes else "Sin historial reciente."


def construir_system_prompt(perfil, alerta_emocional):
    extra_emocional = ""
    if alerta_emocional and alerta_emocional.get("tipo") == "ansiedad_comida":
        extra_emocional = (
            "El usuario puede estar pasando por hambre emocional. "
            "Si habla de antojos, snacks o ganas de comer sin hambre, "
            "responde con empatía y sugiere pausar, hidratarse y elegir una opción ligera sin juzgar.\n"
        )

    return f"""
Eres Nuti, una asistente de nutrición muy inteligente, natural y útil.
Hablas en español claro, cercano y nada robótico.
Cuida mucho la ortografía, acentos y puntuación.
No mezcles palabras en inglés. Nunca uses palabras como "started", "healthy" o "tips" si puedes decirlo en español.
Antes de responder, revisa que la frase suene natural en español mexicano.
Tu trabajo:
- Si el usuario solo saluda o quiere conversación casual, síguele el rollo con naturalidad.
- Si pregunta sobre nutrición, responde como experta pero fácil de entender.
- Usa el perfil del usuario para personalizar.
- No inventes diagnósticos médicos.
- No respondas con listas rígidas a menos que ayuden.
- No uses frases genéricas tipo "sé fuerte" o "todo estará bien" si no vienen al caso.
- Responde breve a media longitud, útil y humana.
Perfil del usuario:
- Nombre: {perfil['nombre']}
- Edad: {perfil['edad']}
- Peso: {perfil['peso']}
- Altura: {perfil['altura']}
- Género: {perfil['genero']}
- Actividad: {perfil['actividad']}
- Meta: {perfil['meta']}
- Condición: {perfil['condicion']}
- Alergias: {perfil['alergias']}
- Gustos: {perfil['gustos']}
- Alimentos que no le gustan o prefiere evitar: {perfil['no_gusta']}
- Rutina diaria: {perfil['rutina']}
{extra_emocional}
Si el mensaje es ambiguo, primero aclara o responde de forma conversacional.
""".strip()


def respuesta_basica_nuti(mensaje, perfil):
    texto = mensaje.lower()
    nombre = str(perfil.get("nombre") or "Usuario").strip() or "Usuario"
    meta = str(perfil.get("meta") or "").strip()
    alergias = str(perfil.get("alergias") or "").strip()
    gustos = str(perfil.get("gustos") or "").strip()
    no_gusta = str(perfil.get("no_gusta") or "").strip()
    rutina = str(perfil.get("rutina") or "").strip()

    if any(palabra in texto for palabra in ["hola", "buenas", "hey"]):
        return (
            f"Hola, {nombre}. Estoy en modo básico porque falta activar el token de IA, "
            "pero puedo ayudarte con orientación general de nutrición. Cuéntame qué comiste, "
            "qué meta tienes o qué duda quieres resolver."
        )

    if any(palabra in texto for palabra in ["desayuno", "comida", "cena", "snack", "colación"]):
        alergias_txt = f" evitando {alergias}" if alergias else ""
        gustos_txt = f" Puedes usar alimentos que te gustan, como {gustos}." if gustos else ""
        evita_txt = f" Si no te gusta o prefieres evitar {no_gusta}, cámbialo por algo similar." if no_gusta else ""
        rutina_txt = f" Toma en cuenta tu rutina: {rutina}." if rutina else ""
        return (
            "Una opción equilibrada puede incluir proteína, verduras o fruta, carbohidrato de buena calidad "
            f"y agua{alergias_txt}. Por ejemplo: huevo o yogur griego, fruta, avena o tortilla, "
            "y una porción de verduras si aplica. Ajusta cantidades según tu hambre y tu objetivo."
            f"{gustos_txt}{evita_txt}{rutina_txt}"
        )

    if any(palabra in texto for palabra in ["bajar", "peso", "adelgazar", "grasa"]):
        return (
            "Para bajar grasa de forma sana, prioriza comidas completas, suficiente proteína, verduras, agua "
            "y movimiento constante. Evita saltarte comidas si eso te causa mucha hambre después. "
            "Lo más importante es que sea sostenible."
        )

    if any(palabra in texto for palabra in ["subir", "masa", "músculo", "musculo", "proteína", "proteina"]):
        return (
            "Para apoyar masa muscular, combina entrenamiento de fuerza con proteína suficiente en el día, "
            "carbohidratos para energía y descanso. Puedes repartir proteína en 3 o 4 comidas."
        )

    meta_txt = f" Tomaré en cuenta tu meta: {meta}." if meta else ""
    return (
        "Puedo orientarte de forma general, pero la IA completa todavía no está activada en esta sesión local."
        f"{meta_txt} Si me dices tu comida, horario o duda específica, te doy una recomendación práctica."
    )


def buscar_respuesta(mensaje, historial):
    perfil = obtener_perfil()
    nombre = str(perfil.get("nombre") or "Usuario").strip() or "Usuario"
    alerta_emocional = obtener_contexto_emocional(nombre)

    hf_token = obtener_hf_token()
    if not hf_token:
        return respuesta_basica_nuti(mensaje, perfil)

    system_prompt = construir_system_prompt(perfil, alerta_emocional)
    historial_texto = resumir_historial(historial)

    user_prompt = f"""
Historial reciente:
{historial_texto}
Mensaje actual del usuario:
{mensaje}
Responde directamente al usuario.
Usa español correcto, natural y con buena ortografía. Evita mezclar inglés.
""".strip()

    try:
        client = InferenceClient(provider="auto", token=hf_token)
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.6,
            max_tokens=220,
        )
        respuesta = completion.choices[0].message.content.strip()
        return respuesta if respuesta else "No pude generar respuesta ahorita."
    except Exception as e:
        return (
            "No pude conectar con la IA completa en este momento. "
            "Revisa que el token HF_TOKEN exista y tenga permiso de Inference Providers.\n\n"
            f"Detalle técnico: {str(e)}"
        )

