from dataclasses import dataclass
from nav_vision import ShipPose, MoveAction, MoveType, Navigation
import pandas as pd
from supplements import TurnInfo


class Warship:
    turn_start_pose: ShipPose
    turn_end_pose: ShipPose=None
    name: str
    speed: float #m/s
    turn_radius: float #meters
    is_commanded: bool
    ship_class: str
    navigator=None
    
    def __init__(self, start_pose:ShipPose, name:str, speed:float, commanded:bool=False, turn_radius:float=400, ship_class:str=""):
        self.turn_start_pose=start_pose
        self.name=name
        self.speed=speed
        self.turn_radius=turn_radius
        self.is_commanded=commanded
        self.ship_class=ship_class.title()
        self.navigator=Navigator(self)
        pass
    def __repr__(self):
        return f"Warship(name={self.name}, speed={self.speed}, class={self.ship_class}, commanded={self.is_commanded}, turn_radius={self.turn_radius}, turn_start_pose={self.turn_start_pose}, turn_end_pose={self.turn_end_pose}, navigator={self.navigator})"


class Fleet: 
    ships: list[Warship]
    name: str
    def __init__(self, name:str):
        self.name=name.upper()
        self.ships=[]
        pass
    def add_ship(self, ship:Warship):
        self.ships.append(ship)
        pass
    def move_ships(self):
        for ship in self.ships:
            ship.navigator.move()
    def __repr__(self):
        return f"Fleet(name={self.name}, ships={self.ships})"
    
    

class Navigator:
        turntime_total_min=TurnInfo.duration_min
        
        def __init__(self, outer:Warship):
            self.ship: Warship=outer
            self.speed: float=outer.speed
            self.poses=[]   
            self.moves: list[MoveAction]=[]
            self.turntime_remaining_min=self.turntime_total_min
            pass
        def give_moves(self, moves: list[MoveAction]):
            self.moves=moves
            pass
        def move(self):
            start_pose=self.ship.turn_start_pose
            current_pose=start_pose
            self.poses.append(current_pose)
            for action in self.moves:
                if self.turntime_remaining_min<=0:
                    print(f"{self.ship.name} has no turn time remaining, cannot execute move {action}")
                    break
                if self.turntime_remaining_min<=action.duration_min:
                    action.duration_min=self.turntime_remaining_min
                match action.type:
                    case MoveType.COURSE_SPEED:
                        nav_list=Navigation.course_speed_linear(current_pose, action.course, 
                                                                    action.speed, self.ship.turn_radius, actiontime_min=action.duration_min)
                        current_pose=nav_list[0]
                        self.poses.append(nav_list[1])
                        self.turntime_remaining_min-=action.duration_min
                    case MoveType.TO_WAYPOINT:
                        nav_list=Navigation.to_waypoint(current_pose, action.waypoint, action.speed, self.ship.turn_radius, turntime_min=action.duration_min)
                        current_pose=nav_list[0]
                        self.poses.append(nav_list[1])
                        self.turntime_remaining_min-=nav_list[4]
                
                self.poses.append(current_pose)
                print(f"added pose {current_pose} to {self.ship.name}'s navigator")
                speed=action.speed
            self.ship.turn_end_pose=current_pose
            self.ship.speed=speed
        def __repr__(self):
            return f"Navigator(moves={self.moves}, turntime_remaining_min={self.turntime_remaining_min}, poses={self.poses})"
            


class FleetMaker:
    @staticmethod
    def csv_to_fleets(num_fleets:int, file_path:str)->list[Fleet]:
        df=pd.read_csv(file_path, index_col=1)
        pass
    
@staticmethod
def plot_course(navigators: list[Navigator], save_path:str="Plots/plot_data.txt"):
    t=open(save_path, "w")
    for navigator in navigators:
        sequence=navigator.poses
        t.write("type	latitude	longitude	name	desc	icon	color\n")
        for pose in sequence:
            t.write(f"T	{pose.latitude}	{pose.longitude}	{navigator.ship.name}, {sequence.index(pose)}\n")
        t.write("\n")
    pass

    