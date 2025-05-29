from flask import Flask
from app.config.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    config_class.init_app(app)
    
    from app.routes.main_routes import main
    app.register_blueprint(main)
    
    return app 