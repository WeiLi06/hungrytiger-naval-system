from dataclasses import dataclass


    
@dataclass
class ShipPose:
    latitude: float
    longitude: float
    bearing: float

class Warship:
    turn_start_pose: ShipPose
    turn_end_pose: ShipPose
    
    
    