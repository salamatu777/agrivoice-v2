from fastapi import APIRouter, Request, Response
from app.config import settings

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.whatsapp_verify_token:
            return Response(content=challenge, status_code=200)
    return Response(status_code=403)

@router.post("/webhook")
async def handle_whatsapp_message(request: Request):
    # This is a stub for handling incoming whatsapp voice messages.
    # In a full implementation, you'd download the audio from the WhatsApp media URL,
    # pass it to pipeline.process_audio, and send back text + audio.
    data = await request.json()
    return {"status": "success"}
