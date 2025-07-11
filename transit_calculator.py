# =============================================================================
# TRANSIT CALCULATOR
# Planetary transits and their effects on birth chart
# =============================================================================

import datetime
from typing import Dict, List, Any, Optional
from vedic_astrology_modular import VedicChartCalculator, RASIS, SIGN_LORDS

class TransitCalculator:
    """Calculate planetary transits and their effects"""
    
    def __init__(self):
        self.chart_calculator = VedicChartCalculator()
    
    def calculate_current_transits(self, date: str, time: str,
                                 latitude: float, longitude: float, timezone: float,
                                 transit_date: Optional[str] = None) -> Dict[str, Any]:
        """Calculate current planetary transits"""
        
        if transit_date is None:
            transit_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Calculate birth chart
        birth_chart = self.chart_calculator.calculate_chart(
            date=date,
            time=time,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )
        lagna_sign = birth_chart['lagna']['sign']
        lagna_sign_index = RASIS.index(lagna_sign)
        
        # Calculate transit chart
        transit_chart = self.chart_calculator.calculate_chart(
            date=transit_date,
            time="12:00",  # Midday transit
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )
        
        # Analyze transits
        transit_analysis = self.analyze_transits(birth_chart, transit_chart, lagna_sign_index)
        
        return {
            'birth_chart': birth_chart,
            'transit_chart': transit_chart,
            'transit_analysis': transit_analysis,
            'transit_date': transit_date
        }
    
    def analyze_transits(self, birth_chart: Dict, transit_chart: Dict, lagna_sign_index: int) -> Dict[str, Any]:
        """Analyze the effects of transits on birth chart"""
        
        birth_planets = birth_chart['planets']
        transit_planets = transit_chart['planets']
        birth_houses = birth_chart['houses']
        
        transit_effects = {}
        
        for planet_name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if planet_name in birth_planets and planet_name in transit_planets:
                birth_house = birth_planets[planet_name]['house']
                transit_sign = transit_planets[planet_name]['sign']
                # Calculate transit house relative to Lagna
                transit_sign_index = RASIS.index(transit_sign)
                transit_house = ((transit_sign_index - lagna_sign_index) % 12) + 1
                # Calculate transit effects
                effects = self.calculate_planet_transit_effects(
                    planet_name, birth_house, transit_sign, transit_house, birth_houses
                )
                transit_effects[planet_name] = {
                    'birth_house': birth_house,
                    'transit_sign': transit_sign,
                    'transit_house': transit_house,
                    'effects': effects
                }
        
        return transit_effects
    
    def calculate_planet_transit_effects(self, planet: str, birth_house: int, 
                                       transit_sign: str, transit_house: int,
                                       birth_houses: Dict) -> Dict[str, Any]:
        """Calculate specific effects of a planet's transit"""
        
        effects = {
            'strength': 'neutral',
            'impact': 'moderate',
            'areas_affected': [],
            'remedies': []
        }
        
        # Transit through own house (strong effect)
        if transit_house == birth_house:
            effects['strength'] = 'strong'
            effects['impact'] = 'high'
            effects['areas_affected'].append(f"House {birth_house} matters")
        
        # Transit through kendra houses (1, 4, 7, 10)
        if transit_house in [1, 4, 7, 10]:
            effects['strength'] = 'strong'
            effects['impact'] = 'high'
            effects['areas_affected'].append("Kendra transit - major life changes")
        
        # Transit through trikona houses (1, 5, 9)
        if transit_house in [1, 5, 9]:
            effects['strength'] = 'moderate'
            effects['impact'] = 'medium'
            effects['areas_affected'].append("Trikona transit - spiritual growth")
        
        # Transit through dusthana houses (6, 8, 12)
        if transit_house in [6, 8, 12]:
            effects['strength'] = 'weak'
            effects['impact'] = 'challenging'
            effects['areas_affected'].append("Dusthana transit - challenges")
        
        # Specific planet effects
        planet_effects = {
            'Sun': "Leadership, authority, father, government",
            'Moon': "Mind, emotions, mother, home",
            'Mars': "Energy, courage, siblings, property",
            'Mercury': "Communication, business, education",
            'Jupiter': "Wisdom, children, guru, spirituality",
            'Venus': "Relationships, luxury, arts, spouse",
            'Saturn': "Discipline, career, obstacles, karma"
        }
        
        if planet in planet_effects:
            effects['areas_affected'].append(planet_effects[planet])
        
        # Remedies based on transit
        if effects['impact'] == 'challenging':
            effects['remedies'].append(f"Chant {planet} mantras")
            effects['remedies'].append(f"Donate items related to {planet}")
        
        return effects
    
    def get_transit_summary(self, transit_analysis: Dict) -> Dict[str, Any]:
        """Get a summary of all current transits"""
        
        summary = {
            'strong_transits': [],
            'moderate_transits': [],
            'weak_transits': [],
            'challenging_transits': []
        }
        
        for planet, transit_info in transit_analysis.items():
            effects = transit_info['effects']
            
            transit_summary = {
                'planet': planet,
                'birth_house': transit_info['birth_house'],
                'transit_house': transit_info['transit_house'],
                'transit_sign': transit_info['transit_sign'],
                'effects': effects['areas_affected']
            }
            
            if effects['strength'] == 'strong':
                summary['strong_transits'].append(transit_summary)
            elif effects['strength'] == 'moderate':
                summary['moderate_transits'].append(transit_summary)
            elif effects['strength'] == 'weak':
                summary['weak_transits'].append(transit_summary)
            
            if effects['impact'] == 'challenging':
                summary['challenging_transits'].append(transit_summary)
        
        return summary

print("✅ Transit Calculator loaded!")

# Example usage
if __name__ == "__main__":
    calculator = TransitCalculator()
    
    transit_info = calculator.calculate_current_transits(
        date="1977-10-29",
        time="21:30",
        latitude=13.08333333,
        longitude=80.28333333,
        timezone=5.5
    )
    
    print("Current Transit Analysis:")
    summary = calculator.get_transit_summary(transit_info['transit_analysis'])
    
    print(f"Strong Transits: {len(summary['strong_transits'])}")
    print(f"Moderate Transits: {len(summary['moderate_transits'])}")
    print(f"Challenging Transits: {len(summary['challenging_transits'])}")
    
    for transit in summary['strong_transits']:
        print(f"  {transit['planet']}: House {transit['transit_house']} ({transit['transit_sign']})") 