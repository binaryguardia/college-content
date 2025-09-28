# JalDoot - AI-Powered Groundwater Assistant

🌊 **JalDoot** is an intelligent groundwater assistant designed for the IN-GRES (India Ground Water Resource Estimation System) platform developed by IIT Hyderabad. It provides voice and text interaction capabilities in multiple languages (English, Hindi, and Hinglish) with advanced data visualization and AI-powered insights.

## 🚀 Features

### 🎤 Voice Interaction
- **Speech-to-Text**: Convert voice queries to text in multiple languages
- **Text-to-Speech**: Get audio responses in your preferred language
- **Real-time Processing**: Instant voice recognition and response

### 🌍 Multilingual Support
- **English**: Full support for English queries and responses
- **Hindi**: Native Hindi language support with proper formatting
- **Hinglish**: Mixed Hindi-English language support for natural conversation

### 📊 Data Visualization
- **Interactive Charts**: Line charts, bar charts, pie charts, and histograms
- **Real-time Updates**: Dynamic visualizations based on query results
- **Export Capabilities**: Download charts and data in various formats

### 🤖 AI-Powered Analysis
- **Intelligent Queries**: Natural language processing for groundwater data queries
- **Contextual Responses**: AI-generated summaries and insights
- **Pattern Recognition**: Identify trends and patterns in groundwater data

### 🏛️ IN-GRES Integration
- **Direct Database Access**: Connect to IN-GRES platform databases
- **Real-time Data**: Fetch latest groundwater measurements
- **Regional Coverage**: Access data from multiple Indian states and districts

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jaldoot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Main Interface: http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard
   - API Health: http://localhost:5000/api/health

### Docker Installation

1. **Using Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

2. **Using Docker directly**
   ```bash
   docker build -t jaldoot .
   docker run -p 5000:5000 jaldoot
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///jaldoot/data/groundwater.db

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# IN-GRES Platform Configuration
INGRES_CONNSTR=your-ingres-connection-string
INGRES_BASE_URL=https://ingres.iith.ac.in
INGRES_API_KEY=your-ingres-api-key

# Voice Configuration
VOICE_ENABLED=True
VOICE_LANGUAGE=en

# Language Configuration
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,hinglish
```

### Database Setup

The application uses SQLite by default for development. For production, configure a PostgreSQL or MySQL database:

```env
DATABASE_URL=postgresql://username:password@localhost/jaldoot
```

## 📱 Usage

### Web Interface

1. **Main Dashboard**
   - Access comprehensive groundwater data
   - Use filters for specific regions and years
   - View interactive charts and visualizations

2. **Query Interface**
   - Type or speak your questions
   - Get AI-powered responses
   - View data visualizations

3. **Voice Interaction**
   - Click the microphone button
   - Speak your query in your preferred language
   - Get audio responses

### API Endpoints

#### Groundwater Data
- `GET /api/groundwater/regions` - Get all available regions
- `GET /api/groundwater/statistics/{region}/{year}` - Get regional statistics
- `POST /api/groundwater/search` - Search with advanced filters

#### Voice Processing
- `POST /voice/recognize` - Convert speech to text
- `POST /voice/synthesize` - Convert text to speech
- `POST /voice/conversation` - Full voice conversation

#### Language Processing
- `POST /api/language/detect` - Detect language of text
- `POST /api/language/translate` - Translate text
- `POST /api/language/extract-location` - Extract location info

### Example Queries

**English:**
- "Show me groundwater data for Punjab Ropar 2024"
- "What is the average groundwater level in Maharashtra?"
- "Compare groundwater levels across different regions"

**Hindi:**
- "पंजाब रोपड़ 2024 का भूजल डेटा दिखाएं"
- "महाराष्ट्र में औसत भूजल स्तर क्या है?"

**Hinglish:**
- "Punjab Ropar 2024 ka groundwater data dikhaiye"
- "Maharashtra mein average groundwater level kya hai?"

## 🏗️ Project Structure

```
jaldoot/
├── app/                    # Main application package
│   ├── core/              # Core services
│   │   ├── groundwater_service.py
│   │   ├── language_service.py
│   │   ├── visualization_service.py
│   │   └── voice_service.py
│   ├── routes/            # Route handlers
│   │   ├── main.py
│   │   ├── api.py
│   │   └── voice.py
│   └── __init__.py
├── config/                # Configuration files
│   └── settings.py
├── static/                # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # HTML templates
│   ├── index.html
│   └── dashboard.html
├── data/                  # Data storage
├── logs/                  # Log files
├── requirements.txt       # Python dependencies
├── run.py                # Application entry point
├── wsgi.py               # WSGI entry point
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Docker Compose configuration
```

## 🔧 Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### Running Tests

```bash
python -m pytest tests/
```

### Code Formatting

```bash
black jaldoot/
flake8 jaldoot/
```

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=your-production-secret-key
   ```

2. **Use a production WSGI server**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
   ```

3. **Set up reverse proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IIT Hyderabad** for the IN-GRES platform
- **OpenAI** for AI capabilities
- **Flask** community for the web framework
- **Plotly** for visualization capabilities

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Roadmap

- [ ] Mobile app development
- [ ] Advanced AI models integration
- [ ] Real-time data streaming
- [ ] Multi-user authentication
- [ ] Advanced analytics dashboard
- [ ] API rate limiting and caching
- [ ] Integration with more data sources

---

**JalDoot** - Making groundwater data accessible to everyone! 🌊🤖
