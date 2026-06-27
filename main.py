import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELNYX_API_KEY = os.environ.get("TELNYX_API_KEY")
TELNYX_BASE = "https://api.telnyx.com/v2/calls"

SYSTEM_PROMPT = """You are Vilo, a warm and genuinely curious AI companion calling to check in.

Your goals on this call:
- Greet them warmly by name.
- Ask how they're doing today, and actually listen.
- Keep the conversation light, supportive, and conversational. Short turns, not monologues.
- If they want to wrap up, thank them and end the call gracefully.

Keep responses brief and natural, like a real phone call - not a recitation."""

# track conversation history per call so the AI has context turn to turn
conversations = {}

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
        print("FULL RESPONSE:", data)  # still logs to Render, just doesn't get spoken
        return "Sorry, I'm having trouble connecting right now. Let's try again in a bit!"
    return data["choices"][0]["message"]["content"]

def telnyx_action(call_control_id, action, payload=None):
    url = f"{TELNYX_BASE}/{call_control_id}/actions/{action}"
    headers = {"Authorization": f"Bearer {TELNYX_API_KEY}"}
    r = requests.post(url, headers=headers, json=payload or {}, timeout=10)
    print(f"Telnyx {action} ->", r.status_code, r.text)
    return r

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    event = request.json["data"]
    event_type = event["event_type"]
    call_control_id = event["payload"]["call_control_id"]

    if event_type == "call.initiated":
        telnyx_action(call_control_id, "answer")

    elif event_type == "call.answered":
        conversations[call_control_id] = []
        telnyx_action(call_control_id, "speak", {
            "payload": "Hi! This is Vilo calling to check in. How are you doing today?",
            "voice": "female",
            "language": "en-US"
        })
        telnyx_action(call_control_id, "transcription_start", {
            "language": "en",
            "transcription_engine": "Telnyx"
        })

    elif event_type == "call.transcription":
        t_data = event["payload"].get("transcription_data", {})
        if t_data.get("is_final") and t_data.get("transcript"):
            user_said = t_data["transcript"]
            history = conversations.setdefault(call_control_id, [])
            history.append({"role": "user", "content": user_said})

            reply = ask_ai(history)
            history.append({"role": "assistant", "content": reply})

            telnyx_action(call_control_id, "speak", {
                "payload": reply,
                "voice": "female",
                "language": "en-US"
            })

    elif event_type == "call.hangup":
        conversations.pop(call_control_id, None)

    return "", 200

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
