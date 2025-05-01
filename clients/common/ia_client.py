import requests

API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
API_KEY = "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"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

GEN_PARAMS = {
    "max_new_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
    "return_full_text": False
}

def solicitar_sugerencia(juego: str, estado: dict) -> str:
    prompt = f"Juego: {juego}. Estado: {estado}. ¿Qué sugerencia me das para el siguiente movimiento?"
    payload = {"inputs": prompt, "parameters": GEN_PARAMS}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    print(">> DEBUG IA respuesta cruda:", data)  # <— Depuración
    if isinstance(data, list) and data and "generated_text" in data[0]:
        return data[0]["generated_text"].strip() or "<sin texto>"
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"].strip() or "<sin texto>"
    return "<sin generated_text>"

def consultar_chatbot(pregunta: str) -> str:
    payload = {"inputs": pregunta, "parameters": GEN_PARAMS}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    print(">> DEBUG Chatbot respuesta cruda:", data)  # <— Depuración
    if isinstance(data, list) and data and "generated_text" in data[0]:
        return data[0]["generated_text"].strip() or "<sin texto>"
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"].strip() or "<sin texto>"
    return "<sin generated_text>"
