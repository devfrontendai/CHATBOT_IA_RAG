import tiktoken
import os

# Carga config de modelo/costos desde variables de entorno
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
try:
    INPUT_COST_PER_MILLION = float(os.getenv("OPENAI_MODEL_COST_INPUT", 2.50))  # USD
    OUTPUT_COST_PER_MILLION = float(os.getenv("OPENAI_MODEL_COST_OUTPUT", 1.25))  # USD
except Exception:
    INPUT_COST_PER_MILLION = 2.50
    OUTPUT_COST_PER_MILLION = 1.25

def num_tokens_from_string(string: str, model: str = MODEL) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(string))

def calcular_costo(input_tokens: int, output_tokens: int) -> float:
    input_cost = input_tokens * (INPUT_COST_PER_MILLION / 1_000_000)
    output_cost = output_tokens * (OUTPUT_COST_PER_MILLION / 1_000_000)
    return input_cost + output_cost

def calcular_tokens_y_costo(prompt: str, respuesta: str, model: str = None) -> dict:
    model = model or MODEL
    input_tokens = num_tokens_from_string(prompt, model)
    output_tokens = num_tokens_from_string(respuesta, model)
    total_tokens = input_tokens + output_tokens
    cost = calcular_costo(input_tokens, output_tokens)
    print(f"[TOKENS] Model: {model} | Input: {input_tokens} | Output: {output_tokens} | Total: {total_tokens} | Cost: ${cost:.6f} USD")
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(cost, 6),
        "model": model,
        "currency": "USD"
    }
