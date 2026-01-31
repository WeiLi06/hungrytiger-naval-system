from ship_data import ShipPose
import math

class Navigation:
    #all distances in meters
    earth_radius=6371000
    # def course_speed_linear(self, init_pose, bearing, speed):
    
    def get_endpoint(self, init_pose: ShipPose, distance: float):
        bearing_rad=math.radians(init_pose.bearing)
        final_lat=math.asin(math.sin(init_pose.latitude) * math.cos(distance/self.earth_radius)
                            + math.cos(init_pose.latitude) * math.sin(distance/self.earth_radius) * math.cos(bearing_rad) )
        final_long= init_pose.longitude + math.atan2(math.sin (bearing_rad) * math.sin (distance/self.earth_radius) * math.cos (init_pose.latitude), 
                                                     math.cos (distance/self.earth_radius) - math.sin (init_pose.latitude) * math.sin(final_lat))
        return ShipPose(final_lat, final_long, init_pose.bearing) # replace init_pose.bearing with actual final bearing
    
    def turn_circle(self, init_pose:ShipPose, target_bearing:float, turn_radius: float): #positive values 
        init_bearing_rad=math.radians(init_pose.bearing)
        target_bearing_rad=math.radians(target_bearing)
        dtheta=(target_bearing_rad-init_bearing_rad)
        dx=0
        if(dtheta!=0):
            dx=turn_radius * (1 - math.cos(dtheta)) * (dtheta / abs(dtheta))
            
