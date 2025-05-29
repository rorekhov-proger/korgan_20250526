from openai import OpenAI
from app.config.config import Config

class GPTService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def get_completion(self, user_message):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты ассистент, помогай пользователю."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"GPT Error: {str(e)}") 