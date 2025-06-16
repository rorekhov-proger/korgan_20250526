import re
from typing import Dict, Any, List
import sys

def extract_protocol_data(text: str, mode: str = 'full') -> Dict[str, Any]:
    """
    Улучшенный парсер для извлечения данных протокола и поручений из текста (поддержка реальных примеров).
    Если не найдено поручений — используется OpenAI GPT для структурирования.
    """
    protocol = {
        'protocol_number': '',
        'protocol_name': '',
        'protocol_date': '',
        'chairman': '',
        'content': '',
        'control': '',
        'tasks': []
    }
    try:
        # Извлечение номера протокола
        m = re.search(r'ПРОТОКОЛ №([\w/]+)', text, re.IGNORECASE)
        if m:
            protocol['protocol_number'] = m.group(1)
        # Извлечение даты (ищем YYYY-MM-DD или DD.MM.YYYY)
        m = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4})', text)
        if m:
            protocol['protocol_date'] = m.group(1)
        # Извлечение председателя
        m = re.search(r'Председательствовал:?\s*([^\n]+)', text, re.IGNORECASE)
        if m:
            protocol['chairman'] = m.group(1).strip()
        # Извлечение присутствующих (можно добавить в content или отдельное поле)
        m = re.search(r'Присутствовали:?\s*([^\n]+)', text, re.IGNORECASE)
        if m:
            protocol['content'] = 'Присутствовали: ' + m.group(1).strip()
        # Извлечение поручений (расширенный шаблон)
        task_pattern = re.compile(
            r'Поручение: (.+?)(?:\n|$)\s*- Ответственный: (.+?)(?:\n|$)(?:\s*- Соисполнители: (.+?)(?:\n|$))?\s*- Срок:? (.+?)(?:\n|$)(?:\s*- Периодичность: (.+?)(?:\n|$))?',
            re.DOTALL | re.IGNORECASE
        )
        for match in task_pattern.finditer(text):
            task = {
                'task_text': match.group(1).strip(),
                'responsible': match.group(2).strip(),
                'co_executors': [x.strip() for x in (match.group(3) or '').split(',') if x.strip()],
                'deadline': match.group(4).strip(),
                'periodicity': (match.group(5) or '').strip(),
                'protocol_basis': '',
                'note': ''
            }
            protocol['tasks'].append(task)
        # Альтернативное извлечение поручений по списку (если не сработал шаблон)
        if not protocol['tasks']:
            try:
                from app.services.openai_service import OpenAIService
                gpt = OpenAIService()
                print('[DEBUG] Отправка текста в OpenAI:', file=sys.stderr)
                print(text, file=sys.stderr)
                gpt_structured = gpt.extract_protocol(text)
                print('[DEBUG] Ответ OpenAI:', file=sys.stderr)
                print(gpt_structured, file=sys.stderr)
                for match in task_pattern.finditer(gpt_structured):
                    task = {
                        'task_text': match.group(1).strip(),
                        'responsible': match.group(2).strip(),
                        'co_executors': [x.strip() for x in (match.group(3) or '').split(',') if x.strip()],
                        'deadline': match.group(4).strip(),
                        'periodicity': (match.group(5) or '').strip(),
                        'protocol_basis': '',
                        'note': ''
                    }
                    protocol['tasks'].append(task)
            except Exception as e:
                print(f"[OpenAI extract error] {e}", file=sys.stderr)
    except Exception as e:
        print(f"[extract_protocol_data error] {e}", file=sys.stderr)
    # Для быстрого режима только задачи
    if mode == 'fast':
        protocol['tasks'] = protocol['tasks'][:3]
        return protocol
    return protocol
