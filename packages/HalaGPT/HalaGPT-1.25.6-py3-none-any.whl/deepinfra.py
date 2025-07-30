
import requests

API_HalaGPT = "http://sii3.moayman.top"

MODELS_DEEPINFRA = [
    "deepseekv3", "deepseekv3x", "deepseekr1", "deepseekr1base",
    "deepseekr1turbo", "deepseekr1llama", "deepseekr1qwen",
    "deepseekprover", "qwen235", "qwen30", "qwen32", "qwen14",
    "mav", "scout", "phi-plus", "guard", "qwq", "gemma27",
    "gemma12", "llama31", "llama332", "llama337", "mixtral24",
    "phi4", "phi-multi", "wizard822", "wizard27", "qwen2572",
    "qwen272", "dolphin26", "dolphin29", "airo70", "lzlv70",
    "mixtral822"
]

class deepinfra:
    @staticmethod
    def ask(text: str, model: str) -> dict:
        if model not in MODELS_DEEPINFRA:
            return {"status": "Error", "error": f"Model '{model}' not supported: {MODELS_DEEPINFRA}"}
        try:
            resp = requests.get(f"{API_HalaGPT}/api/DeepInfra.php", params={model: text})
            res = resp.json()
            return {"status": "OK", "result": res.get("response", res)}
        except Exception as e:
            return {"status": "Error", "error": str(e)}

    @staticmethod
    def models() -> list:
        return MODELS_DEEPINFRA
