# =============================================================================
# VEDIC ASTROLOGY ENGINE - CLEAN, MODULAR, BEST PRACTICES
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

# House characteristics
HOUSE_ATTRIBUTES = {
    1: {'element': 'Fire', 'gender': 'Male', 'purpose': 'Dharma', 'kendra': True, 'trikona': True},
    2: {'element': 'Earth', 'gender': 'Female', 'purpose': 'Artha', 'kendra': False, 'trikona': False},
    3: {'element': 'Air', 'gender': 'Male', 'purpose': 'Kama', 'kendra': False, 'trikona': False},
    4: {'element': 'Water', 'gender': 'Female', 'purpose': 'Moksha', 'kendra': True, 'trikona': False},
    5: {'element': 'Fire', 'gender': 'Male', 'purpose': 'Dharma', 'kendra': False, 'trikona': True},
    6: {'element': 'Earth', 'gender': 'Female', 'purpose': 'Artha', 'kendra': False, 'trikona': False},
    7: {'element': 'Air', 'gender': 'Male', 'purpose': 'Kama', 'kendra': True, 'trikona': False},
    8: {'element': 'Water', 'gender': 'Female', 'purpose': 'Moksha', 'kendra': False, 'trikona': False},
    9: {'element': 'Fire', 'gender': 'Male', 'purpose': 'Dharma', 'kendra': False, 'trikona': True},
    10: {'element': 'Earth', 'gender': 'Female', 'purpose': 'Artha', 'kendra': True, 'trikona': False},
    11: {'element': 'Air', 'gender': 'Male', 'purpose': 'Kama', 'kendra': False, 'trikona': False},
    12: {'element': 'Water', 'gender': 'Female', 'purpose': 'Moksha', 'kendra': False, 'trikona': False}
}

# Sign lordships
SIGN_LORDS = {
    'Mesha': 'Mars', 'Rishaba': 'Venus', 'Mithuna': 'Mercury', 'Kataka': 'Moon',
    'Simha': 'Sun', 'Kanni': 'Mercury', 'Thula': 'Venus', 'Vrischika': 'Mars',
    'Dhanus': 'Jupiter', 'Makara': 'Saturn', 'Kumbha': 'Saturn', 'Meena': 'Jupiter'
}

# Planetary aspects
PLANETARY_ASPECTS = {
    'Sun': [7], 'Moon': [7], 'Mars': [4, 7, 8], 'Mercury': [7],
    'Jupiter': [5, 7, 9], 'Venus': [7], 'Saturn': [3, 7, 10],
    'Rahu': [5, 7, 9], 'Ketu': [5, 7, 9]
}

# Shadbala constants
NAISARGIKA_BALA = {
    'Saturn': 0.25, 'Mars': 0.5, 'Mercury': 0.75, 'Jupiter': 1.0,
    'Venus': 1.25, 'Moon': 1.5, 'Sun': 2.0
}

DIG_BALA = {
    'East': ['Mesha', 'Vrischika'],      # 1, 8
    'South': ['Kataka', 'Simha'],        # 4, 5
    'West': ['Thula', 'Kumbha'],         # 7, 11
    'North': ['Makara', 'Meena']         # 10, 12
}

print("✅ Constants loaded successfully!")

# --- Constants ---
VIMSHOTTARI_PERIODS = {
    'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16,
    'Saturn': 19, 'Mercury': 17, 'Ketu': 7, 'Venus': 20
}
NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
]

