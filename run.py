from app import create_app
import os
from app.config.config import Config
import logging

try:
    # Создаем экземпляр приложения
    app = create_app()
    
    if __name__ == "__main__":
        logging.basicConfig(
            level=logging.DEBUG,  # Установлено DEBUG для более подробных логов
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler()  # Вывод логов в консоль
            ]
        )
        
        # Проверяем наличие необходимых переменных окружения
        missing_vars = Config.validate_config()
        if missing_vars:
            print("ВНИМАНИЕ! Отсутствуют следующие переменные окружения:")
            for var in missing_vars:
                print(f"- {var}")
            print("\nПожалуйста, настройте их в файле .env")
        
        # Получаем настройки из переменных окружения или используем значения по умолчанию
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'
        
        print(f"\nЗапуск приложения на http://{host}:{port}")
        print(f"Режим отладки: {'включен' if debug else 'выключен'}")
        
        app.run(
            host=host,
            port=port,
            debug=debug
        )
except Exception as e:
    print(f"\nОШИБКА при запуске приложения: {str(e)}")
    raise