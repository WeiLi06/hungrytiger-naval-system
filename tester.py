from nav_vision import Direction, Navigation, ShipPose
from ship_data import Warship, Test


print("balls")
print(Navigation.turn_circle(ShipPose(0,0,0), -90, 1112, Direction.NONE))
print(Navigation.get_endpoint(ShipPose(0,0,180), 180,  -111000))
test_pose=Navigation.course_speed_linear(ShipPose(0,0,0), 270, 1, 1112, actiontime_min=1)
print(test_pose)
print(Navigation.to_waypoint(ShipPose(0,0,0), ShipPose(0,0.05,90), 10, 1112, turntime_min=6))
print("ennd")