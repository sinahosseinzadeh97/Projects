from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    return app 