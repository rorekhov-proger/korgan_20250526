import os
import openai

class OpenAIService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key)

    def extract_protocol(self, text: str) -> str:
        prompt = (
            "Выдели поручения строго в формате:\n"
            "Поручение: [текст].\n- Ответственный: [имя].\n- Срок: [дата].\n"
            "Без вводных и заключительных фраз.\n"
            "Если тебе не хватает каких-то данных, задай дополнительные вопросы."
        )
        messages = [
            {"role": "system", "content": "Ты помощник для структурирования протоколов и поручений."},
            {"role": "user", "content": prompt + "\n" + text}
        ]
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            max_tokens=1200
        )
        return response.choices[0].message.content
