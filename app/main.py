from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import io
import os
import wave
import logging
from app.voice_pipeline import VoicePipeline

logger = logging.getLogger(__name__)

try:
    import librosa
    HAVE_LIBROSA = True
except ImportError:
    HAVE_LIBROSA = False

app = FastAPI(title="AgriVoice NAIC 2026", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/outputs", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize pipeline
pipeline = VoicePipeline()

class TextChatRequest(BaseModel):
    query: str
    language: Optional[str] = "ha"

@app.get("/", response_class=HTMLResponse)
def index():
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat(audio: UploadFile = File(...)):
    contents = await audio.read()
    
    audio_data = None
    sr = 16000
    
    if HAVE_LIBROSA:
        try:
            audio_data, sr = librosa.load(io.BytesIO(contents), sr=16000)
        except Exception as e:
            logger.warning(f"Librosa load failed: {e}. Falling back to standard wave reader.")

    if audio_data is None:
        try:
            with wave.open(io.BytesIO(contents), "rb") as wf:
                sr = wf.getframerate()
                n_frames = wf.getnframes()
                raw = wf.readframes(n_frames)
                audio_data = list(raw[:min(len(raw), 32000)])
        except Exception:
            # Fallback dummy buffer for silent/unsupported chunks
            audio_data = [0.0] * 16000

    result = pipeline.process_audio(audio_data, sr)
    return result

@app.post("/api/chat-text")
async def chat_text(req: TextChatRequest):
    result = pipeline.process_text(req.query, req.language)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
