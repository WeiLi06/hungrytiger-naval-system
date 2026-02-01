from dataclasses import dataclass
import math
from enum import Enum
import geopy
from geopy.distance import distance

class Direction(Enum):
    NONE=0
    CLOCKWISE=1
    COUNTERCLOCKWISE=-1
    
class ShipType(Enum):
    UNKNOWN=0
    DD=1
    
class MoveType(Enum):
    NOT_SET=0
    COURSE_SPEED=1
    TO_WAYPOINT=2
    


@dataclass
class ShipPose:
    latitude: float
    longitude: float
    bearing: float
    earth_radius=6371000
        
    
    # def course_speed(self, target_bearing: float, speed: float, turn_radius: float, turn_dir: Direction = Direction.NONE, turntime_min:int=6):
    #     travel_dist=speed*turntime_min*60
    #     circle_list=Navigation.turn_circle(Navigation, self, target_bearing, turn_radius, turn_dir)
    #     if circle_list[1]<travel_dist:
    #         traveled_bearing=(self.bearing+360*travel_dist/turn_radius)(circle_list[2] / abs(circle_list[2]))
    #         return Navigation.turn_circle(Navigation, self, traveled_bearing, turn_radius, turn_dir)
    #     return [Navigation.get_endpoint(Navigation, circle_list[0], travel_dist-circle_list[1]), circle_list[0], travel_dist]
    def get_normalized(self):
        return ShipPose(self.latitude, self.longitude, (self.bearing + 720) % 360)

class MoveAction:
    type: MoveType
    course: float
    speed: float
    duration_min: float
    waypoint: ShipPose
    def __init__(self):
        self.type=MoveType.NOT_SET
        self.course=0
        self.speed=0
        self.duration_min=0
        self.waypoint=ShipPose(0,0,0)
    def course_speed(self, course: float, speed: float, duration_min: float=6):
        self.type=MoveType.COURSE_SPEED
        self.course=course
        self.speed=speed
        self.duration_min=duration_min
        return self
    def to_waypoint(self, waypoint: ShipPose, speed: float, turntime_min: float=6):
        self.type=MoveType.TO_WAYPOINT
        self.waypoint=waypoint
        self.speed=speed
        self.duration_min=turntime_min
        return self

