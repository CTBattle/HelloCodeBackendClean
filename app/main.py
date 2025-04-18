import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from openai.types import CompletionUsage
from openai import RateLimitError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

last_request_time = 0
cooldown_seconds = 1

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    global last_request_time
    now = time.time()
    if now - last_request_time < cooldown_seconds:
        return {"error": "Too many requests. Please wait a moment."}
    
    last_request_time = now

    # Format user prompt
    prompt = f"Write {req.language} code to: {req.prompt}"
    if req.useFString and req.language.lower() == "python":
        prompt += ". Use f-strings where possible."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return {"code": response.choices[0].message.content}
    except RateLimitError:
        return {"error": "Rate limit hit. Try again shortly."}
    except Exception as e:
        return {"error": str(e)}
