import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client (API key is read automatically from environment variable)
client = OpenAI()

# Define request model
class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple cooldown to avoid spamming
last_request_time = 0
cooldown_seconds = 1

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    global last_request_time
    now = time.time()
    if now - last_request_time < cooldown_seconds:
        return {"error": "You're sending requests too quickly. Please wait a moment."}
    last_request_time = now

    system_prompt = f"Generate {req.language} code for this prompt: '{req.prompt}'"
    if req.language.lower() == "python" and req.useFString:
        system_prompt += " using Python f-strings"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.prompt}
            ]
        )
        return {"code": response.choices[0].message.content.strip()}

    except RateLimitError:
        return {"code": "# ⚠️ OpenAI rate limit hit.\nprint('Hello from HelloCode')"}

    except Exception as e:
        return {"error": f"⚠️ Server error: {str(e)}"}
