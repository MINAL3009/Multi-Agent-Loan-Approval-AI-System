import io
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMService:
    def __init__(self):
        self.provider_name = "template"
        self.client: Optional[OpenAI] = None
        self.model = ""

        groq_key = os.getenv("GROQ_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        together_key = os.getenv("TOGETHER_API_KEY")

        if groq_key:
            self.provider_name = "groq"
            self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            self.client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        elif openrouter_key:
            self.provider_name = "openrouter"
            self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
            self.client = OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1")
        elif together_key:
            self.provider_name = "together"
            self.model = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
            self.client = OpenAI(api_key=together_key, base_url="https://api.together.xyz/v1")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            return ""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                timeout=10,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return (response.choices[0].message.content or "").strip()
        except Exception:
            return ""

    def transcribe_audio(self, audio_bytes: bytes, filename: str = "question.wav") -> str:
        if not self.client or self.provider_name != "groq":
            return ""

        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = filename
            response = self.client.audio.transcriptions.create(
                model=os.getenv("GROQ_TRANSCRIPTION_MODEL", "whisper-large-v3-turbo"),
                file=audio_file,
                timeout=20,
            )
            return (getattr(response, "text", "") or "").strip()
        except Exception:
            return ""


llm_service = LLMService()
