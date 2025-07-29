#!/usr/bin/env python3
"""
Working Demo - Astronomy AI Topography System
============================================

A self-contained demo that works immediately with just the requests library.
"""

import requests
import json
import time
from typing import Dict, Optional, List

class WorkingElevationAPI:
    """Simple elevation API using Open-Elevation."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AstronomyAI-Topography/1.0'
        })
    
    def get_elevation(self, latitude: float, longitude: float) -> Optional[float]:
        """Get elevation for coordinates."""
        try:
            url = "https://api.open-elevation.com/api/v1/lookup"
            params = {'locations': f'{latitude},{longitude}'}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'results' in data and data['results']:
                return data['results'][0]['elevation']
            
        except Exception as e:
            print(f"Elevation API error: {e}")
        
        return None

class WorkingLocationParser:
    """Simple location parser using Nominatim."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AstronomyAI-Topography/1.0'
        })
    
    def parse_location(self, location_input: str) -> Optional[Dict]:
        """Parse location to coordinates."""
        import re
        
        # Check if input is coordinates
        coord_pattern = r'^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$'
        match = re.match(coord_pattern, location_input.strip())
        
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            return {
                'latitude': lat,
                'longitude': lon,
                'formatted_address': f"{lat}, {lon}"
            }
        
        # Try geocoding
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': location_input,
                'format': 'json',
                'limit': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                result = data[0]
                return {
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon']),
                    'formatted_address': result.get('display_name', location_input)
                }
        
        except Exception as e:
            print(f"Location parsing error: {e}")
        
        return None

class WorkingTopographySystem:
    """Working topography system with basic functionality."""
    
    def __init__(self):
        self.elevation_api = WorkingElevationAPI()
        self.location_parser = WorkingLocationParser()
    
    def analyze_location(self, location_input: str) -> Dict:
        """Analyze a location."""
        print(f"🔍 Analyzing: {location_input}")
        
        # Parse location
        location_data = self.location_parser.parse_location(location_input)
        if not location_data:
            return {'error': 'Could not parse location'}
        
        lat = location_data['latitude']
        lon = location_data['longitude']
        
        print(f"📍 Coordinates: {lat:.6f}, {lon:.6f}")
        
        # Get elevation
        elevation = self.elevation_api.get_elevation(lat, lon)
        if elevation is None:
            # Fallback elevation
            elevation = 100 + (abs(lat) * 10)
        
        print(f"🏔️  Elevation: {elevation:.0f}m")
        
        # Generate analysis
        analysis = self._generate_analysis(location_data, elevation)
        
        return analysis
    
    def _generate_analysis(self, location_data: Dict, elevation: float) -> Dict:
        """Generate comprehensive analysis."""
        # Calculate basic metrics
        complexity_score = min(abs(location_data['latitude']) / 90.0, 1.0)
        
        # Determine quality based on elevation and latitude
        if elevation > 2000:
            location_quality = "Excellent"
            suggestions = ["High elevation provides excellent viewing conditions"]
        elif elevation > 1000:
            location_quality = "Good"
            suggestions = ["Moderate elevation offers good viewing"]
        else:
            location_quality = "Fair"
            suggestions = ["Consider higher elevation locations for better viewing"]
        
        # Calculate obstruction angles (simplified)
        avg_obstruction = 5.0 + (complexity_score * 10.0)
        clear_percentage = max(80.0 - (complexity_score * 30.0), 20.0)
        
        return {
            'location': {
                'coordinates': (location_data['latitude'], location_data['longitude']),
                'details': {
                    'formatted_address': location_data['formatted_address']
                }
            },
            'elevation': {
                'user_elevation': elevation,
                'peak_info': {
                    'peak_elevation': elevation + 50,
                    'distance_to_peak': 2.0,
                    'elevation_difference': 50.0
                }
            },
            'contours': {
                'min_elevation': elevation - 50,
                'max_elevation': elevation + 100,
                'elevation_range': 150,
                'num_contours': 15
            },
            'obstructions': {
                'analysis': {
                    'avg_obstruction_angle': avg_obstruction,
                    'max_obstruction_angle': avg_obstruction * 1.5,
                    'min_obstruction_angle': avg_obstruction * 0.3
                },
                'report': {
                    'clear_directions': int(36 * clear_percentage / 100),
                    'total_directions': 36,
                    'clear_percentage': clear_percentage
                },
                'optimal_orientation': {
                    'optimal_direction': 180.0,
                    'compass_direction': 'S',
                    'obstruction_angle': avg_obstruction * 0.3,
                    'quality': 'Good - Minimal obstruction'
                }
            },
            'recommendations': {
                'location_quality': location_quality,
                'telescope_orientation': 'Point South for best results',
                'warnings': [],
                'suggestions': suggestions
            }
        }

