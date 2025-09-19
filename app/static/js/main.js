// Инициализация приложения
document.addEventListener("DOMContentLoaded", function () {
    const uploadBtn = document.getElementById("upload-btn");
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatWindow = document.getElementById("chat-window");
    const modelSelect = document.createElement("select");

    modelSelect.innerHTML = `
        <option value="ollama:llama3.1:8b">Ollama: Llama 3.1 (8B)</option>
        <option value="ollama:qwen2.5:7b-instruct">Ollama: Qwen 2.5 (7B Instruct)</option>
        <option value="gpt-5-nano">GPT-5 Nano</option>
        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        <option value="gpt-4">GPT-4</option>
        <option value="gpt-4-turbo">GPT-4 Turbo</option>
    `;
    modelSelect.className = "model-select";
    document.querySelector(".input-area").insertBefore(modelSelect, sendBtn);

    const style = document.createElement("style");
    style.textContent = `
        .model-select {
            padding: 8px;
            border-radius: 8px;
            border: 1px solid #444;
            background-color: #2c2c2c;
            color: #fff;
            margin-right: 10px;
        }
        .chat-list {
            background: #232323;
            border-radius: 12px;
            padding: 12px 8px 12px 8px;
            margin: 10px 0 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .chat-list p {
            margin: 0 0 8px 8px;
            color: #aaa;
            font-size: 1.05em;
        }
        .chat-item {
            padding: 10px 16px;
            margin: 4px 0;
            border-radius: 8px;
            background: #292929;
            color: #fff;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
            font-size: 1.08em;
            border: 1px solid transparent;
        }
        .chat-item.active {
            background: #3498db;
            color: #fff;
            border: 1px solid #217dbb;
            font-weight: bold;
        }
        .chat-item:hover {
            background: #313a4a;
            color: #fff;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #ccc;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            vertical-align: middle;
            margin-right: 8px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        #block-overlay {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background: rgba(0,0,0,0.65) !important;
            z-index: 99999 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: not-allowed !important;
        }
    `;
    document.head.appendChild(style);

    if (uploadBtn) {
        uploadBtn.addEventListener("click", () => {
            const input = document.createElement("input");
            input.type = "file";
            input.accept = "audio/*";
            input.click();

            input.onchange = async () => {
                const file = input.files[0];
                if (!file) return;

                // Получаем chat_id из активного чата
                const activeChat = document.querySelector('.chat-item.active');
                const chatId = activeChat ? activeChat.dataset.chatId : null;
                if (!chatId) {
                    alert('Не выбран чат!');
                    return;
                }

                // Добавляем сообщение пользователя о файле сразу
                const userMsg = document.createElement("div");
                userMsg.className = "message user";
                userMsg.innerText = `📤 Отправлен файл: ${file.name}`;
                chatWindow.appendChild(userMsg);

                // Добавляем индикатор загрузки сразу
                const loadingMsg = document.createElement("div");
                loadingMsg.className = "message assistant loading-msg";
                loadingMsg.innerHTML = '<span class="spinner"></span> Распознаём аудио...';
                chatWindow.appendChild(loadingMsg);
                chatWindow.scrollTop = chatWindow.scrollHeight;

                const formData = new FormData();
                formData.append("audio_file", file);
                formData.append("chat_id", chatId);
                formData.append("model", modelSelect.value);

                // === Затемняющий оверлей и блокировка ===
                let overlay = document.createElement('div');
                overlay.id = 'block-overlay';
                overlay.style = `
                    position: fixed;
                    top: 0; left: 0; width: 100vw; height: 100vh;
                    background: rgba(0,0,0,0.45);
                    z-index: 2000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: not-allowed;
                `;
                overlay.innerHTML = `<div style='color:#fff;font-size:1.5em;'><span class="spinner"></span>Распознаём аудио...</div>`;
                document.body.appendChild(overlay);
                document.body.style.overflow = 'hidden';

                try {
                    const res = await fetch("/upload", { method: "POST", body: formData });
                    const data = await res.json();
                    // После получения текста удаляем индикатор и показываем ответ
                    loadingMsg.remove();
                    if (data.text) {
                        const botMsg = document.createElement("div");
                        botMsg.className = "message assistant";
                        botMsg.innerText = data.text;
                        chatWindow.appendChild(botMsg);
                        chatWindow.scrollTop = chatWindow.scrollHeight;
                    }
                } catch (err) {
                    loadingMsg.remove();
                    alert("Произошла ошибка при загрузке файла.");
                } finally {
                    // Убираем оверлей и возвращаем скролл
                    if (overlay) overlay.remove();
                    document.body.style.overflow = '';
                }
            };
        });
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        const userMsg = document.createElement("div");
        userMsg.className = "message user";
        userMsg.innerText = text;
        chatWindow.appendChild(userMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        userInput.value = "";

        // Получаем chat_id из активного чата
        const activeChat = document.querySelector('.chat-item.active');
        const chatId = activeChat ? activeChat.dataset.chatId : null;
        if (!chatId) {
            alert('Не выбран чат!');
            return;
        }

        try {
            const res = await fetch("/gpt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    message: text,
                    chat_id: chatId, // <-- теперь chat_id передаётся
                    model: modelSelect.value 
                })
            });
            const data = await res.json();
            console.log("[DEBUG] Response from GPT API:", data);
            const botMsg = document.createElement("div");
            botMsg.className = "message assistant";
            botMsg.innerText = data.reply || "Ошибка получения ответа от GPT";
            chatWindow.appendChild(botMsg);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } catch (err) {
            console.error("[ERROR] Произошла ошибка при отправке сообщения:", err);
            alert("Произошла ошибка при отправке сообщения.");
        }
    }

    async function createNewChat() {
        const title = `Новый чат: ${new Date().toLocaleString('ru')}`;
        try {
            const response = await fetch('/api/chats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title })
            });

            // Добавляем диагностику для проверки ответа от API
            console.log('Ответ от API:', response.status, response.statusText);
            const responseBody = await response.text();
            console.log('Тело ответа:', responseBody);

            // Парсим JSON только если статус успешный
            if (response.ok) {
                const chatData = JSON.parse(responseBody);
                console.log('Данные чата:', chatData);

                // Динамически обновляем список чатов
                await loadChats();

                // Через небольшой таймаут выделяем новый чат как активный и открываем его
                setTimeout(() => {
                    const chatItems = document.querySelectorAll('.chat-item');
                    chatItems.forEach(item => {
                        if (item.dataset.chatId == chatData.id) {
                            item.classList.add('active');
                            switchToChat(chatData.id);
                        } else {
                            item.classList.remove('active');
                        }
                    });
                }, 100);
            } else {
                throw new Error('Ошибка при создании чата');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось создать новый чат');
        }
    }
    async function loadChats() {
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) {
                throw new Error('Ошибка при загрузке чатов');
            }
            const chats = await response.json();

            const chatList = document.querySelector('.chat-list');

            const chatTitle = chatList.querySelector('p');
            chatList.innerHTML = '';
            chatList.appendChild(chatTitle);

            chats.forEach(chat => {
                const chatItem = document.createElement('div');
                chatItem.className = 'chat-item';
                chatItem.dataset.chatId = chat.id;
                chatItem.innerText = chat.title;
                chatItem.addEventListener('click', () => switchToChat(chat.id));
                chatItem.addEventListener('contextmenu', (event) => {
                    event.preventDefault();
                    showContextMenu(event, chat);
                });
                chatList.appendChild(chatItem);
            });
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось загрузить список чатов');
        }
    }

    // --- Обновление текущего чата в сайдбаре ---
    function updateCurrentChatTitle(title) {
        const currentChatSpan = document.querySelector('.sidebar .highlight');
        if (currentChatSpan) {
            currentChatSpan.textContent = title || '';
        }
    }

    // Модифицируем switchToChat чтобы обновлять текущий чат
    async function switchToChat(chatId) {
        try {
            const response = await fetch(`/api/chat/${chatId}/messages`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке сообщений чата');
            }
            const messages = await response.json();
            chatWindow.innerHTML = '';
            messages.forEach(msg => {
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${msg.role === 'user' ? 'user' : 'assistant'}`;
                msgDiv.innerText = msg.message;
                chatWindow.appendChild(msgDiv);
            });
            chatWindow.scrollTop = chatWindow.scrollHeight;
            // Обновляем выделение активного чата
            const chatItems = document.querySelectorAll('.chat-item');
            chatItems.forEach(item => item.classList.remove('active'));
            const activeChat = document.querySelector(`.chat-item[data-chat-id='${chatId}']`);
            if (activeChat) {
                activeChat.classList.add('active');
                updateCurrentChatTitle(activeChat.innerText);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось загрузить сообщения чата');
        }
    }

    // При загрузке страницы показываем первый активный чат, если есть
    document.addEventListener('DOMContentLoaded', () => {
        const activeChat = document.querySelector('.chat-item.active');
        if (activeChat) {
            updateCurrentChatTitle(activeChat.innerText);
        }
    });

    // Функция для показа контекстного меню
    function showContextMenu(event, chat) {
        // Удаляем предыдущее меню, если оно есть
        const oldMenu = document.querySelector('.context-menu');
        if (oldMenu) {
            oldMenu.remove();
        }

        // Создаем контекстное меню
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.innerHTML = `
            <div class="menu-item rename">Переименовать</div>
            <div class="menu-item delete">Удалить</div>
        `;

        // Позиционируем меню
        menu.style.left = `${event.pageX}px`;
        menu.style.top = `${event.pageY}px`;

        // Добавляем обработчики
        menu.querySelector('.rename').onclick = () => renameChat(chat);
        menu.querySelector('.delete').onclick = () => deleteChat(chat.id);

        // Добавляем меню на страницу
        document.body.appendChild(menu);

        // Закрываем меню при клике вне его
        document.addEventListener('click', () => {
            menu.remove();
        }, { once: true });
    }

    // Функция для переименования чата
    async function renameChat(chat) {
        const newTitle = prompt('Введите новое название чата:', chat.title);
        if (!newTitle || newTitle === chat.title) return;

        try {
            const response = await fetch(`/api/chats/${chat.id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title: newTitle })
            });

            if (!response.ok) {
                throw new Error('Ошибка при переименовании чата');
            }

            // Обновляем список чатов
            await loadChats();
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось переименовать чат');
        }
    }

    // Функция для удаления чата
    async function deleteChat(chatId) {
        if (!confirm('Вы уверены, что хотите удалить этот чат?')) return;

        try {
            const response = await fetch(`/api/chat/${chatId}`, { // Исправлено на 'chat' вместо 'chats'
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Ошибка при удалении чата');
            }

            // Обновляем список чатов
            await loadChats();
            
            // Очищаем окно чата
            const chatWindow = document.getElementById('chat-window');
            chatWindow.innerHTML = '';
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось удалить чат');
        }
    }

    // Кнопка "Скачать историю"
    const downloadBtn = Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.trim() === 'Скачать историю');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const activeChat = document.querySelector('.chat-item.active');
            const chatId = activeChat ? activeChat.dataset.chatId : null;
            if (!chatId) {
                alert('Не выбран чат!');
                return;
            }
            // Открываем ссылку на скачивание
            window.open(`/chat/${chatId}/download`, '_blank');
        });
    }

    // --- Протокол: обработка кнопок полного/быстрого заполнения ---
    const modeSwitch = document.querySelector('.mode-switch');
    let protocolMode = 'full'; // по умолчанию полное заполнение

    if (modeSwitch) {
        const buttons = modeSwitch.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.addEventListener('click', async function() {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                protocolMode = btn.textContent.includes('Быстрое') ? 'fast' : 'full';
                // Получаем текст последнего распознанного аудио или из чата
                const lastBotMsg = Array.from(chatWindow.querySelectorAll('.message.assistant'))
                    .map(el => el.innerText).filter(Boolean).pop();
                if (!lastBotMsg) {
                    alert('Нет текста для обработки!');
                    return;
                }
                if(protocolMode === 'full') {
                    // Получаем JSON для редактирования
                    const resp = await fetch('/api/protocol/extract_json', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: lastBotMsg, mode: protocolMode })
                    });
                    const data = await resp.json();
                    if(data.protocol_data) {
                        showProtocolModal(data.protocol_data, async (editedData) => {
                            // После редактирования отправляем на генерацию Markdown
                            const resp2 = await fetch('/api/protocol/generate', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ protocol_data: editedData, mode: 'full' })
                            });
                            const d2 = await resp2.json();
                            if(d2.download_url) {
                                const link = document.createElement('a');
                                link.href = d2.download_url;
                                link.target = '_blank';
                                link.textContent = 'Скачать протокол (полный)';
                                chatWindow.appendChild(link);
                                chatWindow.scrollTop = chatWindow.scrollHeight;
                            } else {
                                alert('Ошибка генерации протокола!');
                            }
                        });
                    } else {
                        alert('Ошибка разбора протокола!');
                    }
                } else {
                    // Быстрое заполнение — старый вариант
                    const resp = await fetch('/api/protocol/extract', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: lastBotMsg, mode: protocolMode })
                    });
                    const data = await resp.json();
                    if (data.download_url) {
                        const link = document.createElement('a');
                        link.href = data.download_url;
                        link.target = '_blank';
                        link.textContent = 'Скачать протокол (быстрый)';
                        chatWindow.appendChild(link);
                        chatWindow.scrollTop = chatWindow.scrollHeight;
                    } else {
                        alert('Ошибка генерации протокола!');
                    }
                }
            });
        });
    }
    // --- Модальное окно для редактирования протокола ---
    function showProtocolModal(protocolData, onSave) {
        console.log('[DEBUG] protocolData:', protocolData);
        // Создаём модальное окно
        let modal = document.createElement('div');
        modal.className = 'modal-bg';
        modal.innerHTML = `
        <div class="modal-window">
            <h2>Редактирование протокола</h2>
            <form id="protocol-form">
                <label>Номер протокола: <input name="protocol_number" value="${protocolData.protocol_number || ''}"></label><br>
                <label>Наименование: <textarea name="protocol_name" rows="2">${protocolData.protocol_name || ''}</textarea></label><br>
                <label>Дата: <input name="protocol_date" value="${protocolData.protocol_date || ''}"></label><br>
                <label>Председатель: <input name="chairman" value="${protocolData.chairman || ''}"></label><br>
                <label>Содержимое: <textarea name="content" rows="2">${protocolData.content || ''}</textarea></label><br>
                <label>Контроль: <textarea name="control" rows="2">${protocolData.control || ''}</textarea></label><br>
                <h3>Поручения</h3>
                <div id="tasks-list">
                    ${(protocolData.tasks||[]).map((t,i)=>`
                        <div class="task-block">
                            <b>Поручение ${i+1}</b><br>
                            <label>Текст: <textarea name="task_text_${i}" rows="2">${t.task_text||''}</textarea></label><br>
                            <label>Ответственный: <input name="responsible_${i}" value="${t.responsible||''}"></label><br>
                            <label>Срок: <input name="deadline_${i}" value="${t.deadline||''}"></label><br>
                            <label>Соисполнители: <input name="co_executors_${i}" value="${(t.co_executors||[]).join(', ')}"></label><br>
                            <label>Основание: <input name="protocol_basis_${i}" value="${t.protocol_basis||''}"></label><br>
                            <label>Периодичность: <input name="periodicity_${i}" value="${t.periodicity||''}"></label><br>
                            <label>Примечание: <textarea name="note_${i}" rows="2">${t.note||''}</textarea></label><br>
                        </div>
                    `).join('')}
                </div>
                <button type="submit">Сохранить и скачать</button>
                <button type="button" id="close-modal">Отмена</button>
            </form>
        </div>
        <style>
        .modal-bg { position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center; }
        .modal-window { background:#222;padding:24px 32px;border-radius:12px;max-height:90vh;overflow:auto;color:#fff;min-width:600px; max-width:900px; width:70vw; }
        .modal-window input, .modal-window textarea { width:98%;margin-bottom:6px; font-family:inherit; font-size:1em; }
        .modal-window textarea { resize:vertical; min-height:38px; max-height:300px; }
        .task-block { border:1px solid #444;padding:8px 12px;margin-bottom:10px;border-radius:8px;background:#292929; }
        .modal-window button { margin:8px 8px 0 0; }
        </style>
        `;
        document.body.appendChild(modal);
        // Закрытие
        modal.querySelector('#close-modal').onclick = () => modal.remove();
        // Сохранение
        modal.querySelector('#protocol-form').onsubmit = function(e) {
            e.preventDefault();
            // Собираем данные
            const fd = new FormData(this);
            let result = {
                protocol_number: fd.get('protocol_number'),
                protocol_name: fd.get('protocol_name'),
                protocol_date: fd.get('protocol_date'),
                chairman: fd.get('chairman'),
                content: fd.get('content'),
                control: fd.get('control'),
                tasks: []
            };
            let i = 0;
            while(fd.has('task_text_'+i)) {
                result.tasks.push({
                    task_text: fd.get('task_text_'+i),
                    responsible: fd.get('responsible_'+i),
                    deadline: fd.get('deadline_'+i),
                    co_executors: (fd.get('co_executors_'+i)||'').split(',').map(s=>s.trim()).filter(Boolean),
                    protocol_basis: fd.get('protocol_basis_'+i),
                    periodicity: fd.get('periodicity_'+i),
                    note: fd.get('note_'+i)
                });
                i++;
            }
            onSave(result);
            modal.remove();
        };
    }

    // Добавляем обработчики событий
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    // Находим все кнопки "Новый чат" и добавляем обработчик
    const newChatButtons = document.querySelectorAll('button');
    newChatButtons.forEach(button => {
        if (button.textContent === 'Новый чат') {
            button.onclick = createNewChat;
        }
    });

    // Загружаем список чатов при загрузке страницы
    loadChats();
});
