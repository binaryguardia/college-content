#!/usr/bin/env python3
"""
JalDoot - AI-Powered Groundwater Assistant
Main application entry point
"""

import os
import sys
from flask import Flask

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jaldoot.app import create_app
from jaldoot.config.settings import config

def main():
    """Main application entry point"""
    
    # Get configuration from environment
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask application
    app = create_app(config_name)
    
    # Get host and port from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("🌊 JalDoot - AI-Powered Groundwater Assistant")
    print("=" * 60)
    print(f"🚀 Starting server on http://{host}:{port}")
    print(f"🔧 Environment: {config_name}")
    print(f"🐛 Debug mode: {debug}")
    print(f"🗄️  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print(f"🤖 OpenAI API: {'Configured' if app.config.get('OPENAI_API_KEY') else 'Not configured'}")
    print(f"🏛️  IN-GRES: {'Configured' if app.config.get('INGRES_CONNSTR') else 'Not configured'}")
    print("=" * 60)
    print("📱 Access the application at:")
    print(f"   • Main Interface: http://{host}:{port}")
    print(f"   • Dashboard: http://{host}:{port}/dashboard")
    print(f"   • API Health: http://{host}:{port}/api/health")
    print("=" * 60)
    
    # Run the application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
