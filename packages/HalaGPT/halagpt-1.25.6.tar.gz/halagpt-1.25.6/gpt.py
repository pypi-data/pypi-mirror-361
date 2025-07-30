
import requests

API_HalaGPT = "http://sii3.moayman.top"

MODELS_GPT = [
    "gpt-4", "gpt-4o", "gpt-4-1", "gpt-voice",
    "llama8", "llamascout", "mistral", "mistralcf",
    "phi", "qwen", "bidara", "gpt-music", "o3"
]

class gpt:
    @staticmethod
    def ask(text: str, model: str) -> dict:
        if model not in MODELS_GPT:
            return {"status": "Error", "error": f"Model '{model}' not supported: {MODELS_GPT}"}
        try:
            return requests.get(f"{API_HalaGPT}/api/gpt.php", params={model: text}).json()
        except Exception as e:
            return {"status": "Error", "error": str(e)}

    @staticmethod
    def models() -> list:
        return MODELS_GPT
