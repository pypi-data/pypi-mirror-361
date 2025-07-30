
import requests

API_HalaGPT = "http://sii3.moayman.top"

class deepseek:
    @staticmethod
    def codeify(text: str) -> dict:
        url = f"{API_HalaGPT}/api/DeepSeek/DeepSeek.php"
        resp = requests.get(url, params={"text": text})
        try:
            data = resp.json()
            if "result" in data:
                return {"status": "OK", "result": data["result"]}
            if "response" in data:
                return {"status": "OK", "result": data["response"]}
            return {"status": "OK", "result": str(data)}
        except ValueError:
            return {"status": "OK", "result": resp.text}
