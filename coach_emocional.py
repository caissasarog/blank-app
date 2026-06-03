import os
import json
from datetime import datetime
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


def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def obtener_nombre_usuario():
    usuario = obtener_usuario_actual()
    datos = obtener_datos_usuario(usuario) if usuario else None
    perfil = datos.get("perfil", {}) if datos else {}

    nombre = perfil.get("nombre", usuario or "Usuario")
    return nombre.strip() if isinstance(nombre, str) and nombre.strip() else "Usuario"


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


def detectar_alerta_nutricion(texto):
    t = texto.lower()
    frases = [
        "quiero comer por ansiedad",
        "ando ansiosa y quiero comer",
        "como por ansiedad",
        "hambre emocional",
        "quiero comer para sentirme mejor",
        "quiero comer pero no tengo hambre",
        "me quiero atracar",
        "atracón",
        "atracon",
    ]
    for frase in frases:
        if frase in t:
            return {
                "fecha": str(datetime.now()),
                "tipo": "ansiedad_comida",
                "mensaje": "El usuario puede estar experimentando hambre emocional."
            }
    return None


def construir_system_prompt(nombre_usuario):
    return f"""
Eres un coach emocional muy humano, cálido y natural.
Hablas en español cercano y real, no robótico.
Cuida mucho la ortografía, acentos y puntuación.
No mezcles palabras en inglés. Si una idea aparece en inglés, tradúcela a español natural.
Tu estilo:
- Si el usuario solo saluda o quiere platicar casual, responde casual.
- Si el usuario está triste, ansioso, estresado o enojado, responde con empatía real.
- No uses frases vacías o repetitivas.
- No suenes como libro de autoayuda.
- Habla como alguien presente, atento y amable.
- No diagnostiques.
- Puedes hacer preguntas suaves para entender mejor.
- Responde breve a media longitud.
Usuario actual: {nombre_usuario}
Si notas ansiedad relacionada con comida, acompaña emocionalmente y deja espacio para que luego Nuti ayude con la parte de nutrición.
""".strip()


def respuesta_basica_coach(pregunta):
    texto = pregunta.lower()

    if any(palabra in texto for palabra in ["hola", "buenas", "hey"]):
        return (
            "Hola. Estoy en modo básico porque falta activar el token de IA, "
            "pero puedo acompañarte un poco. ¿Cómo te sientes hoy?"
        )

    if any(palabra in texto for palabra in ["ansiedad", "ansiosa", "ansioso", "estrés", "estres", "nervios"]):
        return (
            "Siento que estés pasando por eso. Haz una pausa pequeña: respira lento, toma agua "
            "y nombra tres cosas que sí están bajo tu control ahora. Si esto se siente muy fuerte "
            "o frecuente, busca apoyo de una persona de confianza o un profesional."
        )

    if any(palabra in texto for palabra in ["triste", "llorar", "mal", "sola", "solo", "cansada", "cansado"]):
        return (
            "Gracias por decirlo. No tienes que resolver todo de golpe; empieza por algo pequeño: "
            "descansar, comer algo sencillo, escribir lo que sientes o hablar con alguien seguro. "
            "Estoy aquí para escucharte."
        )

    if any(palabra in texto for palabra in ["comer por ansiedad", "hambre emocional", "atracón", "atracon"]):
        return (
            "Eso puede pasar cuando una emoción pide salida a través de la comida. Antes de decidir, "
            "prueba esperar cinco minutos, respirar, tomar agua y preguntarte: ¿tengo hambre física "
            "o necesito calma? No es para juzgarte, es para entenderte."
        )

    return (
        "Te leo. En esta sesión local estoy en modo básico porque falta activar la IA completa, "
        "pero puedes contarme qué pasó y te acompaño con una respuesta breve y tranquila."
    )


def coach_emocional_inteligente(pregunta, historial):
    hf_token = obtener_hf_token()
    if not hf_token:
        return respuesta_basica_coach(pregunta)

    usuario = obtener_nombre_usuario()
    memoria = cargar_json(MEMORIA_EMOCIONAL_FILE, {})

    if usuario not in memoria:
        memoria[usuario] = {
            "historial": [],
            "alertas_nutricion": []
        }

    historial_guardado = memoria[usuario]["historial"]
    historial_texto = resumir_historial(historial)

    system_prompt = construir_system_prompt(usuario)
    user_prompt = f"""
Historial reciente:
{historial_texto}
Mensaje actual del usuario:
{pregunta}
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
            temperature=0.65,
            max_tokens=220,
        )
        respuesta = completion.choices[0].message.content.strip()
        if not respuesta:
            respuesta = "Aquí estoy contigo. Cuéntame un poquito más."

        alerta = detectar_alerta_nutricion(pregunta)
        if alerta:
            memoria[usuario]["alertas_nutricion"].append(alerta)
            memoria[usuario]["alertas_nutricion"] = memoria[usuario]["alertas_nutricion"][-10:]

        historial_guardado.append({
            "fecha": str(datetime.now()),
            "entrada": pregunta,
            "respuesta": respuesta
        })
        memoria[usuario]["historial"] = historial_guardado[-20:]
        guardar_json(MEMORIA_EMOCIONAL_FILE, memoria)

        return respuesta
    except Exception as e:
        return (
            "No pude conectar con la IA completa en este momento. "
            "Revisa que el token HF_TOKEN exista y tenga permiso de Inference Providers.\n\n"
            f"Detalle técnico: {str(e)}"
        )

