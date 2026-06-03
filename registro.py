import json
import os

# Nombre del archivo donde se guardará tu información
ARCHIVO_REGISTRO = "registro_personal.json"

# Función para guardar el estado completo
def guardar_registro(estado):
    """
    Guarda todo el estado personal en un archivo JSON.
    - estado: diccionario con todas tus variables (calorías, comidas, actividad, hidratación, sueño, estrés, etc.)
    """
    try:
        with open(ARCHIVO_REGISTRO, "w") as f:
            json.dump(estado, f, indent=4, default=str)  # default=str para datetime
        return True
    except Exception as e:
        print(f"Error al guardar registro: {e}")
        return False

# Función para cargar el estado desde el archivo
def cargar_registro():
    """
    Carga el estado desde el archivo JSON.
    Devuelve un diccionario vacío si no existe el archivo.
    """
    if os.path.exists(ARCHIVO_REGISTRO):
        try:
            with open(ARCHIVO_REGISTRO, "r") as f:
                estado = json.load(f)
            return estado
        except Exception as e:
            print(f"Error al cargar registro: {e}")
            return {}
    else:
        # Si no existe, devolver un estado vacío
        return {}

# Función para reiniciar el registro (opcional)
def reiniciar_registro():
    """
    Borra todo el historial y el archivo de registro.
    """
    if os.path.exists(ARCHIVO_REGISTRO):
        os.remove(ARCHIVO_REGISTRO)
    return {}

