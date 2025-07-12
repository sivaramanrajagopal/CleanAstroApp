# =============================================================================
# VEDIC ASTROLOGY ENGINE - MODULAR IMPLEMENTATION
# Complete implementation based on Parashara principles
# =============================================================================

import swisseph as swe
import datetime
import json
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple

# Initialize Swiss Ephemeris
swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# =============================================================================
# CONSTANTS AND DATA STRUCTURES
# =============================================================================

# Zodiac Signs (Rasis)
RASIS = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]

# Nakshatras
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Planetary dignity information
PLANETARY_DIGNITY = {
    'Sun': {'exalted': 'Mesha', 'debilitated': 'Thula', 'own': ['Simha']},
    'Moon': {'exalted': 'Rishaba', 'debilitated': 'Vrischika', 'own': ['Kataka']},
    'Mars': {'exalted': 'Makara', 'debilitated': 'Kataka', 'own': ['Mesha', 'Vrischika']},
    'Mercury': {'exalted': 'Kanni', 'debilitated': 'Meena', 'own': ['Mithuna', 'Kanni']},
    'Jupiter': {'exalted': 'Kataka', 'debilitated': 'Makara', 'own': ['Dhanus', 'Meena']},
    'Venus': {'exalted': 'Meena', 'debilitated': 'Kanni', 'own': ['Rishaba', 'Thula']},
    'Saturn': {'exalted': 'Thula', 'debilitated': 'Mesha', 'own': ['Makara', 'Kumbha']},
}

# House characteristics with MOBILITY
HOUSE_ATTRIBUTES = {
    1: {'element': 'Fire', 'gender': 'Male', 'purpose': 'Dharma', 'mobility': 'Movable', 'kendra': True, 'trikona': True},
    2: {'element': 'Earth', 'gender': 'Female', 'purpose': 'Artha', 'mobility': 'Fixed', 'kendra': False, 'trikona': False},
    3: {'element': 'Air', 'gender': 'Male', 'purpose': 'Kama', 'mobility': 'Dual', 'kendra': False, 'trikona': False},
    4: {'element': 'Water', 'gender': 'Female', 'purpose': 'Moksha', 'mobility': 'Movable', 'kendra': True, 'trikona': False},
    5: {'element': 'Fire', 'gender': 'Male', 'purpose': 'Dharma', 'mobility': 'Fixed', 'kendra': False, 'trikona': True},
    6: {'element': 'Earth', 'gender': 'Female', 'purpose': 'Artha', 'mobility': 'Dual', 'kendra': False, 'trikona': False},
    7: {'element': 'Air', 'gender': 'Male', 'purpose': 'Kama', 'mobility': 'Movable', 'kendra': True, 'trikona': False},
    8: {'element': 'Water', 'gender': 'Female', 'purpose': 'Moksha', 'mobility': 'Fixed', 'kendra': False, 'trikona': False},
    9: {'element': 'Fire', 'gender': 'Male', 'purpose': 'Dharma', 'mobility': 'Dual', 'kendra': False, 'trikona': True},
    10: {'element': 'Earth', 'gender': 'Female', 'purpose': 'Artha', 'mobility': 'Movable', 'kendra': True, 'trikona': False},
    11: {'element': 'Air', 'gender': 'Male', 'purpose': 'Kama', 'mobility': 'Fixed', 'kendra': False, 'trikona': False},
    12: {'element': 'Water', 'gender': 'Female', 'purpose': 'Moksha', 'mobility': 'Dual', 'kendra': False, 'trikona': False}
}

# Sign lordships
SIGN_LORDS = {
    'Mesha': 'Mars', 'Rishaba': 'Venus', 'Mithuna': 'Mercury', 'Kataka': 'Moon',
    'Simha': 'Sun', 'Kanni': 'Mercury', 'Thula': 'Venus', 'Vrischika': 'Mars',
    'Dhanus': 'Jupiter', 'Makara': 'Saturn', 'Kumbha': 'Saturn', 'Meena': 'Jupiter'
}

