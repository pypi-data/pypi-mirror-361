"""
Elevation API Module
===================

Provides elevation data using multiple free APIs with fallback mechanisms.
"""

import requests
import time
import random
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from ..model_context_protocol import ModelContextProtocol

@dataclass
class ElevationPoint:
    """Represents an elevation data point."""
    latitude: float
    longitude: float
    elevation: float
    source: str

class ElevationAPI(ModelContextProtocol):
    """
    Elevation API with multiple fallback sources.
    
    Uses free APIs in order of preference:
    1. OpenTopography API
    2. Open-Elevation API
    3. USGS Elevation Point Query Service
    """
    
    def __init__(self):
        self._context = {}
        self._configuration = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AstronomyAI-Topography/1.0'
        })
        
        # API endpoints
        self.apis = {
            'opentopography': {
                'url': 'https://portal.opentopography.org/API/globe',
                'params': lambda lat, lon: {
                    'demtype': 'SRTMGL1',
                    'south': lat - 0.01,
                    'north': lat + 0.01,
                    'west': lon - 0.01,
                    'east': lon + 0.01,
                    'outputFormat': 'AAIGrid'
                }
            },
            'open_elevation': {
                'url': 'https://api.open-elevation.com/api/v1/lookup',
                'params': lambda lat, lon: {
                    'locations': f'{lat},{lon}'
                }
            },
            'usgs': {
                'url': 'https://nationalmap.gov/epqs/pqs.php',
                'params': lambda lat, lon: {
                    'x': lon,
                    'y': lat,
                    'units': 'Meters',
                    'output': 'json'
                }
            }
        }
    
    def set_context(self, context):
        self._context = context

    def get_context(self):
        return self._context

    def configure(self, **kwargs):
        self._configuration.update(kwargs)

    def get_configuration(self):
        return self._configuration

    def run(self, latitude, longitude):
        # For this API, run() will call get_elevation
        return self.get_elevation(latitude, longitude)

    def reset(self):
        self._context = {}
        self._configuration = {}

    def close(self):
        # Clean up session if needed
        if hasattr(self, 'session'):
            self.session.close()
    
    def get_elevation(self, latitude: float, longitude: float) -> Optional[float]:
        """
        Get elevation for a single point.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Elevation in meters, or None if all APIs fail
        """
        for api_name, api_config in self.apis.items():
            try:
                elevation = self._query_api(api_name, api_config, latitude, longitude)
                if elevation is not None:
                    return elevation
            except Exception as e:
                print(f"Warning: {api_name} API failed: {e}")
                continue
        
        return None
    
    def get_elevation_grid(self, 
                          center_lat: float, 
                          center_lon: float, 
                          radius_km: float = 10,
                          resolution: int = 50) -> Optional[List[ElevationPoint]]:
        """
        Get elevation data for a grid around a center point.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers
            resolution: Number of points per side (resolution x resolution grid)
            
        Returns:
            List of elevation points, or None if failed
        """
        # Calculate grid bounds
        lat_step = (radius_km / 111.0) / resolution  # Approximate km to degrees
        lon_step = (radius_km / (111.0 * abs(center_lat))) / resolution
        
        points = []
        
        for i in range(resolution):
            for j in range(resolution):
                lat = center_lat + (i - resolution//2) * lat_step
                lon = center_lon + (j - resolution//2) * lon_step
                
                elevation = self.get_elevation(lat, lon)
                if elevation is not None:
                    points.append(ElevationPoint(
                        latitude=lat,
                        longitude=lon,
                        elevation=elevation,
                        source='grid_query'
                    ))
                
                # Rate limiting
                time.sleep(0.1)
        
        return points if points else None
    
    def _query_api(self, api_name: str, api_config: Dict, lat: float, lon: float) -> Optional[float]:
        """Query a specific API for elevation data."""
        try:
            params = api_config['params'](lat, lon)
            response = self.session.get(api_config['url'], params=params, timeout=10)
            response.raise_for_status()
            
            if api_name == 'opentopography':
                return self._parse_opentopography(response.text)
            elif api_name == 'open_elevation':
                return self._parse_open_elevation(response.json())
            elif api_name == 'usgs':
                return self._parse_usgs(response.json())
                
        except Exception as e:
            print(f"Error querying {api_name}: {e}")
            return None
    
    def _parse_opentopography(self, data: str) -> Optional[float]:
        """Parse OpenTopography response."""
        try:
            # OpenTopography returns ASCII grid format
            lines = data.strip().split('\n')
            if len(lines) < 6:
                return None
            
            # Skip header lines and get center value
            header_lines = 6
            if len(lines) > header_lines:
                # Get middle value from the grid
                grid_lines = lines[header_lines:]
                if grid_lines:
                    middle_line = grid_lines[len(grid_lines)//2]
                    values = middle_line.split()
                    if values:
                        middle_value = values[len(values)//2]
                        return float(middle_value)
        except:
            pass
        return None
    
    def _parse_open_elevation(self, data: Dict) -> Optional[float]:
        """Parse Open-Elevation response."""
        try:
            if 'results' in data and data['results']:
                return data['results'][0]['elevation']
        except:
            pass
        return None
    
    def _parse_usgs(self, data: Dict) -> Optional[float]:
        """Parse USGS response."""
        try:
            if 'USGS_Elevation_Point_Query_Service' in data:
                elevation_data = data['USGS_Elevation_Point_Query_Service']
                if 'Elevation_Query' in elevation_data:
                    query_data = elevation_data['Elevation_Query']
                    if 'Elevation' in query_data:
                        return float(query_data['Elevation'])
        except:
            pass
        return None
    
    def get_peak_info(self, center_lat: float, center_lon: float, radius_km: float = 10) -> Optional[Dict]:
        """
        Find the highest point within a radius.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Search radius in kilometers
            
        Returns:
            Dictionary with peak information, or None if failed
        """
        points = self.get_elevation_grid(center_lat, center_lon, radius_km, resolution=20)
        
        if not points:
            return None
        
        # Find highest point
        highest_point = max(points, key=lambda p: p.elevation)
        
        # Calculate distance to peak
        distance_km = self._calculate_distance(
            center_lat, center_lon,
            highest_point.latitude, highest_point.longitude
        )
        
        center_elevation = self.get_elevation(center_lat, center_lon)
        elevation_diff = highest_point.elevation - (center_elevation or 0)
        
        return {
            'peak_latitude': highest_point.latitude,
            'peak_longitude': highest_point.longitude,
            'peak_elevation': highest_point.elevation,
            'distance_to_peak': distance_km,
            'elevation_difference': elevation_diff
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c 