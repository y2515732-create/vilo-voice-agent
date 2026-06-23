import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests

app = Flask(__name__)

SYSTEM_PROMPT = """You are Vilo, a warm and genuinely curious AI companion calling to check in.

Your goals on this call:
- Greet them warmly by name.
- Ask how they're doing today, and actually listen.
- Keep the conversation light, supportive, and conversational. Short turns, not monologues.
- If they want to wrap up, thank them and end the call gracefully.

Keep responses brief and natural, like a real phone call - not a recitation."""

def ask_ai(conversation_history):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
        json={
            "model": "anthropic/claude-sonnet-4-5",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
        },
        timeout=10,
    )
    data = response.json()
    if "choices" not in data:
        print("FULL RESPONSE:", data)
        return "Sorry, I had a little trouble there. Could you say that again?"
    return data["choices"][0]["message"]["content"]
    
@app.route("/incoming-call", methods=["GET", "POST"])
def incoming_call():
    response = VoiceResponse()
    gather = Gather(input="speech", action="/handle-speech", method="POST", speechTimeout="auto")
    gather.say("Hi! This is Vilo calling to check in. How are you doing today?", voice="alice")
    response.append(gather)
    response.say("Sorry, I didn't catch that. Talk to you soon!", voice="alice")
    return Response(str(response), mimetype="text/xml")

@app.route("/handle-speech", methods=["POST"])
def handle_speech():
    user_said = request.form.get("SpeechResult", "")
    reply = ask_ai([{"role": "user", "content": user_said}])

    response = VoiceResponse()
    gather = Gather(input="speech", action="/handle-speech", method="POST", speechTimeout="auto")
    gather.say(reply, voice="alice")
    response.append(gather)
    response.say("Take care, talk soon!", voice="alice")
    return Response(str(response), mimetype="text/xml")

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
