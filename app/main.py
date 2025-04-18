import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

app = FastAPI()

# Enable CORS for all origins (helpful for web/mobile)
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
        return {"error": "⏳ Too fast. Wait a second."}
    last_request_time = now

    system_prompt = f"Generate {req.language} code for this: {req.prompt}"
    if req.language.lower() == "python" and req.useFString:
        system_prompt += " using f-strings"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.prompt}
            ]
        )
        return {"code": response.choices[0].message["content"]}

    except openai.error.OpenAIError as e:
        return {"error": f"OpenAI error: {str(e)}"}

    except Exception as e:
        return {"error": f"Server error: {str(e)}"}
