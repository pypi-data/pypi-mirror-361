#!/usr/bin/env python3
"""
Simple Demo - Astronomy AI Topography System
===========================================

A minimal demo showing basic functionality.
"""

import json
import math
from typing import Dict

def simple_elevation_estimate(latitude: float, longitude: float) -> float:
    """Simple elevation estimation based on coordinates."""
    # Basic elevation estimation
    base_elevation = 100 + (abs(latitude) * 10) + (abs(longitude) * 2)
    return base_elevation

def simple_location_parse(location_input: str) -> Dict:
    """Simple location parsing."""
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
    
    # For text input, use simple mapping
    location_map = {
        'denver': {'lat': 39.7392, 'lon': -104.9903, 'name': 'Denver, Colorado'},
        'flagstaff': {'lat': 35.1995, 'lon': -111.6513, 'name': 'Flagstaff, Arizona'},
        'los angeles': {'lat': 34.0522, 'lon': -118.2437, 'name': 'Los Angeles, California'},
        'new york': {'lat': 40.7589, 'lon': -73.9851, 'name': 'New York City'},
        'mount wilson': {'lat': 34.2244, 'lon': -118.0572, 'name': 'Mount Wilson Observatory'}
    }
    
    input_lower = location_input.lower()
    for key, data in location_map.items():
        if key in input_lower:
            return {
                'latitude': data['lat'],
                'longitude': data['lon'],
                'formatted_address': data['name']
            }
    
    # Default to a central location
    return {
        'latitude': 39.8283,
        'longitude': -98.5795,
        'formatted_address': 'Central United States'
    }

def analyze_location_simple(location_input: str) -> Dict:
    """Simple location analysis."""
    print(f"🔍 Analyzing: {location_input}")
    
    # Parse location
    location_data = simple_location_parse(location_input)
    lat = location_data['latitude']
    lon = location_data['longitude']
    
    print(f"📍 Coordinates: {lat:.6f}, {lon:.6f}")
    
    # Get elevation
    elevation = simple_elevation_estimate(lat, lon)
    print(f"🏔️  Elevation: {elevation:.0f}m")
    
    # Generate analysis
    analysis = generate_simple_analysis(location_data, elevation)
    
    return analysis

def generate_simple_analysis(location_data: Dict, elevation: float) -> Dict:
    """Generate simple analysis."""
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

def print_simple_results(results: Dict):
    """Print results in a simple format."""
    print("\n" + "="*50)
    print("ASTRONOMY AI - SIMPLE ANALYSIS RESULTS")
    print("="*50)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Location Information
    location = results['location']
    print(f"\n📍 Location: {location['details']['formatted_address']}")
    print(f"   Coordinates: {location['coordinates'][0]:.6f}, {location['coordinates'][1]:.6f}")
    
    # Elevation Information
    elevation = results['elevation']
    print(f"\n🏔️  Elevation: {elevation['user_elevation']:.0f}m")
    
    # Obstruction Analysis
    obstructions = results['obstructions']
    analysis = obstructions['analysis']
    report = obstructions['report']
    
    print(f"\n🔭 Telescope Analysis:")
    print(f"   Average obstruction: {analysis['avg_obstruction_angle']:.1f}°")
    print(f"   Clear viewing: {report['clear_percentage']:.1f}%")
    
    # Optimal Orientation
    optimal = obstructions['optimal_orientation']
    print(f"\n🎯 Best Direction: {optimal['compass_direction']}")
    print(f"   Quality: {optimal['quality']}")
    
    # Recommendations
    recommendations = results['recommendations']
    print(f"\n💡 Quality: {recommendations['location_quality']}")
    print(f"   Orientation: {recommendations['telescope_orientation']}")
    
    if recommendations['suggestions']:
        print(f"\n💡 Suggestion: {recommendations['suggestions'][0]}")
    
    print("\n" + "="*50)

def main():
    """Main simple demo function."""
    print("🌌 Astronomy AI - Simple Topography Demo")
    print("="*40)
    
    # Example locations
    example_locations = [
        "Denver",
        "Flagstaff", 
        "Los Angeles",
        "New York",
        "Mount Wilson"
    ]
    
    print("\nExample locations you can analyze:")
    for i, location in enumerate(example_locations, 1):
        print(f"   {i}. {location}")
    
    print("\nOr enter your own location:")
    
    while True:
        try:
            user_input = input("\nEnter location (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 🌟")
                break
            
            if not user_input:
                print("Please enter a location.")
                continue
            
            # Perform analysis
            results = analyze_location_simple(user_input)
            
            # Print results
            print_simple_results(results)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 🌟")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with a different location.")

if __name__ == "__main__":
    main() 