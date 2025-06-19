import re
from typing import Dict, Any, List
import logging
from app.services.gpt_service import GPTService

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
            r'Поручение: (.+?)(?:\n|$)'  # Поручение
            r'\s*- Ответственный: (.+?)(?:\n|$)'  # Ответственный
            r'\s*- Срок:? (.+?)(?:\n|$)'  # Срок
            r'\s*- Соисполнители: (.*?)(?:\n|$)'  # Соисполнители
            r'\s*- Основание: (.*?)(?:\n|$)'  # Основание
            r'\s*- Периодичность: (.*?)(?:\n|$)'  # Периодичность
            r'\s*- Примечание: (.*?)(?:\n|$)',  # Примечание
            re.DOTALL | re.IGNORECASE
        )
        # Альтернативное разбиение, если шаблон не сработал
        fallback_pattern = re.compile(r'Поручение:', re.IGNORECASE)
        if not task_pattern.search(text) and fallback_pattern.search(text):
            tasks = text.split('Поручение:')
            for raw_task in tasks[1:]:
                task_lines = raw_task.strip().split('\n')
                task = {
                    'task_text': task_lines[0].strip(),
                    'responsible': '',
                    'deadline': '',
                    'co_executors': [],
                    'protocol_basis': '',
                    'periodicity': '',
                    'note': ''
                }
                protocol['tasks'].append(task)
        else:
            for match in task_pattern.finditer(text):
                task = {
                    'task_text': match.group(1).strip(),
                    'responsible': match.group(2).strip(),
                    'deadline': match.group(3).strip(),
                    'co_executors': [x.strip() for x in (match.group(4) or '').split(',') if x.strip()],
                    'protocol_basis': (match.group(5) or '').strip(),
                    'periodicity': (match.group(6) or '').strip(),
                    'note': (match.group(7) or '').strip(),
                }
                protocol['tasks'].append(task)
        # Альтернативное извлечение поручений по списку (если не сработал шаблон)
        if not protocol['tasks']:
            try:
                gpt = GPTService()
                logging.info('[extract_protocol_data] Отправка текста в OpenAI')
                gpt_structured = gpt.get_completion([
                    {"role": "system", "content": "Ты помощник для структурирования протоколов и поручений."},
                    {"role": "user", "content": text}
                ], model="gpt-4o")
                logging.info('[extract_protocol_data] Ответ OpenAI получен')
                for match in task_pattern.finditer(gpt_structured):
                    task = {
                        'task_text': match.group(1).strip(),
                        'responsible': match.group(2).strip(),
                        'co_executors': [x.strip() for x in (match.group(4) or '').split(',') if x.strip()],
                        'protocol_basis': (match.group(5) or '').strip(),
                        'periodicity': (match.group(6) or '').strip(),
                        'note': (match.group(7) or '').strip(),
                        'deadline': match.group(3).strip(),
                    }
                    protocol['tasks'].append(task)
            except Exception as e:
                logging.error(f"[OpenAI extract error] {e}")
    except Exception as e:
        logging.error(f"[extract_protocol_data error] {e}")
    # После основного парсинга — пост-обработка для защиты от склеивания
    for task in protocol['tasks']:
        # Если в поле 'responsible' попали маркеры других полей или начало следующего поручения — обрезаем
        for marker in ['- Срок:', '- Соисполнители:', '- Основание:', '- Периодичность:', '- Примечание:', 'Поручение:']:
            if marker in task['responsible']:
                task['responsible'] = task['responsible'].split(marker)[0].strip()
    # Для быстрого режима больше не ограничиваем количество задач
    return protocol
