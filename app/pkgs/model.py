import os
import requests
from dotenv import load_dotenv

load_dotenv()

session = requests.Session()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")


# Hàm gọi mô hình AI từ Docker
def call_gemma3n_api(prompt: str, system_prompt: str = None) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})
    messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})

    payload = {
        "model": "ai/gemma3n",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": -1
    }

    res = session.post("http://localhost:12434/engines/v1/chat/completions", json=payload)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]




def call_openrouter_api(prompt: str, system_prompt: str = None) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        res = session.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Lỗi gọi OpenRouter:", e)



def call_llm_studio_api(prompt: str, system_prompt: str = None) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})
    messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": -1 # Không giới hạn số token trả về
    }

    res = session.post("http://localhost:1234/v1/chat/completions", json=payload)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]


