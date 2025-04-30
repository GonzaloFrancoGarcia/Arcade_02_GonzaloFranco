import os
import requests
import json

# URL y llave de tu cuenta de Hugging Face
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
API_KEY = os.getenv("HF_API_KEY")  # Pon aquí tu token o usa variable de entorno
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def solicitar_sugerencia(juego: str, estado: dict) -> str:
    """
    Envía el estado actual del juego y devuelve la sugerencia de estrategia.
    - juego: 'nreinas' | 'caballo' | 'hanoi'
    - estado: dict serializable con la información relevante
    """
    payload = {
        "inputs": {
            "juego": juego,
            "estado": estado
        }
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # Ajusta según formato real de la API
    return data.get("generated_text", str(data))

def consultar_chatbot(pregunta: str) -> str:
    """
    Envía una pregunta libre al modelo y devuelve la respuesta.
    """
    payload = {"inputs": pregunta}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("generated_text", str(data))
