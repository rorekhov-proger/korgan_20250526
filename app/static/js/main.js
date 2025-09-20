// Инициализация приложения с улучшениями UI (тема, тосты, markdown, dnd)
document.addEventListener("DOMContentLoaded", function () {
    const uploadBtn = document.getElementById("upload-btn");
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatWindow = document.getElementById("chat-window");
    const modelSelect = document.createElement("select");

    // Тема: загрузка и переключение
    const themeToggle = document.getElementById('theme-toggle');
    const applyTheme = (t) => document.documentElement.setAttribute('data-theme', t);
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
    if (themeToggle) {
        themeToggle.textContent = savedTheme === 'light' ? 'Тёмная' : 'Светлая';
        themeToggle.onclick = () => {
            const curr = document.documentElement.getAttribute('data-theme') || 'dark';
            const next = curr === 'light' ? 'dark' : 'light';
            applyTheme(next);
            localStorage.setItem('theme', next);
            themeToggle.textContent = next === 'light' ? 'Тёмная' : 'Светлая';
            showToast(`Тема: ${next === 'light' ? 'светлая' : 'тёмная'}`, 'info');
        };
    }

    // Тосты
    const toastContainer = document.getElementById('toast-container');
    function showToast(message, type='info', timeout=3000) {
        if (!toastContainer) { alert(message); return; }
        const t = document.createElement('div');
        t.className = `toast ${type}`;
        t.textContent = message;
        toastContainer.appendChild(t);
        requestAnimationFrame(()=> t.classList.add('show'));
        setTimeout(()=>{
            t.classList.remove('show');
            setTimeout(()=> t.remove(), 200);
        }, timeout);
    }

    // Markdown + highlight
    function renderMarkdown(html) {
        try {
            if (window.marked) {
                marked.setOptions({
                    breaks: true,
                    highlight: function(code, lang) {
                        if (window.hljs && lang && hljs.getLanguage(lang)) {
                            return hljs.highlight(code, { language: lang }).value;
                        }
                        if (window.hljs) return hljs.highlightAuto(code).value;
                        return code;
                    }
                });
                return marked.parse(html);
            }
        } catch (e) {
            console.warn('MD render error', e);
        }
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    // Селектор моделей
    modelSelect.innerHTML = `
        <option value="ollama:llama3.1:8b">Ollama: Llama 3.1 (8B)</option>
        <option value="ollama:qwen2.5:7b-instruct">Ollama: Qwen 2.5 (7B Instruct)</option>
        <option value="gpt-5-nano">GPT-5 Nano</option>
        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        <option value="gpt-4">GPT-4</option>
        <option value="gpt-4-turbo">GPT-4 Turbo</option>
    `;
    modelSelect.className = "model-select";
    document.querySelector(".input-area").insertBefore(modelSelect, userInput);

    // Локальные стили: спиннер и оверлей
    const style = document.createElement("style");
    style.textContent = `
        .model-select { padding: 8px; border-radius: 8px; border: 1px solid var(--btn-border); background-color: var(--input-bg); color: var(--text-color); margin-right: 10px; }
        .spinner { display:inline-block; width:20px; height:20px; border:3px solid #ccc; border-top:3px solid #3498db; border-radius:50%; animation: spin 1s linear infinite; vertical-align:middle; margin-right: 8px; }
        @keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }
        #block-overlay { position: fixed !important; top:0 !important; left:0 !important; width:100vw !important; height:100vh !important; background: rgba(0,0,0,0.65) !important; z-index: 99999 !important; display:flex !important; align-items:center !important; justify-content:center !important; cursor:not-allowed !important; }
    `;
    document.head.appendChild(style);

    // Рендер сообщения с аватаром, баблом и временем
    function timeNow() { return new Date().toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' }); }
    function addMessage(role, content, opts={ markdown: false, loading: false }) {
        const wrap = document.createElement('div');
        wrap.className = `message ${role}` + (opts.loading ? ' typing' : '');
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = role === 'user' ? 'Вы' : 'ИИ';
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        if (opts.loading) {
            bubble.innerHTML = `ИИ печатает… <span class="dots"><span></span><span></span><span></span></span>`;
        } else {
            bubble.innerHTML = opts.markdown ? renderMarkdown(content) : (content || '');
        }
        const t = document.createElement('span');
        t.className = 'time';
        t.textContent = timeNow();
        bubble.appendChild(document.createElement('br'));
        bubble.appendChild(t);
        wrap.appendChild(avatar);
        wrap.appendChild(bubble);
        chatWindow.appendChild(wrap);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return wrap;
    }

    // Drag & Drop на футер
    const inputArea = document.querySelector('.input-area');
    if (inputArea) {
        ['dragenter','dragover'].forEach(evt => inputArea.addEventListener(evt, (e)=>{ e.preventDefault(); inputArea.classList.add('drop-hover'); }));
        ['dragleave','drop'].forEach(evt => inputArea.addEventListener(evt, (e)=>{ e.preventDefault(); inputArea.classList.remove('drop-hover'); }));
        inputArea.addEventListener('drop', (e)=>{ const file = e.dataTransfer.files && e.dataTransfer.files[0]; if (file) handleAudioUpload(file); });
    }

    // Загрузка аудио (общая логика)
    async function handleAudioUpload(file) {
        const activeChat = document.querySelector('.chat-item.active');
        const chatId = activeChat ? activeChat.dataset.chatId : null;
        if (!chatId) { showToast('Не выбран чат!', 'error'); return; }

        addMessage('user', `📤 Отправлен файл: ${file.name}`);
        const loadingMsg = addMessage('assistant', '', { loading: true });

        const formData = new FormData();
        formData.append("audio_file", file);
        formData.append("chat_id", chatId);
        formData.append("model", modelSelect.value);

        let overlay = document.createElement('div');
        overlay.id = 'block-overlay';
        overlay.innerHTML = `<div style='color:#fff;font-size:1.5em;'><span class="spinner"></span>Распознаём аудио...</div>`;
        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';
        try {
            const res = await fetch("/upload", { method: "POST", body: formData });
            const data = await res.json();
            loadingMsg.remove();
            if (data.text) {
                addMessage('assistant', data.text, { markdown: true });
            } else {
                showToast('Сервис не вернул текст', 'error');
            }
        } catch (err) {
            loadingMsg.remove();
            console.error(err);
            showToast('Произошла ошибка при загрузке файла.', 'error');
        } finally {
            overlay.remove();
            document.body.style.overflow = '';
        }
    }

    // Кнопка загрузки аудио
    if (uploadBtn) {
        uploadBtn.addEventListener("click", () => {
            const input = document.createElement("input");
            input.type = "file";
            input.accept = "audio/*";
            input.click();
            input.onchange = async () => { const file = input.files[0]; if (!file) return; handleAudioUpload(file); };
        });
    }

    // Отправка сообщения
    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;
        addMessage('user', text);
        userInput.value = "";

        const activeChat = document.querySelector('.chat-item.active');
        const chatId = activeChat ? activeChat.dataset.chatId : null;
        if (!chatId) { showToast('Не выбран чат!', 'error'); return; }

        const typing = addMessage('assistant', '', { loading: true });

        try {
            const res = await fetch("/gpt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, chat_id: chatId, model: modelSelect.value })
            });
            const data = await res.json();
            typing.remove();
            addMessage('assistant', data.reply || "Ошибка получения ответа от GPT", { markdown: true });
        } catch (err) {
            console.error("[ERROR] Произошла ошибка при отправке сообщения:", err);
            typing.remove();
            showToast("Произошла ошибка при отправке сообщения.", 'error');
        }
    }

    // Создать новый чат
    async function createNewChat() {
        const title = `Новый чат: ${new Date().toLocaleString('ru')}`;
        try {
            const response = await fetch('/api/chats', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title }) });
            const responseBody = await response.text();
            if (response.ok) {
                const chatData = JSON.parse(responseBody);
                await loadChats();
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
                showToast('Чат создан', 'success');
            } else { throw new Error('Ошибка при создании чата'); }
        } catch (error) {
            console.error('Ошибка:', error);
            showToast('Не удалось создать новый чат', 'error');
        }
    }

    // Загрузить список чатов
    async function loadChats() {
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) throw new Error('Ошибка при загрузке чатов');
            const chats = await response.json();
            const chatList = document.querySelector('.chat-list .chat-items') || document.querySelector('.chat-list');
            chatList.innerHTML = '';
            chats.forEach(chat => {
                const chatItem = document.createElement('div');
                chatItem.className = 'chat-item';
                chatItem.dataset.chatId = chat.id;
                chatItem.innerText = chat.title;
                chatItem.addEventListener('click', () => switchToChat(chat.id));
                chatItem.addEventListener('contextmenu', (event) => { event.preventDefault(); showContextMenu(event, chat); });
                chatList.appendChild(chatItem);
            });
        } catch (error) { console.error('Ошибка:', error); showToast('Не удалось загрузить список чатов', 'error'); }
    }

    // Обновление текущего чата в сайдбаре
    function updateCurrentChatTitle(title) {
        const currentChatSpan = document.querySelector('.sidebar .highlight');
        if (currentChatSpan) currentChatSpan.textContent = title || '';
    }

    // Переключение чата
    async function switchToChat(chatId) {
        try {
            const response = await fetch(`/api/chat/${chatId}/messages`);
            if (!response.ok) throw new Error('Ошибка при загрузке сообщений чата');
            const messages = await response.json();
            chatWindow.innerHTML = '';
            messages.forEach(msg => { addMessage(msg.role === 'user' ? 'user' : 'assistant', msg.message, { markdown: msg.role !== 'user' }); });
            chatWindow.scrollTop = chatWindow.scrollHeight;
            const chatItems = document.querySelectorAll('.chat-item');
            chatItems.forEach(item => item.classList.remove('active'));
            const activeChat = document.querySelector(`.chat-item[data-chat-id='${chatId}']`);
            if (activeChat) { activeChat.classList.add('active'); updateCurrentChatTitle(activeChat.innerText); }
        } catch (error) { console.error('Ошибка:', error); showToast('Не удалось загрузить сообщения чата', 'error'); }
    }

    // При первой загрузке показываем заголовок активного чата, если он уже отмечен
    const preActiveChat = document.querySelector('.chat-item.active');
    if (preActiveChat) { updateCurrentChatTitle(preActiveChat.innerText); }

    // Контекстное меню
    function showContextMenu(event, chat) {
        const oldMenu = document.querySelector('.context-menu');
        if (oldMenu) oldMenu.remove();
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.innerHTML = `
            <div class="menu-item rename">Переименовать</div>
            <div class="menu-item delete">Удалить</div>
        `;
        menu.style.left = `${event.pageX}px`;
        menu.style.top = `${event.pageY}px`;
        menu.querySelector('.rename').onclick = () => renameChat(chat);
        menu.querySelector('.delete').onclick = () => deleteChat(chat.id);
        document.body.appendChild(menu);
        document.addEventListener('click', () => { menu.remove(); }, { once: true });
    }

    async function renameChat(chat) {
        const newTitle = prompt('Введите новое название чата:', chat.title);
        if (!newTitle || newTitle === chat.title) return;
        try {
            const response = await fetch(`/api/chats/${chat.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: newTitle }) });
            if (!response.ok) throw new Error('Ошибка при переименовании чата');
            await loadChats();
        } catch (error) { console.error('Ошибка:', error); showToast('Не удалось переименовать чат', 'error'); }
    }

    async function deleteChat(chatId) {
        if (!confirm('Вы уверены, что хотите удалить этот чат?')) return;
        try {
            const response = await fetch(`/api/chat/${chatId}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Ошибка при удалении чата');
            await loadChats();
            chatWindow.innerHTML = '';
        } catch (error) { console.error('Ошибка:', error); showToast('Не удалось удалить чат', 'error'); }
    }

    // Кнопка "Скачать историю"
    const downloadBtn = Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.trim() === 'Скачать историю');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const activeChat = document.querySelector('.chat-item.active');
            const chatId = activeChat ? activeChat.dataset.chatId : null;
            if (!chatId) { showToast('Не выбран чат!', 'error'); return; }
            window.open(`/chat/${chatId}/download`, '_blank');
        });
    }

    // Режим протокола
    const modeSwitch = document.querySelector('.mode-switch');
    let protocolMode = 'full';
    if (modeSwitch) {
        const buttons = modeSwitch.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.addEventListener('click', async function() {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                protocolMode = btn.textContent.includes('Быстрое') ? 'fast' : 'full';
                const lastBotMsg = Array.from(chatWindow.querySelectorAll('.message.assistant .bubble'))
                    .map(el => el.innerText).filter(Boolean).pop();
                if (!lastBotMsg) { showToast('Нет текста для обработки!', 'error'); return; }
                if(protocolMode === 'full') {
                    const resp = await fetch('/api/protocol/extract_json', {
                        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: lastBotMsg, mode: protocolMode })
                    });
                    const data = await resp.json();
                    if(data.protocol_data) {
                        showProtocolModal(data.protocol_data, async (editedData) => {
                            const resp2 = await fetch('/api/protocol/generate', {
                                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ protocol_data: editedData, mode: 'full' })
                            });
                            const d2 = await resp2.json();
                            if(d2.download_url) {
                                const link = document.createElement('a');
                                link.href = d2.download_url; link.target = '_blank'; link.textContent = 'Скачать протокол (полный)';
                                chatWindow.appendChild(link); chatWindow.scrollTop = chatWindow.scrollHeight;
                                showToast('Готово: протокол сформирован', 'success');
                            } else { showToast('Ошибка генерации протокола!', 'error'); }
                        });
                    } else { showToast('Ошибка разбора протокола!', 'error'); }
                } else {
                    const resp = await fetch('/api/protocol/extract', {
                        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: lastBotMsg, mode: protocolMode })
                    });
                    const data = await resp.json();
                    if (data.download_url) {
                        const link = document.createElement('a');
                        link.href = data.download_url; link.target = '_blank'; link.textContent = 'Скачать протокол (быстрый)';
                        chatWindow.appendChild(link); chatWindow.scrollTop = chatWindow.scrollHeight;
                        showToast('Протокол (быстрый) готов', 'success');
                    } else { showToast('Ошибка генерации протокола!', 'error'); }
                }
            });
        });
    }

    // --- Модальное окно для редактирования протокола ---
    function showProtocolModal(protocolData, onSave) {
        console.log('[DEBUG] protocolData:', protocolData);
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
        modal.querySelector('#close-modal').onclick = () => modal.remove();
        modal.querySelector('#protocol-form').onsubmit = function(e) {
            e.preventDefault();
            const fd = new FormData(this);
            let result = { protocol_number: fd.get('protocol_number'), protocol_name: fd.get('protocol_name'), protocol_date: fd.get('protocol_date'), chairman: fd.get('chairman'), content: fd.get('content'), control: fd.get('control'), tasks: [] };
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

    // Обработчики
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", (e) => { if (e.key === "Enter") { sendMessage(); } });
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) newChatBtn.onclick = createNewChat;
    loadChats();
});
