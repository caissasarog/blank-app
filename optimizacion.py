from PIL import Image

# Reducir resolución de imagen antes de enviarla al modelo
def resize_imagen(img, size=(224,224)):
    return img.resize(size)

# Función para preprocesar varias imágenes en batch
def batch_preprocesar(imagenes, size=(224,224)):
    return [img.resize(size) for img in imagenes]

# Limitar la carga del modelo solo una vez
def cargar_modelo_ligero():
    from transformers import pipeline
    # Modelo más rápido y ligero que nateraw/food
    modelo = pipeline("image-classification", model="google/vit-base-patch16-224")
    return modelo

# Función para cachear resultados y no recalcular lo mismo
_cache = {}
def cache_resultado(key, funcion, *args, **kwargs):
    if key in _cache:
        return _cache[key]
    resultado = funcion(*args, **kwargs)
    _cache[key] = resultado
    return resultado

