from ship_data import ShipPose
import math
from enum import Enum

class Direction(Enum):
    NONE=0
    CLOCKWISE=1
    COUNTERCLOCKWISE=-1

class Navigation:
    #all distances and radii in meters, speeds in m/s, turn duration in min
    earth_radius=6371000
    
    def course_speed_linear(self, init_pose: ShipPose, bearing: float, speed: float, turn_radius: float, turn_dir: Direction = Direction.NONE, turn_duration:int=6):
        travel_dist=speed
        return self.get_endpoint(self, Navigation.turn_circle(self, init_pose, bearing, turn_radius, turn_dir), )
    
    def get_endpoint(self, init_pose: ShipPose, bearing: float, distance: float):
        bearing_rad=math.radians(bearing)
        lat_rad=math.radians(init_pose.latitude)
        angular_dist=distance/Navigation.earth_radius
        final_lat=math.degrees(math.asin(math.sin(lat_rad) * math.cos(angular_dist)
                            + math.cos(lat_rad) * math.sin(angular_dist) * math.cos(bearing_rad)))
        final_long= init_pose.longitude + math.degrees(math.atan2(math.sin (bearing_rad) * math.sin (angular_dist) * math.cos (lat_rad)
                                                     ,math.cos (angular_dist) - math.sin (lat_rad) * math.sin(final_lat)))
        return ShipPose(final_lat, final_long, init_pose.bearing) # replace init_pose.bearing with actual final bearing
    
    def get_endpoint(self, init_pose: ShipPose, distance: float):
        bearing_rad=math.radians(init_pose.bearing)
        lat_rad=math.radians(init_pose.latitude)
        angular_dist=distance/Navigation.earth_radius
        final_lat=math.degrees(math.asin(math.sin(lat_rad) * math.cos(angular_dist)
                            + math.cos(lat_rad) * math.sin(angular_dist) * math.cos(bearing_rad)))
        final_long= init_pose.longitude + math.degrees(math.atan2(math.sin (bearing_rad) * math.sin (angular_dist) * math.cos (lat_rad)
                                                     ,math.cos (angular_dist) - math.sin (lat_rad) * math.sin(final_lat)))
        return ShipPose(final_lat, final_long, init_pose.bearing) # replace init_pose.bearing with actual final bearing
    
    def turn_circle(self, init_pose:ShipPose, target_bearing:float, turn_radius: float, turn_dir: Direction = Direction.NONE):
        init_bearing_rad=math.radians(init_pose.bearing)
        target_bearing_rad=math.radians(target_bearing)
        
        if(turn_dir!=Direction.NONE):
            dtheta=((target_bearing_rad-init_bearing_rad)+ turn_dir.value*720) % turn_dir.value*360
        else:
            dtheta=((target_bearing_rad-init_bearing_rad)+540)%360-180
            
        dx=0
        dy=0
        if(dtheta!=0):
            dx=turn_radius * (1 - math.cos(dtheta)) * (dtheta / abs(dtheta))
            dy=turn_radius * (math.sin(dtheta)) * (dtheta / abs(dtheta))
        final_pos=self.get_endpoint(self, self.get_endpoint(self, init_pose, init_pose.bearing+0, dy), init_pose.bearing+90, dx)
        
        
        return ShipPose(final_pos.latitude,final_pos.longitude,target_bearing)
        
            