# Planetary aspects (Drishti)
PLANETARY_ASPECTS = {
    'Sun': [7], 'Moon': [7], 'Mars': [4, 7, 8], 'Mercury': [7],
    'Jupiter': [5, 7, 9], 'Venus': [7], 'Saturn': [3, 7, 10],
    'Rahu': [5, 7, 9], 'Ketu': [5, 7, 9]
}

# Naisargika Bala (Natural Strength)
NAISARGIKA_BALA = {
    'Saturn': 0.25, 'Mars': 0.5, 'Mercury': 0.75, 'Jupiter': 1.0,
    'Venus': 1.25, 'Moon': 1.5, 'Sun': 2.0
}

print("✅ Constants loaded successfully!")

# =============================================================================
# MODULE 1: CORE CALCULATION FUNCTIONS
# =============================================================================

def get_julian_day(date_str: str, time_str: str, timezone_offset: float) -> float:
    """Convert local datetime to Julian Day (UT)"""
    local_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    utc_dt = local_dt - datetime.timedelta(hours=timezone_offset)
    
    return swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0
    )

def get_rasi_info(longitude: float) -> Dict[str, Any]:
    """Get rasi, nakshatra, and pada from longitude"""
    # Rasi (30-degree divisions)
    rasi_index = int(longitude // 30)
    rasi = RASIS[rasi_index]
    
    # Nakshatra (13.333... degree divisions)
    nakshatra_span = 360 / 27
    nakshatra_index = int(longitude // nakshatra_span)
    nakshatra = NAKSHATRAS[nakshatra_index]
    
    # Pada (1/4 of nakshatra)
    pada_span = nakshatra_span / 4
    pada = int((longitude % nakshatra_span) // pada_span) + 1
    
    return {
        'rasi': rasi,
        'nakshatra': nakshatra,
        'pada': pada,
        'degrees_in_rasi': longitude % 30
    }

def calculate_planet_position(jd: float, planet_id: int) -> Dict[str, Any]:
    """Calculate position for a single planet"""
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    result = swe.calc_ut(jd, planet_id, flags)[0]
    longitude, latitude, speed = result[0], result[1], result[3]
    
    rasi_info = get_rasi_info(longitude)
    
    return {
        'longitude': longitude,
        'latitude': latitude,
        'speed': speed,
        'retrograde': speed < 0,
        'rasi': rasi_info['rasi'],
        'nakshatra': rasi_info['nakshatra'],
        'pada': rasi_info['pada'],
        'degrees_in_rasi': rasi_info['degrees_in_rasi']
    }

print("✅ Core calculation functions loaded!")

# =============================================================================
# MODULE 2: SHADBALA CALCULATIONS
# =============================================================================

def calculate_sthana_bala(planet_name: str, rasi: str, house: int) -> Dict[str, Any]:
    """Calculate Sthana Bala (Positional Strength)"""
    sthana_bala = 0.0
    dignity = 'neutral'
    
    if planet_name in PLANETARY_DIGNITY:
        dignity_info = PLANETARY_DIGNITY[planet_name]
        
        if rasi == dignity_info['exalted']:
            sthana_bala = 1.0
            dignity = 'exalted'
        elif rasi == dignity_info['debilitated']:
            sthana_bala = 0.25
            dignity = 'debilitated'
        elif rasi in dignity_info['own']:
            sthana_bala = 0.75
            dignity = 'own'
        else:
            sthana_bala = 0.5
            dignity = 'neutral'
    
    # House bonuses
    house_attrs = HOUSE_ATTRIBUTES[house]
    if house_attrs['kendra']:
        sthana_bala += 0.25
    if house_attrs['trikona']:
        sthana_bala += 0.25
    
    return {
        'sthana_bala': round(sthana_bala, 3),
        'dignity': dignity
    }

def calculate_dig_bala(planet_rasi: str, asc_rasi: str) -> float:
    """Calculate Dig Bala (Directional Strength)"""
    asc_index = RASIS.index(asc_rasi)
    planet_index = RASIS.index(planet_rasi)
    relative_position = (planet_index - asc_index) % 12
    
    if relative_position in [0, 1]:  # East
        return 1.0
    elif relative_position in [3, 4]:  # South
        return 0.75
    elif relative_position in [6, 7]:  # West
        return 0.5
    elif relative_position in [9, 10]:  # North
        return 0.25
    else:
        return 0.5

def calculate_kala_bala(jd: float, planet_name: str) -> Dict[str, float]:
    """Calculate Kala Bala (Temporal Strength)"""
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    planet_pos = swe.calc_ut(jd, get_planet_id(planet_name), swe.FLG_SIDEREAL)[0][0]
    
    sun_house = int(sun_pos // 30)
    planet_house = int(planet_pos // 30)
    
    day_planets = ['Sun', 'Jupiter', 'Saturn']
    night_planets = ['Moon', 'Mars', 'Venus']
    
    is_day = sun_house in [0, 1, 2, 3, 4, 5]
    
    if planet_name in day_planets:
        nathonnata = 1.0 if is_day else 0.5
    elif planet_name in night_planets:
        nathonnata = 0.5 if is_day else 1.0
    else:  # Mercury
        nathonnata = 0.75
    
    return {
        'nathonnata_bala': round(nathonnata, 3),
        'abda_bala': 0.75,  # Simplified
        'masa_bala': 0.75,  # Simplified
        'vara_bala': 0.75,  # Simplified
        'hora_bala': 0.75,  # Simplified
        'kala_bala': round((nathonnata + 0.75 + 0.75 + 0.75 + 0.75) / 5, 3)
    }

def calculate_cheshta_bala(planet_name: str, speed: float) -> float:
    """Calculate Cheshta Bala (Motional Strength)"""
    return 1.0 if speed < 0 else 0.5

def calculate_naisargika_bala(planet_name: str) -> float:
    """Calculate Naisargika Bala (Natural Strength)"""
    return NAISARGIKA_BALA.get(planet_name, 1.0)

def calculate_drik_bala(planet_name: str, house: int) -> float:
    """Calculate Drik Bala (Aspectual Strength)"""
    if house in [1, 4, 7, 10]:  # Kendra houses
        return 1.0
    elif house in [5, 9]:  # Trikona houses
        return 0.75
    else:
        return 0.5

def get_planet_id(planet_name: str) -> int:
    """Get Swiss Ephemeris planet ID"""
    planet_ids = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN
    }
    return planet_ids.get(planet_name, swe.SUN)

def calculate_shadbala(jd: float, planet_name: str, planet_data: Dict) -> Dict[str, Any]:
    """Calculate complete Shadbala for a planet"""
    
    sthana = calculate_sthana_bala(planet_name, planet_data['rasi'], planet_data['house'])
    dig = calculate_dig_bala(planet_data['rasi'], planet_data.get('asc_rasi', 'Mesha'))
    kala = calculate_kala_bala(jd, planet_name)
    cheshta = calculate_cheshta_bala(planet_name, planet_data['speed'])
    naisargika = calculate_naisargika_bala(planet_name)
    drik = calculate_drik_bala(planet_name, planet_data['house'])
    
    total_shadbala = (sthana['sthana_bala'] + dig + kala['kala_bala'] + 
                      cheshta + naisargika + drik) / 6
    
    return {
        'sthana_bala': sthana['sthana_bala'],
        'dig_bala': round(dig, 3),
        'kala_bala': kala['kala_bala'],
        'cheshta_bala': round(cheshta, 3),
        'naisargika_bala': round(naisargika, 3),
        'drik_bala': round(drik, 3),
        'total_shadbala': round(total_shadbala, 3),
        'dignity': sthana['dignity']
    }

print("✅ Shadbala calculations loaded!")

# =============================================================================
# MODULE 3: YOGA DETECTION
# =============================================================================

def detect_gajakesari_yoga(planets: Dict, houses: Dict) -> bool:
    """Detect Gajakesari Yoga: Moon and Jupiter in mutual Kendra"""
    moon_house = planets['Moon']['house']
    jupiter_house = planets['Jupiter']['house']
    kendra_diff = abs(moon_house - jupiter_house) % 12
    return kendra_diff in [0, 3, 6, 9]

def detect_budhaditya_yoga(planets: Dict) -> bool:
    """Detect Budhaditya Yoga: Sun and Mercury together"""
    return planets['Sun']['rasi'] == planets['Mercury']['rasi']

def detect_chandra_mangal_yoga(planets: Dict) -> bool:
    """Detect Chandra Mangal Yoga: Moon and Mars together"""
    return planets['Moon']['rasi'] == planets['Mars']['rasi']

def detect_dhana_yoga(planets: Dict, houses: Dict) -> bool:
    """Detect Dhana Yoga: Strong 2nd, 5th, 9th, 11th houses"""
    wealth_houses = [2, 5, 9, 11]
    strong_wealth_houses = 0
    
    for house_num in wealth_houses:
        if houses[house_num]['strength'] > 5.0:
            strong_wealth_houses += 1
    
    return strong_wealth_houses >= 2

def detect_raja_yoga(planets: Dict, houses: Dict) -> bool:
    """Detect Raja Yoga: Strong 1st, 4th, 7th, 10th houses"""
    kendra_houses = [1, 4, 7, 10]
    strong_kendra_houses = 0
    
    for house_num in kendra_houses:
        if houses[house_num]['strength'] > 6.0:
            strong_kendra_houses += 1
    
    return strong_kendra_houses >= 2

def detect_mahapurusha_yogas(planets: Dict, houses: Dict) -> List[str]:
    """Detect Panch Mahapurusha Yogas"""
    mahapurusha_rules = {
        'Mars': (['Mesha', 'Vrischika', 'Makara'], 'Ruchaka Yoga'),
        'Mercury': (['Mithuna', 'Kanni'], 'Bhadra Yoga'),
        'Jupiter': (['Dhanus', 'Meena', 'Kataka'], 'Hamsa Yoga'),
        'Venus': (['Rishaba', 'Thula', 'Meena'], 'Malavya Yoga'),
        'Saturn': (['Makara', 'Kumbha', 'Thula'], 'Sasha Yoga')
    }
    
    detected_yogas = []
    for planet, (signs, yoga_name) in mahapurusha_rules.items():
        planet_data = planets[planet]
        if (planet_data['rasi'] in signs and 
            houses[planet_data['house']]['kendra']):
            detected_yogas.append(yoga_name)
    
    return detected_yogas

def detect_kuja_dosha(planets: Dict) -> bool:
    """Detect Kuja Dosha (Manglik)"""
    mars_house = planets['Mars']['house']
    return mars_house in [1, 2, 4, 7, 8, 12]

def detect_all_yogas(planets: Dict, houses: Dict) -> Dict[str, bool]:
    """Detect all yogas"""
    return {
        'Gajakesari': detect_gajakesari_yoga(planets, houses),
        'Budhaditya': detect_budhaditya_yoga(planets),
        'Chandra_Mangal': detect_chandra_mangal_yoga(planets),
        'Dhana': detect_dhana_yoga(planets, houses),
        'Raja': detect_raja_yoga(planets, houses),
        'Kuja_Dosha': detect_kuja_dosha(planets),
        'Mahapurusha': len(detect_mahapurusha_yogas(planets, houses)) > 0
    }

print("✅ Yoga detection loaded!")

# =============================================================================
# MODULE 4: MAIN CHART CALCULATOR
# =============================================================================

class VedicChartCalculator:
    """Main Vedic Chart Calculator with all modules"""
    
    def __init__(self):
        self.chart_data = {}
        
    def calculate_chart(self, date: str, time: str, latitude: float, 
                       longitude: float, timezone: float) -> Dict[str, Any]:
        """Calculate complete Vedic birth chart"""
        
        # Get Julian Day
        jd = get_julian_day(date, time, timezone)
        ayanamsa = swe.get_ayanamsa(jd)
        
        # Calculate planets
        planets = {}
        
        # Main planets
        planet_names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for i, name in enumerate(planet_names):
            planets[name] = calculate_planet_position(jd, i)
        
        # Rahu and Ketu
        rahu_result = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
        rahu_info = get_rasi_info(rahu_result[0])
        ketu_lon = (rahu_result[0] + 180.0) % 360.0
        ketu_info = get_rasi_info(ketu_lon)
        
        planets['Rahu'] = {
            'longitude': rahu_result[0],
            'speed': rahu_result[3],
            'retrograde': True,
            'rasi': rahu_info['rasi'],
            'nakshatra': rahu_info['nakshatra'],
            'pada': rahu_info['pada']
        }
        
        planets['Ketu'] = {
            'longitude': ketu_lon,
            'speed': rahu_result[3],
            'retrograde': True,
            'rasi': ketu_info['rasi'],
            'nakshatra': ketu_info['nakshatra'],
            'pada': ketu_info['pada']
        }
        
        # Ascendant
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
        asc_info = get_rasi_info(ascmc[0])
        
        lagna = {
            'sign': asc_info['rasi'],
            'degree': round(ascmc[0], 2)
        }
        
        # Calculate houses for each planet
        asc_rasi_index = int(ascmc[0] // 30)
        
        for planet_data in planets.values():
            planet_rasi_index = int(planet_data['longitude'] // 30)
            house = ((planet_rasi_index - asc_rasi_index) % 12) + 1
            planet_data['house'] = house
            planet_data['asc_rasi'] = asc_info['rasi']
            
        # Calculate Shadbala for each planet
        for name, planet_data in planets.items():
            if name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
                shadbala = calculate_shadbala(jd, name, planet_data)
                planet_data['shadbala'] = shadbala
                planet_data['strength'] = shadbala['total_shadbala'] * 10  # Scale for display
                planet_data['dignity'] = shadbala['dignity']
            else:
                # For Rahu/Ketu, use basic strength calculation
                strength = 3.5  # Base strength for nodes
                planet_data['strength'] = strength
                planet_data['dignity'] = 'neutral'
        
        # Calculate houses with their characteristics
        houses = {}
        # Parashara mapping: start from Lagna sign
        lagna_sign_index = asc_rasi_index
        for i in range(12):
            house_num = i + 1
            # The sign in this house (starting from Lagna)
            sign_index = (lagna_sign_index + i) % 12
            sign = RASIS[sign_index]
            lord = SIGN_LORDS[sign]
            # Map element, purpose, mobility, etc. from the sign
            sign_attrs = HOUSE_ATTRIBUTES[sign_index + 1]
            # Find planets in this house
            house_planets = [name for name, planet in planets.items() if planet['house'] == house_num]
            # Calculate house strength including lord strength
            house_strength = sum(planets[p]['strength'] for p in house_planets)
            if lord in planets:
                lord_strength = planets[lord]['strength'] * 0.5
                house_strength += lord_strength
            houses[house_num] = {
                'sign': sign,
                'element': sign_attrs['element'],
                'gender': sign_attrs['gender'],
                'purpose': sign_attrs['purpose'],
                'mobility': sign_attrs['mobility'],
                'planets': house_planets,
                'strength': round(house_strength, 2),
                'kendra': sign_attrs['kendra'],
                'trikona': sign_attrs['trikona']
            }
        
        # Calculate aspects
        aspects = {}
        for name, planet in planets.items():
            if name in PLANETARY_ASPECTS:
                planet_house = planet['house']
                aspect_houses = []
                for offset in PLANETARY_ASPECTS[name]:
                    target_house = ((planet_house - 1 + offset - 1) % 12) + 1
                    aspect_houses.append(target_house)
                aspects[name] = sorted(aspect_houses)
        
        # Detect yogas
        yogas = detect_all_yogas(planets, houses)
        
        # Format planets for JSON output
        formatted_planets = {}
        for name, planet in planets.items():
            formatted_planets[name] = {
                'sign': planet['rasi'],
                'house': planet['house'],
                'longitude': round(planet['longitude'], 2),
                'degree': round(planet['longitude'], 2),  # Keep both for compatibility
                'strength': round(planet['strength'], 2),
                'dignity': planet['dignity'],
                'retrograde': planet['retrograde'],
                'nakshatra': planet['nakshatra'],
                'pada': planet['pada'],
                'shadbala': planet.get('shadbala', {})
            }
        
        return {
            'lagna': lagna,
            'planets': formatted_planets,
            'houses': houses,
            'aspects': aspects,
            'yogas': yogas,
            'birth_info': {
                'date': date,
                'time': time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone': timezone,
                'ayanamsa': round(ayanamsa, 6)
            }
        }

print("✅ Main chart calculator loaded!")

# =============================================================================
# MODULE 5: DISPLAY AND UTILITIES
# =============================================================================

def display_chart_analysis(chart_data: Dict[str, Any]):
    """Display comprehensive chart analysis"""
    
    print("🧘‍♂️ VEDIC BIRTH CHART ANALYSIS")
    print("=" * 60)
    
    # Birth Info
    birth = chart_data['birth_info']
    print(f"\n📍 Birth Details:")
    print(f"Date: {birth['date']}")
    print(f"Time: {birth['time']}")
    print(f"Location: {birth['latitude']:.3f}°N, {birth['longitude']:.3f}°E")
    print(f"Ayanamsa: {birth['ayanamsa']}°")
    
    # Lagna
    lagna = chart_data['lagna']
    print(f"\n🌅 Lagna (Ascendant):")
    print(f"Sign: {lagna['sign']}")
    print(f"Degree: {lagna['degree']}°")
    
    # Planets
    print(f"\n🪐 Planetary Positions:")
    planets = chart_data['planets']
    for name, planet in planets.items():
        retro = " (R)" if planet['retrograde'] else ""
        strength_indicator = "💪" if planet['strength'] >= 4 else "⚡" if planet['strength'] >= 2 else "⚠️"
        print(f"{name:<8}: {planet['sign']:<10} | House {planet['house']} | "
              f"Strength: {planet['strength']:+.1f} {strength_indicator} | "
              f"{planet['dignity'].title()}{retro}")
    
    # Houses
    print(f"\n🏠 House Analysis:")
    houses = chart_data['houses']
    for num in range(1, 13):
        house = houses[num]
        planets_str = ", ".join(house['planets']) if house['planets'] else "Empty"
        special = []
        if house['kendra']: special.append("Kendra")
        if house['trikona']: special.append("Trikona")
        special_str = f" ({', '.join(special)})" if special else ""
        
        print(f"House {num:2d}: {house['element']:<6} | {house['gender']:<6} | "
              f"{house['purpose']:<6} | {house['mobility']:<6} | "
              f"Strength: {house['strength']:4.1f} | {planets_str}{special_str}")
    
    # Aspects
    print(f"\n🔗 Planetary Aspects:")
    aspects = chart_data['aspects']
    for planet, aspected_houses in aspects.items():
        if aspected_houses:
            print(f"{planet}: aspects houses {aspected_houses}")
    
    # Yogas
    yogas = chart_data['yogas']
    print(f"\n🧘‍♂️ Yogas Detected:")
    for yoga, detected in yogas.items():
        if detected:
            print(f"✓ {yoga}")
    
    # Chart Summary
    strongest_planet = max(planets.items(), key=lambda x: x[1]['strength'])
    strongest_house = max(houses.items(), key=lambda x: x[1]['strength'])
    retrograde_planets = [name for name, planet in planets.items() if planet['retrograde']]
    
    print(f"\n📊 Chart Summary:")
    print(f"Strongest Planet: {strongest_planet[0]} (Strength: {strongest_planet[1]['strength']})")
    print(f"Strongest House: House {strongest_house[0]} (Strength: {strongest_house[1]['strength']})")
    print(f"Retrograde Planets: {retrograde_planets}")
    print(f"Total Yogas: {sum(yogas.values())}")

def get_chart_json(chart_data: Dict[str, Any]) -> str:
    """Get chart data as formatted JSON"""
    return json.dumps(chart_data, indent=2, ensure_ascii=False)

print("✅ Display functions loaded!")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to demonstrate the complete Vedic Astrology Engine"""
    
    print("\n🚀 VEDIC ASTROLOGY ENGINE - MODULAR IMPLEMENTATION")
    print("📝 Complete calculation for birth chart:")
    
    # Initialize calculator
    chart_calc = VedicChartCalculator()

    # Calculate chart
    chart = chart_calc.calculate_chart(
        date="1977-10-29",      # YYYY-MM-DD format
        time="21:30",           # HH:MM format (24-hour)
        latitude=13.08333333,   # Birth place latitude
        longitude=80.28333333,  # Birth place longitude  
        timezone=5.5            # Timezone offset from UTC
    )

    # Display analysis
    display_chart_analysis(chart)

    # Get JSON data
    json_data = get_chart_json(chart)
    print("\n📄 JSON Data:")
    print(json_data)

if __name__ == "__main__":
    main() 