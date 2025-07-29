"""
Contour Analyzer Module
======================

Analyzes elevation data to generate contour information and topographic analysis.
"""

import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from ..model_context_protocol import ModelContextProtocol

# Built-in statistical functions (no numpy dependency)
def mean(values):
    """Calculate mean of values."""
    return sum(values) / len(values) if values else 0

def median(values):
    """Calculate median of values."""
    if not values:
        return 0
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 0:
        return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
    else:
        return sorted_values[n//2]

def std(values):
    """Calculate standard deviation of values."""
    if not values:
        return 0
    avg = mean(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return variance ** 0.5

@dataclass
class ContourLine:
    """Represents a contour line."""
    elevation: float
    points: List[Tuple[float, float]]
    length: float

@dataclass
class ContourAnalysis:
    """Results of contour analysis."""
    min_elevation: float
    max_elevation: float
    elevation_range: float
    num_contours: int
    contour_lines: List[ContourLine]
    complexity_score: float

class ContourAnalyzer(ModelContextProtocol):
    """
    Analyzes elevation data to generate contour information.
    
    Provides topographic analysis including elevation ranges,
    contour line generation, and complexity scoring.
    """
    
    def __init__(self):
        self._context = {}
        self._configuration = {}
        self.min_contour_interval = 10  # meters
        self.max_contour_interval = 100  # meters
    
    def set_context(self, context):
        self._context = context

    def get_context(self):
        return self._context

    def configure(self, **kwargs):
        self._configuration.update(kwargs)

    def get_configuration(self):
        return self._configuration

    def run(self, elevation_points):
        # For this analyzer, run() will call analyze_elevation_data
        return self.analyze_elevation_data(elevation_points)

    def reset(self):
        self._context = {}
        self._configuration = {}

    def close(self):
        # No resources to clean up in this implementation
        pass
    
    def analyze_elevation_data(self, elevation_points: List) -> Optional[ContourAnalysis]:
        """
        Analyze elevation data to generate contour information.
        
        Args:
            elevation_points: List of elevation points with lat, lon, elevation
            
        Returns:
            ContourAnalysis object, or None if analysis failed
        """
        if not elevation_points:
            return None
        
        try:
            # Extract elevation values
            elevations = [point.elevation for point in elevation_points]
            
            # Basic statistics
            min_elevation = min(elevations)
            max_elevation = max(elevations)
            elevation_range = max_elevation - min_elevation
            
            # Generate contour lines
            contour_lines = self._generate_contour_lines(elevation_points, min_elevation, max_elevation)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(elevations, contour_lines)
            
            return ContourAnalysis(
                min_elevation=min_elevation,
                max_elevation=max_elevation,
                elevation_range=elevation_range,
                num_contours=len(contour_lines),
                contour_lines=contour_lines,
                complexity_score=complexity_score
            )
            
        except Exception as e:
            print(f"Error analyzing elevation data: {e}")
            return None
    
    def _generate_contour_lines(self, elevation_points: List, min_elev: float, max_elev: float) -> List[ContourLine]:
        """Generate contour lines from elevation data."""
        contour_lines = []
        
        # Determine contour interval based on elevation range
        elevation_range = max_elev - min_elev
        if elevation_range <= 50:
            interval = 5
        elif elevation_range <= 200:
            interval = 10
        elif elevation_range <= 500:
            interval = 25
        else:
            interval = 50
        
        # Generate contour elevations
        contour_elevations = []
        current_elev = min_elev + interval
        while current_elev < max_elev:
            contour_elevations.append(current_elev)
            current_elev += interval
        
        # For each contour elevation, find points at that elevation
        for contour_elev in contour_elevations:
            contour_points = self._find_contour_points(elevation_points, contour_elev)
            
            if contour_points:
                # Calculate contour length
                length = self._calculate_contour_length(contour_points)
                
                contour_lines.append(ContourLine(
                    elevation=contour_elev,
                    points=contour_points,
                    length=length
                ))
        
        return contour_lines
    
    def _find_contour_points(self, elevation_points: List, target_elevation: float, tolerance: float = 5.0) -> List[Tuple[float, float]]:
        """Find points that are close to the target elevation."""
        contour_points = []
        
        for point in elevation_points:
            if abs(point.elevation - target_elevation) <= tolerance:
                contour_points.append((point.latitude, point.longitude))
        
        return contour_points
    
    def _calculate_contour_length(self, points: List[Tuple[float, float]]) -> float:
        """Calculate the total length of a contour line."""
        if len(points) < 2:
            return 0.0
        
        total_length = 0.0
        
        for i in range(len(points) - 1):
            lat1, lon1 = points[i]
            lat2, lon2 = points[i + 1]
            
            # Calculate distance between points
            distance = self._calculate_distance(lat1, lon1, lat2, lon2)
            total_length += distance
        
        return total_length
    
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
    
    def _calculate_complexity_score(self, elevations: List[float], contour_lines: List[ContourLine]) -> float:
        """Calculate topographic complexity score."""
        if not elevations:
            return 0.0
        
        # Calculate standard deviation of elevations
        elevation_std = std(elevations) if len(elevations) > 1 else 0.0
        
        # Calculate contour density
        contour_density = len(contour_lines) / max(1, len(elevations))
        
        # Calculate average contour length
        avg_contour_length = mean([line.length for line in contour_lines]) if contour_lines else 0.0
        
        # Normalize factors
        elevation_factor = min(elevation_std / 100.0, 1.0)  # Normalize to 0-1
        density_factor = min(contour_density * 10, 1.0)  # Normalize to 0-1
        length_factor = min(avg_contour_length / 10.0, 1.0)  # Normalize to 0-1
        
        # Calculate complexity score (0-1, higher = more complex)
        complexity = (elevation_factor * 0.4 + 
                     density_factor * 0.4 + 
                     length_factor * 0.2)
        
        return min(complexity, 1.0)
    
    def get_contour_summary(self, analysis: ContourAnalysis) -> Dict:
        """Get a summary of contour analysis results."""
        if not analysis:
            return {}
        
        return {
            'min_elevation': analysis.min_elevation,
            'max_elevation': analysis.max_elevation,
            'elevation_range': analysis.elevation_range,
            'num_contours': analysis.num_contours,
            'complexity_score': analysis.complexity_score,
            'complexity_description': self._get_complexity_description(analysis.complexity_score),
            'total_contour_length': sum(line.length for line in analysis.contour_lines),
            'avg_contour_length': mean([line.length for line in analysis.contour_lines]) if analysis.contour_lines else 0.0
        }
    
    def _get_complexity_description(self, complexity_score: float) -> str:
        """Get human-readable description of complexity."""
        if complexity_score < 0.2:
            return "Very Low - Flat terrain"
        elif complexity_score < 0.4:
            return "Low - Gentle slopes"
        elif complexity_score < 0.6:
            return "Medium - Moderate terrain"
        elif complexity_score < 0.8:
            return "High - Rugged terrain"
        else:
            return "Very High - Extremely rugged terrain"
    
    def get_elevation_statistics(self, elevation_points: List) -> Dict:
        """Get basic elevation statistics."""
        if not elevation_points:
            return {}
        
        elevations = [point.elevation for point in elevation_points]
        
        return {
            'count': len(elevations),
            'min': min(elevations),
            'max': max(elevations),
            'mean': mean(elevations),
            'median': median(elevations),
            'std': std(elevations),
            'range': max(elevations) - min(elevations)
        } 