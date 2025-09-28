"""
JalDoot Voice Routes
Voice interaction endpoints
"""

from flask import Blueprint, request, jsonify
from jaldoot.app.core.voice_service import VoiceService
from jaldoot.app.core.language_service import LanguageService
import base64
import io

voice_bp = Blueprint('voice', __name__)

# Initialize services
voice_service = VoiceService()
language_service = LanguageService()

@voice_bp.route('/status')
def voice_status():
    """Check voice service status"""
    try:
        is_available = voice_service.is_audio_available()
        supported_formats = voice_service.get_supported_formats()
        
        return jsonify({
            'success': True,
            'audio_available': is_available,
            'supported_formats': supported_formats,
            'supported_languages': list(language_service.supported_languages.keys())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/recognize', methods=['POST'])
def recognize_speech():
    """Recognize speech from audio data"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'en')
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Process audio
        result = voice_service.speech_to_text(audio_data, language)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'confidence': result['confidence'],
            'language': result.get('language', language)
        })
        
    except Exception as e:
        return jsonify({'error': f'Speech recognition failed: {str(e)}'}), 500

@voice_bp.route('/recognize-base64', methods=['POST'])
def recognize_speech_base64():
    """Recognize speech from base64 encoded audio data"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio_data', '').strip()
        language = data.get('language', 'en')
        
        if not audio_base64:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio data
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception as e:
            return jsonify({'error': 'Invalid base64 audio data'}), 400
        
        # Process audio
        result = voice_service.speech_to_text(audio_data, language)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'confidence': result['confidence'],
            'language': result.get('language', language)
        })
        
    except Exception as e:
        return jsonify({'error': f'Speech recognition failed: {str(e)}'}), 500

@voice_bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """Synthesize speech from text"""
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
        return jsonify({'error': f'Speech synthesis failed: {str(e)}'}), 500

@voice_bp.route('/audio-info', methods=['POST'])
def get_audio_info():
    """Get information about audio data"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Get audio information
        info = voice_service.get_audio_info(audio_data)
        
        if 'error' in info:
            return jsonify({'error': info['error']}), 400
        
        return jsonify({
            'success': True,
            'audio_info': info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/audio-info-base64', methods=['POST'])
def get_audio_info_base64():
    """Get information about base64 encoded audio data"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio_data', '').strip()
        
        if not audio_base64:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio data
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception as e:
            return jsonify({'error': 'Invalid base64 audio data'}), 400
        
        # Get audio information
        info = voice_service.get_audio_info(audio_data)
        
        if 'error' in info:
            return jsonify({'error': info['error']}), 400
        
        return jsonify({
            'success': True,
            'audio_info': info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/conversation', methods=['POST'])
def voice_conversation():
    """Handle voice conversation with groundwater assistant"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'en')
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Convert speech to text
        speech_result = voice_service.speech_to_text(audio_data, language)
        
        if not speech_result['success']:
            return jsonify({'error': speech_result['error']}), 400
        
        # Process the text query (this would integrate with the main query processing)
        # For now, we'll return the recognized text
        response_text = f"I heard: {speech_result['text']}. This is a placeholder response."
        
        # Convert response to speech
        tts_result = voice_service.text_to_speech(response_text, language)
        
        if not tts_result['success']:
            return jsonify({
                'success': True,
                'recognized_text': speech_result['text'],
                'response_text': response_text,
                'audio_response': None,
                'error': tts_result['error']
            })
        
        return jsonify({
            'success': True,
            'recognized_text': speech_result['text'],
            'response_text': response_text,
            'audio_response': tts_result['audio_data'],
            'format': tts_result['format']
        })
        
    except Exception as e:
        return jsonify({'error': f'Voice conversation failed: {str(e)}'}), 500

@voice_bp.route('/cleanup', methods=['POST'])
def cleanup_voice_service():
    """Clean up voice service resources"""
    try:
        voice_service.cleanup()
        
        return jsonify({
            'success': True,
            'message': 'Voice service cleaned up successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
