from dataclasses import dataclass
from nav_vision import ShipPose, MoveAction, MoveType, Navigation

    


class Warship:
    turn_start_pose: ShipPose
    turn_end_pose: ShipPose
    name: str
    speed: float #m/s
    navigator: Navigator
    turn_radius: float #meters
    
    
    def __init__(self, start_pose:ShipPose, name:str):
        self.turn_start_pose=start_pose
        self.name=name
        self.navigator=Navigator(self)
        pass
    

class Navigator:
        ship: Warship
        
        def __init__(self, outer:Warship):
            self.ship=outer
            pass
        
        def move_chain(self, moves: list[MoveAction]):
            start_pose=self.ship.turn_start_pose
            current_pose=start_pose
            for action in moves:
                match action.type:
                    case MoveType.COURSE_SPEED:
                        current_pose=Navigation.course_speed_linear(current_pose, action.course, 
                                                                    action.speed, self.ship.turn_radius, actiontime_min=action.duration_min)
                    case MoveType.TO_WAYPOINT:
                        current_pose=Navigation.to_waypoint(current_pose, action.waypoint, action.speed, self.ship.turn_radius, turntime_min=action.turntime_min)
            self.ship.turn_end_pose=current_pose
            
            