class Navigation:
    #all distances and radii in meters, speeds in m/s, turn duration in min
    earth_radius=6371000
    
    def course_speed_linear(init_pose: ShipPose, target_bearing: float, speed: float, turn_radius: float, turn_dir: Direction = Direction.NONE, actiontime_min:int=6):
        travel_dist=speed*actiontime_min*60
        circle_list=Navigation.turn_circle(init_pose, target_bearing, turn_radius, turn_dir)
        if circle_list[1]>travel_dist:
            traveled_bearing=(init_pose.bearing+360*travel_dist/turn_radius)*(circle_list[2] / abs(circle_list[2]))
            return Navigation.turn_circle(init_pose, traveled_bearing, turn_radius, turn_dir)
        return Navigation.get_endpoint(circle_list[0], circle_list[0].bearing, travel_dist-circle_list[1]), circle_list[0], travel_dist
    
    def to_waypoint(init_pose: ShipPose, target_pose: ShipPose, speed: float, turn_radius: float, turntime_min:int=6):
        if (((Navigation.get_dist_bearing(init_pose, target_pose)[1]-init_pose.bearing+540)%360-180)<0):
            circle_center=Navigation.get_endpoint(init_pose, init_pose.bearing-90, turn_radius)
        else:
            circle_center=Navigation.get_endpoint(init_pose, init_pose.bearing+90, turn_radius)
        alpha=Navigation.tangent_angle_alpha(math.radians(circle_center.latitude), math.radians(circle_center.longitude),
                                       math.radians(target_pose.latitude), math.radians(target_pose.longitude),
                                       turn_radius/Navigation.earth_radius)
        circle_bearing=((Navigation.get_dist_bearing(circle_center, target_pose)[1]+540)%360-180)
        target_bearing=(circle_bearing- math.degrees(alpha)) % 360 if circle_bearing<0 else (circle_bearing+ math.degrees(alpha)) % 360
        tangents_azi=Navigation.tangent_azimuths(math.radians(circle_center.latitude), math.radians(circle_center.longitude),
                                       math.radians(target_pose.latitude), math.radians(target_pose.longitude),
                                       turn_radius)
        #target_bearing=math.degrees(tangents_azi[0])-90 if circle_bearing>0 else math.degrees(tangents_azi[1])+90
        print ("Tangent bearing: ", target_bearing)
        print ("Target pose: ", target_pose)
        print ("Init pose bearing: ", init_pose.bearing)
        print("Circle center: ", circle_center)
        print("Alpha (deg): ", math.degrees(alpha))
        print("Circle bearing: ", circle_bearing)
        circle_list=Navigation.turn_circle(init_pose, target_bearing, turn_radius)
        travel_dist=speed*turntime_min*60
        remainder_dist=Navigation.get_dist_bearing(circle_list[0], target_pose)[0]
        
        # Determine if the travel distance covers the turn and/or the straight segment. Returns final pose, intermediate pose, distance traveled, and whether the target was reached.
        if circle_list[1]>travel_dist:
            traveled_bearing=(init_pose.bearing+360*travel_dist/turn_radius)*(circle_list[2] / abs(circle_list[2]))
            return Navigation.turn_circle(init_pose, traveled_bearing, turn_radius)[0], Navigation.turn_circle(init_pose, traveled_bearing, turn_radius)[0], travel_dist, False
        elif(remainder_dist>travel_dist - circle_list[1]):
            return Navigation.get_endpoint(circle_list[0], circle_list[0].bearing, travel_dist - circle_list[1]), circle_list[0], travel_dist, False
        else:
            return Navigation.get_endpoint(circle_list[0], circle_list[0].bearing, remainder_dist),  circle_list[0], remainder_dist+circle_list[1], True
        
    
    # def get_endpoint(init_pose: ShipPose, bearing: float, distance: float):
    #     bearing_rad=math.radians(bearing)
    #     lat_rad=math.radians(init_pose.latitude)
    #     angular_dist=distance/Navigation.earth_radius
    #     final_lat=math.degrees(math.asin(math.sin(lat_rad) * math.cos(angular_dist)
    #                         + math.cos(lat_rad) * math.sin(angular_dist) * math.cos(bearing_rad)))
    #     final_long= init_pose.longitude + math.degrees(math.atan2(math.sin (bearing_rad) * math.sin (angular_dist) * math.cos (lat_rad)
    #                                                  ,math.cos (angular_dist) - math.sin (lat_rad) * math.sin(final_lat)))
    #     return ShipPose(final_lat, final_long, init_pose.bearing) # replace init_pose.bearing with actual final bearing
    
    def get_endpoint(init_pose: ShipPose, bearing: float, dist: float):
        start_point = geopy.Point(init_pose.latitude, init_pose.longitude)

        # Compute destination point
        destination = distance(kilometers=dist/1000).destination(point=start_point, bearing=bearing)
        final_bearing = (Navigation.get_dist_bearing(ShipPose(destination.latitude, destination.longitude, 0), init_pose)[1]+180) % 360
        return ShipPose(destination.latitude, destination.longitude, final_bearing)
    
    def turn_circle(init_pose:ShipPose, target_bearing:float, turn_radius: float, turn_dir: Direction = Direction.NONE):
        if(turn_dir!=Direction.NONE):
            dtheta_rad=math.radians((target_bearing-init_pose.bearing+ turn_dir.value*720) % turn_dir.value*360)
        else:
            dtheta_rad=math.radians((target_bearing-init_pose.bearing+540)%360-180)
        dx=0
        dy=0
        if(dtheta_rad!=0):
            dx=turn_radius * (1 - math.cos(dtheta_rad)) * (dtheta_rad / abs(dtheta_rad))
            dy=turn_radius * (math.sin(dtheta_rad)) * (dtheta_rad / abs(dtheta_rad))
        final_pos=Navigation.get_endpoint( Navigation.get_endpoint(init_pose, init_pose.bearing+0, dy), init_pose.bearing+90, dx)
        return ShipPose(final_pos.latitude,final_pos.longitude,target_bearing).get_normalized(), abs(turn_radius*(dtheta_rad)), dtheta_rad
    
    def get_dist_bearing(pose1: ShipPose, pose2: ShipPose):
        start_point = geopy.Point(pose1.latitude, pose1.longitude)
        end_point = geopy.Point(pose2.latitude, pose2.longitude)

        lat1 = math.radians(start_point.latitude)
        lon1 = math.radians(start_point.longitude)
        lat2 = math.radians(end_point.latitude)
        lon2 = math.radians(end_point.longitude)

        d_lon = lon2 - lon1
        x = math.sin(d_lon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
        initial_bearing = math.atan2(x, y)

        # Normalize the bearing to 0-360 degrees
        bearing = (math.degrees(initial_bearing) + 720) % 360

        # Compute distance
        distance_km = geopy.distance.geodesic(start_point, end_point).km
        return distance_km * 1000, bearing
    
    def tangent_angle_alpha(lat_c, lon_c, lat_p, lon_p, r):
        
        # Angular distance theta between center and point
        cos_theta = (
            math.sin(lat_c) * math.sin(lat_p)
            + math.cos(lat_c) * math.cos(lat_p) * math.cos(lon_p - lon_c)
        )

        # Clamp for numerical safety
        cos_theta = max(-1.0, min(1.0, cos_theta))
        theta = math.acos(cos_theta)

        if theta < r:
            raise ValueError("Point lies inside the circle; no tangent exists.")

        # Angle between CP and CT
        sin_theta = math.sin(theta)
        if sin_theta == 0:
            raise ValueError("Degenerate configuration.")

        alpha = math.asin(math.sin(r) / sin_theta)

        return alpha
    
    

    def tangent_azimuths(lat_c, lon_c, lat_p, lon_p, r):
        """
        Compute left/right tangent azimuths from circle center to a point
        using a local ellipsoidal ENU approximation.

        lat/lon in radians
        r in meters
        returns (az1, az2) in radians, clockwise from true north
        """
        A = 6378137.0
        F = 1 / 298.257223563
        E2 = F * (2 - F)

        # Radii of curvature at center latitude
        sin_lat = math.sin(lat_c)
        denom = math.sqrt(1 - E2 * sin_lat * sin_lat)
        N = A / denom
        M = A * (1 - E2) / (denom ** 3)

        # Local ENU projection (meters)
        dlat = lat_p - lat_c
        dlon = lon_p - lon_c
        east  = dlon * N * math.cos(lat_c)
        north = dlat * M

        # Distance from center to point
        d = math.hypot(east, north)
        if d < r:
            raise ValueError("Point lies inside the circle; no tangent exists.")

        # Azimuth from center to point
        theta = math.atan2(east, north)  # clockwise from north

        # Tangent offset
        alpha = math.acos(r / d)

        # Left/right tangent azimuths
        az1 = (theta + alpha) % (2 * math.pi)
        az2 = (theta - alpha) % (2 * math.pi)

        return az1, az2
                    
        
                
