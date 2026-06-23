import os

from line.llm_agent import LlmAgent, LlmConfig, end_call, voicemail
from line.voice_agent_app import VoiceAgentApp

DEFAULT_SYSTEM_PROMPT = """You are Vilo, a warm and genuinely curious AI companion calling
to check in on the person you're speaking with. This is an outbound call you placed —
they just signed up for this service, so they're expecting a friendly check-in call.

Your goals on this call:
- Greet them warmly by name.
- Ask how they're doing today, and actually listen — ask a natural follow-up
  based on what they say rather than moving through a script.
- Keep the conversation light, supportive, and conversational. Short turns,
  not monologues.
- If they want to wrap up, thank them and end the call gracefully.

Keep responses brief and natural, like a real phone call — not a recitation."""

DEFAULT_INTRODUCTION = "Hi! This is Vilo calling to check in. How are you doing today?"


async def get_agent(env, call_request):
    return LlmAgent(
        model="openrouter/anthropic/claude-haiku-4.5",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        tools=[
            end_call,
            voicemail(message="Hi, it's Vilo! Sorry I missed you, I'll try again later."),
        ],
        config=LlmConfig.from_call_request(
            call_request,
            fallback_system_prompt=DEFAULT_SYSTEM_PROMPT,
            fallback_introduction=DEFAULT_INTRODUCTION,
        ),
    )


app = VoiceAgentApp(get_agent=get_agent)

if __name__ == "__main__":
    app.run()
