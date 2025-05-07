# clients/common/ia_client.py

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Modelo local
MODEL_NAME = "microsoft/DialoGPT-medium"

# Cargamos modelo y tokenizador una sola vez
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()

# Parámetros de generación
GEN_PARAMS = {
    "max_new_tokens": 60,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3
}

def solicitar_sugerencia(juego: str, estado: dict) -> str:
    # Formatea prompt en texto natural
    if juego == "nreinas":
        prompt = (
            f"Estoy jugando al problema de {estado['N']} reinas. "
            f"Las reinas están en {estado['reinas']}. "
            "¿Dónde debo colocar la siguiente reina?"
        )
    elif juego == "caballo":
        prompt = (
            f"Knight’s Tour en un tablero {estado['N']}×{estado['N']}. "
            f"Empecé en {estado.get('inicio')} y he visitado {estado['visitadas']}. "
            "¿Cuál es mi próximo movimiento?"
        )
    elif juego == "hanoi":
        prompt = (
            f"Torres de Hanói con {estado['discos']} discos. "
            f"Configuración: {estado['pegs']}. "
            "¿Qué movimiento hago ahora?"
        )
    else:
        prompt = f"Estado: {estado}. ¿Sugerencia?"

    # Tokeniza y genera
    inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[-1] + GEN_PARAMS["max_new_tokens"],
            pad_token_id=tokenizer.eos_token_id,
            temperature=GEN_PARAMS["temperature"],
            top_p=GEN_PARAMS["top_p"],
            top_k=GEN_PARAMS["top_k"],
            repetition_penalty=GEN_PARAMS["repetition_penalty"],
            no_repeat_ngram_size=GEN_PARAMS["no_repeat_ngram_size"],
        )
    # Extrae solo la parte nueva
    generated = outputs[0][inputs.shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip() or "<sin sugerencia>"

def consultar_chatbot(pregunta: str) -> str:
    prompt = pregunta + tokenizer.eos_token
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[-1] + GEN_PARAMS["max_new_tokens"],
            pad_token_id=tokenizer.eos_token_id,
            temperature=GEN_PARAMS["temperature"],
            top_p=GEN_PARAMS["top_p"],
            top_k=GEN_PARAMS["top_k"],
            repetition_penalty=GEN_PARAMS["repetition_penalty"],
            no_repeat_ngram_size=GEN_PARAMS["no_repeat_ngram_size"],
        )
    generated = outputs[0][inputs.shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip() or "<sin respuesta>"
