// Обработка всех кнопок
const buttons = document.querySelectorAll('button');
buttons.forEach(button => {
    button.addEventListener('click', () => {
        alert(`Вы нажали: "${button.innerText}"`);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const uploadBtn = document.getElementById("upload-btn");
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatWindow = document.getElementById("chat-window");

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
                    botMsg.className = "message bot";
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
        userMsg.innerText = `🗣 ${text}`;
        chatWindow.appendChild(userMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        userInput.value = "";

        try {
            const res = await fetch("/gpt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            const botMsg = document.createElement("div");
            botMsg.className = "message bot";
            botMsg.innerText = data.reply || "Ошибка получения ответа от GPT";
            chatWindow.appendChild(botMsg);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } catch (err) {
            alert("Произошла ошибка при отправке сообщения.");
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});
