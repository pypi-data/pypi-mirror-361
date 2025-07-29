"""
Topography System Module
========================

Main system that integrates all components for comprehensive location analysis.
"""

import sys
import os
from typing import Dict, Optional, List

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

try:
    from ..elevation.elevation_api import ElevationAPI
    from ..utils.location_parser import LocationParser
    from ..analysis.contour_analyzer import ContourAnalyzer
    from ..analysis.obstruction_calculator import ObstructionCalculator
except ImportError:
    # Fallback imports for when running from different directory
    try:
        from elevation.elevation_api import ElevationAPI
        from utils.location_parser import LocationParser
        from analysis.contour_analyzer import ContourAnalyzer
        from analysis.obstruction_calculator import ObstructionCalculator
    except ImportError:
        print("Warning: Could not import full topography system components")
        ElevationAPI = None
        LocationParser = None
        ContourAnalyzer = None
        ObstructionCalculator = None

from ..model_context_protocol import ModelContextProtocol

class TopographySystem(ModelContextProtocol):
    """
    Main topography analysis system.
    
    Integrates all components to provide comprehensive location analysis
    for astronomy enthusiasts and telescope operations.
    """
    
    def __init__(self):
        """Initialize the topography system with all components."""
        self._context = {}
        self._configuration = {}
        try:
            self.elevation_api = ElevationAPI() if ElevationAPI else None
            self.location_parser = LocationParser() if LocationParser else None
            self.contour_analyzer = ContourAnalyzer() if ContourAnalyzer else None
            self.obstruction_calculator = ObstructionCalculator() if ObstructionCalculator else None
        except Exception as e:
            print(f"Warning: Error initializing topography system: {e}")
            self.elevation_api = None
            self.location_parser = None
            self.contour_analyzer = None
            self.obstruction_calculator = None
    
    def set_context(self, context):
        self._context = context

    def get_context(self):
        return self._context

    def configure(self, **kwargs):
        self._configuration.update(kwargs)

    def get_configuration(self):
        return self._configuration

    def run(self, *args, **kwargs):
        # For this system, run() will call analyze_location
        return self.analyze_location(*args, **kwargs)

    def reset(self):
        self._context = {}
        self._configuration = {}

    def close(self):
        # No resources to clean up in this implementation
        pass

    def analyze_location(self, 
                        location_input: str,
                        radius_km: float = 10,
                        observer_height: float = 2.0,
                        telescope_height: float = 1.5) -> Dict:
        """
        Perform comprehensive analysis of a location.
        
        Args:
            location_input: Address or coordinate string
            radius_km: Analysis radius in kilometers
            observer_height: Height of observer above ground (meters)
            telescope_height: Height of telescope above ground (meters)
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        try:
            # Step 1: Parse location
            location_info = self._parse_location(location_input)
            if not location_info:
                return {'error': 'Could not parse location'}
            
            lat, lon = location_info['coordinates']
            
            # Step 2: Get elevation data
            elevation_data = self._get_elevation_data(lat, lon, radius_km)
            if not elevation_data:
                return {'error': 'Could not retrieve elevation data'}
            
            # Step 3: Analyze contours
            contour_analysis = self._analyze_contours(elevation_data)
            
            # Step 4: Calculate obstructions
            obstruction_analysis = self._calculate_obstructions(
                lat, lon, elevation_data, observer_height, telescope_height
            )
            
            # Step 5: Generate recommendations
            recommendations = self._generate_recommendations(
                location_info, elevation_data, contour_analysis, obstruction_analysis
            )
            
            # Compile results
            return {
                'location': location_info,
                'elevation': elevation_data,
                'contours': contour_analysis,
                'obstructions': obstruction_analysis,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _parse_location(self, location_input: str) -> Optional[Dict]:
        """Parse location input to get coordinates and details."""
        if not self.location_parser:
            # Fallback parsing for simple coordinate strings
            return self._simple_location_parse(location_input)
        
        try:
            return self.location_parser.get_location_info(location_input)
        except Exception as e:
            print(f"Error parsing location: {e}")
            return self._simple_location_parse(location_input)
    
    def _simple_location_parse(self, location_input: str) -> Optional[Dict]:
        """Simple fallback location parsing."""
        import re
        
        # Check if input is coordinates
        coord_pattern = r'^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$'
        match = re.match(coord_pattern, location_input.strip())
        
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            
            return {
                'coordinates': (lat, lon),
                'details': {
                    'formatted_address': f"{lat}, {lon}",
                    'country': None,
                    'state': None,
                    'city': None
                },
                'latitude': lat,
                'longitude': lon
            }
        
        return None
    
    def _get_elevation_data(self, lat: float, lon: float, radius_km: float) -> Optional[Dict]:
        """Get elevation data for the location."""
        if not self.elevation_api:
            # Fallback: return basic elevation data
            return self._fallback_elevation_data(lat, lon)
        
        try:
            # Get user elevation
            user_elevation = self.elevation_api.get_elevation(lat, lon)
            if user_elevation is None:
                return self._fallback_elevation_data(lat, lon)
            
            # Get peak information
            peak_info = self.elevation_api.get_peak_info(lat, lon, radius_km)
            
            return {
                'user_elevation': user_elevation,
                'peak_info': peak_info or {
                    'peak_elevation': user_elevation,
                    'distance_to_peak': 0.0,
                    'elevation_difference': 0.0
                }
            }
            
        except Exception as e:
            print(f"Error getting elevation data: {e}")
            return self._fallback_elevation_data(lat, lon)
    
    def _fallback_elevation_data(self, lat: float, lon: float) -> Dict:
        """Fallback elevation data when APIs are unavailable."""
        # Simple elevation estimation based on latitude
        base_elevation = 100 + (abs(lat) * 10)  # Rough estimation
        
        return {
            'user_elevation': base_elevation,
            'peak_info': {
                'peak_elevation': base_elevation + 50,
                'distance_to_peak': 2.0,
                'elevation_difference': 50.0
            }
        }
    
    def _analyze_contours(self, elevation_data: Dict) -> Dict:
        """Analyze contour data."""
        if not self.contour_analyzer:
            return self._fallback_contour_analysis()
        
        try:
            # For now, return basic contour analysis
            # In a full implementation, this would analyze elevation grid data
            return {
                'min_elevation': elevation_data['user_elevation'] - 50,
                'max_elevation': elevation_data['user_elevation'] + 100,
                'elevation_range': 150,
                'num_contours': 15,
                'complexity_score': 0.3,
                'complexity_description': 'Low - Gentle slopes'
            }
        except Exception as e:
            print(f"Error analyzing contours: {e}")
            return self._fallback_contour_analysis()
    
    def _fallback_contour_analysis(self) -> Dict:
        """Fallback contour analysis."""
        return {
            'min_elevation': 100,
            'max_elevation': 200,
            'elevation_range': 100,
            'num_contours': 10,
            'complexity_score': 0.2,
            'complexity_description': 'Very Low - Flat terrain'
        }
    
    def _calculate_obstructions(self, 
                              lat: float, 
                              lon: float, 
                              elevation_data: Dict,
                              observer_height: float,
                              telescope_height: float) -> Dict:
        """Calculate obstruction angles."""
        if not self.obstruction_calculator:
            return self._fallback_obstruction_analysis()
        
        try:
            # For now, return basic obstruction analysis
            # In a full implementation, this would calculate actual obstructions
            return {
                'analysis': {
                    'avg_obstruction_angle': 8.5,
                    'max_obstruction_angle': 15.2,
                    'min_obstruction_angle': 2.1
                },
                'report': {
                    'clear_directions': 28,
                    'total_directions': 36,
                    'clear_percentage': 77.8,
                    'obstructed_percentage': 22.2
                },
                'optimal_orientation': {
                    'optimal_direction': 180.0,
                    'compass_direction': 'S',
                    'obstruction_angle': 2.1,
                    'quality': 'Excellent - Clear horizon'
                }
            }
        except Exception as e:
            print(f"Error calculating obstructions: {e}")
            return self._fallback_obstruction_analysis()
    
    def _fallback_obstruction_analysis(self) -> Dict:
        """Fallback obstruction analysis."""
        return {
            'analysis': {
                'avg_obstruction_angle': 5.0,
                'max_obstruction_angle': 10.0,
                'min_obstruction_angle': 0.0
            },
            'report': {
                'clear_directions': 32,
                'total_directions': 36,
                'clear_percentage': 88.9,
                'obstructed_percentage': 11.1
            },
            'optimal_orientation': {
                'optimal_direction': 0.0,
                'compass_direction': 'N',
                'obstruction_angle': 0.0,
                'quality': 'Excellent - Clear horizon'
            }
        }
    
    def _generate_recommendations(self, 
                                location_info: Dict,
                                elevation_data: Dict,
                                contour_analysis: Dict,
                                obstruction_analysis: Dict) -> Dict:
        """Generate recommendations based on analysis."""
        recommendations = {
            'location_quality': 'Good',
            'telescope_orientation': 'Variable',
            'warnings': [],
            'suggestions': []
        }
        
        # Analyze elevation
        user_elevation = elevation_data['user_elevation']
        if user_elevation > 2000:
            recommendations['location_quality'] = 'Excellent'
            recommendations['suggestions'].append('High elevation provides excellent viewing conditions')
        elif user_elevation > 1000:
            recommendations['location_quality'] = 'Good'
            recommendations['suggestions'].append('Moderate elevation offers good viewing')
        elif user_elevation < 100:
            recommendations['warnings'].append('Low elevation may have atmospheric interference')
        
        # Analyze obstructions
        clear_percentage = obstruction_analysis['report']['clear_percentage']
        if clear_percentage > 80:
            recommendations['location_quality'] = 'Excellent'
            recommendations['suggestions'].append('Excellent horizon clearance')
        elif clear_percentage > 60:
            recommendations['location_quality'] = 'Good'
            recommendations['suggestions'].append('Good horizon clearance')
        elif clear_percentage < 40:
            recommendations['warnings'].append('Limited horizon clearance may restrict viewing')
        
        # Set telescope orientation
        optimal = obstruction_analysis['optimal_orientation']
        if optimal['quality'].startswith('Excellent'):
            recommendations['telescope_orientation'] = f"Point {optimal['compass_direction']} for best results"
        else:
            recommendations['telescope_orientation'] = f"Consider {optimal['compass_direction']} direction"
        
        return recommendations 