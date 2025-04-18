import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI, OpenAIError

# Initialize OpenAI client (1.3.8 syntax)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request body model
class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

# FastAPI app setup
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
last_request_time = 0
cooldown_seconds = 1

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    global last_request_time
    now = time.time()
    if now - last_request_time < cooldown_seconds:
        return {"error": "⏳ Slow down! Try again in a second."}
    last_request_time = now

    system_prompt = f"Generate {req.language} code for this: {req.prompt}"
    if req.language.lower() == "python" and req.useFString:
        system_prompt += " using f-strings"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.prompt}
            ]
        )
        return {"code": response.choices[0].message.content}
    
    except OpenAIError as e:
        return {"error": f"⚠️ OpenAI error: {str(e)}"}
    
    except Exception as e:
        return {"error": f"⚠️ Server error: {str(e)}"}
