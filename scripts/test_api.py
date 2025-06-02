from openai import OpenAI
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
project_id = os.getenv('OPENAI_PROJECT_ID', 'proj_q9HWIMPFxlHs4MBuauU0aYie')

print(f"API Key: {api_key[:10]}... (скрыт)")
print(f"Project ID: {project_id}")

# Инициализируем клиент
client = OpenAI(
    api_key=api_key,
    project=project_id
)

try:
    # Тестовый запрос
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Привет! Это тестовое сообщение."}]
    )
    print("\nОтвет от API:")
    print(response.choices[0].message.content)
    print("\nТест успешно пройден!")
except Exception as e:
    print(f"\nОшибка при выполнении запроса: {str(e)}") 