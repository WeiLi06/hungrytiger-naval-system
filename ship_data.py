from dataclasses import dataclass
from nav_vision import ShipPose, MoveAction, MoveType, Navigation
import pandas as pd

    


class Warship:
    turn_start_pose: ShipPose
    turn_end_pose: ShipPose
    name: str
    speed: float #m/s
    turn_radius: float #meters
    is_commanded: bool
    
    def __init__(self, start_pose:ShipPose, name:str, commanded:bool=False, turn_radius:float=400):
        self.turn_start_pose=start_pose
        self.name=name
        self.turn_radius=turn_radius
        self.is_commanded=commanded
        self.navigator=Navigator(self)
        pass

class Fleet: 
    ships: list[Warship]
    name: str
    def __init__(self, name:str):
        self.name=name
        self.ships=[]
        pass
    def add_ship(self, ship:Warship):
        self.ships.append(ship)
        pass
    
    

class Navigator:
        ship: Warship
        turntime_total_min=6
        moves: list[MoveAction]=[]
        turntime_remaining_min=turntime_total_min
        intermediate_poses: list[ShipPose]=[]
        def __init__(self, outer:Warship):
            self.ship=outer
            pass
        def give_moves(self, moves: list[MoveAction]):
            self.moves=moves
            pass
        
        def move(self):
            start_pose=self.ship.turn_start_pose
            current_pose=start_pose
            for action in self.moves:
                if self.turntime_remaining_min<=action.duration_min:
                    action.duration_min=self.turntime_remaining_min
                match action.type:
                    case MoveType.COURSE_SPEED:
                        current_pose=Navigation.course_speed_linear(current_pose, action.course, 
                                                                    action.speed, self.ship.turn_radius, actiontime_min=action.duration_min)[0]
                        self.turntime_remaining_min-=action.duration_min
                    case MoveType.TO_WAYPOINT:
                        nav_list=Navigation.to_waypoint(current_pose, action.waypoint, action.speed, self.ship.turn_radius, turntime_min=action.duration_min)
                        current_pose=nav_list[0]
                        self.turntime_remaining_min-=nav_list[4]
                self.intermediate_poses.append(current_pose)
            self.ship.turn_end_pose=current_pose
            


class FleetMaker:
    @staticmethod
    def csv_to_fleets(num_fleets:int, file_path:str)->list[Fleet]:
        df=pd.read_csv(file_path, index_col=1)
        pass