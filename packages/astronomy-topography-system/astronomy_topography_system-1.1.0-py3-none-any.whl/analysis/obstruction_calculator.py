"""
Obstruction Calculator Module
============================

Calculates telescope obstruction angles based on surrounding topography.
"""

import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from ..model_context_protocol import ModelContextProtocol

@dataclass
class ObstructionData:
    """Represents obstruction data for a direction."""
    direction_degrees: float
    obstruction_angle: float
    distance_to_obstruction: float
    obstruction_elevation: float

@dataclass
class ObstructionAnalysis:
    """Results of obstruction analysis."""
    directions: List[ObstructionData]
    avg_obstruction_angle: float
    max_obstruction_angle: float
    clear_directions: int
    total_directions: int
    clear_percentage: float

class ObstructionCalculator(ModelContextProtocol):
    """
    Calculates telescope obstruction angles based on surrounding topography.
    
    Analyzes the horizon in all directions to determine optimal
    telescope orientation and viewing conditions.
    """
    
    def __init__(self):
        self._context = {}
        self._configuration = {}
        self.num_directions = 36  # Analyze every 10 degrees
        self.min_clear_angle = 5.0  # Minimum angle above horizon for clear viewing
        self.observer_height = 2.0  # Default observer height in meters
        self.telescope_height = 1.5  # Default telescope height in meters
    
    def set_context(self, context):
        self._context = context

    def get_context(self):
        return self._context

    def configure(self, **kwargs):
        self._configuration.update(kwargs)

    def get_configuration(self):
        return self._configuration

    def run(self, center_lat, center_lon, elevation_points, observer_height=2.0, telescope_height=1.5):
        # For this calculator, run() will call calculate_obstructions
        return self.calculate_obstructions(center_lat, center_lon, elevation_points, observer_height, telescope_height)

    def reset(self):
        self._context = {}
        self._configuration = {}

    def close(self):
        # No resources to clean up in this implementation
        pass

    def calculate_obstructions(self, 
                             center_lat: float, 
                             center_lon: float, 
                             elevation_points: List,
                             observer_height: float = 2.0,
                             telescope_height: float = 1.5) -> Optional[ObstructionAnalysis]:
        """
        Calculate obstruction angles in all directions.
        
        Args:
            center_lat: Observer latitude
            center_lon: Observer longitude
            elevation_points: List of elevation points
            observer_height: Height of observer above ground (meters)
            telescope_height: Height of telescope above ground (meters)
            
        Returns:
            ObstructionAnalysis object, or None if calculation failed
        """
        if not elevation_points:
            return None
        
        try:
            self.observer_height = observer_height
            self.telescope_height = telescope_height
            
            # Calculate obstructions in all directions
            obstructions = []
            for i in range(self.num_directions):
                direction_degrees = i * (360.0 / self.num_directions)
                obstruction_data = self._calculate_direction_obstruction(
                    center_lat, center_lon, direction_degrees, elevation_points
                )
                if obstruction_data:
                    obstructions.append(obstruction_data)
            
            if not obstructions:
                return None
            
            # Calculate statistics
            obstruction_angles = [obs.obstruction_angle for obs in obstructions]
            avg_obstruction = sum(obstruction_angles) / len(obstruction_angles)
            max_obstruction = max(obstruction_angles)
            
            # Count clear directions
            clear_directions = sum(1 for angle in obstruction_angles if angle <= self.min_clear_angle)
            total_directions = len(obstruction_angles)
            clear_percentage = (clear_directions / total_directions) * 100
            
            return ObstructionAnalysis(
                directions=obstructions,
                avg_obstruction_angle=avg_obstruction,
                max_obstruction_angle=max_obstruction,
                clear_directions=clear_directions,
                total_directions=total_directions,
                clear_percentage=clear_percentage
            )
            
        except Exception as e:
            print(f"Error calculating obstructions: {e}")
            return None
    
    def _calculate_direction_obstruction(self, 
                                       center_lat: float, 
                                       center_lon: float, 
                                       direction_degrees: float,
                                       elevation_points: List) -> Optional[ObstructionData]:
        """Calculate obstruction for a specific direction."""
        try:
            # Calculate points along the direction line
            max_distance = 50.0  # kilometers
            step_distance = 1.0  # kilometers
            
            max_obstruction_angle = 0.0
            distance_to_obstruction = 0.0
            obstruction_elevation = 0.0
            
            for distance in range(1, int(max_distance / step_distance) + 1):
                distance_km = distance * step_distance
                
                # Calculate point at this distance
                point_lat, point_lon = self._calculate_point_at_distance(
                    center_lat, center_lon, direction_degrees, distance_km
                )
                
                # Find elevation at this point
                elevation = self._get_elevation_at_point(point_lat, point_lon, elevation_points)
                
                if elevation is not None:
                    # Calculate obstruction angle
                    obstruction_angle = self._calculate_obstruction_angle(
                        distance_km, elevation, center_lat, center_lon, elevation_points
                    )
                    
                    if obstruction_angle > max_obstruction_angle:
                        max_obstruction_angle = obstruction_angle
                        distance_to_obstruction = distance_km
                        obstruction_elevation = elevation
            
            return ObstructionData(
                direction_degrees=direction_degrees,
                obstruction_angle=max_obstruction_angle,
                distance_to_obstruction=distance_to_obstruction,
                obstruction_elevation=obstruction_elevation
            )
            
        except Exception as e:
            print(f"Error calculating direction obstruction: {e}")
            return None
    
    def _calculate_point_at_distance(self, 
                                   center_lat: float, 
                                   center_lon: float, 
                                   direction_degrees: float, 
                                   distance_km: float) -> Tuple[float, float]:
        """Calculate coordinates of a point at given distance and direction."""
        R = 6371  # Earth's radius in kilometers
        
        # Convert direction to radians
        direction_rad = math.radians(direction_degrees)
        
        # Convert distance to angular distance
        angular_distance = distance_km / R
        
        # Convert center coordinates to radians
        center_lat_rad = math.radians(center_lat)
        center_lon_rad = math.radians(center_lon)
        
        # Calculate new coordinates
        new_lat_rad = math.asin(
            math.sin(center_lat_rad) * math.cos(angular_distance) +
            math.cos(center_lat_rad) * math.sin(angular_distance) * math.cos(direction_rad)
        )
        
        new_lon_rad = center_lon_rad + math.atan2(
            math.sin(direction_rad) * math.sin(angular_distance) * math.cos(center_lat_rad),
            math.cos(angular_distance) - math.sin(center_lat_rad) * math.sin(new_lat_rad)
        )
        
        return math.degrees(new_lat_rad), math.degrees(new_lon_rad)
    
    def _get_elevation_at_point(self, lat: float, lon: float, elevation_points: List) -> Optional[float]:
        """Get elevation at a specific point using nearest neighbor."""
        if not elevation_points:
            return None
        
        # Find nearest point
        min_distance = float('inf')
        nearest_elevation = None
        
        for point in elevation_points:
            distance = self._calculate_distance(lat, lon, point.latitude, point.longitude)
            if distance < min_distance:
                min_distance = distance
                nearest_elevation = point.elevation
        
        return nearest_elevation
    
    def _calculate_obstruction_angle(self, 
                                   distance_km: float, 
                                   elevation: float,
                                   center_lat: float, 
                                   center_lon: float, 
                                   elevation_points: List) -> float:
        """Calculate obstruction angle from observer to a point."""
        # Get observer elevation
        observer_elevation = self._get_elevation_at_point(center_lat, center_lon, elevation_points)
        if observer_elevation is None:
            observer_elevation = 0.0
        
        # Calculate height difference
        height_diff = elevation - observer_elevation - self.observer_height
        
        # Calculate angle using trigonometry
        if distance_km > 0:
            angle_rad = math.atan2(height_diff, distance_km * 1000)  # Convert km to meters
            return math.degrees(angle_rad)
        else:
            return 0.0
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
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
    
    def find_optimal_orientation(self, analysis: ObstructionAnalysis) -> Dict:
        """Find the optimal telescope orientation."""
        if not analysis or not analysis.directions:
            return {
                'optimal_direction': None,
                'compass_direction': 'Unknown',
                'obstruction_angle': 0.0,
                'quality': 'No data available'
            }
        
        # Find direction with minimum obstruction
        best_direction = min(analysis.directions, key=lambda d: d.obstruction_angle)
        
        # Determine compass direction
        compass_direction = self._degrees_to_compass(best_direction.direction_degrees)
        
        # Determine quality based on obstruction angle
        quality = self._get_quality_description(best_direction.obstruction_angle)
        
        return {
            'optimal_direction': best_direction.direction_degrees,
            'compass_direction': compass_direction,
            'obstruction_angle': best_direction.obstruction_angle,
            'quality': quality
        }
    
    def _degrees_to_compass(self, degrees: float) -> str:
        """Convert degrees to compass direction."""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        
        # Normalize degrees to 0-360
        degrees = degrees % 360
        
        # Convert to 16-point compass
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def _get_quality_description(self, obstruction_angle: float) -> str:
        """Get quality description based on obstruction angle."""
        if obstruction_angle <= 5.0:
            return "Excellent - Clear horizon"
        elif obstruction_angle <= 10.0:
            return "Good - Minimal obstruction"
        elif obstruction_angle <= 20.0:
            return "Fair - Moderate obstruction"
        elif obstruction_angle <= 30.0:
            return "Poor - Significant obstruction"
        else:
            return "Very Poor - Heavy obstruction"
    
    def get_obstruction_report(self, analysis: ObstructionAnalysis) -> Dict:
        """Generate a comprehensive obstruction report."""
        if not analysis:
            return {}
        
        optimal = self.find_optimal_orientation(analysis)
        
        return {
            'analysis': {
                'avg_obstruction_angle': analysis.avg_obstruction_angle,
                'max_obstruction_angle': analysis.max_obstruction_angle,
                'min_obstruction_angle': min(d.obstruction_angle for d in analysis.directions)
            },
            'report': {
                'clear_directions': analysis.clear_directions,
                'total_directions': analysis.total_directions,
                'clear_percentage': analysis.clear_percentage,
                'obstructed_percentage': 100 - analysis.clear_percentage
            },
            'optimal_orientation': optimal
        } 