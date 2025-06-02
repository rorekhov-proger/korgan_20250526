// Инициализация приложения
document.addEventListener("DOMContentLoaded", function () {
    const uploadBtn = document.getElementById("upload-btn");
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatWindow = document.getElementById("chat-window");
    const modelSelect = document.createElement("select");
    
    // Add model options
    modelSelect.innerHTML = `
        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        <option value="gpt-4">GPT-4</option>
        <option value="gpt-4-turbo">GPT-4 Turbo</option>
    `;
    modelSelect.className = "model-select";
    document.querySelector(".input-area").insertBefore(modelSelect, sendBtn);

    // Add styles for model select
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
    `;
    document.head.appendChild(style);

    // Загрузка аудио-файла
    if (uploadBtn) {
        uploadBtn.addEventListener("click", () => {
            const input = document.createElement("input");
            input.type = "file";
            input.accept = "audio/*";
            input.click();

            input.onchange = async () => {
                const file = input.files[0];
                if (!file) return;

                const userMsg = document.createElement("div");
                userMsg.className = "message user";
                userMsg.innerText = `📤 Отправлен файл: ${file.name}`;
                chatWindow.appendChild(userMsg);

                const formData = new FormData();
                formData.append("audio_file", file);

                try {
                    const res = await fetch("/upload", { method: "POST", body: formData });
                    const data = await res.json();
                    const botMsg = document.createElement("div");
                    botMsg.className = "message assistant";
                    botMsg.innerText = data.text || "Ошибка распознавания";
                    chatWindow.appendChild(botMsg);
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                } catch (err) {
                    alert("Произошла ошибка при загрузке файла.");
                }
            };
        });
    }

    // Отправка текста в GPT
    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        const userMsg = document.createElement("div");
        userMsg.className = "message user";
        userMsg.innerText = text;
        chatWindow.appendChild(userMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        userInput.value = "";

        try {
            const res = await fetch("/gpt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    message: text,
                    model: modelSelect.value 
                })
            });
            const data = await res.json();
            const botMsg = document.createElement("div");
            botMsg.className = "message assistant";
            botMsg.innerText = data.reply || "Ошибка получения ответа от GPT";
            chatWindow.appendChild(botMsg);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } catch (err) {
            alert("Произошла ошибка при отправке сообщения.");
        }
    }

    // Функция для создания нового чата
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

            if (!response.ok) {
                throw new Error('Ошибка при создании чата');
            }

            const chat = await response.json();
            // Обновляем список чатов
            await loadChats();
            // Переключаемся на новый чат
            switchToChat(chat.id);
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось создать новый чат');
        }
    }

    // Функция для загрузки списка чатов
    async function loadChats() {
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) {
                throw new Error('Ошибка при загрузке чатов');
            }
            const chats = await response.json();
            
            // Очищаем список чатов
            const chatList = document.querySelector('.chat-list');
            // Оставляем только параграф "Чаты:"
            const chatTitle = chatList.querySelector('p');
            chatList.innerHTML = '';
            chatList.appendChild(chatTitle);
            
            // Добавляем чаты в список
            chats.forEach(chat => {
                const button = document.createElement('button');
                button.textContent = chat.title;
                button.dataset.chatId = chat.id;
                button.onclick = () => switchToChat(chat.id);
                
                // Добавляем обработчик правого клика
                button.addEventListener('contextmenu', (e) => {
                    e.preventDefault(); // Отменяем стандартное контекстное меню
                    showContextMenu(e, chat);
                });
                
                chatList.appendChild(button);
            });
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    // Функция для переключения на чат
    async function switchToChat(chatId) {
        try {
            const response = await fetch(`/api/chats/${chatId}/messages`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке сообщений');
            }
            const messages = await response.json();
            
            // Очищаем окно чата
            chatWindow.innerHTML = '';
            
            // Добавляем сообщения в окно чата
            messages.forEach(message => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${message.role}`;
                messageDiv.textContent = message.content;
                chatWindow.appendChild(messageDiv);
            });
            
            // Прокручиваем к последнему сообщению
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

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
            const response = await fetch(`/api/chats/${chatId}`, {
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