# --- Utility Functions ---
def calculate_birth_nakshatra(moon_longitude: float) -> Dict[str, Any]:
    nakshatra_span = 360 / 27
    nakshatra_index = int(moon_longitude // nakshatra_span)
    lord = NAKSHATRA_LORDS[nakshatra_index]
    progress = (moon_longitude % nakshatra_span) / nakshatra_span
    return {
        'index': nakshatra_index,
        'lord': lord,
        'progress': progress,
        'remaining': 1 - progress
    }

def calculate_mahadasha_periods(birth_nakshatra: Dict, birth_date: datetime.date) -> List[Dict]:
    periods = []
    current_lord = birth_nakshatra['lord']
    remaining_years = VIMSHOTTARI_PERIODS[current_lord] * birth_nakshatra['remaining']
    periods.append({
        'dasha': current_lord,
        'start_date': birth_date,
        'end_date': birth_date + datetime.timedelta(days=int(remaining_years * 365.25)),
        'years': round(remaining_years, 2)
    })
    lords = list(VIMSHOTTARI_PERIODS.keys())
    current_index = lords.index(current_lord)
    for i in range(1, 9):
        next_index = (current_index + i) % 9
        next_lord = lords[next_index]
        period_years = VIMSHOTTARI_PERIODS[next_lord]
        start_date = periods[-1]['end_date']
        end_date = start_date + datetime.timedelta(days=int(period_years * 365.25))
        periods.append({
            'dasha': next_lord,
            'start_date': start_date,
            'end_date': end_date,
            'years': period_years
        })
    return periods

def get_current_mahadasha(mahadasha_periods: List[Dict], date: datetime.date) -> Optional[Dict]:
    for period in mahadasha_periods:
        if period['start_date'] <= date <= period['end_date']:
            return period
    return None

def calculate_antardasha_periods(mahadasha_lord: str, mahadasha_years: float, mahadasha_start: datetime.date) -> List[Dict]:
    periods = []
    lords = list(VIMSHOTTARI_PERIODS.keys())
    lord_index = lords.index(mahadasha_lord)
    start_date = mahadasha_start
    for i in range(9):
        antardasha_lord = lords[(lord_index + i) % 9]
        antardasha_years = (VIMSHOTTARI_PERIODS[antardasha_lord] * mahadasha_years) / 120
        end_date = start_date + datetime.timedelta(days=int(antardasha_years * 365.25))
        periods.append({
            'dasha': antardasha_lord,
            'start_date': start_date,
            'end_date': end_date,
            'years': round(antardasha_years, 2)
        })
        start_date = end_date
    return periods

# --- Main API for Flask ---
def get_dasha_info(moon_longitude: float, birth_date: str, current_date: Optional[str] = None) -> Dict[str, Any]:
    birth_dt = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
    if current_date:
        current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    else:
        current_dt = datetime.date.today()
    birth_nakshatra = calculate_birth_nakshatra(moon_longitude)
    mahadasha_periods = calculate_mahadasha_periods(birth_nakshatra, birth_dt)
    current_mahadasha = get_current_mahadasha(mahadasha_periods, current_dt)
    antardasha_periods = []
    if current_mahadasha:
        antardasha_periods = calculate_antardasha_periods(
            current_mahadasha['dasha'],
            current_mahadasha['years'],
            current_mahadasha['start_date']
        )
    return {
        'birth_nakshatra': birth_nakshatra,
        'mahadasha_periods': mahadasha_periods,
        'current_mahadasha': current_mahadasha,
        'antardasha_periods': antardasha_periods
    }

# =============================================================================
# STEP 3: Core Calculation Functions
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

# =============================================================================
# SHADBALA CALCULATIONS
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
    # Determine direction based on ascendant
    asc_index = RASIS.index(asc_rasi)
    
    # Calculate planet's direction relative to ascendant
    planet_index = RASIS.index(planet_rasi)
    relative_position = (planet_index - asc_index) % 12
    
    # Directional strength based on relative position
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
    # Nathonnata Bala (Day/Night strength)
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    planet_pos = swe.calc_ut(jd, get_planet_id(planet_name), swe.FLG_SIDEREAL)[0][0]
    
    # Determine if it's day or night based on Sun's position
    sun_house = int(sun_pos // 30)
    planet_house = int(planet_pos // 30)
    
    # Day planets: Sun, Jupiter, Saturn
    # Night planets: Moon, Mars, Venus
    # Mercury is both
    day_planets = ['Sun', 'Jupiter', 'Saturn']
    night_planets = ['Moon', 'Mars', 'Venus']
    
    is_day = sun_house in [0, 1, 2, 3, 4, 5]  # First 6 houses = day
    
    if planet_name in day_planets:
        nathonnata = 1.0 if is_day else 0.5
    elif planet_name in night_planets:
        nathonnata = 0.5 if is_day else 1.0
    else:  # Mercury
        nathonnata = 0.75
    
    # Abda Bala (Annual strength) - simplified
    abda_bala = 0.75  # Placeholder
    
    # Masa Bala (Monthly strength) - simplified
    masa_bala = 0.75  # Placeholder
    
    # Vara Bala (Weekday strength) - simplified
    vara_bala = 0.75  # Placeholder
    
    # Hora Bala (Hourly strength) - simplified
    hora_bala = 0.75  # Placeholder
    
    return {
        'nathonnata_bala': round(nathonnata, 3),
        'abda_bala': round(abda_bala, 3),
        'masa_bala': round(masa_bala, 3),
        'vara_bala': round(vara_bala, 3),
        'hora_bala': round(hora_bala, 3),
        'kala_bala': round((nathonnata + abda_bala + masa_bala + vara_bala + hora_bala) / 5, 3)
    }

def calculate_cheshta_bala(planet_name: str, speed: float) -> float:
    """Calculate Cheshta Bala (Motional Strength)"""
    # For retrograde planets, strength increases
    if speed < 0:  # Retrograde
        return 1.0
    else:
        return 0.5

def calculate_naisargika_bala(planet_name: str) -> float:
    """Calculate Naisargika Bala (Natural Strength)"""
    return NAISARGIKA_BALA.get(planet_name, 1.0)

def calculate_drik_bala(planet_name: str, house: int) -> float:
    """Calculate Drik Bala (Aspectual Strength)"""
    # Simplified aspectual strength
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
    
    # Calculate all six strengths
    sthana = calculate_sthana_bala(planet_name, planet_data['rasi'], planet_data['house'])
    dig = calculate_dig_bala(planet_data['rasi'], planet_data.get('asc_rasi', 'Mesha'))
    kala = calculate_kala_bala(jd, planet_name)
    cheshta = calculate_cheshta_bala(planet_name, planet_data['speed'])
    naisargika = calculate_naisargika_bala(planet_name)
    drik = calculate_drik_bala(planet_name, planet_data['house'])
    
    # Total Shadbala
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

def get_planetary_strength(planet_name: str, rasi: str, house: int) -> Tuple[float, str]:
    """Calculate basic planetary strength (legacy function)"""
    strength = 2.5  # Base neutral strength
    dignity = 'neutral'
    
    if planet_name in PLANETARY_DIGNITY:
        dignity_info = PLANETARY_DIGNITY[planet_name]
        
        if rasi == dignity_info['exalted']:
            strength = 5.0
            dignity = 'exalted'
        elif rasi == dignity_info['debilitated']:
            strength = -1.0
            dignity = 'debilitated'
        elif rasi in dignity_info['own']:
            strength = 4.0
            dignity = 'own'
    
    # House bonuses
    house_attrs = HOUSE_ATTRIBUTES[house]
    if house_attrs['kendra']:
        strength += 1.0
    if house_attrs['trikona']:
        strength += 1.5
    
    return round(strength, 2), dignity

print("✅ Core calculation functions loaded!")

# =============================================================================
# STEP 4: Main Chart Calculation Class
# =============================================================================

class VedicChart:
    """Main Vedic Chart Calculator with Shadbala"""
    
    def __init__(self):
        self.chart_data = {}
        
    def calculate_chart(self, date: str, time: str, latitude: float, 
                       longitude: float, timezone: float) -> Dict[str, Any]:
        """Calculate complete Vedic birth chart with Shadbala"""
        
        # Get Julian Day
        jd = get_julian_day(date, time, timezone)
        ayanamsa = swe.get_ayanamsa(jd)
        
        # Calculate planets
        planets = {}
        
        # Main planets (Sun = 0, Moon = 1, Mercury = 2, Venus = 3, Mars = 4, Jupiter = 5, Saturn = 6)
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
            'longitude': ascmc[0],
            'rasi': asc_info['rasi'],
            'nakshatra': asc_info['nakshatra'],
            'pada': asc_info['pada']
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
                strength, dignity = get_planetary_strength(name, planet_data['rasi'], planet_data['house'])
                planet_data['strength'] = strength
                planet_data['dignity'] = dignity
        
        # Calculate houses with their characteristics
        houses = {}
        for i in range(12):
            house_num = i + 1
            cusp_longitude = cusps[i]
            sign_index = int(cusp_longitude // 30)
            sign = RASIS[sign_index]
            lord = SIGN_LORDS[sign]
            
            # Find planets in this house
            house_planets = [name for name, planet in planets.items() if planet['house'] == house_num]
            
            # Calculate house strength
            house_strength = sum(planets[p]['strength'] for p in house_planets)
            if lord in planets:
                house_strength += planets[lord]['strength'] * 0.5
            
            houses[house_num] = {
                'cusp_longitude': cusp_longitude,
                'sign': sign,
                'lord': lord,
                'planets': house_planets,
                'strength': round(house_strength, 2),
                **HOUSE_ATTRIBUTES[house_num]
            }
        
        # Detect basic yogas
        yogas = self._detect_yogas(planets, houses)
        
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
        
        return {
            'birth_info': {
                'date': date,
                'time': time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone': timezone,
                'ayanamsa': round(ayanamsa, 6)
            },
            'lagna': lagna,
            'planets': planets,
            'houses': houses,
            'aspects': aspects,
            'yogas': yogas
        }
    
    def _detect_yogas(self, planets: Dict, houses: Dict) -> List[str]:
        """Detect classical yogas"""
        yogas = []
        
        # Gaja Kesari Yoga: Moon and Jupiter in mutual Kendra
        moon_house = planets['Moon']['house']
        jupiter_house = planets['Jupiter']['house']
        kendra_diff = abs(moon_house - jupiter_house) % 12
        if kendra_diff in [0, 3, 6, 9]:
            yogas.append("Gaja Kesari Yoga")
        
        # Budhaditya Yoga: Sun and Mercury together
        if planets['Sun']['rasi'] == planets['Mercury']['rasi']:
            yogas.append("Budhaditya Yoga")
        
        # Chandra Mangal Yoga: Moon and Mars together
        if planets['Moon']['rasi'] == planets['Mars']['rasi']:
            yogas.append("Chandra Mangal Yoga")
        
        # Panch Mahapurusha Yogas
        mahapurusha_rules = {
            'Mars': (['Mesha', 'Vrischika', 'Makara'], 'Ruchaka Yoga'),
            'Mercury': (['Mithuna', 'Kanni'], 'Bhadra Yoga'),
            'Jupiter': (['Dhanus', 'Meena', 'Kataka'], 'Hamsa Yoga'),
            'Venus': (['Rishaba', 'Thula', 'Meena'], 'Malavya Yoga'),
            'Saturn': (['Makara', 'Kumbha', 'Thula'], 'Sasha Yoga')
        }
        
        for planet, (signs, yoga_name) in mahapurusha_rules.items():
            planet_data = planets[planet]
            if (planet_data['rasi'] in signs and 
                houses[planet_data['house']]['kendra']):
                yogas.append(yoga_name)
        
        # Kuja Dosha (Manglik)
        mars_house = planets['Mars']['house']
        if mars_house in [1, 2, 4, 7, 8, 12]:
            yogas.append("Kuja Dosha (Manglik)")
        
        # Guru Chandala Yoga: Jupiter with Rahu
        if planets['Jupiter']['rasi'] == planets['Rahu']['rasi']:
            yogas.append("Guru Chandala Yoga")
        
        # Lakshmi Yoga: Venus strong in Kendra/Trikona
        venus = planets['Venus']
        if (venus['house'] in [1, 4, 5, 7, 9, 10] and venus['strength'] >= 3.0):
            yogas.append("Lakshmi Yoga")
        
        return sorted(yogas)

print("✅ VedicChart class loaded successfully!")

# =============================================================================
# STEP 5: Testing and Display Functions
# =============================================================================

def display_chart_analysis(chart_data: Dict[str, Any]):
    """Display comprehensive chart analysis with Shadbala"""
    
    print("🧘‍♂️ VEDIC BIRTH CHART ANALYSIS WITH SHADBALA")
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
    print(f"Sign: {lagna['rasi']}")
    print(f"Longitude: {lagna['longitude']:.4f}°")
    print(f"Nakshatra: {lagna['nakshatra']} Pada {lagna['pada']}")
    
    # Planets with Shadbala
    print(f"\n🪐 Planetary Positions with Shadbala:")
    planets = chart_data['planets']
    for name, planet in planets.items():
        retro = " (R)" if planet['retrograde'] else ""
        strength_indicator = "💪" if planet['strength'] >= 4 else "⚡" if planet['strength'] >= 2 else "⚠️"
        
        if 'shadbala' in planet:
            shadbala = planet['shadbala']
            print(f"{name:<8}: {planet['rasi']:<10} | House {planet['house']} | "
                  f"Strength: {planet['strength']:+.1f} {strength_indicator} | "
                  f"{planet['dignity'].title()}{retro}")
            print(f"         Shadbala: Sthana={shadbala['sthana_bala']:.3f}, "
                  f"Dig={shadbala['dig_bala']:.3f}, Kala={shadbala['kala_bala']:.3f}, "
                  f"Cheshta={shadbala['cheshta_bala']:.3f}, "
                  f"Naisargika={shadbala['naisargika_bala']:.3f}, "
                  f"Drik={shadbala['drik_bala']:.3f}")
        else:
            print(f"{name:<8}: {planet['rasi']:<10} | House {planet['house']} | "
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
        
        print(f"House {num:2d}: {house['sign']:<10} | Lord: {house['lord']:<7} | "
              f"Strength: {house['strength']:4.1f} | {planets_str}{special_str}")
    
    # Aspects
    print(f"\n🔗 Planetary Aspects:")
    aspects = chart_data['aspects']
    for planet, aspected_houses in aspects.items():
        if aspected_houses:
            print(f"{planet}: aspects houses {aspected_houses}")
    
    # Yogas
    yogas = chart_data['yogas']
    print(f"\n🧘‍♂️ Yogas Detected ({len(yogas)} total):")
    if yogas:
        for yoga in yogas:
            # Add descriptions for common yogas
            descriptions = {
                "Gaja Kesari Yoga": "Brings wisdom, wealth, and high status",
                "Budhaditya Yoga": "Enhances intelligence and communication",
                "Chandra Mangal Yoga": "Indicates wealth through own efforts",
                "Ruchaka Yoga": "Mars Mahapurusha - courage and leadership",
                "Bhadra Yoga": "Mercury Mahapurusha - intelligence and learning",
                "Hamsa Yoga": "Jupiter Mahapurusha - wisdom and spirituality",
                "Malavya Yoga": "Venus Mahapurusha - luxury and beauty",
                "Sasha Yoga": "Saturn Mahapurusha - perseverance and authority",
                "Kuja Dosha": "Mars affliction affecting relationships",
                "Lakshmi Yoga": "Brings wealth and prosperity"
            }
            
            desc = descriptions.get(yoga, "Classical astrological combination")
            print(f"✓ {yoga}")
            print(f"  → {desc}")
    else:
        print("No major yogas detected")
    
    # Chart Summary
    strongest_planet = max(planets.items(), key=lambda x: x[1]['strength'])
    strongest_house = max(houses.items(), key=lambda x: x[1]['strength'])
    retrograde_planets = [name for name, planet in planets.items() if planet['retrograde']]
    
    print(f"\n📊 Chart Summary:")
    print(f"Strongest Planet: {strongest_planet[0]} (Strength: {strongest_planet[1]['strength']})")
    print(f"Strongest House: House {strongest_house[0]} (Strength: {strongest_house[1]['strength']})")
    print(f"Retrograde Planets: {retrograde_planets}")
    print(f"Total Yogas: {len(yogas)}")

def get_chart_json(chart_data: Dict[str, Any]) -> str:
    """Get chart data as formatted JSON"""
    return json.dumps(chart_data, indent=2, ensure_ascii=False)

print("✅ Display functions loaded successfully!")

# =============================================================================
# STEP 6: READY TO USE - EXAMPLE CALCULATIONS
# =============================================================================

def main():
    """Main function to demonstrate the Vedic Astrology Engine with Shadbala"""
    
    print("\n🚀 VEDIC ASTROLOGY ENGINE WITH SHADBALA IS READY!")
    print("📝 Example calculation for birth chart:")
    
    # Initialize calculator
    chart_calc = VedicChart()

    # Calculate chart (example values)
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