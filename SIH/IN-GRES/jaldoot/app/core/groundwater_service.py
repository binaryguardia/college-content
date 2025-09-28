"""
JalDoot Groundwater Data Service
Enhanced service for IN-GRES platform integration
"""

import os
import json
import sqlite3
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

try:
    import pyodbc
    HAVE_PYODBC = True
except ImportError:
    pyodbc = None
    HAVE_PYODBC = False

try:
    import openai
    HAVE_OPENAI = True
except ImportError:
    openai = None
    HAVE_OPENAI = False

class GroundwaterService:
    """Enhanced groundwater data service with IN-GRES integration"""
    
    def __init__(self):
        self.sqlite_db_path = "jaldoot/data/groundwater.db"
        self.ingres_connstr = os.getenv('INGRES_CONNSTR')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.ingres_base_url = os.getenv('INGRES_BASE_URL', 'https://ingres.iith.ac.in')
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with enhanced schema"""
        os.makedirs(os.path.dirname(self.sqlite_db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.sqlite_db_path)
        cursor = conn.cursor()
        
        # Enhanced groundwater records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groundwater_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                district TEXT,
                state TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER,
                measurement REAL,
                unit TEXT DEFAULT 'm',
                well_type TEXT,
                aquifer_type TEXT,
                notes TEXT,
                source_url TEXT,
                data_quality TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Regional metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regional_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT UNIQUE NOT NULL,
                state TEXT NOT NULL,
                district TEXT,
                latitude REAL,
                longitude REAL,
                population INTEGER,
                area_sqkm REAL,
                climate_zone TEXT,
                aquifer_types TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Query history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_query TEXT NOT NULL,
                language TEXT,
                response TEXT,
                region TEXT,
                year INTEGER,
                response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert sample data if empty
        self._insert_sample_data()
    
    def _insert_sample_data(self):
        """Insert comprehensive sample data for testing"""
        conn = sqlite3.connect(self.sqlite_db_path)
        cursor = conn.cursor()
        
        # Check if data exists
        cursor.execute("SELECT COUNT(*) FROM groundwater_records")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample groundwater data for various regions
        sample_data = [
            # Punjab - Ropar
            ("Ropar", "Ropar", "Punjab", 2024, 1, 8.5, "m", "Borewell", "Alluvial", "Pre-monsoon levels", "https://ingres.iith.ac.in/punjab/ropar/2024/01", "High"),
            ("Ropar", "Ropar", "Punjab", 2024, 6, 12.3, "m", "Borewell", "Alluvial", "Post-monsoon levels", "https://ingres.iith.ac.in/punjab/ropar/2024/06", "High"),
            ("Ropar", "Ropar", "Punjab", 2023, 1, 7.8, "m", "Borewell", "Alluvial", "Historical comparison", "https://ingres.iith.ac.in/punjab/ropar/2023/01", "High"),
            
            # Maharashtra
            ("Maharashtra", "Mumbai", "Maharashtra", 2024, 1, 10.5, "m", "Monitoring Well", "Basalt", "Coastal aquifer", "https://ingres.iith.ac.in/maharashtra/mumbai/2024/01", "High"),
            ("Maharashtra", "Pune", "Maharashtra", 2024, 1, 15.2, "m", "Borewell", "Basalt", "Urban area", "https://ingres.iith.ac.in/maharashtra/pune/2024/01", "High"),
            ("Maharashtra", "Nagpur", "Maharashtra", 2024, 1, 18.7, "m", "Borewell", "Granite", "Central region", "https://ingres.iith.ac.in/maharashtra/nagpur/2024/01", "Medium"),
            
            # Gujarat
            ("Gujarat", "Ahmedabad", "Gujarat", 2024, 1, 7.4, "m", "Borewell", "Alluvial", "Industrial area", "https://ingres.iith.ac.in/gujarat/ahmedabad/2024/01", "High"),
            ("Gujarat", "Surat", "Gujarat", 2024, 1, 9.1, "m", "Borewell", "Alluvial", "Coastal region", "https://ingres.iith.ac.in/gujarat/surat/2024/01", "High"),
            
            # Rajasthan
            ("Rajasthan", "Jaipur", "Rajasthan", 2024, 1, 25.3, "m", "Borewell", "Sandstone", "Arid region", "https://ingres.iith.ac.in/rajasthan/jaipur/2024/01", "Medium"),
            ("Rajasthan", "Jodhpur", "Rajasthan", 2024, 1, 32.1, "m", "Borewell", "Sandstone", "Desert region", "https://ingres.iith.ac.in/rajasthan/jodhpur/2024/01", "Low"),
            
            # Karnataka
            ("Karnataka", "Bangalore", "Karnataka", 2024, 1, 12.8, "m", "Borewell", "Granite", "IT hub", "https://ingres.iith.ac.in/karnataka/bangalore/2024/01", "High"),
            ("Karnataka", "Mysore", "Karnataka", 2024, 1, 14.2, "m", "Borewell", "Granite", "Heritage city", "https://ingres.iith.ac.in/karnataka/mysore/2024/01", "High"),
        ]
        
        cursor.executemany("""
            INSERT INTO groundwater_records 
            (region, district, state, year, month, measurement, unit, well_type, aquifer_type, notes, source_url, data_quality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        # Regional metadata
        regional_metadata = [
            ("Ropar", "Punjab", "Ropar", 30.9686, 76.5264, 315000, 1356.0, "Semi-arid", "Alluvial, Hard Rock"),
            ("Maharashtra", "Maharashtra", None, 19.7515, 75.7139, 112374333, 307713.0, "Tropical", "Basalt, Granite, Alluvial"),
            ("Gujarat", "Gujarat", None, 23.0225, 72.5714, 60439692, 196024.0, "Arid to Semi-arid", "Alluvial, Hard Rock"),
            ("Rajasthan", "Rajasthan", None, 27.0238, 74.2179, 68548437, 342239.0, "Arid", "Sandstone, Hard Rock"),
            ("Karnataka", "Karnataka", None, 15.3173, 75.7139, 61130704, 191791.0, "Tropical", "Granite, Basalt, Alluvial"),
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO regional_metadata 
            (region, state, district, latitude, longitude, population, area_sqkm, climate_zone, aquifer_types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, regional_metadata)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection (INGRES or SQLite fallback)"""
        if HAVE_PYODBC and self.ingres_connstr:
            try:
                return pyodbc.connect(self.ingres_connstr, autocommit=True)
            except Exception as e:
                print(f"INGRES connection failed: {e}, falling back to SQLite")
        
        return sqlite3.connect(self.sqlite_db_path)
    
    def fetch_groundwater_data(self, region: str, year: int, district: str = None) -> List[Dict]:
        """Fetch groundwater data for a specific region and year"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build query based on available parameters
        if district:
            query = """
                SELECT id, region, district, state, year, month, measurement, unit, 
                       well_type, aquifer_type, notes, source_url, data_quality, recorded_at
                FROM groundwater_records 
                WHERE region = ? AND year = ? AND district = ?
                ORDER BY month, recorded_at DESC
            """
            cursor.execute(query, (region, year, district))
        else:
            query = """
                SELECT id, region, district, state, year, month, measurement, unit, 
                       well_type, aquifer_type, notes, source_url, data_quality, recorded_at
                FROM groundwater_records 
                WHERE region = ? AND year = ?
                ORDER BY month, recorded_at DESC
            """
            cursor.execute(query, (region, year))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'region': row[1],
                'district': row[2],
                'state': row[3],
                'year': row[4],
                'month': row[5],
                'measurement': row[6],
                'unit': row[7],
                'well_type': row[8],
                'aquifer_type': row[9],
                'notes': row[10],
                'source_url': row[11],
                'data_quality': row[12],
                'recorded_at': str(row[13])
            })
        
        return data
    
    def get_regional_metadata(self, region: str) -> Optional[Dict]:
        """Get regional metadata for a specific region"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT region, state, district, latitude, longitude, population, 
                   area_sqkm, climate_zone, aquifer_types
            FROM regional_metadata 
            WHERE region = ?
        """, (region,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'region': row[0],
                'state': row[1],
                'district': row[2],
                'latitude': row[3],
                'longitude': row[4],
                'population': row[5],
                'area_sqkm': row[6],
                'climate_zone': row[7],
                'aquifer_types': row[8]
            }
        
        return None
    
    def search_ingres_platform(self, query: str) -> Dict:
        """Search IN-GRES platform for additional data"""
        try:
            # This would be the actual API call to IN-GRES platform
            # For now, we'll simulate the response
            response = {
                'status': 'success',
                'data': [],
                'message': 'IN-GRES platform integration simulated'
            }
            
            # In a real implementation, you would make HTTP requests to IN-GRES API
            # headers = {'Authorization': f'Bearer {self.ingres_api_key}'}
            # response = requests.get(f'{self.ingres_base_url}/api/search', 
            #                       params={'q': query}, headers=headers)
            
            return response
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to search IN-GRES platform: {str(e)}'
            }
    
    def log_query(self, user_query: str, language: str, response: str, 
                  region: str = None, year: int = None, response_time: float = None):
        """Log user query for analytics and improvement"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO query_history 
            (user_query, language, response, region, year, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_query, language, response, region, year, response_time))
        
        conn.commit()
        conn.close()
    
    def get_available_regions(self) -> List[str]:
        """Get list of available regions in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT region FROM groundwater_records ORDER BY region")
        regions = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return regions
    
    def get_available_years(self, region: str = None) -> List[int]:
        """Get list of available years for a region or all regions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if region:
            cursor.execute("SELECT DISTINCT year FROM groundwater_records WHERE region = ? ORDER BY year DESC", (region,))
        else:
            cursor.execute("SELECT DISTINCT year FROM groundwater_records ORDER BY year DESC")
        
        years = [row[0] for row in cursor.fetchall()]
        conn.close()
        return years
