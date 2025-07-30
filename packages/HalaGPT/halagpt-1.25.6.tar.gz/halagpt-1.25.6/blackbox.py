
import requests

API_HalaGPT = "http://sii3.moayman.top"

MODELS_BLACKBOX = [
    "blackbox", "gpt-4-1", "gpt-4-1-n", "gpt-4", "gpt-4o",
    "gpt-4o-m", "python", "html", "builder", "java", "js",
    "react", "android", "flutter", "nextjs", "angularjs",
    "swift", "mongodb", "pytorch", "xcode", "azure",
    "bitbucket", "digitalocean", "docker", "electron",
    "erlang", "fastapi", "firebase", "flask", "git",
    "gitlab", "go", "godot", "googlecloud", "heroku"
]

class blackbox:
    @staticmethod
    def ask(text: str, model: str) -> dict:
        if model not in MODELS_BLACKBOX:
            return {"status": "Error", "error": f"Model '{model}' not supported: {MODELS_BLACKBOX}"}
        data = requests.get(f"{API_HalaGPT}/api/black.php", params={model: text}).json()
        return {"status": "OK", "result": data.get("response")}

    @staticmethod
    def models() -> list:
        return MODELS_BLACKBOX
