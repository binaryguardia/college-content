#!/usr/bin/env python3
"""
JalDoot - AI-Powered Groundwater Assistant
Simple runner script for development
"""

import os
import sys
from dotenv import load_dotenv

# Set the OpenAI API key directly
os.environ['OPENAI_API_KEY'] = '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'

# Add the parent directory of 'jaldoot' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'jaldoot')))

def main():
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['MOCK_OPENAI'] = 'False'  # Use real OpenAI API
    os.environ['SECRET_KEY'] = 'jaldoot-secret-key-2024'
    os.environ['DATABASE_URL'] = 'sqlite:///jaldoot/data/groundwater.db'
    os.environ['VOICE_ENABLED'] = 'True'
    os.environ['DEFAULT_LANGUAGE'] = 'en'
    os.environ['SUPPORTED_LANGUAGES'] = 'en,hi,hinglish'
    
    try:
        from jaldoot.app import create_app
        app = create_app('development')
        
        print("🌊 JalDoot - AI-Powered Groundwater Assistant")
        print("=" * 50)
        print("🚀 Starting development server...")
        print("🔧 Debug mode: ON")
        print("🤖 OpenAI API: ENABLED")
        print("📱 Access: http://localhost:5000")
        print("📊 Dashboard: http://localhost:5000/dashboard")
        print("🔍 API Health: http://localhost:5000/api/health")
        print("=" * 50)
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory and dependencies are installed")
        print("💡 Try: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
