#!/bin/bash

# JalDoot Installation Script
# This script sets up the JalDoot application with all dependencies

set -e  # Exit on any error

echo "🌊 JalDoot - AI-Powered Groundwater Assistant"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        print_error "Python 3.9 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install system dependencies (for Ubuntu/Debian)
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            python3-dev \
            python3-pip \
            libffi-dev \
            libssl-dev \
            portaudio19-dev \
            gcc \
            g++ \
            curl
        print_success "System dependencies installed"
    else
        print_warning "System package manager not found. Please install dependencies manually:"
        echo "  - python3-dev"
        echo "  - libffi-dev"
        echo "  - libssl-dev"
        echo "  - portaudio19-dev"
        echo "  - gcc"
        echo "  - g++"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p jaldoot/data
    mkdir -p jaldoot/logs
    mkdir -p jaldoot/static/images
    
    print_success "Directories created"
}

# Set up environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# JalDoot Environment Configuration
SECRET_KEY=jaldoot-secret-key-$(date +%s)
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///jaldoot/data/groundwater.db

# OpenAI Configuration (Set your API key here)
OPENAI_API_KEY=your-openai-api-key-here

# IN-GRES Platform Configuration (Set your connection string here)
INGRES_CONNSTR=your-ingres-connection-string
INGRES_BASE_URL=https://ingres.iith.ac.in

# Voice Configuration
VOICE_ENABLED=True
VOICE_LANGUAGE=en

# Language Configuration
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,hinglish

# Development Configuration
MOCK_OPENAI=False
MOCK_INGRES=False
DEBUG_MODE=True
EOF
        print_success "Environment file created (.env)"
        print_warning "Please edit .env file and add your API keys"
    else
        print_warning "Environment file already exists"
    fi
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    python -c "
from jaldoot.app.core.groundwater_service import GroundwaterService
service = GroundwaterService()
print('Database initialized successfully')
"
    
    print_success "Database initialized"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test imports
    python -c "
import jaldoot.app
from jaldoot.app.core.groundwater_service import GroundwaterService
from jaldoot.app.core.language_service import LanguageService
from jaldoot.app.core.visualization_service import VisualizationService
from jaldoot.app.core.voice_service import VoiceService
print('All modules imported successfully')
"
    
    print_success "Installation test passed"
}

# Main installation function
main() {
    echo "Starting JalDoot installation..."
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Install system dependencies
    read -p "Install system dependencies? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_system_deps
    fi
    
    # Create and activate virtual environment
    create_venv
    activate_venv
    
    # Install Python dependencies
    install_python_deps
    
    # Create directories
    create_directories
    
    # Set up environment
    setup_env
    
    # Initialize database
    init_database
    
    # Test installation
    test_installation
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY (for AI features)"
    echo "   - INGRES_CONNSTR (for IN-GRES integration)"
    echo ""
    echo "2. Run the application:"
    echo "   source venv/bin/activate"
    echo "   python run.py"
    echo ""
    echo "3. Access the application:"
    echo "   - Main Interface: http://localhost:5000"
    echo "   - Dashboard: http://localhost:5000/dashboard"
    echo "   - API Health: http://localhost:5000/api/health"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@"
