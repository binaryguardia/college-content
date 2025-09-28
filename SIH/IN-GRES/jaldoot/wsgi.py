"""
JalDoot WSGI Application
Production WSGI entry point
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jaldoot.app import create_app

# Create Flask application
application = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    application.run()
