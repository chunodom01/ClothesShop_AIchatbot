import logging
import requests
from fastapi import APIRouter, Request, Response

from app.config import settings
from app.messenger import send_message
from app.agent import reply

logger = logging.getLogger(__name__)
router = APIRouter()

SHEETDB_API = "https://sheetdb.io/api/v1/1jwvbhi2iyqpb2"

@router.post("/webhook")
async def receive_message(request: Request) -> Response:
    payload = await request.json()
    logger.info("Incoming webhook payload: %s", payload)

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            message = event.get("message", {})

            if message.get("is_echo"):
                continue

            sender_id = event.get("sender", {}).get("id")
            message_text = message.get("text")
            if not sender_id or not message_text:
                continue

            logger.info("Message from %s: %s", sender_id, message_text)

            # --- Save USER message to Google Sheet ---
            try:
                requests.post(SHEETDB_API, json={
                    "data": [{"SenderID": sender_id, "Role": "User", "Message": message_text}]
                })
                logger.info("Saved user message to SheetDB.")
            except Exception as e:
                logger.error("Failed to save user message: %s", e)

            # --- Generate reply and send back to user ---
            reply_text = await reply(sender_id, message_text)
            await send_message(sender_id, reply_text)

            # --- Save BOT reply to Google Sheet ---
            try:
                requests.post(SHEETDB_API, json={
                    "data": [{"SenderID": sender_id, "Role": "Bot", "Message": reply_text}]
                })
                logger.info("Saved bot reply to SheetDB.")
            except Exception as e:
                logger.error("Failed to save bot reply: %s", e)

    return Response(content="ok", status_code=200)
