"""
JalDoot Configuration Settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'jaldoot-secret-key-2024')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///jaldoot/data/groundwater.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    
    # IN-GRES Platform Configuration
    INGRES_CONNSTR = os.getenv('INGRES_CONNSTR')
    INGRES_BASE_URL = os.getenv('INGRES_BASE_URL', 'https://ingres.iith.ac.in')
    INGRES_API_KEY = os.getenv('INGRES_API_KEY')
    
    # Voice Configuration
    VOICE_ENABLED = os.getenv('VOICE_ENABLED', 'True').lower() == 'true'
    VOICE_LANGUAGE = os.getenv('VOICE_LANGUAGE', 'en')
    
    # Visualization Configuration
    CHART_THEME = os.getenv('CHART_THEME', 'default')
    CHART_COLORS = os.getenv('CHART_COLORS', '#2E86AB,#A23B72,#F18F01,#C73E1D,#FFD23F').split(',')
    
    # Language Configuration
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
    SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'en,hi,hinglish').split(',')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'jaldoot.log')
    
    # Security Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    
    # Performance Configuration
    MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', '1000'))
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))
    
    # Development Configuration
    MOCK_OPENAI = os.getenv('MOCK_OPENAI', 'False').lower() == 'true'
    MOCK_INGRES = os.getenv('MOCK_INGRES', 'False').lower() == 'true'
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production settings
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MOCK_OPENAI = True
    MOCK_INGRES = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
