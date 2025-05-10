#!/usr/bin/env python3
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def initialize_model():
    MODEL_NAME = "microsoft/DialoGPT-medium"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # Si no tiene pad_token, lo asignamos al eos_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model

# Inicializamos
tokenizer, model = initialize_model()

# Parámetros de generación
GEN_PARAMS = {
    "max_new_tokens": 60,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
    "do_sample": True,
}

def solicitar_sugerencia(juego: str, estado: dict) -> str:
    """
    Construye un prompt en inglés para el estado del juego y devuelve la sugerencia.
    """
    if juego == "nreinas":
        prompt = (
            f"I'm playing the {estado['N']}-Queens puzzle on a {estado['N']}×{estado['N']} board. "
            f"The queens are at positions {estado['reinas']}. "
            "Where should I place the next queen? "
            "Please answer with coordinates (row, column), 1-based indexing."
        )
    elif juego == "caballo":
        prompt = (
            f"I'm playing the Knight's Tour on a {estado['N']}×{estado['N']} chessboard. "
            f"The knight started at {estado.get('inicio')} and has visited {estado['visitadas']}. "
            "What is the next move? "
            "Provide the position as (row, column), 1-based indexing."
        )
    elif juego == "hanoi":
        prompt = (
            f"I'm solving the Towers of Hanoi puzzle with {estado['discos']} disks. "
            f"The rods configuration is {estado['pegs']}. "
            "What is the next move I should make? "
            "Please specify the move as (from_rod, to_rod), 1-based indexing."
        )
    else:
        prompt = (
            f"Game state: {estado}. "
            "What is the next move? Provide coordinates or appropriate format."
        )

    # Tokenización con padding confiable
    encoded = tokenizer(prompt + tokenizer.eos_token,
                        return_tensors="pt",
                        padding=True,
                        truncation=True)
    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pad_token_id=tokenizer.pad_token_id,
            max_length=input_ids.shape[-1] + GEN_PARAMS["max_new_tokens"],
            **GEN_PARAMS
        )
    # Extraemos solo la parte generada
    generated = outputs[0][input_ids.shape[-1]:]
    text = tokenizer.decode(generated, skip_special_tokens=True).strip()
    return text or "<no suggestion available>"

def consultar_chatbot(pregunta: str) -> str:
    """
    Envía una pregunta libre al modelo y devuelve su respuesta.
    """
    prompt = pregunta + tokenizer.eos_token
    encoded = tokenizer(prompt,
                        return_tensors="pt",
                        padding=True,
                        truncation=True)
    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pad_token_id=tokenizer.pad_token_id,
            max_length=input_ids.shape[-1] + GEN_PARAMS["max_new_tokens"],
            **GEN_PARAMS
        )
    generated = outputs[0][input_ids.shape[-1]:]
    text = tokenizer.decode(generated, skip_special_tokens=True).strip()
    return text or "<no response available>"
