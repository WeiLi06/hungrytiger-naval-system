from dataclasses import dataclass
import math
from nav_vision import ShipPose, MoveAction, MoveType, Navigation
import pandas as pd
from supplements import TurnInfo
import supplements as sp


class Warship:
    turn_start_pose: ShipPose
    turn_end_pose: ShipPose=None
    name: str
    speed: float #m/s
    turn_radius: float #meters
    is_commanded: bool
    ship_class: str
    navigator=None
    
    def __init__(self, start_pose:ShipPose, name:str, speed:float, commanded:bool=False, turn_radius:float=0, ship_class:str=""):
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
            self.poses_timestamp=[] #list of poses and timestamps corresponding to poses, in minutes
            self.moves: list[MoveAction]=[]
            self.remaining_moves: list[MoveAction]=[]
            self.turntime_remaining_min=self.turntime_total_min
            self.has_moved=False
            pass
        def give_moves(self, moves: list[MoveAction]):
            self.moves=moves
            self.remaining_moves=moves
            pass
        def move(self):
            start_pose=self.ship.turn_start_pose
            start_time=TurnInfo.turn_start_time
            current_time=start_time
            current_timestamp=TurnInfo.turn_start_timestamp
            current_pose=start_pose
            self.poses_timestamp.append((current_pose, current_time, current_timestamp))
            for action in self.moves:
                check_completion=False
                if self.turntime_remaining_min<=0:
                    print(f"{self.ship.name} has no turn time remaining, cannot execute move {action}")
                    break
                elif self.turntime_remaining_min<=action.duration_min:
                    if action.type==MoveType.COURSE_SPEED:
                        if action.duration_min==TurnInfo.duration_min or round(action.duration_min-self.turntime_remaining_min)==0:
                            self.remaining_moves[self.remaining_moves.index(action)]=MoveAction()
                            check_completion=True
                        else:
                            self.remaining_moves[self.remaining_moves.index(action)]=MoveAction().course_speed(course=action.course, speed=action.speed, duration_min=action.duration_min-self.turntime_remaining_min)
                            
                    action.duration_min=self.turntime_remaining_min
                else:
                    self.remaining_moves[self.remaining_moves.index(action)]=MoveAction()
                    check_completion=True
                match action.type:
                    case MoveType.COURSE_SPEED:
                        nav_list=Navigation.course_speed_linear(current_pose, action.course, 
                                                                    action.speed, self.ship.turn_radius, actiontime_min=action.duration_min)
                        current_pose=nav_list["final pose"]
                        if self.ship.turn_radius>0:
                            self.poses_timestamp.append((nav_list["intermediate pose"], current_time+nav_list["time elapsed (turn)"], current_timestamp+pd.Timedelta(minutes=nav_list["time elapsed (turn)"])))
                        current_time+=nav_list["time elapsed"]
                        current_timestamp+=pd.Timedelta(minutes=nav_list["time elapsed"])
                        self.turntime_remaining_min-=action.duration_min
                    case MoveType.TO_WAYPOINT:
                        nav_list=Navigation.to_waypoint(current_pose, action.waypoint, action.speed, self.ship.turn_radius, turntime_min=action.duration_min)
                        current_pose=nav_list["final pose"]
                        if self.ship.turn_radius>0:
                            self.poses_timestamp.append((nav_list["intermediate pose"], current_time+nav_list["time elapsed (turn)"], current_timestamp+pd.Timedelta(minutes=nav_list["time elapsed (turn)"])))
                        current_time+=nav_list["time elapsed"]
                        current_timestamp+=pd.Timedelta(minutes=nav_list["time elapsed"])
                        self.turntime_remaining_min-=nav_list["time elapsed"]
                        if not check_completion:
                            if nav_list["target reached"]:
                                self.remaining_moves[self.remaining_moves.index(action)]=MoveAction()
                    case MoveType.MAINTAIN_STATION:
                        pass
                
                self.poses_timestamp.append((current_pose, current_time, current_timestamp))
                print(f"added pose {current_pose} to {self.ship.name}'s navigator")
                self.ship.speed=action.speed
            self.ship.turn_end_pose=current_pose
            self.has_moved=True
        def __repr__(self):
            return f"Navigator(moves={self.moves}, turntime_remaining_min={self.turntime_remaining_min}, poses={self.poses_timestamp})"
            


