from nav_vision import Direction, MoveAction, MoveType, Navigation, ShipPose
from ship_data import Warship


print("balls")
# print(Navigation.turn_circle(ShipPose(0,0,0), -90, 1112, Direction.NONE))
# print(Navigation.get_endpoint(ShipPose(0,0,180), 180,  -111000))
# test_pose=Navigation.course_speed_linear(ShipPose(0,0,0), 270, 1, 1112, actiontime_min=1)
# print(test_pose)
# print(Navigation.to_waypoint(ShipPose(75,0,0), ShipPose(74.98, -.03,90), 10, 400, turntime_min=12))
warship=Warship(ShipPose(0,0,0), "TestShip")
warship.navigator.move_chain([MoveAction().course_speed( course=45, speed=10, duration_min=3), 
                              MoveAction().to_waypoint( waypoint=ShipPose(0.1,0.1,0), speed=10, turntime_min=5)])
print(warship.turn_end_pose, warship.navigator.intermediate_poses)
print(Navigation.to_waypoint(Navigation.course_speed_linear(ShipPose(0,0,0), 45, 10, 400, actiontime_min=3)[0], ShipPose(0.1,0.1,0), 10, 400, turntime_min=5))
print("ennd")