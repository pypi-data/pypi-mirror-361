
import requests

API_HalaGPT = "http://sii3.moayman.top"

MODELS_IMAGE = [
    "fluex-pro", "flux", "schnell", "imger-12", "deepseek",
    "gemini-2-5-pro", "blackbox", "redux", "halagpt-7-i",
    "r1", "gpt-4-1"
]

class image:
    @staticmethod
    def generate(prompt: str, model: str = "halagpt-7-i") -> dict:
        if model not in MODELS_IMAGE:
            return {"status": "Error", "error": f"Model '{model}' not supported: {MODELS_IMAGE}"}
        resp = requests.get(f"{API_HalaGPT}/api/img.php", params={model: prompt})
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}

    @staticmethod
    def models() -> list:
        return MODELS_IMAGE
