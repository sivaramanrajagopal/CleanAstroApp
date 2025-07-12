# =============================================================================
# VEDIC ASTROLOGY DASHBOARD - FLASK WEB APP
# =============================================================================

from flask import Flask, render_template, request, jsonify, session
from vedic_astrology_modular import VedicChartCalculator, display_chart_analysis
from vedic_astrology_engine import (
    get_dasha_info, get_julian_day,
    calculate_sthana_bala, calculate_dig_bala, calculate_kala_bala,
    calculate_cheshta_bala, calculate_naisargika_bala, calculate_drik_bala,
    NAKSHATRAS, NAKSHATRA_LORDS
)
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
        moon_longitude = chart['planets']['Moon']['longitude']
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

@app.route('/shadbala')
def shadbala_dashboard():
    """Shadbala Dashboard page"""
    return render_template('shadbala.html')

@app.route('/api/calculate_shadbala', methods=['POST'])
def calculate_shadbala():
    """API endpoint to calculate detailed Shadbala analysis"""
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
        
        # Calculate chart
        chart = chart_calculator.calculate_chart(**birth_details)
        
        # Calculate detailed Shadbala for each planet
        detailed_shadbala = {}
        for planet_name, planet_data in chart['planets'].items():
            if planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
                # Get detailed Shadbala analysis
                shadbala_analysis = calculate_detailed_shadbala(
                    chart['birth_info']['date'], 
                    chart['birth_info']['time'],
                    float(chart['birth_info']['latitude']),
                    float(chart['birth_info']['longitude']),
                    float(chart['birth_info']['timezone']),
                    planet_name,
                    planet_data
                )
                detailed_shadbala[planet_name] = shadbala_analysis
        
        return jsonify({
            'success': True,
            'shadbala': detailed_shadbala,
            'chart': chart,
            'birth_details': birth_details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def calculate_detailed_shadbala(date: str, time: str, latitude: float, 
                               longitude: float, timezone: float, 
                               planet_name: str, planet_data: Dict) -> Dict[str, Any]:
    """Calculate detailed Shadbala analysis with tick marks for each principle"""
    
    # Get Julian Day
    jd = get_julian_day(date, time, timezone)
    
    # Calculate all six Shadbala components
    sthana = calculate_sthana_bala(planet_name, planet_data['sign'], planet_data['house'])
    dig = calculate_dig_bala(planet_data['sign'], planet_data.get('asc_rasi', 'Mesha'))
    kala = calculate_kala_bala(jd, planet_name)
    cheshta = calculate_cheshta_bala(planet_name, planet_data.get('speed', 0))
    naisargika = calculate_naisargika_bala(planet_name)
    drik = calculate_drik_bala(planet_name, planet_data['house'])
    
    # Determine tick marks based on strength thresholds
    def get_tick_mark(value, threshold=0.5):
        return "✓" if value >= threshold else "✗"
    
    # Calculate total Shadbala
    total_shadbala = (sthana['sthana_bala'] + dig + kala['kala_bala'] + 
                      cheshta + naisargika + drik) / 6
    
    return {
        'planet_name': planet_name,
        'sign': planet_data['sign'],
        'house': planet_data['house'],
        'dignity': sthana['dignity'],
        'retrograde': planet_data.get('retrograde', False),
        'total_shadbala': round(total_shadbala, 3),
        'components': {
            'sthana_bala': {
                'value': round(sthana['sthana_bala'], 3),
                'tick': get_tick_mark(sthana['sthana_bala'], 0.5),
                'description': f"Positional strength based on dignity ({sthana['dignity']}) and house placement",
                'details': {
                    'dignity': sthana['dignity'],
                    'house_bonus': 'Kendra (+0.25)' if planet_data['house'] in [1,4,7,10] else 
                                  'Trikona (+0.25)' if planet_data['house'] in [5,9] else 'None'
                }
            },
            'dig_bala': {
                'value': round(dig, 3),
                'tick': get_tick_mark(dig, 0.5),
                'description': "Directional strength based on planet's position relative to ascendant",
                'details': {
                    'direction': 'East' if dig >= 0.8 else 'South' if dig >= 0.6 else 'West' if dig >= 0.4 else 'North',
                    'strength': 'Strong' if dig >= 0.8 else 'Moderate' if dig >= 0.6 else 'Weak'
                }
            },
            'kala_bala': {
                'value': round(kala['kala_bala'], 3),
                'tick': get_tick_mark(kala['kala_bala'], 0.5),
                'description': "Temporal strength including day/night, seasonal, and time-based factors",
                'details': {
                    'nathonnata': round(kala['nathonnata_bala'], 3),
                    'abda': round(kala['abda_bala'], 3),
                    'masa': round(kala['masa_bala'], 3),
                    'vara': round(kala['vara_bala'], 3),
                    'hora': round(kala['hora_bala'], 3)
                }
            },
            'cheshta_bala': {
                'value': round(cheshta, 3),
                'tick': get_tick_mark(cheshta, 0.5),
                'description': "Motional strength based on planet's movement and speed",
                'details': {
                    'motion': 'Retrograde' if planet_data.get('retrograde', False) else 'Direct',
                    'strength': 'Strong' if cheshta >= 0.8 else 'Moderate' if cheshta >= 0.5 else 'Weak'
                }
            },
            'naisargika_bala': {
                'value': round(naisargika, 3),
                'tick': get_tick_mark(naisargika, 0.5),
                'description': "Natural strength inherent to each planet",
                'details': {
                    'natural_strength': 'High' if naisargika >= 1.0 else 'Medium' if naisargika >= 0.5 else 'Low',
                    'planet_type': 'Benefic' if planet_name in ['Jupiter', 'Venus'] else 'Malefic' if planet_name in ['Mars', 'Saturn'] else 'Neutral'
                }
            },
            'drik_bala': {
                'value': round(drik, 3),
                'tick': get_tick_mark(drik, 0.5),
                'description': "Aspectual strength based on house placement and aspects",
                'details': {
                    'house_type': 'Kendra' if planet_data['house'] in [1,4,7,10] else 'Trikona' if planet_data['house'] in [5,9] else 'Dusthana',
                    'aspect_strength': 'Strong' if drik >= 0.8 else 'Moderate' if drik >= 0.5 else 'Weak'
                }
            }
        },
        'overall_assessment': {
            'score': round(total_shadbala * 10, 1),
            'grade': 'Strong' if total_shadbala >= 0.7 else 'Moderate' if total_shadbala >= 0.5 else 'Weak',
            'color': '#28a745' if total_shadbala >= 0.7 else '#ffc107' if total_shadbala >= 0.5 else '#dc3545'
        }
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050) 