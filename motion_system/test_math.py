import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from motion_math import get_cardinal_angle

print(f"North_East: {get_cardinal_angle('North_East')}")
print(f"north_east: {get_cardinal_angle('north_east')}")
print(f"direction='North_East'.lower(): {'North_East'.lower()}")
