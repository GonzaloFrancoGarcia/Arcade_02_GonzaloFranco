import os
import requests

# URL de la Inference API para DialoGPT-medium
API_URL = "https://huggingface.co/microsoft/DialoGPT-medium/tree/main"


# Leemos el token desde la variable de entorno
API_KEY = os.getenv("HF_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "❌ No se encontró la variable HF_API_KEY.\n"
        "Define tu token con:\n"
        "  export HF_API_KEY=\"<tu_token>\"   (Linux/macOS)\n"
        "  $Env:HF_API_KEY=\"<tu_token>\"     (PowerShell)\n"
    )

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Parámetros de generación
GEN_PARAMS = {
    "max_new_tokens": 60,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
    "return_full_text": False
}

def solicitar_sugerencia(juego: str, estado: dict) -> str:
    # Construye un prompt en lenguaje natural según el juego
    if juego == "nreinas":
        prompt = (
            f"Estoy jugando al problema de {estado['N']} reinas. "
            f"Las reinas están en {estado['reinas']}. "
            "¿Dónde debo colocar la siguiente reina?"
        )
    elif juego == "caballo":
        prompt = (
            f"Estoy en Knight’s Tour en un tablero de {estado['N']}×{estado['N']}. "
            f"Empecé en {estado.get('inicio')} y he visitado {estado['visitadas']}. "
            "¿Cuál es mi próximo movimiento?"
        )
    elif juego == "hanoi":
        prompt = (
            f"Solucionando Torres de Hanói con {estado['discos']} discos. "
            f"Configuración actual: {estado['pegs']}. "
            "¿Qué movimiento debería hacer ahora?"
        )
    else:
        prompt = f"Estado del juego: {estado}. ¿Qué sugerencia tienes?"

    payload = {"inputs": prompt, "parameters": GEN_PARAMS}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # Extrae el campo generated_text, atiende lista o dict
    if isinstance(data, list) and data and "generated_text" in data[0]:
        text = data[0]["generated_text"]
    elif isinstance(data, dict) and "generated_text" in data:
        text = data["generated_text"]
    else:
        text = ""

    return text.strip() or "<sin sugerencia disponible>"

def consultar_chatbot(pregunta: str) -> str:
    payload = {"inputs": pregunta, "parameters": GEN_PARAMS}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list) and data and "generated_text" in data[0]:
        text = data[0]["generated_text"]
    elif isinstance(data, dict) and "generated_text" in data:
        text = data["generated_text"]
    else:
        text = ""
    return text.strip() or "<sin respuesta disponible>"