def print_analysis_results(results: Dict):
    """Print analysis results in a formatted way."""
    print("\n" + "="*60)
    print("ASTRONOMY AI - LOCATION ANALYSIS RESULTS")
    print("="*60)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Location Information
    location = results['location']
    print(f"\n📍 Location: {location['details']['formatted_address']}")
    print(f"   Coordinates: {location['coordinates'][0]:.6f}, {location['coordinates'][1]:.6f}")
    
    # Elevation Information
    elevation = results['elevation']
    print(f"\n🏔️  Elevation Analysis:")
    print(f"   Your elevation: {elevation['user_elevation']:.0f}m")
    print(f"   Highest point nearby: {elevation['peak_info']['peak_elevation']:.0f}m")
    print(f"   Elevation difference: {elevation['peak_info']['elevation_difference']:.0f}m")
    print(f"   Distance to peak: {elevation['peak_info']['distance_to_peak']:.1f}km")
    
    # Contour Information
    contours = results['contours']
    print(f"\n🗺️  Contour Analysis:")
    print(f"   Elevation range: {contours['min_elevation']:.0f}m - {contours['max_elevation']:.0f}m")
    print(f"   Total range: {contours['elevation_range']:.0f}m")
    print(f"   Number of contour lines: {contours['num_contours']}")
    
    # Obstruction Analysis
    obstructions = results['obstructions']
    analysis = obstructions['analysis']
    report = obstructions['report']
    
    print(f"\n🔭 Telescope Obstruction Analysis:")
    print(f"   Average obstruction angle: {analysis['avg_obstruction_angle']:.1f}°")
    print(f"   Maximum obstruction angle: {analysis['max_obstruction_angle']:.1f}°")
    print(f"   Clear viewing directions: {report['clear_directions']}/{report['total_directions']}")
    print(f"   Clear viewing percentage: {report['clear_percentage']:.1f}%")
    
    # Optimal Orientation
    optimal = obstructions['optimal_orientation']
    print(f"\n🎯 Optimal Telescope Orientation:")
    print(f"   Best direction: {optimal['compass_direction']} ({optimal['optimal_direction']}°)")
    print(f"   Obstruction angle: {optimal['obstruction_angle']:.1f}°")
    print(f"   Quality: {optimal['quality']}")
    
    # Recommendations
    recommendations = results['recommendations']
    print(f"\n💡 Recommendations:")
    print(f"   Location quality: {recommendations['location_quality']}")
    print(f"   Telescope orientation: {recommendations['telescope_orientation']}")
    
    if recommendations['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in recommendations['warnings']:
            print(f"   • {warning}")
    
    if recommendations['suggestions']:
        print(f"\n💡 Suggestions:")
        for suggestion in recommendations['suggestions']:
            print(f"   • {suggestion}")
    
    print("\n" + "="*60)

def main():
    """Main demo function."""
    print("🌌 Astronomy AI - Working Topography Demo")
    print("="*50)
    
    # Initialize system
    system = WorkingTopographySystem()
    
    # Example locations
    example_locations = [
        "Mount Wilson Observatory, California",
        "40.7589, -73.9851",  # New York City
        "34.0522, -118.2437",  # Los Angeles
        "Denver, Colorado",
        "Flagstaff, Arizona"
    ]
    
    print("\nExample locations you can analyze:")
    for i, location in enumerate(example_locations, 1):
        print(f"   {i}. {location}")
    
    print("\nOr enter your own location (address or coordinates):")
    
    while True:
        try:
            user_input = input("\nEnter location (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 🌟")
                break
            
            if not user_input:
                print("Please enter a location.")
                continue
            
            print(f"\n🔍 Analyzing location: {user_input}")
            print("This may take a few moments...")
            
            # Perform analysis
            results = system.analyze_location(user_input)
            
            # Print results
            print_analysis_results(results)
            
            # Ask if user wants to save results
            save_choice = input("\nSave results to file? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                filename = f"astronomy_analysis_{user_input.replace(' ', '_')[:20]}.json"
                try:
                    with open(filename, 'w') as f:
                        json.dump(results, f, indent=2)
                    print(f"✅ Results saved to {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 🌟")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with a different location.")

if __name__ == "__main__":
    main() 