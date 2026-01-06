from enum import Enum

class Direction(Enum):
    """Cardinal and diagonal directions for movement and facing."""
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    NORTH_EAST = "North_East"
    NORTH_WEST = "North_West"
    SOUTH_EAST = "South_East"
    SOUTH_WEST = "South_West"


class Tilt(Enum):
    """Vertical camera orientation presets."""
    UP = "Up"       # Looking upward (negative pitch)
    DOWN = "Down"   # Looking downward (positive pitch)
    LEVEL = "Level" # Horizontal (pitch = 0)


class DistanceUnit(Enum):
    """Distance units with conversion factor to meters."""
    Meters = 1.0
    Centimeters = 0.01
    Kilometers = 1000.0
    Feet = 0.3048


class LightType(Enum):
    POINT = "Point"
    DIRECTIONAL = "Directional"
    SPOT = "Spot"
    RECT = "Rect"
    SKY = "Sky"

class LightColor(Enum):
    # Standard Temps
    WHITE = (1.0, 1.0, 1.0)
    WARM_WHITE = (1.0, 0.9, 0.7)
    COOL_WHITE = (0.7, 0.8, 1.0)
    # Basic Colors
    RED = (1.0, 0.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    # Nature
    SUNLIGHT = (1.0, 0.95, 0.9)
    MOONLIGHT = (0.6, 0.7, 0.9)

class LightUnit(Enum):
    UNITLESS = 0
    LUMENS = 1
    CANDELAS = 2


class TimeUnit(Enum):
    """Time units with conversion factor to seconds."""
    Seconds = 1.0
    Minutes = 60.0
    Hours = 3600.0


class SpeedUnit(Enum):
    """Speed units with conversion factor to meters/second."""
    MetersPerSecond = 1.0
    KilometersPerHour = 0.277778
    MilesPerHour = 0.44704
