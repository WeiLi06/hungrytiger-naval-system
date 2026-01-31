from nav_vision import Direction, Navigation
from ship_data import ShipPose


print("balls")
print(Navigation.turn_circle(Navigation, ShipPose(0,0,0), 45, 1112, Direction.NONE))
print(Navigation.get_endpoint(Navigation, ShipPose(0,0,180), 180,  -111000))
print("ennd")