class FleetMaker:
    @staticmethod
    def csv_to_fleets(num_fleets:int, file_path:str)->list[Fleet]:
        df=pd.read_csv(file_path, index_col=1)
        pass
    
@staticmethod
def plot_course(navigators: list[Navigator], save_path:str="Output/Plots/plot_data.txt"):
    t=open(save_path, "w")
    t.write("type	latitude	longitude	name	desc	icon	color\n")
    for navigator in navigators:
        sequence=navigator.poses_timestamp
        t.write(f"W	{round(sequence[-1][0].latitude, 6)}	{round(sequence[-1][0].longitude, 6)}	{navigator.ship.name}	{TurnInfo.turn_end_timestamp.round(freq='min').strftime("%m-%d-%H%M")}\n")   
    t.write("\n")
    t.write("\n")
    for navigator in navigators:
        sequence=navigator.poses_timestamp
        t.write("type	latitude	longitude	name	desc	icon	color\n")
        for pose, time, timestamp in sequence:
            print(f"plotting pose {pose} for {navigator.ship.name} at time {timestamp}")
            t.write(f"T	{round(pose.latitude, 6)}	{round(pose.longitude, 6)}	{navigator.ship.name}	{timestamp.round(freq='min').strftime("%m-%d-%H%M")}\n")
        t.write("\n")
        t.write(f"W	{round(sequence[-1][0].latitude, 6)}	{round(sequence[-1][0].longitude, 6)}	{navigator.ship.name}	{TurnInfo.turn_end_timestamp.round(freq='min').strftime("%m-%d-%H%M")}\n")
        t.write("\n\n")
        print(f"plotted navigator for {navigator.ship.name}")

@staticmethod
def weather_report(navigators: list[Navigator], df: pd.DataFrame, save_path:str="Output/Plots/weather_report.txt"):
    t=open(save_path, "w")
    t.write(f"WEATHER REPORT, {TurnInfo.turn_end_timestamp.round(freq='min').strftime('%m-%d-%H%M')}\n\n")
    for navigator in navigators:
        local_weather=sp.weighted_average_weather_data(df, navigator.poses_timestamp[-1][0].latitude, navigator.poses_timestamp[-1][0].longitude).to_dict()
        sequence=navigator.poses_timestamp
        t.write(f"{navigator.ship.name} at (lat, long)=({round(sequence[-1][0].latitude, 6)}, {round(sequence[-1][0].longitude, 6)})\n")
        t.write(f"Temperature: {round(local_weather['t2m']-273.15, 1)} C\n")
        t.write(f"Wind: {round(sp.convert_mps_to_kt(math.hypot(local_weather['u10'], local_weather['v10'])), 1)} kt gusting to {round(sp.convert_mps_to_kt(local_weather['fg10']), 1)} kt from {round((math.degrees(math.atan2(local_weather['u10'], local_weather['v10']))+180)%360)} degrees\n")
        t.write(f"Wave height: {round(local_weather['swh'], 2)} m\n")
        t.write(f"Precipitation: {round(local_weather['tp']*1000, 2)} mm/h\n")
        t.write(f"Temperature-Dewpoint spread: {round(local_weather['t2m']-local_weather['d2m'], 1)} C\n")
        t.write(f"Cloud cover: {round(local_weather['tcc']*100, 1)}%\n")
        t.write(f"Sea Ice cover: {round(local_weather['siconc']*100, 1)}%\n")
        t.write(f"Surface pressure: {round(local_weather['sp']/100, 1)} hPa\n")
        t.write(f"Surface Solar radiation: {round(local_weather['ssrd'])} J/m^2\n")
        t.write(f"Surface Thermal radiation: {round(local_weather['strd'])} J/m^2\n")
        match local_weather["ptype"]:
            case 0:
                t.write("Precipitation type: None\n")
            case 1:
                t.write("Precipitation type: Rain\n")
            case 3:
                t.write("Precipitation type: Freezing Rain\n")
            case 5:
                t.write("Precipitation type: Snow\n")
            case 6:
                t.write("Precipitation type: Wet snow\n")
            case 7:
                t.write("Precipitation type: Slush\n")
            case 8:
                t.write("Precipitation type: Ice pellets\n")
        t.write("\n\n")
        