"""
JalDoot Main Routes
Main web interface routes
"""

from flask import Blueprint, render_template, request, jsonify, session
from jaldoot.app.core.groundwater_service import GroundwaterService
from jaldoot.app.core.language_service import LanguageService
from jaldoot.app.core.visualization_service import VisualizationService
from jaldoot.app.core.voice_service import VoiceService
import time

main_bp = Blueprint('main', __name__)

# Initialize services
groundwater_service = GroundwaterService()
language_service = LanguageService()
visualization_service = VisualizationService()
voice_service = VoiceService()

@main_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with groundwater data overview"""
    # Get available regions and years
    regions = groundwater_service.get_available_regions()
    years = groundwater_service.get_available_years()
    
    return render_template('dashboard.html', 
                         regions=regions, 
                         years=years)

@main_bp.route('/query', methods=['POST'])
def query_groundwater():
    """Handle groundwater queries"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        language = data.get('language', 'en')
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        start_time = time.time()
        
        # Detect language if not specified
        if language == 'auto':
            language = language_service.detect_language(user_query)
        
        # Extract location and year information
        location_info = language_service.extract_location_info(user_query, language)
        year = language_service.extract_year_info(user_query)
        
        # Default to current year if not specified
        if not year:
            year = 2024
        
        # Get region from location info
        region = location_info.get('region')
        if not region:
            # Try to extract region from query
            for available_region in groundwater_service.get_available_regions():
                if available_region.lower() in user_query.lower():
                    region = available_region
                    break
        
        if not region:
            return jsonify({
                'error': 'Please specify a region or location in your query',
                'suggestions': groundwater_service.get_available_regions()
            }), 400
        
        # Fetch groundwater data
        groundwater_data = groundwater_service.fetch_groundwater_data(
            region, year, location_info.get('district')
        )
        
        if not groundwater_data:
            return jsonify({
                'message': f'No groundwater data found for {region} in {year}',
                'suggestions': {
                    'regions': groundwater_service.get_available_regions(),
                    'years': groundwater_service.get_available_years(region)
                }
            }), 404
        
        # Get regional metadata
        regional_metadata = groundwater_service.get_regional_metadata(region)
        
        # Create visualizations
        dashboard_charts = visualization_service.create_comprehensive_dashboard(
            groundwater_data, region, year
        )
        
        # Generate AI response
        ai_response = _generate_ai_response(
            user_query, groundwater_data, regional_metadata, language
        )
        
        response_time = time.time() - start_time
        
        # Log the query
        groundwater_service.log_query(
            user_query, language, ai_response, region, year, response_time
        )
        
        return jsonify({
            'success': True,
            'query': user_query,
            'language': language,
            'region': region,
            'year': year,
            'data': groundwater_data,
            'metadata': regional_metadata,
            'ai_response': ai_response,
            'visualizations': dashboard_charts,
            'response_time': response_time
        })
        
    except Exception as e:
        return jsonify({'error': f'Query processing failed: {str(e)}'}), 500

@main_bp.route('/voice/process', methods=['POST'])
def process_voice():
    """Process voice input"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'en')
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Process audio file
        result = voice_service.process_audio_file(audio_file, language)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'confidence': result['confidence'],
            'language': result.get('language', language)
        })
        
    except Exception as e:
        return jsonify({'error': f'Voice processing failed: {str(e)}'}), 500

@main_bp.route('/voice/speak', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Convert text to speech
        result = voice_service.text_to_speech(text, language)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'audio_data': result['audio_data'],
            'format': result['format']
        })
        
    except Exception as e:
        return jsonify({'error': f'Text-to-speech failed: {str(e)}'}), 500

@main_bp.route('/regions')
def get_regions():
    """Get available regions"""
    try:
        regions = groundwater_service.get_available_regions()
        return jsonify({'regions': regions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/years/<region>')
def get_years(region):
    """Get available years for a region"""
    try:
        years = groundwater_service.get_available_years(region)
        return jsonify({'years': years})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/data/<region>/<int:year>')
def get_region_data(region, year):
    """Get groundwater data for a specific region and year"""
    try:
        data = groundwater_service.fetch_groundwater_data(region, year)
        metadata = groundwater_service.get_regional_metadata(region)
        
        return jsonify({
            'data': data,
            'metadata': metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _generate_ai_response(query: str, data: list, metadata: dict, language: str) -> str:
    """Generate AI response based on query and data"""
    try:
        # This would integrate with OpenAI or other AI service
        # For now, we'll create a simple response based on the data
        
        if not data:
            return language_service.format_response(
                "No groundwater data available for the specified region and year.",
                language
            )
        
        # Calculate basic statistics
        measurements = [d['measurement'] for d in data if d['measurement'] is not None]
        
        if not measurements:
            return language_service.format_response(
                "Groundwater data is available but measurements are not recorded.",
                language
            )
        
        avg_level = sum(measurements) / len(measurements)
        min_level = min(measurements)
        max_level = max(measurements)
        
        # Create response based on language
        if language == 'hi':
            response = f"""
            {metadata['region'] if metadata else 'इस क्षेत्र'} में {len(data)} भूजल रिकॉर्ड मिले हैं।
            औसत भूजल स्तर: {avg_level:.2f} मीटर
            न्यूनतम स्तर: {min_level:.2f} मीटर
            अधिकतम स्तर: {max_level:.2f} मीटर
            """
        elif language == 'hinglish':
            response = f"""
            {metadata['region'] if metadata else 'Is region'} mein {len(data)} groundwater records mile hain.
            Average groundwater level: {avg_level:.2f} meter
            Minimum level: {min_level:.2f} meter
            Maximum level: {max_level:.2f} meter
            """
        else:
            response = f"""
            Found {len(data)} groundwater records for {metadata['region'] if metadata else 'this region'}.
            Average groundwater level: {avg_level:.2f} meters
            Minimum level: {min_level:.2f} meters
            Maximum level: {max_level:.2f} meters
            """
        
        return language_service.format_response(response, language)
        
    except Exception as e:
        return f"Error generating response: {str(e)}"
