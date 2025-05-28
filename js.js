// Задание 2:Обработка всех кнопок
const buttons = document.querySelectorAll('button');
buttons.forEach(button => {
    button.addEventListener('click', () => {
        alert(`Вы нажали: "${button.innerText}"`);
    });
});

// Задание 3: Загрузка аудио-файла и вывод текста в чат
document.addEventListener("DOMContentLoaded", function () {
    const uploadBtn = document.getElementById("upload-btn");
    const chatWindow = document.getElementById("chat-window");

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
                    const res = await fetch("/upload", {
                        method: "POST",
                        body: formData
                    });

                    const data = await res.json();
                    console.log("Ответ сервера:", data);

                    const botMsg = document.createElement("div");
                    botMsg.className = "message bot";
                    botMsg.innerText = data.text || "Ошибка распознавания";
                    chatWindow.appendChild(botMsg);

                    chatWindow.scrollTop = chatWindow.scrollHeight;

                } catch (err) {
                    console.error("Ошибка при загрузке файла:", err);
                    alert("Произошла ошибка при загрузке файла.");
                }
            };
        });
    }
});
