"""
JalDoot API Routes
REST API endpoints for groundwater data
"""

from flask import Blueprint, request, jsonify
from jaldoot.app.core.groundwater_service import GroundwaterService
from jaldoot.app.core.language_service import LanguageService
from jaldoot.app.core.visualization_service import VisualizationService
import time

api_bp = Blueprint('api', __name__)

# Initialize services
groundwater_service = GroundwaterService()
language_service = LanguageService()
visualization_service = VisualizationService()

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'JalDoot API',
        'version': '1.0.0',
        'timestamp': time.time()
    })

@api_bp.route('/groundwater/search', methods=['POST'])
def search_groundwater():
    """Search groundwater data with advanced filters"""
    try:
        data = request.get_json()
        
        region = data.get('region')
        year = data.get('year')
        district = data.get('district')
        state = data.get('state')
        well_type = data.get('well_type')
        aquifer_type = data.get('aquifer_type')
        min_level = data.get('min_level')
        max_level = data.get('max_level')
        
        # Fetch data
        if region and year:
            groundwater_data = groundwater_service.fetch_groundwater_data(region, year, district)
        else:
            return jsonify({'error': 'Region and year are required'}), 400
        
        # Apply filters
        filtered_data = groundwater_data
        
        if state:
            filtered_data = [d for d in filtered_data if d.get('state', '').lower() == state.lower()]
        
        if well_type:
            filtered_data = [d for d in filtered_data if d.get('well_type', '').lower() == well_type.lower()]
        
        if aquifer_type:
            filtered_data = [d for d in filtered_data if d.get('aquifer_type', '').lower() == aquifer_type.lower()]
        
        if min_level is not None:
            filtered_data = [d for d in filtered_data if d.get('measurement', 0) >= min_level]
        
        if max_level is not None:
            filtered_data = [d for d in filtered_data if d.get('measurement', float('inf')) <= max_level]
        
        return jsonify({
            'success': True,
            'data': filtered_data,
            'total_records': len(filtered_data),
            'filters_applied': {
                'region': region,
                'year': year,
                'district': district,
                'state': state,
                'well_type': well_type,
                'aquifer_type': aquifer_type,
                'min_level': min_level,
                'max_level': max_level
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@api_bp.route('/groundwater/regions', methods=['GET'])
def get_all_regions():
    """Get all available regions with metadata"""
    try:
        regions = groundwater_service.get_available_regions()
        regions_with_metadata = []
        
        for region in regions:
            metadata = groundwater_service.get_regional_metadata(region)
            years = groundwater_service.get_available_years(region)
            
            regions_with_metadata.append({
                'region': region,
                'metadata': metadata,
                'available_years': years
            })
        
        return jsonify({
            'success': True,
            'regions': regions_with_metadata,
            'total_regions': len(regions_with_metadata)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/groundwater/statistics/<region>/<int:year>')
def get_region_statistics(region, year):
    """Get statistical analysis for a region and year"""
    try:
        data = groundwater_service.fetch_groundwater_data(region, year)
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        # Calculate statistics
        measurements = [d['measurement'] for d in data if d['measurement'] is not None]
        
        if not measurements:
            return jsonify({'error': 'No measurements available'}), 404
        
        import statistics
        
        stats = {
            'count': len(measurements),
            'mean': statistics.mean(measurements),
            'median': statistics.median(measurements),
            'mode': statistics.mode(measurements) if len(set(measurements)) < len(measurements) else None,
            'min': min(measurements),
            'max': max(measurements),
            'std_dev': statistics.stdev(measurements) if len(measurements) > 1 else 0,
            'variance': statistics.variance(measurements) if len(measurements) > 1 else 0
        }
        
        # Additional analysis
        well_types = {}
        aquifer_types = {}
        data_quality = {}
        
        for record in data:
            # Well type distribution
            well_type = record.get('well_type', 'Unknown')
            well_types[well_type] = well_types.get(well_type, 0) + 1
            
            # Aquifer type distribution
            aquifer_type = record.get('aquifer_type', 'Unknown')
            aquifer_types[aquifer_type] = aquifer_types.get(aquifer_type, 0) + 1
            
            # Data quality distribution
            quality = record.get('data_quality', 'Unknown')
            data_quality[quality] = data_quality.get(quality, 0) + 1
        
        return jsonify({
            'success': True,
            'region': region,
            'year': year,
            'statistics': stats,
            'distributions': {
                'well_types': well_types,
                'aquifer_types': aquifer_types,
                'data_quality': data_quality
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/visualizations/chart/<chart_type>', methods=['POST'])
def create_chart(chart_type):
    """Create specific chart type"""
    try:
        data = request.get_json()
        region = data.get('region')
        year = data.get('year')
        chart_data = data.get('data', [])
        
        if not chart_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create chart based on type
        if chart_type == 'groundwater_levels':
            chart = visualization_service.create_groundwater_level_chart(chart_data, region, year)
        elif chart_type == 'regional_comparison':
            chart = visualization_service.create_regional_comparison_chart(chart_data)
        elif chart_type == 'aquifer_types':
            chart = visualization_service.create_aquifer_type_chart(chart_data)
        elif chart_type == 'well_types':
            chart = visualization_service.create_well_type_chart(chart_data)
        elif chart_type == 'data_quality':
            chart = visualization_service.create_data_quality_chart(chart_data)
        elif chart_type == 'summary_stats':
            chart = visualization_service.create_summary_statistics_chart(chart_data)
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
        
        return jsonify({
            'success': True,
            'chart_type': chart_type,
            'chart_data': chart
        })
        
    except Exception as e:
        return jsonify({'error': f'Chart creation failed: {str(e)}'}), 500

@api_bp.route('/visualizations/dashboard', methods=['POST'])
def create_dashboard():
    """Create comprehensive dashboard"""
    try:
        data = request.get_json()
        region = data.get('region')
        year = data.get('year')
        chart_data = data.get('data', [])
        
        if not chart_data:
            return jsonify({'error': 'No data provided'}), 400
        
        dashboard = visualization_service.create_comprehensive_dashboard(
            chart_data, region, year
        )
        
        return jsonify({
            'success': True,
            'dashboard': dashboard
        })
        
    except Exception as e:
        return jsonify({'error': f'Dashboard creation failed: {str(e)}'}), 500

@api_bp.route('/language/detect', methods=['POST'])
def detect_language():
    """Detect language of input text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        language = language_service.detect_language(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'detected_language': language,
            'language_name': language_service.supported_languages.get(language, 'Unknown')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/language/translate', methods=['POST'])
def translate_text():
    """Translate text to target language"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_language = data.get('target_language', 'en')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        translated_text = language_service.translate_text(text, target_language)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated_text,
            'target_language': target_language
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/language/extract-location', methods=['POST'])
def extract_location():
    """Extract location information from text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        location_info = language_service.extract_location_info(text, language)
        year = language_service.extract_year_info(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'location_info': location_info,
            'year': year
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ingres/search', methods=['POST'])
def search_ingres_platform():
    """Search IN-GRES platform for additional data"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        result = groundwater_service.search_ingres_platform(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/queries', methods=['GET'])
def get_query_analytics():
    """Get analytics about user queries"""
    try:
        # This would typically query the query_history table
        # For now, return sample analytics
        
        analytics = {
            'total_queries': 0,
            'language_distribution': {},
            'popular_regions': {},
            'average_response_time': 0,
            'recent_queries': []
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
