import math
import CoordConverter
import Terrain
from time import sleep
from geopy.distance import distance
import matplotlib.pyplot as plt

# Variables
kp = 0.01                   # Proportional corrector gain for heading
kp_speed = 0.4              # Proportional corrector gain for speed 
tolerance = 0.0003          # Tolerance for detecting a reached target position

# Drefs
dref_breaks    = "sim/multiplayer/controls/parking_brake"
dref_mixture   = "sim/multiplayer/controls/engine_mixture_request"
dref_heading   = "sim/multiplayer/controls/yoke_heading_ratio"
dref_vel_ac0   = "sim/flightmodel/position/groundspeed"
dref_speed_x   = "sim/multiplayer/position/plane{}_v_x"
dref_speed_y   = "sim/multiplayer/position/plane{}_v_y"
dref_speed_z   = "sim/multiplayer/position/plane{}_v_z"

class Aircraft:

    # CONSTRUCTOR ****************************************
    def __init__(self, client, ID):
        self.client = client
        self.ID = ID
        print(f'Aircraft {ID} created successfully')
    
    def __repr__(self):
        return f"Aircraft {self.ID}"

    # SET & GET ******************************
    def printCTRL(self):
        res = self.client.getCTRL(self.ID)
        print(f"Aircraft {self.ID} CTRL : {res}")
    
    def setCTRL(self, controls):
        self.client.sendCTRL(controls, self.ID)

    def printPOSI(self):
        res = self.client.getPOSI(self.ID)
        print(f"Aircraft {self.ID} POSI : {res}")

    def setPOSI(self, pos):
        self.client.sendPOSI(pos, self.ID)

    def setPOST(self, pos):
        Terrain.sendPOST(self.client, pos, self.ID)

    def getSPEED(self):

        if self.ID == 0 :
            res = self.client.getDREF(dref_vel_ac0)
        else :
            resx = self.client.getDREF(dref_speed_x.format(self.ID))
            resy = self.client.getDREF(dref_speed_y.format(self.ID))
            resz = self.client.getDREF(dref_speed_z.format(self.ID))
            res = math.sqrt(resx[0]**2 + resy[0]**2 + resz[0]**2)
        return res

    # DRIVING ********************************************

    def set_breaks(self, breaks_value):

        if breaks_value > 1 or breaks_value < 0 :
            print(f'Warning : breaks value out of bounds (aircraft {self.ID})')
            return
        
        breaks = list(self.client.getDREF(dref_breaks))
        breaks[self.ID] = breaks_value
        self.client.sendDREF(dref_breaks, tuple(breaks))

    def set_mixture(self, mixture_value):

        if mixture_value > 1 or mixture_value < 0 :
            print(f'Warning : mixture value out of bounds (aircraft {self.ID})')
            return
       
        mixture = list(self.client.getDREF(dref_mixture))
        
        mixture[self.ID] = mixture_value
        self.client.sendDREF(dref_mixture, tuple(mixture))

    # HEADING ********************************************
    def compute_target_heading(self, target_lat, target_lon):
        """Compute the aircraft target heading to face towards waypoint

            Args :
                target lat and lon in degrees 
        """

        # Retrieve aircraft current heading, lat and lon
        pos = self.client.getPOSI(self.ID)
        current_heading = pos[5]
        current_lat = pos[0]
        current_lon = pos[1]

        # Converts geographic coordinates into utm coordinates
        x1, y1 = CoordConverter.geo_to_utm(current_lat, current_lon)
        x2, y2 = CoordConverter.geo_to_utm(target_lat, target_lon)
        
        # Compute trajectory vector
        vector_x = x2 - x1
        vector_y = y2 - y1
        
        # Compute vector angle (regarding y axis)
        cartesian_angle = math.degrees(math.atan2(vector_x, vector_y))
        cartesian_angle = cartesian_angle - current_heading

        # Compute aircraft heading to align towards vector
        target_heading = (current_heading + cartesian_angle +360) %360

        return target_heading


    def correct_heading(self, target_lat, target_lon):
        """Compute and send fixed heading command to face towards waypoint

            Args :
                target lat and lon in degrees      
        """

        target_heading = self.compute_target_heading(target_lat, target_lon)
                    
        # Retrieve current aircraft heading
        position = self.client.getPOSI(self.ID)
        current_heading = position[5]

        # Compute error angle
        error = target_heading - current_heading

        # Normalize error angle 
        if error > 180 :
            error -= 360
        elif error < -180 :
            error += 360

        # Compute and send fixed value of heading command
        correction_value = error * kp
        if correction_value > 1.0 :
            correction_value = 1.0
        elif correction_value < -1.0 :
            correction_value = -1.0

        fixed_heading = list(self.client.getDREF(dref_heading))
        fixed_heading[self.ID] = correction_value
        self.client.sendDREF(dref_heading, fixed_heading)
        
    def reached_target(self, target_lat, target_lon):
        """Detects when the aircraft has reached the target waypoint

            Args :
                target lat and lon in degrees      
        """

        position = self.client.getPOSI(self.ID)
        current_lat = position[0]
        current_lon = position[1]
        if ( (current_lat < (target_lat + tolerance) and current_lat > (target_lat - tolerance)) and (current_lon < (target_lon + tolerance) and current_lon > (target_lon - tolerance)) ) :
            return 1
        else :
            return 0 

    def next_waypoint(self, xml_list, index_waypoint):
        """Replaces current target waypoint by the next one. Raises flag when there are no more waypoints left.

            Args :
                target lat and lon in degrees      
        """

        # Retrieve self trajectory list in xml_list
        self_list = []
        for lists in xml_list :
            if lists[0] == self.ID :
                self_list = lists       

        # Increments indexes to match next waypoint coordinates
        index_lat = index_waypoint + 3
        index_lon = index_waypoint + 4
        index_vel = index_waypoint + 5

        # Checks rather the next waypoint exists or not
        if (index_lat > len(self_list) or index_lon > len(self_list)) :
            flag_end = 1
            return flag_end, 0, 0, 0
        else :
            flag_end = 0
            # Next waypoint coordinates
            next_lat = self_list[index_lat]
            next_lon = self_list[index_lon]
            next_speed = self_list[index_vel]

            return flag_end, next_lat, next_lon, next_speed

    def correct_speed(self, target_speed, flag_speed_null):
        """Correct aircraft velocity to match target velocity

            Args :
                   target_speed : target speed in m/s
        """

        current_speed = self.getSPEED()

        # Detect if aircraft is not moving
        if current_speed < 1.0 :
            flag_speed_null += 1 

        # Compute speed error
        speed_error = target_speed - current_speed

        # Compute breaks value to match target speed
        new_breaks_value = -(speed_error * kp_speed)
        if new_breaks_value > 1.0 :
            new_breaks_value = 1.0
        elif new_breaks_value < 0.0 :
            new_breaks_value = 0.0

        # Get current breaks values and add the fixed one
        breaks = list(self.client.getDREF(dref_breaks))
        breaks[self.ID] = new_breaks_value

        self.client.sendDREF(dref_breaks, breaks)

        return flag_speed_null

    def correct_speed2(self, conflict_pos, conflict_offset):
        """Calculate the target velocity to generate conflict between ia and user aircraft
            Args :
                    target_speed : target speed in m/s
                    conflict_pos : tuple (latitude, longitude)
        """
        
        ia_position = self.client.getPOSI(self.ID)
        ia_pos = (ia_position[0], ia_position[1])
        user_position = self.client.getPOSI()
        user_pos = (user_position[0], user_position[1])

        user_dist = distance(user_pos, conflict_pos).meters
        ia_dist = distance(ia_pos, conflict_pos).meters

        user_speed = self.client.getDREF(dref_vel_ac0)[0]

        if (ia_dist + conflict_offset) <= 0 :
            conflict_offset = 0

        target_speed = (ia_dist + conflict_offset) * user_speed / user_dist

        return target_speed

    def current_position(self):
        current_pos = self.client.getPOSI(self.ID)
        return (current_pos[0], current_pos[1])
        

    def show1(self, AIVelocity, userVelocity, list_target_speed, flag_reduced_speed):
        plt.figure()
        
        x_axis = [i for i in range(len(AIVelocity))]
        plt.plot(x_axis, AIVelocity, label="AI")
        plt.plot(x_axis, userVelocity, label="User")
        plt.scatter(x_axis, list_target_speed, label="Target", color="black")

        plt.axvline(x = flag_reduced_speed[0], color="red", linestyle="--", linewidth=2)
        plt.axvline(x = flag_reduced_speed[1], color="red", linestyle="--", linewidth=2)

        plt.legend()
        plt.title(f"Speed comparison with ac{self.ID}")
        plt.savefig(f"ac{self.ID}.png")
        plt.close()
