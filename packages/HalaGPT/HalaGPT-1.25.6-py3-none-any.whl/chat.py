
import requests

API_HalaGPT = "http://sii3.moayman.top"

class chat:
    @staticmethod
    def ask(prompt: str) -> dict:
        return requests.get(f"{API_HalaGPT}/api/chat/gpt-3.5.php", params={"ai": prompt}).json()
