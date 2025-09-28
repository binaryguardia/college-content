#!/usr/bin/env python3
"""
JalDoot Development Server
Quick development server with auto-reload and debugging
"""

import os
import sys
from flask import Flask

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Development server entry point"""
    
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['MOCK_OPENAI'] = 'True'  # Use mock for development
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from jaldoot.app import create_app
        
        # Create Flask application
        app = create_app('development')
        
        print("🌊 JalDoot Development Server")
        print("=" * 40)
        print("🚀 Starting development server...")
        print("🔧 Debug mode: ON")
        print("🤖 Mock OpenAI: ON")
        print("📱 Access: http://localhost:5000")
        print("=" * 40)
        
        # Run with auto-reload
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory and dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
