import os
import openai

class OpenAIService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key)

    def extract_protocol(self, text: str) -> str:
        prompt = (
            "Раздели текст на максимальное количество отдельных поручений. "
            "Если в одном предложении несколько поручений — выделяй каждое как отдельное. "
            "Для каждого поручения выдели строго все поля в формате:\n"
            "Поручение: [текст]\n"
            "- Ответственный: [имя]\n"
            "- Срок: [дата]\n"
            "- Соисполнители: [имена, через запятую, если есть]\n"
            "- Основание: [текст, если есть]\n"
            "- Периодичность: [текст, если есть]\n"
            "- Примечание: [текст, если есть]\n"
            "\nПример:\n"
            "Поручение: Подготовить отчет о продажах за месяц.\n"
            "- Ответственный: Иван Иванов\n"
            "- Срок: 2025-06-20\n"
            "- Соисполнители: Петр Петров, Анна Смирнова\n"
            "- Основание: Запрос руководства\n"
            "- Периодичность: Ежемесячно\n"
            "- Примечание: Учитывать данные за последний квартал.\n"
            "\nТеперь обработай следующий текст:\n"
        )
        messages = [
            {"role": "system", "content": "Ты помощник для структурирования протоколов и поручений."},
            {"role": "user", "content": prompt + "\n" + text}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            max_tokens=1200
        )
        return response.choices[0].message.content
