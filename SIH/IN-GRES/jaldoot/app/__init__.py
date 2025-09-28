"""
JalDoot - AI-Powered Groundwater Assistant
Main Flask Application Factory
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
socketio = SocketIO()
cors = CORS()

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'jaldoot-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///jaldoot.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # OpenAI Configuration
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    app.config['INGRES_CONNSTR'] = os.getenv('INGRES_CONNSTR')
    
    # Initialize extensions
    cors.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from jaldoot.app.routes.main import main_bp
    from jaldoot.app.routes.api import api_bp
    from jaldoot.app.routes.voice import voice_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(voice_bp, url_prefix='/voice')
    
    return app
