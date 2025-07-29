"""
Astronomy AI
============

A comprehensive system for analyzing topography and elevation data
for astronomy enthusiasts and telescope operations.
"""

__version__ = "1.0.0"
__author__ = "Astronomy AI Team"
__email__ = "contact@astronomy-ai.com"

# Import main components for easy access
try:
    from .topography.topography_system import TopographySystem
    from .utils.location_parser import LocationParser
    from .elevation.elevation_api import ElevationAPI
    from .analysis.contour_analyzer import ContourAnalyzer
    from .analysis.obstruction_calculator import ObstructionCalculator
    from .mcp_server import start_mcp_server
    from .model_context_protocol import ModelContextProtocol
except ImportError:
    # Handle import errors gracefully
    pass

__all__ = [
    'TopographySystem',
    'LocationParser', 
    'ElevationAPI',
    'ContourAnalyzer',
    'ObstructionCalculator',
    'start_mcp_server',
    'ModelContextProtocol',
] 