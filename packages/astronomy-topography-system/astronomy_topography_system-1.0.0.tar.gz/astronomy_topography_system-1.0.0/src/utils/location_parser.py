"""
Location Parser Module
=====================

Converts addresses and coordinates to standardized format using Nominatim (OpenStreetMap).
"""

import requests
import re
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

@dataclass
class LocationData:
    """Represents parsed location data."""
    latitude: float
    longitude: float
    formatted_address: str
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None

class LocationParser:
    """
    Location parser using Nominatim (OpenStreetMap) for geocoding.
    
    Converts addresses and coordinates to standardized format.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AstronomyAI-Topography/1.0'
        })
        self.base_url = "https://nominatim.openstreetmap.org"
    
    def parse_location(self, location_input: str) -> Optional[LocationData]:
        """
        Parse location input (address or coordinates) to standardized format.
        
        Args:
            location_input: Address string or coordinate string
            
        Returns:
            LocationData object, or None if parsing failed
        """
        # Check if input is coordinates
        if self._is_coordinate_string(location_input):
            return self._parse_coordinates(location_input)
        else:
            return self._geocode_address(location_input)
    
    def _is_coordinate_string(self, location_input: str) -> bool:
        """Check if input string represents coordinates."""
        # Pattern for coordinate strings like "34.0522, -118.2437" or "34.0522,-118.2437"
        coord_pattern = r'^-?\d+\.?\d*\s*,\s*-?\d+\.?\d*$'
        return bool(re.match(coord_pattern, location_input.strip()))
    
    def _parse_coordinates(self, coord_string: str) -> Optional[LocationData]:
        """Parse coordinate string to LocationData."""
        try:
            # Clean and split the coordinate string
            cleaned = coord_string.strip().replace(' ', '')
            lat_str, lon_str = cleaned.split(',')
            
            latitude = float(lat_str)
            longitude = float(lon_str)
            
            # Validate coordinate ranges
            if not (-90 <= latitude <= 90):
                raise ValueError(f"Invalid latitude: {latitude}")
            if not (-180 <= longitude <= 180):
                raise ValueError(f"Invalid longitude: {longitude}")
            
            # Reverse geocode to get address
            address_data = self._reverse_geocode(latitude, longitude)
            
            return LocationData(
                latitude=latitude,
                longitude=longitude,
                formatted_address=address_data.get('formatted_address', f"{latitude}, {longitude}"),
                country=address_data.get('country'),
                state=address_data.get('state'),
                city=address_data.get('city')
            )
            
        except Exception as e:
            print(f"Error parsing coordinates '{coord_string}': {e}")
            return None
    
    def _geocode_address(self, address: str) -> Optional[LocationData]:
        """Geocode address string to coordinates."""
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            response = self.session.get(f"{self.base_url}/search", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                print(f"No results found for address: {address}")
                return None
            
            result = data[0]
            
            return LocationData(
                latitude=float(result['lat']),
                longitude=float(result['lon']),
                formatted_address=result.get('display_name', address),
                country=self._extract_address_component(result, 'country'),
                state=self._extract_address_component(result, 'state'),
                city=self._extract_address_component(result, 'city')
            )
            
        except Exception as e:
            print(f"Error geocoding address '{address}': {e}")
            return None
    
    def _reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """Reverse geocode coordinates to address."""
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1
            }
            
            response = self.session.get(f"{self.base_url}/reverse", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'address' not in data:
                return {'formatted_address': f"{latitude}, {longitude}"}
            
            address = data['address']
            
            return {
                'formatted_address': data.get('display_name', f"{latitude}, {longitude}"),
                'country': address.get('country'),
                'state': address.get('state'),
                'city': address.get('city') or address.get('town') or address.get('village')
            }
            
        except Exception as e:
            print(f"Error reverse geocoding coordinates {latitude}, {longitude}: {e}")
            return {'formatted_address': f"{latitude}, {longitude}"}
    
    def _extract_address_component(self, result: Dict, component: str) -> Optional[str]:
        """Extract specific address component from geocoding result."""
        if 'address' not in result:
            return None
        
        address = result['address']
        return address.get(component)
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate coordinate ranges."""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def get_location_info(self, location_input: str) -> Optional[Dict]:
        """
        Get comprehensive location information.
        
        Args:
            location_input: Address or coordinate string
            
        Returns:
            Dictionary with location details, or None if failed
        """
        location_data = self.parse_location(location_input)
        
        if not location_data:
            return None
        
        return {
            'coordinates': (location_data.latitude, location_data.longitude),
            'details': {
                'formatted_address': location_data.formatted_address,
                'country': location_data.country,
                'state': location_data.state,
                'city': location_data.city
            },
            'latitude': location_data.latitude,
            'longitude': location_data.longitude
        } 