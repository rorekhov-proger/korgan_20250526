import requests

def test_add_message():
    url = "http://127.0.0.1:5000/api/chats/1/messages"
    payload = {
        "role": "user",
        "message": "Тестовое сообщение"
    }
    response = requests.post(url, json=payload)
    print("Статус ответа:", response.status_code)
    print("Ответ:", response.json())

def test_create_chat():
    url = "http://127.0.0.1:5000/api/chats"
    payload = {
        "title": "Тестовый чат"
    }
    response = requests.post(url, json=payload)
    print("Статус ответа:", response.status_code)
    print("Ответ:", response.json())

if __name__ == "__main__":
    test_add_message()
    test_create_chat()
