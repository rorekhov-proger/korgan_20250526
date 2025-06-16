import os
from datetime import datetime
from typing import List, Dict, Optional

def save_markdown(content: str, filename: Optional[str] = None) -> str:
    """
    Сохраняет Markdown-файл в папку static/uploads и возвращает относительный путь для скачивания.
    """
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    if not filename:
        filename = f"protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    file_path = os.path.join(uploads_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"/static/uploads/{filename}"

def generate_protocol_markdown(data: Dict, mode: str = 'full') -> str:
    """
    Генерирует Markdown для протокола. mode: 'full' или 'fast'.
    Не выводит пустые строки и поля.
    """
    lines = []
    # Заголовок
    if data.get('protocol_number'):
        lines.append(f"# Протокол №{data.get('protocol_number')}")
    else:
        lines.append(f"# Протокол")
    # Основные поля
    if mode == 'full':
        if data.get('protocol_name'):
            lines.append(f"**Наименование:** {data.get('protocol_name')}")
    if data.get('protocol_date'):
        lines.append(f"**Дата:** {data.get('protocol_date')}")
    if mode == 'full' and data.get('chairman'):
        lines.append(f"**Председатель:** {data.get('chairman')}")
    if mode == 'full' and data.get('content'):
        lines.append(f"**Содержимое:** {data.get('content')}")
    if mode == 'full' and data.get('control'):
        lines.append(f"**Контроль:** {data.get('control')}")
    lines.append("\n## Список поручений\n")
    for i, task in enumerate(data.get('tasks', []), 1):
        if not task.get('task_text'):
            continue
        lines.append(f"{i}. **Поручение:** {task.get('task_text')}")
        if task.get('responsible'):
            lines.append(f"   - **Ответственный:** {task.get('responsible')}")
        if mode == 'full' and task.get('co_executors'):
            lines.append(f"   - **Соисполнители:** {', '.join(task.get('co_executors', []))}")
        if mode == 'full' and task.get('protocol_basis'):
            lines.append(f"   - **Основание:** {task.get('protocol_basis')}")
        if mode == 'full' and task.get('periodicity'):
            lines.append(f"   - **Периодичность:** {task.get('periodicity')}")
        if mode == 'full' and task.get('note'):
            lines.append(f"   - **Примечание:** {task.get('note')}")
        if task.get('deadline'):
            lines.append(f"   - **Срок:** {task.get('deadline')}")
        lines.append("")
    # Удаляем лишние пустые строки
    result = '\n'.join([l for l in lines if l.strip()])
    return result
