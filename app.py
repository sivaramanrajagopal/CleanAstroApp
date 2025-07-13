# =============================================================================
# VEDIC ASTROLOGY DASHBOARD - FLASK WEB APP
# =============================================================================

from flask import Flask, render_template, request, jsonify, session, send_file
from vedic_astrology_modular import VedicChartCalculator, display_chart_analysis
from vedic_astrology_engine import (
    get_dasha_info, get_julian_day,
    calculate_sthana_bala, calculate_dig_bala, calculate_kala_bala,
    calculate_cheshta_bala, calculate_naisargika_bala, calculate_drik_bala,
    NAKSHATRAS, NAKSHATRA_LORDS
)
from transit_calculator import TransitCalculator
from compatibility_analyzer import CompatibilityAnalyzer
from cache_manager import cache_manager
from pdf_generator import pdf_generator
from keep_alive import start_keep_alive, stop_keep_alive
import json
from typing import Optional, Dict, Any
import datetime
import os

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
    """API endpoint to calculate birth chart with caching"""
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
        
        # Generate cache key
        cache_key = cache_manager.generate_cache_key(birth_details)
        
        # Check cache first
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return jsonify({
                'success': True,
                'chart': cached_result['chart'],
                'dasha': cached_result['dasha'],
                'transits': cached_result['transits'],
                'birth_details': birth_details,
                'cached': True
            })
        
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
        
        # Cache the result
        result_data = {
            'chart': chart,
            'dasha': dasha_info,
            'transits': transit_info
        }
        cache_manager.set(cache_key, result_data)
        
        return jsonify({
            'success': True,
            'chart': chart,
            'dasha': dasha_info,
            'transits': transit_info,
            'birth_details': birth_details,
            'cached': False
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

@app.route('/cosmic_connections')
def cosmic_connections():
    return render_template('cosmic_connections.html')

@app.route('/api/calculate_cosmic_connections', methods=['POST'])
def calculate_cosmic_connections():
    data = request.get_json()
    birth_details = {
        'date': data['date'],
        'time': data['time'],
        'latitude': float(data['latitude']),
        'longitude': float(data['longitude']),
        'timezone': float(data['timezone'])
    }
    
    # Calculate chart
    chart = chart_calculator.calculate_chart(**birth_details)
    
    # Get cosmic connections analysis
    cosmic_data = analyze_cosmic_connections(chart)
    
    return jsonify(cosmic_data)

def analyze_cosmic_connections(chart):
    """Analyze cosmic connections based on Parashara principles"""
    
    # Planet to house lord relationships
    planet_house_connections = []
    house_lord_connections = []
    nakshatra_connections = []
    aspect_connections = []
    
    planets = chart['planets']
    houses = chart['houses']
    lagna = chart['lagna']
    
    # Nakshatra Lords mapping
    nakshatra_lords = {
        'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun', 'Rohini': 'Moon',
        'Mrigashira': 'Mars', 'Ardra': 'Rahu', 'Punarvasu': 'Jupiter', 'Pushya': 'Saturn',
        'Ashlesha': 'Mercury', 'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
        'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu', 'Vishakha': 'Jupiter',
        'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury', 'Mula': 'Ketu', 'Purva Ashadha': 'Venus',
        'Uttara Ashadha': 'Sun', 'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
        'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
    }
    
    # Add nakshatra lords and pada to planet data
    for planet, pdata in planets.items():
        nakshatra = pdata.get('nakshatra', '')
        longitude = pdata.get('longitude', 0)
        
        # Calculate pada
        if longitude > 0:
            nakshatra_degree = (longitude % (360 / 27))  # Degree within nakshatra
            pada = int(nakshatra_degree / (360 / 27 / 4)) + 1  # 4 padas per nakshatra
            pdata['pada'] = pada
        else:
            pdata['pada'] = 0
            
        # Add nakshatra lord
        if nakshatra in nakshatra_lords:
            pdata['nakshatra_lord'] = nakshatra_lords[nakshatra]
    
    # Planet-House Lord Connections
    for planet, pdata in planets.items():
        if planet in ['Rahu', 'Ketu']:
            continue
            
        planet_house = pdata.get('house', 0)
        planet_sign = pdata.get('sign', '')  # Use 'sign' field for Rasi
        
        # Find which house lord this planet is
        for house_num, hdata in houses.items():
            if hdata.get('sign') == planet_sign:
                # Fix house number formatting
                house_suffix = get_ordinal_suffix(house_num)
                planet_house_connections.append({
                    'type': 'Planet-House Lord',
                    'planet': planet,
                    'house': house_num,
                    'sign': planet_sign,
                    'connection': f"{planet} is lord of {house_num}{house_suffix} house",
                    'significance': get_house_lord_significance(planet, house_num)
                })
    
    # House Lord in Houses
    for house_num, hdata in houses.items():
        house_sign = hdata.get('sign', '')
        house_lord = get_planet_for_sign(house_sign)
        
        # Find where this house lord is placed
        for planet, pdata in planets.items():
            if planet == house_lord:
                lord_house = pdata.get('house', 0)
                lord_sign = pdata.get('sign', '')  # Use 'sign' field for Rasi
                
                # Fix house number formatting
                house_suffix = get_ordinal_suffix(house_num)
                lord_house_suffix = get_ordinal_suffix(lord_house)
                house_lord_connections.append({
                    'type': 'House Lord Placement',
                    'house': house_num,
                    'lord': house_lord,
                    'lord_house': lord_house,
                    'lord_sign': lord_sign,
                    'connection': f"{house_num}{house_suffix} house lord {house_lord} is in {lord_house}{lord_house_suffix} house",
                    'significance': get_lord_placement_significance(house_num, lord_house)
                })
    
    # Nakshatra Lord Connections
    for planet, pdata in planets.items():
        nakshatra = pdata.get('nakshatra', '')
        nakshatra_lord = pdata.get('nakshatra_lord', '')
        planet_house = pdata.get('house', 0)
        
        if nakshatra_lord and nakshatra_lord in planets:
            nakshatra_lord_data = planets[nakshatra_lord]
            nakshatra_lord_house = nakshatra_lord_data.get('house', 0)
            
            # Fix house number formatting
            lord_house_suffix = get_ordinal_suffix(nakshatra_lord_house)
            nakshatra_connections.append({
                'type': 'Nakshatra Lord Connection',
                'planet': planet,
                'nakshatra': nakshatra,
                'nakshatra_lord': nakshatra_lord,
                'planet_house': planet_house,
                'lord_house': nakshatra_lord_house,
                'connection': f"{planet} in {nakshatra} (lord: {nakshatra_lord}) - {nakshatra_lord} in {nakshatra_lord_house}{lord_house_suffix} house",
                'significance': get_nakshatra_connection_significance(planet, nakshatra_lord, planet_house, nakshatra_lord_house)
            })
    
    # Planet Aspects (Corrected Parashara aspects)
    # According to Parashara: Sun aspects 7th house from its position
    # Mars aspects 4th, 7th, 8th houses from its position
    # Jupiter aspects 5th, 7th, 9th houses from its position
    # Saturn aspects 3rd, 7th, 10th houses from its position
    # Other planets aspect 7th house from their position
    aspect_rules = {
        'Sun': [7], 'Moon': [7], 'Mars': [4, 7, 8], 'Mercury': [7], 
        'Jupiter': [5, 7, 9], 'Venus': [7], 'Saturn': [3, 7, 10]
    }
    
    for planet, pdata in planets.items():
        if planet in aspect_rules:
            planet_house = pdata.get('house', 0)
            aspects = aspect_rules[planet]
            
            for aspect_distance in aspects:
                # Calculate aspect house: planet_house + aspect_distance - 1
                # This gives the correct house number from the planet's position
                aspect_house = planet_house + aspect_distance - 1
                if aspect_house > 12:
                    aspect_house = aspect_house - 12
                
                aspect_sign = houses.get(aspect_house, {}).get('sign', '')
                
                # Fix house number formatting
                planet_house_suffix = get_ordinal_suffix(planet_house)
                aspect_house_suffix = get_ordinal_suffix(aspect_house)
                aspect_connections.append({
                    'type': 'Planet Aspect',
                    'planet': planet,
                    'planet_house': planet_house,
                    'aspect_house': aspect_house,
                    'aspect_sign': aspect_sign,
                    'connection': f"{planet} in {planet_house}{planet_house_suffix} house aspects {aspect_house}{aspect_house_suffix} house ({aspect_sign})",
                    'significance': get_aspect_significance(planet, aspect_house)
                })
    
    return {
        'planet_house_connections': planet_house_connections,
        'house_lord_connections': house_lord_connections,
        'nakshatra_connections': nakshatra_connections,
        'aspect_connections': aspect_connections,
        'chart_data': {
            'planets': planets,
            'houses': houses,
            'lagna': lagna
        }
    }

def get_ordinal_suffix(num):
    """Get the correct ordinal suffix for a number"""
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
    return suffix

def get_planet_for_sign(sign):
    """Get the ruling planet for a sign"""
    sign_lords = {
        'Mesha': 'Mars', 'Rishaba': 'Venus', 'Mithuna': 'Mercury',
        'Kataka': 'Moon', 'Simha': 'Sun', 'Kanni': 'Mercury',
        'Thula': 'Venus', 'Vrischika': 'Mars', 'Dhanus': 'Jupiter',
        'Makara': 'Saturn', 'Kumbha': 'Saturn', 'Meena': 'Jupiter'
    }
    return sign_lords.get(sign, '')

def get_house_lord_significance(planet, house):
    """Get significance of planet being lord of a house"""
    significances = {
        'Sun': 'Leadership, authority, father, government',
        'Moon': 'Mind, mother, emotions, public',
        'Mars': 'Courage, brothers, property, disputes',
        'Mercury': 'Communication, business, education',
        'Jupiter': 'Wisdom, children, guru, dharma',
        'Venus': 'Relationships, arts, luxury, spouse',
        'Saturn': 'Discipline, obstacles, service, karma'
    }
    return significances.get(planet, 'General significations')

def get_lord_placement_significance(house, lord_house):
    """Get significance of house lord placement"""
    placements = {
        (1, 1): 'Strong personality, self-focused',
        (1, 2): 'Wealth through self-effort',
        (1, 3): 'Courage and communication',
        (1, 4): 'Happiness and property',
        (1, 5): 'Intelligence and children',
        (1, 6): 'Health challenges, enemies',
        (1, 7): 'Marriage and partnerships',
        (1, 8): 'Longevity and occult',
        (1, 9): 'Spirituality and fortune',
        (1, 10): 'Career and reputation',
        (1, 11): 'Gains and income',
        (1, 12): 'Expenses and foreign lands'
    }
    return placements.get((house, lord_house), 'General placement effects')

def get_nakshatra_connection_significance(planet, nakshatra_lord, planet_house, lord_house):
    """Get significance of nakshatra lord connection"""
    planet_suffix = get_ordinal_suffix(planet_house)
    lord_suffix = get_ordinal_suffix(lord_house)
    return f"Planet {planet} in {planet_house}{planet_suffix} house connected to {nakshatra_lord} in {lord_house}{lord_suffix} house through nakshatra lordship"

def get_aspect_significance(planet, aspect_house):
    """Get significance of planet aspecting a house"""
    aspects = {
        'Sun': 'Authority and leadership influence',
        'Moon': 'Emotional and mental influence',
        'Mars': 'Energy and courage influence',
        'Mercury': 'Communication and business influence',
        'Jupiter': 'Wisdom and expansion influence',
        'Venus': 'Relationships and luxury influence',
        'Saturn': 'Discipline and restriction influence'
    }
    return aspects.get(planet, 'General aspect influence')

# PDF Generation Endpoints
@app.route('/api/generate_chart_pdf', methods=['POST'])
def generate_chart_pdf():
    """Generate PDF for birth chart analysis"""
    try:
        data = request.get_json()
        
        # Get chart data from cache or calculate
        birth_details = {
            'date': data['date'],
            'time': data['time'],
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'timezone': float(data['timezone'])
        }
        
        cache_key = cache_manager.generate_cache_key(birth_details)
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            chart_data = cached_result['chart']
        else:
            chart_data = chart_calculator.calculate_chart(**birth_details)
        
        # Prepare data for PDF
        pdf_data = {
            'name': data.get('name', 'N/A'),
            'dob': data['date'],
            'tob': data['time'],
            'pob': data.get('place', 'N/A'),
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'planets': chart_data['planets'],
            'houses': chart_data['houses'],
            'yogas': chart_data.get('yogas', []),
            'overall_health': chart_data.get('overall_health', 0)
        }
        
        # Generate PDF
        filename = pdf_generator.generate_chart_pdf(pdf_data)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_pdf/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/generate_dasha_pdf', methods=['POST'])
def generate_dasha_pdf():
    """Generate PDF for Dasha analysis"""
    try:
        data = request.get_json()
        
        # Get dasha data
        birth_details = {
            'date': data['date'],
            'time': data['time'],
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'timezone': float(data['timezone'])
        }
        
        cache_key = cache_manager.generate_cache_key(birth_details)
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            chart_data = cached_result['chart']
            dasha_data = cached_result['dasha']
        else:
            chart_data = chart_calculator.calculate_chart(**birth_details)
            moon_longitude = chart_data['planets']['Moon']['longitude']
            dasha_data = get_dasha_info(moon_longitude=moon_longitude, birth_date=data['date'])
        
        # Prepare data for PDF
        pdf_data = {
            'name': data.get('name', 'N/A'),
            'dob': data['date'],
            'birth_nakshatra': dasha_data.get('birth_nakshatra', 'N/A'),
            'nakshatra_lord': dasha_data.get('nakshatra_lord', 'N/A'),
            'current_dasha': dasha_data.get('current_dasha', {}),
            'antardashas': dasha_data.get('antardashas', [])
        }
        
        # Generate PDF
        filename = pdf_generator.generate_dasha_pdf(pdf_data)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_pdf/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/generate_shadbala_pdf', methods=['POST'])
def generate_shadbala_pdf():
    """Generate PDF for Shadbala analysis"""
    try:
        data = request.get_json()
        
        # Get shadbala data
        birth_details = {
            'date': data['date'],
            'time': data['time'],
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'timezone': float(data['timezone'])
        }
        
        # Calculate shadbala (this would need to be implemented)
        pdf_data = {
            'name': data.get('name', 'N/A'),
            'dob': data['date'],
            'tob': data['time'],
            'pob': data.get('place', 'N/A'),
            'shadbala_components': data.get('shadbala_components', []),
            'planet_strengths': data.get('planet_strengths', [])
        }
        
        # Generate PDF
        filename = pdf_generator.generate_shadbala_pdf(pdf_data)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_pdf/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/generate_cosmic_connections_pdf', methods=['POST'])
def generate_cosmic_connections_pdf():
    """Generate PDF for Cosmic Connections analysis"""
    try:
        data = request.get_json()
        
        # Get cosmic connections data
        birth_details = {
            'date': data['date'],
            'time': data['time'],
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'timezone': float(data['timezone'])
        }
        
        # Convert planets dictionary to list format for PDF generation
        planets_dict = data.get('planets', {})
        planets_list = []
        for planet_name, planet_data in planets_dict.items():
            planet_data['name'] = planet_name
            planets_list.append(planet_data)
        
        # Get the actual cosmic connections data
        cache_key = cache_manager.generate_cache_key(birth_details)
        cached_result = cache_manager.get(cache_key)
        
        if cached_result and 'cosmic_connections' in cached_result:
            cosmic_data = cached_result['cosmic_connections']
        else:
            # Calculate cosmic connections
            chart = chart_calculator.calculate_chart(**birth_details)
            cosmic_data = analyze_cosmic_connections(chart)
            # Cache the result
            if cached_result:
                cached_result['cosmic_connections'] = cosmic_data
                cache_manager.set(cache_key, cached_result)
        
        # Combine all connections into a single list for PDF
        all_connections = []
        
        # Add planet-house lord connections
        for conn in cosmic_data.get('planet_house_connections', []):
            all_connections.append({
                'type': conn['type'],
                'details': conn['connection'],
                'strength': conn['significance']
            })
        
        # Add house lord placement connections
        for conn in cosmic_data.get('house_lord_connections', []):
            all_connections.append({
                'type': conn['type'],
                'details': conn['connection'],
                'strength': conn['significance']
            })
        
        # Add nakshatra lord connections
        for conn in cosmic_data.get('nakshatra_connections', []):
            all_connections.append({
                'type': conn['type'],
                'details': conn['connection'],
                'strength': conn['significance']
            })
        
        # Add aspect connections
        for conn in cosmic_data.get('aspect_connections', []):
            all_connections.append({
                'type': conn['type'],
                'details': conn['connection'],
                'strength': conn['significance']
            })
        
        pdf_data = {
            'name': data.get('name', 'N/A'),
            'dob': data['date'],
            'tob': data['time'],
            'pob': data.get('place', 'N/A'),
            'planets': planets_list,
            'connections': all_connections
        }
        
        # Generate PDF
        filename = pdf_generator.generate_cosmic_connections_pdf(pdf_data)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_pdf/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/generate_transits_pdf', methods=['POST'])
def generate_transits_pdf():
    """Generate PDF for Transit analysis"""
    try:
        data = request.get_json()
        
        pdf_data = {
            'name': data.get('name', 'N/A'),
            'dob': data['date'],
            'analysis_date': data.get('analysis_date', 'N/A'),
            'transits': data.get('transits', [])
        }
        
        # Generate PDF
        filename = pdf_generator.generate_transits_pdf(pdf_data)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_pdf/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/generate_compatibility_pdf', methods=['POST'])
def generate_compatibility_pdf():
    """Generate PDF for Compatibility analysis"""
    try:
        data = request.get_json()
        
        pdf_data = {
            'person1_name': data.get('person1_name', 'N/A'),
            'person2_name': data.get('person2_name', 'N/A'),
            'analysis_date': data.get('analysis_date', 'N/A'),
            'compatibility_scores': data.get('compatibility_scores', []),
            'overall_compatibility': data.get('overall_compatibility', 0)
        }
        
        # Generate PDF
        filename = pdf_generator.generate_compatibility_pdf(pdf_data)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_pdf/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    """Download generated PDF file"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'File not found: {filename}'
        }), 404

@app.route('/api/clear_cache', methods=['POST'])
def clear_cache():
    """Clear all cached data"""
    try:
        cleared_count = cache_manager.clear_all()
        return jsonify({
            'success': True,
            'message': f'Cleared {cleared_count} cached items'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/cache_stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    try:
        cache_dir = cache_manager.cache_dir
        if os.path.exists(cache_dir):
            file_count = len([f for f in os.listdir(cache_dir) if f.endswith('.json')])
        else:
            file_count = 0
        
        return jsonify({
            'success': True,
            'cache_files': file_count,
            'cache_dir': cache_dir
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    # Start keep-alive service automatically when deployed to Render
    # The service will auto-detect the Render URL from environment variables
    print("🚀 Starting Vedic Astrology Dashboard...")
    start_keep_alive()  # Will auto-detect Render URL if available
    
    app.run(debug=True, host='0.0.0.0', port=5050) 