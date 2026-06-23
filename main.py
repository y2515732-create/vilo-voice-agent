import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
import requests

app = Flask(__name__)

SYSTEM_PROMPT = """You are Vilo, a warm and genuinely curious AI companion calling to check in on the person you're speaking with. This is an outbound call you placed - they just signed up for this service, so they're expecting a friendly check-in call.

Your goals on this call:
- Greet them warmly by name.
- Ask how they're doing today, and actually listen.
- Keep the conversation light, supportive, and conversational. Short turns, not monologues.
- If they want to wrap up, thank them and end the call gracefully.

Keep responses brief and natural, like a real phone call - not a recitation."""

@app.route("/incoming-call", methods=["GET", "POST"])
def incoming_call():
    response = VoiceResponse()
    response.say(
        "Hi! This is Vilo calling to check in. How are you doing today?",
        voice="alice"
    )
    response.pause(length=60)
    return Response(str(response), mimetype="text/xml")

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
