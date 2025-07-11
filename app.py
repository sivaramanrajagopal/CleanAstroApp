# =============================================================================
# VEDIC ASTROLOGY DASHBOARD - FLASK WEB APP
# =============================================================================

from flask import Flask, render_template, request, jsonify, session
from vedic_astrology_modular import VedicChartCalculator, display_chart_analysis
from vedic_astrology_engine import get_dasha_info
from transit_calculator import TransitCalculator
from compatibility_analyzer import CompatibilityAnalyzer
import json
from typing import Optional, Dict, Any
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a strong secret key for session

# Initialize calculators
chart_calculator = VedicChartCalculator()
transit_calculator = TransitCalculator()
compatibility_analyzer = CompatibilityAnalyzer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/calculate_chart', methods=['POST'])
def calculate_chart():
    """API endpoint to calculate birth chart"""
    try:
        data = request.get_json()
        
        # Extract birth details
        birth_details = {
            'date': data['date'],
            'time': data['time'],
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'timezone': float(data['timezone'])
        }
        
        # Cache birth details in session
        session['birth_details'] = birth_details
        
        # Calculate chart
        chart = chart_calculator.calculate_chart(**birth_details)
        
        # Calculate dasha using new engine
        moon_longitude = chart['planets']['Moon']['degree']
        dasha_info = get_dasha_info(
            moon_longitude=moon_longitude,
            birth_date=data['date']
        )
        
        # Calculate transits
        transit_info = transit_calculator.calculate_current_transits(
            date=data['date'],
            time=data['time'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            timezone=float(data['timezone'])
        )
        
        return jsonify({
            'success': True,
            'chart': chart,
            'dasha': dasha_info,
            'transits': transit_info,
            'birth_details': birth_details  # Return cached info for frontend
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/compatibility', methods=['POST'])
def calculate_compatibility():
    """API endpoint to calculate compatibility"""
    try:
        data = request.get_json()
        
        person1 = {
            'date': data['person1']['date'],
            'time': data['person1']['time'],
            'latitude': float(data['person1']['latitude']),
            'longitude': float(data['person1']['longitude']),
            'timezone': float(data['person1']['timezone'])
        }
        
        person2 = {
            'date': data['person2']['date'],
            'time': data['person2']['time'],
            'latitude': float(data['person2']['latitude']),
            'longitude': float(data['person2']['longitude']),
            'timezone': float(data['person2']['timezone'])
        }
        
        compatibility = compatibility_analyzer.analyze_compatibility(person1, person2)
        
        return jsonify({
            'success': True,
            'compatibility': compatibility
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/chart')
def chart_page():
    """Birth chart analysis page"""
    return render_template('chart.html')

@app.route('/compatibility')
def compatibility_page():
    """Compatibility analysis page"""
    return render_template('compatibility.html')

@app.route('/dasha')
def dasha_page():
    """Dasha analysis page"""
    return render_template('dasha.html')

@app.route('/transits')
def transits_page():
    """Transit analysis page"""
    return render_template('transits.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050) 