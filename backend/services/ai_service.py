"""
AI Service — Groq (Llama 3.1)
"""
from groq import Groq
from config import Config


class AIService:
    def __init__(self):
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.history = []
        print("✅ AI Service initialized")

    def chat(self, message, web_context=None):
        try:
            messages = [{
                "role": "system",
                "content": (
                    "You are a kitchen assistant. "
                    "Rules: "
                    "1. Reply in 1-5 short sentences MAX. "
                    "2. Be direct. No fluff, no greetings, no filler. "
                    "3. If giving a recipe, list only key steps in bullet points. "
                    "4. Use simple everyday language. "
                    "5. Never say 'Great question' or 'I'd be happy to help'. "
                    "6. Just answer."
                )
            }]

            for msg in self.history[-Config.MAX_HISTORY_MESSAGES:]:
                messages.append(msg)

            content = message
            if web_context:
                content = (
                    f"Info:\n{web_context}\n\n"
                    f"Question: {message}\n\n"
                    "Answer in 1-2 sentences."
                )

            messages.append({"role": "user", "content": content})

            completion = self.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=messages,
                temperature=0.6,
                max_tokens=150,
            )

            response = completion.choices[0].message.content.strip()

            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": response})
            if len(self.history) > Config.MAX_HISTORY_MESSAGES * 2:
                self.history = self.history[-Config.MAX_HISTORY_MESSAGES:]

            print("✅ AI response:", response[:80])
            return response

        except Exception as e:
            print(f"❌ AI error: {e}")
            return f"Error: {str(e)[:80]}"

    def clear_history(self):
        self.history = []