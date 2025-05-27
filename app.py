from flask import Flask

app = Flask(__name__)

@app.route("/login")
def login():
    return "Страница входа"

@app.route("/logout")
def logout():
    return "Вы вышли из системы"

@app.route("/home")
def home():
    return "Добро пожаловать домой!"

if __name__ == "__main__":
    app.run(debug=True)

#pip install -r requirements.txt