from nav_vision import Direction, MoveAction, MoveType, Navigation, ShipPose
import ship_data as sd

# print(Navigation.turn_circle(ShipPose(0,0,0), -90, 1112, Direction.NONE))
# print(Navigation.get_endpoint(ShipPose(0,0,180), 180,  -111000))
# test_pose=Navigation.course_speed_linear(ShipPose(0,0,0), 270, 1, 1112, actiontime_min=1)
# print(test_pose)
# print(Navigation.to_waypoint(ShipPose(75,0,0), ShipPose(74.98, -.03,90), 10, 400, turntime_min=12))
print(Navigation.midpoint(ShipPose(0,0,0), ShipPose(0, 1, 0)))