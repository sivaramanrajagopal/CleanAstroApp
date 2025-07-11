# =============================================================================
# COMPATIBILITY ANALYZER
# Synastry and relationship analysis
# =============================================================================

from typing import Dict, List, Any, Tuple
from vedic_astrology_modular import VedicChartCalculator, RASIS, SIGN_LORDS

class CompatibilityAnalyzer:
    """Analyze compatibility between two birth charts"""
    
    def __init__(self):
        self.chart_calculator = VedicChartCalculator()
    
    def analyze_compatibility(self, person1_details: Dict, person2_details: Dict) -> Dict[str, Any]:
        """Analyze compatibility between two people"""
        
        # Calculate both charts
        chart1 = self.chart_calculator.calculate_chart(**person1_details)
        chart2 = self.chart_calculator.calculate_chart(**person2_details)
        
        # Perform various compatibility analyses
        compatibility = {
            'overall_score': 0,
            'mangal_dosha': self.check_mangal_dosha(chart1, chart2),
            'nakshatra_compatibility': self.analyze_nakshatra_compatibility(chart1, chart2),
            'planetary_compatibility': self.analyze_planetary_compatibility(chart1, chart2),
            'house_compatibility': self.analyze_house_compatibility(chart1, chart2),
            'remedies': []
        }
        
        # Calculate overall score
        compatibility['overall_score'] = self.calculate_overall_score(compatibility)
        
        return {
            'person1_chart': chart1,
            'person2_chart': chart2,
            'compatibility': compatibility
        }
    
    def check_mangal_dosha(self, chart1: Dict, chart2: Dict) -> Dict[str, Any]:
        """Check for Mangal Dosha (Kuja Dosha) compatibility"""
        
        mars1_house = chart1['planets']['Mars']['house']
        mars2_house = chart2['planets']['Mars']['house']
        
        mangal_dosha1 = mars1_house in [1, 2, 4, 7, 8, 12]
        mangal_dosha2 = mars2_house in [1, 2, 4, 7, 8, 12]
        
        compatibility_score = 0
        if mangal_dosha1 and mangal_dosha2:
            compatibility_score = 100  # Both have dosha - compatible
        elif not mangal_dosha1 and not mangal_dosha2:
            compatibility_score = 100  # Neither has dosha - compatible
        else:
            compatibility_score = 50   # One has dosha - partial compatibility
        
        return {
            'person1_mangal_dosha': mangal_dosha1,
            'person2_mangal_dosha': mangal_dosha2,
            'compatibility_score': compatibility_score,
            'description': self.get_mangal_dosha_description(mangal_dosha1, mangal_dosha2)
        }
    
    def get_mangal_dosha_description(self, dosha1: bool, dosha2: bool) -> str:
        """Get description for Mangal Dosha compatibility"""
        if dosha1 and dosha2:
            return "Both have Mangal Dosha - Highly Compatible"
        elif not dosha1 and not dosha2:
            return "Neither has Mangal Dosha - Compatible"
        else:
            return "One person has Mangal Dosha - Partial Compatibility"
    
    def analyze_nakshatra_compatibility(self, chart1: Dict, chart2: Dict) -> Dict[str, Any]:
        """Analyze Nakshatra compatibility"""
        
        moon1_nakshatra = chart1['planets']['Moon']['nakshatra']
        moon2_nakshatra = chart2['planets']['Moon']['nakshatra']
        
        # Nakshatra compatibility rules
        compatible_nakshatras = {
            'Ashwini': ['Bharani', 'Krittika'],
            'Bharani': ['Ashwini', 'Krittika'],
            'Krittika': ['Ashwini', 'Bharani', 'Rohini'],
            'Rohini': ['Krittika', 'Mrigashira'],
            'Mrigashira': ['Rohini', 'Ardra'],
            'Ardra': ['Mrigashira', 'Punarvasu'],
            'Punarvasu': ['Ardra', 'Pushya'],
            'Pushya': ['Punarvasu', 'Ashlesha'],
            'Ashlesha': ['Pushya', 'Magha'],
            'Magha': ['Ashlesha', 'Purva Phalguni'],
            'Purva Phalguni': ['Magha', 'Uttara Phalguni'],
            'Uttara Phalguni': ['Purva Phalguni', 'Hasta'],
            'Hasta': ['Uttara Phalguni', 'Chitra'],
            'Chitra': ['Hasta', 'Swati'],
            'Swati': ['Chitra', 'Vishakha'],
            'Vishakha': ['Swati', 'Anuradha'],
            'Anuradha': ['Vishakha', 'Jyeshtha'],
            'Jyeshtha': ['Anuradha', 'Mula'],
            'Mula': ['Jyeshtha', 'Purva Ashadha'],
            'Purva Ashadha': ['Mula', 'Uttara Ashadha'],
            'Uttara Ashadha': ['Purva Ashadha', 'Shravana'],
            'Shravana': ['Uttara Ashadha', 'Dhanishta'],
            'Dhanishta': ['Shravana', 'Shatabhisha'],
            'Shatabhisha': ['Dhanishta', 'Purva Bhadrapada'],
            'Purva Bhadrapada': ['Shatabhisha', 'Uttara Bhadrapada'],
            'Uttara Bhadrapada': ['Purva Bhadrapada', 'Revati'],
            'Revati': ['Uttara Bhadrapada', 'Ashwini']
        }
        
        compatibility_score = 0
        if moon1_nakshatra == moon2_nakshatra:
            compatibility_score = 100  # Same nakshatra
        elif moon2_nakshatra in compatible_nakshatras.get(moon1_nakshatra, []):
            compatibility_score = 75   # Compatible nakshatra
        else:
            compatibility_score = 50   # Neutral compatibility
        
        return {
            'person1_nakshatra': moon1_nakshatra,
            'person2_nakshatra': moon2_nakshatra,
            'compatibility_score': compatibility_score,
            'description': self.get_nakshatra_description(compatibility_score)
        }
    
    def get_nakshatra_description(self, score: int) -> str:
        """Get description for Nakshatra compatibility"""
        if score == 100:
            return "Same Nakshatra - Excellent Compatibility"
        elif score == 75:
            return "Compatible Nakshatras - Good Compatibility"
        else:
            return "Neutral Nakshatra Compatibility"
    
    def analyze_planetary_compatibility(self, chart1: Dict, chart2: Dict) -> Dict[str, Any]:
        """Analyze planetary compatibility"""
        
        compatibility_scores = {}
        total_score = 0
        
        # Analyze key planets for compatibility
        key_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        
        for planet in key_planets:
            if planet in chart1['planets'] and planet in chart2['planets']:
                planet1 = chart1['planets'][planet]
                planet2 = chart2['planets'][planet]
                
                score = self.calculate_planet_compatibility(planet, planet1, planet2)
                compatibility_scores[planet] = score
                total_score += score
        
        avg_score = total_score / len(compatibility_scores) if compatibility_scores else 0
        
        return {
            'individual_scores': compatibility_scores,
            'average_score': round(avg_score, 2),
            'description': self.get_planetary_description(avg_score)
        }
    
    def calculate_planet_compatibility(self, planet: str, planet1: Dict, planet2: Dict) -> int:
        """Calculate compatibility between two planets"""
        
        # Same sign - excellent compatibility
        if planet1['sign'] == planet2['sign']:
            return 100
        
        # Compatible signs
        compatible_signs = {
            'Sun': ['Simha', 'Mesha'],
            'Moon': ['Kataka', 'Rishaba'],
            'Mars': ['Mesha', 'Vrischika', 'Makara'],
            'Mercury': ['Mithuna', 'Kanni'],
            'Jupiter': ['Dhanus', 'Meena', 'Kataka'],
            'Venus': ['Rishaba', 'Thula', 'Meena'],
            'Saturn': ['Makara', 'Kumbha', 'Thula']
        }
        
        if planet in compatible_signs:
            if planet1['sign'] in compatible_signs[planet] and planet2['sign'] in compatible_signs[planet]:
                return 75
        
        # Neutral compatibility
        return 50
    
    def get_planetary_description(self, score: float) -> str:
        """Get description for planetary compatibility"""
        if score >= 80:
            return "Excellent Planetary Compatibility"
        elif score >= 60:
            return "Good Planetary Compatibility"
        else:
            return "Moderate Planetary Compatibility"
    
    def analyze_house_compatibility(self, chart1: Dict, chart2: Dict) -> Dict[str, Any]:
        """Analyze house compatibility for marriage"""
        
        # Key houses for marriage compatibility
        marriage_houses = {
            '7th_house': 7,  # Spouse
            '2nd_house': 2,  # Family
            '4th_house': 4,  # Home
            '5th_house': 5,  # Children
            '9th_house': 9   # Fortune
        }
        
        compatibility_scores = {}
        total_score = 0
        
        for house_name, house_num in marriage_houses.items():
            house1 = chart1['houses'][house_num]
            house2 = chart2['houses'][house_num]
            
            score = self.calculate_house_compatibility(house1, house2)
            compatibility_scores[house_name] = score
            total_score += score
        
        avg_score = total_score / len(compatibility_scores) if compatibility_scores else 0
        
        return {
            'house_scores': compatibility_scores,
            'average_score': round(avg_score, 2),
            'description': self.get_house_description(avg_score)
        }
    
    def calculate_house_compatibility(self, house1: Dict, house2: Dict) -> int:
        """Calculate compatibility between two houses"""
        
        # Strong houses are compatible
        if house1['strength'] > 5 and house2['strength'] > 5:
            return 100
        elif house1['strength'] > 3 and house2['strength'] > 3:
            return 75
        else:
            return 50
    
    def get_house_description(self, score: float) -> str:
        """Get description for house compatibility"""
        if score >= 80:
            return "Excellent House Compatibility"
        elif score >= 60:
            return "Good House Compatibility"
        else:
            return "Moderate House Compatibility"
    
    def calculate_overall_score(self, compatibility: Dict) -> int:
        """Calculate overall compatibility score"""
        
        scores = [
            compatibility['mangal_dosha']['compatibility_score'],
            compatibility['nakshatra_compatibility']['compatibility_score'],
            compatibility['planetary_compatibility']['average_score'],
            compatibility['house_compatibility']['average_score']
        ]
        
        return round(sum(scores) / len(scores))

print("✅ Compatibility Analyzer loaded!")

# Example usage
if __name__ == "__main__":
    analyzer = CompatibilityAnalyzer()
    
    person1 = {
        "date": "1977-10-29",
        "time": "21:30",
        "latitude": 13.08333333,
        "longitude": 80.28333333,
        "timezone": 5.5
    }
    
    person2 = {
        "date": "1980-05-15",
        "time": "14:30",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "timezone": 5.5
    }
    
    compatibility = analyzer.analyze_compatibility(person1, person2)
    
    print("Compatibility Analysis:")
    print(f"Overall Score: {compatibility['compatibility']['overall_score']}%")
    print(f"Mangal Dosha: {compatibility['compatibility']['mangal_dosha']['description']}")
    print(f"Nakshatra: {compatibility['compatibility']['nakshatra_compatibility']['description']}")
    print(f"Planetary: {compatibility['compatibility']['planetary_compatibility']['description']}")
    print(f"House: {compatibility['compatibility']['house_compatibility']['description']}") 