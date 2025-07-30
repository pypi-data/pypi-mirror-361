
import requests

API_HalaGPT = "http://sii3.moayman.top"

VOICES = ["alloy", "coral", "echo", "shimmer", "verse", "onyx"]
STYLES = ["friendly", "calm", "noir_detective", "cowboy"]

class voice:
    @staticmethod
    def openai(text: str, voice: str = "alloy", style: str = None, method: str = "GET") -> dict:
        if voice not in VOICES:
            return {"status": "Error", "error": f"Voice '{voice}' not supported: {VOICES}"}
        if style and style not in STYLES:
            return {"status": "Error", "error": f"Style '{style}' not supported: {STYLES}"}
        params = {"text": text, "voice": voice}
        if style:
            params["style"] = style
        url = f"{API_HalaGPT}/DARK/voice.php"
        resp = requests.post(url, data=params) if method.upper() == "POST" else requests.get(url, params=params)
        return {"status": "ok" if "audio_url" in resp.text else "Bad", "result": resp.text}

    @staticmethod
    def models() -> list:
        return VOICES

    @staticmethod
    def styles() -> list:
        return STYLES
