
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    # Initialize Flask app
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # Configure API keys
    app.config['HUGGINGFACE_API_TOKEN'] = os.getenv('HUGGINGFACE_API_TOKEN')
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    app.config['HUGGINGFACE_API_URL'] = "https://api-inference.huggingface.co/models/hadson0/distilbert-email-productivity-classifier-pt"

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app