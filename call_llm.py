import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral-nemo:latest"  


def call_llm(prompt: str, system: str | None = None) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    if system:
        payload["system"] = system

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    return response.json()["response"].strip()