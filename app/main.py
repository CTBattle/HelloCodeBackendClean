import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

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
        return {"error": "Too many requests. Please wait a second."}

    last_request_time = now

    # Example generation using prompt and options
    code = f"print('hello world')"
    return {"result": f"```{req.language.lower()}\n{code}\n```"}
