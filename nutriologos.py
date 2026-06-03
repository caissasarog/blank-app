# nutriologos.py
#  Base de datos local de nutriólogos y funciones de búsqueda

nutriologos = [
    #  México
    {"nombre": "Dra. Ana López", "pais": "México", "estado": "Sonora", "ciudad": "Hermosillo",
     "especialidad": "Nutrición deportiva", "direccion": "Av. Universidad 200",
     "contacto": "Instagram: @dra.analpz"},
    
    {"nombre": "Lic. Jorge Ramírez", "pais": "México", "estado": "CDMX", "ciudad": "Coyoacán",
     "especialidad": "Control de peso", "direccion": "Centro NutriVida, Av. Pacífico 300",
     "contacto": "Tel: +52 55 1234 5678"},
    
    {"nombre": "Lic. Sofía Rivera", "pais": "México", "estado": "Jalisco", "ciudad": "Guadalajara",
     "especialidad": "Nutrición general y recetas personalizadas",
     "direccion": "Av. Chapultepec 100", "contacto": "IG: @sofiariveranutri"},

    #  Colombia
    {"nombre": "Dra. Camila Torres", "pais": "Colombia", "estado": "Antioquia", "ciudad": "Medellín",
     "especialidad": "Nutrición infantil", "direccion": "Cra 40 #23",
     "contacto": "Email: camilatorresnutri@gmail.com"},

    #  España
    {"nombre": "Dr. Luis Fernández", "pais": "España", "estado": "Madrid", "ciudad": "Madrid",
     "especialidad": "Nutrición clínica", "direccion": "Calle Mayor 45",
     "contacto": "Web: www.drfernandez.es"},

    {"nombre": "Dra. Laura Soler", "pais": "España", "estado": "Cataluña", "ciudad": "Barcelona",
     "especialidad": "Nutrición vegetariana y vegana", "direccion": "Av. Diagonal 350",
     "contacto": "Email: laurasoler@nutribarcelona.es"},
]

def obtener_paises():
    """Devuelve una lista de países disponibles"""
    return sorted(set(n["pais"] for n in nutriologos))

def obtener_estados(pais):
    """Devuelve los estados disponibles según el país elegido"""
    return sorted(set(n["estado"] for n in nutriologos if n["pais"].lower() == pais.lower()))

def obtener_ciudades(pais, estado):
    """Devuelve las ciudades disponibles según el país y estado"""
    return sorted(set(n["ciudad"] for n in nutriologos
                      if n["pais"].lower() == pais.lower() and n["estado"].lower() == estado.lower()))

def buscar_nutriologos(pais, estado, ciudad):
    """Busca nutriólogos según país, estado y ciudad"""
    resultados = [n for n in nutriologos
                  if n["pais"].lower() == pais.lower() and
                     n["estado"].lower() == estado.lower() and
                     n["ciudad"].lower() == ciudad.lower()]
    if not resultados:
        return " No se encontraron nutriólogos en esa zona."
    
    salida = " Nutriólogos disponibles:\n"
    for n in resultados:
        salida += f"""
• {n['nombre']} — {n['especialidad']}
   {n['direccion']}
   {n['pais']}, {n['estado']}, {n['ciudad']}
   {n['contacto']}
"""
    return salida

