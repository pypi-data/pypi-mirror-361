
import requests

API_HalaGPT = "http://sii3.moayman.top"

class gemini:
    @staticmethod
    def ask(prompt: str) -> dict:
        try:
            return requests.get(f"{API_HalaGPT}/DARK/gemini.php", params={"text": prompt}).json()
        except:
            return {"status": "Error", "result": ""}
