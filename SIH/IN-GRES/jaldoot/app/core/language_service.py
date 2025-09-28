"""
JalDoot Language Service
Multilingual support for Hinglish, Hindi, and English
"""

import re
from typing import Dict, List, Optional, Tuple
from langdetect import detect, DetectorFactory

# Set seed for consistent language detection
DetectorFactory.seed = 0

class LanguageService:
    """Service for handling multilingual interactions"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'hinglish': 'Hinglish'
        }
        
        # Common Hinglish patterns
        self.hinglish_patterns = [
            r'\b(ka|ki|ke|ko|se|me|par|kaun|kya|kab|kahan|kyun|kaise)\b',
            r'\b(hai|hain|tha|thi|the|raha|rahi|rahe)\b',
            r'\b(achha|accha|bilkul|zaroor|pakka|sahi|galat)\b',
            r'\b(groundwater|water|level|data|information|details)\b'
        ]
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        try:
            # Check for Hinglish patterns first
            if self._is_hinglish(text):
                return 'hinglish'
            
            # Use langdetect for other languages
            detected = detect(text)
            
            # Map detected language to our supported languages
            if detected in ['hi', 'hin']:
                return 'hi'
            elif detected in ['en']:
                return 'en'
            else:
                return 'en'  # Default to English
                
        except Exception:
            return 'en'  # Default to English on error
    
    def _is_hinglish(self, text: str) -> bool:
        """Check if text contains Hinglish patterns"""
        text_lower = text.lower()
        hinglish_score = 0
        
        for pattern in self.hinglish_patterns:
            if re.search(pattern, text_lower):
                hinglish_score += 1
        
        # If we find multiple Hinglish patterns, consider it Hinglish
        return hinglish_score >= 2
    
    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        try:
            if target_language == 'hinglish':
                return self._convert_to_hinglish(text)
            elif target_language == 'hi':
                return self._convert_to_hindi(text)
            else:
                return text  # Return original text for English
                
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text on error
    
    def _convert_to_hinglish(self, text: str) -> str:
        """Convert English text to Hinglish"""
        # Simple Hinglish conversion rules
        hinglish_mappings = {
            'water': 'paani',
            'groundwater': 'bhoomi paani',
            'level': 'level',
            'data': 'data',
            'information': 'jaankari',
            'details': 'details',
            'year': 'saal',
            'month': 'mahina',
            'region': 'kshetra',
            'state': 'rajya',
            'district': 'jila',
            'measurement': 'maap',
            'well': 'kuan',
            'borewell': 'borewell',
            'aquifer': 'aquifer',
            'depth': 'gahrai',
            'meter': 'meter',
            'below': 'neeche',
            'ground': 'zameen',
            'surface': 'surface',
            'average': 'average',
            'high': 'high',
            'low': 'low',
            'good': 'achha',
            'bad': 'galat',
            'very': 'bahut',
            'much': 'zyada',
            'less': 'kam',
            'more': 'zyada',
            'please': 'please',
            'thank you': 'dhanyawad',
            'yes': 'haan',
            'no': 'nahi',
            'okay': 'theek hai',
            'right': 'sahi',
            'wrong': 'galat'
        }
        
        result = text.lower()
        for english, hinglish in hinglish_mappings.items():
            result = re.sub(r'\b' + english + r'\b', hinglish, result, flags=re.IGNORECASE)
        
        return result
    
    def _convert_to_hindi(self, text: str) -> str:
        """Convert English text to Hindi (simplified)"""
        # Simple Hindi conversion rules
        hindi_mappings = {
            'water': 'पानी',
            'groundwater': 'भूजल',
            'level': 'स्तर',
            'data': 'डेटा',
            'information': 'जानकारी',
            'details': 'विवरण',
            'year': 'वर्ष',
            'month': 'महीना',
            'region': 'क्षेत्र',
            'state': 'राज्य',
            'district': 'जिला',
            'measurement': 'माप',
            'well': 'कुआं',
            'borewell': 'बोरवेल',
            'aquifer': 'जलभृत',
            'depth': 'गहराई',
            'meter': 'मीटर',
            'below': 'नीचे',
            'ground': 'जमीन',
            'surface': 'सतह',
            'average': 'औसत',
            'high': 'उच्च',
            'low': 'निम्न',
            'good': 'अच्छा',
            'bad': 'बुरा',
            'very': 'बहुत',
            'much': 'ज्यादा',
            'less': 'कम',
            'more': 'अधिक',
            'please': 'कृपया',
            'thank you': 'धन्यवाद',
            'yes': 'हाँ',
            'no': 'नहीं',
            'okay': 'ठीक है',
            'right': 'सही',
            'wrong': 'गलत'
        }
        
        result = text.lower()
        for english, hindi in hindi_mappings.items():
            result = re.sub(r'\b' + english + r'\b', hindi, result, flags=re.IGNORECASE)
        
        return result
    
    def format_response(self, response: str, language: str) -> str:
        """Format response according to the detected language"""
        if language == 'hinglish':
            return self._format_hinglish_response(response)
        elif language == 'hi':
            return self._format_hindi_response(response)
        else:
            return self._format_english_response(response)
    
    def _format_hinglish_response(self, response: str) -> str:
        """Format response in Hinglish style"""
        # Add common Hinglish expressions
        if 'groundwater' in response.lower():
            response = response.replace('groundwater', 'bhoomi paani')
        
        if 'level' in response.lower():
            response = response.replace('level', 'level')
        
        # Add friendly Hinglish expressions
        if response.startswith('The'):
            response = response.replace('The', 'Aapka', 1)
        
        return response
    
    def _format_hindi_response(self, response: str) -> str:
        """Format response in Hindi style"""
        # This would contain Hindi-specific formatting
        return response
    
    def _format_english_response(self, response: str) -> str:
        """Format response in English style"""
        # This would contain English-specific formatting
        return response
    
    def get_language_greeting(self, language: str) -> str:
        """Get greeting in the specified language"""
        greetings = {
            'en': "Hello! I'm JalDoot, your groundwater assistant. How can I help you today?",
            'hi': "नमस्ते! मैं JalDoot हूं, आपका भूजल सहायक। आज मैं आपकी कैसे मदद कर सकता हूं?",
            'hinglish': "Namaste! Main JalDoot hun, aapka groundwater assistant. Aaj main aapki kaise help kar sakta hun?"
        }
        return greetings.get(language, greetings['en'])
    
    def get_language_instructions(self, language: str) -> str:
        """Get usage instructions in the specified language"""
        instructions = {
            'en': "You can ask me about groundwater levels, data for specific regions, or request visualizations. Try asking: 'Show me groundwater data for Punjab Ropar 2024'",
            'hi': "आप मुझसे भूजल स्तर, विशिष्ट क्षेत्रों के डेटा, या दृश्यीकरण के बारे में पूछ सकते हैं। कोशिश करें: 'पंजाब रोपड़ 2024 के लिए भूजल डेटा दिखाएं'",
            'hinglish': "Aap mujhse groundwater levels, specific regions ke data, ya visualizations ke baare mein puch sakte hain. Try kariye: 'Punjab Ropar 2024 ka groundwater data dikhaiye'"
        }
        return instructions.get(language, instructions['en'])
    
    def extract_location_info(self, text: str, language: str) -> Dict[str, Optional[str]]:
        """Extract location information from user query"""
        location_info = {
            'state': None,
            'district': None,
            'region': None
        }
        
        # Common state names in different languages
        state_mappings = {
            'punjab': 'Punjab',
            'maharashtra': 'Maharashtra',
            'gujarat': 'Gujarat',
            'rajasthan': 'Rajasthan',
            'karnataka': 'Karnataka',
            'पंजाब': 'Punjab',
            'महाराष्ट्र': 'Maharashtra',
            'गुजरात': 'Gujarat',
            'राजस्थान': 'Rajasthan',
            'कर्नाटक': 'Karnataka'
        }
        
        # Common district names
        district_mappings = {
            'ropar': 'Ropar',
            'mumbai': 'Mumbai',
            'pune': 'Pune',
            'ahmedabad': 'Ahmedabad',
            'jaipur': 'Jaipur',
            'bangalore': 'Bangalore',
            'रोपड़': 'Ropar',
            'मुंबई': 'Mumbai',
            'पुणे': 'Pune',
            'अहमदाबाद': 'Ahmedabad',
            'जयपुर': 'Jaipur',
            'बैंगलोर': 'Bangalore'
        }
        
        text_lower = text.lower()
        
        # Extract state
        for key, value in state_mappings.items():
            if key in text_lower:
                location_info['state'] = value
                break
        
        # Extract district
        for key, value in district_mappings.items():
            if key in text_lower:
                location_info['district'] = value
                break
        
        # Set region based on state or district
        if location_info['district']:
            location_info['region'] = location_info['district']
        elif location_info['state']:
            location_info['region'] = location_info['state']
        
        return location_info
    
    def extract_year_info(self, text: str) -> Optional[int]:
        """Extract year information from user query"""
        # Look for 4-digit years
        year_pattern = r'\b(19|20)\d{2}\b'
        matches = re.findall(year_pattern, text)
        
        if matches:
            return int(matches[0])
        
        # Look for relative years
        if 'current' in text.lower() or 'this year' in text.lower():
            return 2024
        
        return None
