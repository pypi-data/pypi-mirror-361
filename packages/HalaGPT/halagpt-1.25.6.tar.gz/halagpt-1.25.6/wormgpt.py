
import requests

API_HalaGPT = "http://sii3.moayman.top"

class wormgpt:
    @staticmethod
    def worm(text: str) -> dict:
        res = requests.get(f"{API_HalaGPT}/DARK/api/wormgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response")}

    @staticmethod
    def darkgpt(text: str) -> dict:
        res = requests.get(f"{API_HalaGPT}/DARK/api2/darkgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response")}
