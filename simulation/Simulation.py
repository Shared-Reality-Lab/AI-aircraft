import xml.etree.ElementTree as ET
from time import sleep
from Aircraft import Aircraft
from geopy.distance import distance
from pathlib import Path

dref_user_vel_x = 'sim/flightmodel/position/local_vx'
dref_user_vel_y = 'sim/flightmodel/position/local_vy'
dref_user_vel_z = 'sim/flightmodel/position/local_vz'
dref_user_velocity = 'sim/flightmodel/position/groundspeed'
dref_user_acc_x = 'sim/flightmodel/position/local_ax'
dref_user_acc_y = 'sim/flightmodel/position/local_ay'
dref_user_acc_z = 'sim/flightmodel/position/local_az'
dref_vel_x = 'sim/multiplayer/position/plane{}_v_x'
dref_vel_y = 'sim/multiplayer/position/plane{}_v_y'
dref_vel_z = 'sim/multiplayer/position/plane{}_v_z'
dref_gear = 'sim/multiplayer/controls/gear_request'
dref_breaks    = "sim/multiplayer/controls/parking_brake"

class Simulation:

    def __init__(self, client, scenario):
        self.client = client
        self.scenario = scenario

    def printDREF(self, dref):
        """Print a specific Dref
        
        """     
        result = self.client.getDREF(dref)
        print(f'{dref} : {result}')


    def Read_XML(self):
        """Read information from the trajectories.xml file.

            return format : [ [ac_ID, lat-wp1, lon_wp1, lat_wp2, lon_wp2] , [ac_ID, lat-wp1, lon_wp1, lat_wp2, lon_wp2] , ... ]
                                                    ^                                                ^
                                        Waypoints for first ac                            Waypoints for second ac
        
        """
        # Load and analyse XML file
        tree = ET.parse(self.scenario)
        root = tree.getroot()

        # Create a main list for all trajectory information
        xml_list = []
        
        # Loop that goes through every trajectories
        for trajectory in root.findall('ac'):
            
            # Get aircraft ID and store it in a local list
            ac_id = int(trajectory.get('id'))
            current_trajectory = [ac_id]
            
            # Analyze waypoints the aircraft will have to go to
            waypoints = trajectory.find('waypoints')
            
            # Go through every waypoint coordinates and store them in the local list
            if waypoints is not None:
                for waypoint in waypoints.findall('waypoint'):
                    lat = float(waypoint.get('lat'))
                    lon = float(waypoint.get('lon'))
                    speed = float(waypoint.get('speed')) #* 0.5144 #Conversion noeuds -> m/s
                    current_trajectory.extend([lat, lon, speed])

            # Add all information about the current trajectory list to the main list
            xml_list.append(current_trajectory)
        return xml_list

    def Read_XMLSimu(self):
        """Read information from the sumulation.xml file.
        
        """
        # Load and analyse XML file
        tree = ET.parse(self.scenario)
        root = tree.getroot()

        # Create 2 main lists for all conflicts and lead-follows information
        intersections_dico = {}
        leadFollow_dico = {}
        
        # Loop that goes through every aircraft
        for ac in root.findall('ac'):
            
            ac_id = int(ac.get('id'))
            
            conflict = ac.find('conflict')

            if conflict is not None:
                conflict_type = conflict.get('type')
                
                location = conflict.find('location')
                offset = conflict.find('offset')

                lat = float(location.get('lat'))
                lon = float(location.get('lon'))
                offset = int(float(offset.get('dist')))

                # Check the type of conflict
                if conflict_type == "intersection" :
                    intersections_dico[ac_id] = [(lat, lon), offset]

                if conflict_type == "lead-follow" :
                    slow_down = conflict.find('slow-down')
                    dist_before_slow = int(slow_down.get('dist'))
                    speed_reduction = int(slow_down.get('reduc'))
                    leadFollow_dico[ac_id] = [(lat, lon), offset, dist_before_slow, speed_reduction]

        return intersections_dico, leadFollow_dico

    def Initialize(self):
        """Create Aircraft objects and set controls and positions of each aircraft
        
        """
        
        # Read XML simulation file
        xml_list = self.Read_XML()

        intersections_dico, followings_dico = self.Read_XMLSimu()
        
        # Enable all gears
        self.client.sendDREF(dref_gear, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        # Set all ai aircraft velocities to null
        for i in range (1, 21):
            vel_x = dref_vel_x.format(i)
            vel_y = dref_vel_y.format(i)
            vel_z = dref_vel_z.format(i)
            self.client.sendDREF(vel_x, 0.0)
            sleep(0.1)
            self.client.sendDREF(vel_y, 0.0)
            sleep(0.1)
            self.client.sendDREF(vel_z, 0.0)
            sleep(0.1)
        self.client.sendDREF(dref_user_vel_x, 0.0)
        sleep(0.1)
        self.client.sendDREF(dref_user_vel_y, 0.0)
        sleep(0.1)
        self.client.sendDREF(dref_user_vel_z, 0.0)
        sleep(0.1)

        # List of every Aircraft objects
        aircraft_list = []

        for i in range (len(xml_list)):

            # Create an Aircraft object for each aircraft in the simulation
            ac = Aircraft(self.client, xml_list[i][0])

            if xml_list[i][0] != 0:
                aircraft_list.append(ac)
            
            # Initialize controls and positions of every aircrafts
            sleep(1)
            if ac.ID == 0 :
                ac.setPOST([xml_list[i][1], xml_list[i][2], 110.20504630126953, -1.0, 0.6105514168739319, 190, 1.0])
            elif ac.ID != 0 :
                ac.setCTRL([0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0])
                ac.setPOST([xml_list[i][1], xml_list[i][2], 110.20504630126953, -1.0, 0.6105514168739319, 190, 1.0])
            sleep(1)
            # Set initial heading so make aircrafts face the first next waypoint
            initial_heading = ac.compute_target_heading(xml_list[i][4],xml_list[i][5])
            ac.setPOST([-998, -998, -998, -998, -998, initial_heading, -998])

            # Enable breaks 
            ac.set_breaks(1.0)

            # Enable mixture
            ac.set_mixture(1.0)
        
        return aircraft_list, xml_list, followings_dico, intersections_dico


    def main_loop(self, aircraft_list, xml_list, followings_dico, intersections_dico):
        """Simulation main running loop

            Args :
                all_trajectories : list returned by the function Read_XML()
        
        """
               
        # Overide AI autopilot over all aircrafts
        dref_override_planepath = "sim/operation/override/override_planepath"
        table_override_planepath = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.client.sendDREF(dref_override_planepath, table_override_planepath)
        
        flag_end_movement = [1] * 20

        flag_speed_null = [0] * 20

        index_waypoint = [1] *20

        wp_lat = [0] * 20
        wp_lon = [0] * 20
        wp_vel = [0] * 20

        i = 1
        # Loop that goes through every aircrafts
        for ac in aircraft_list :
            ac_ID = ac.ID

            # Disable aircraft breaks
            ac.set_breaks(0.0)

            # Store waypoints in a list
            wp_lat[ac_ID] = xml_list[i][4]
            wp_lon[ac_ID] = xml_list[i][5]
            wp_vel[ac_ID] = xml_list[i][6]

            # Initialize end of movement flag
            flag_end_movement[ac_ID] = 0

            flag_speed_null[ac_ID] = 0

            i += 1
        
        flag_end_movement[0] = 1 # User aircraft should not interfere with AI aircraft

        j = 0

        flagd = [0] * 20
        flagf = [0] * 20

        flag_figure = [[0,0] for _ in range(20)]

        list_AI_speed = [[] for _ in range(20)]
        list_user_speed = [[] for _ in range(20)]
        list_target_speed = [[] for _ in range(20)]

        # Main loop
        while True :

            try :

                # print user velocity
                user_vel = self.client.getDREF(dref_user_velocity)[0]
                print(f'user_velocity = {user_vel*1.944:.1f} kt')

                for ac in aircraft_list :

                    ac_ID = ac.ID
                    user_vel = self.client.getDREF(dref_user_velocity)[0]

                    # User aircraft not included in simulation
                    if ac_ID != 0 :

                            # Test if current aircraft needs to be moved
                        if flag_end_movement[ac_ID] == 0 :

                            # check if ac is in test_conflict or test_follow
                            if ac_ID in followings_dico :

                                infos = followings_dico[ac_ID]
                                conflict_pos = infos[0]
                                offset = infos[1]
                                slow_distance = infos[2]
                                reduced_speed = infos[3] * 0.514 # en m/s

                                flag1 = flagd[ac_ID]
                                flag2 = flagf[ac_ID]

                                current_position = ac.current_position()
                                list_AI_speed[ac_ID].append(round(ac.getSPEED()*1.944, 1))  # in kt
                                list_user_speed[ac_ID].append(round(user_vel*1.944, 1))

                                if flag1 == 0 :
                                    target_speed = ac.correct_speed2(conflict_pos, offset)
                                else :
                                    if flag2 == 0 :
                                        target_speed = user_vel
                                        user_pos = self.client.getPOSI()
                                    else :
                                        target_speed = flag2 + reduced_speed

                                list_target_speed[ac_ID].append(round(target_speed*1.944, 1)) # in kt
                                
                                flag_speed_null[ac_ID] = ac.correct_speed(target_speed, flag_speed_null[ac_ID])

                                if flag1 == 0 and ac.reached_target(conflict_pos[0], conflict_pos[1]) == 1 :
                                    flagd[ac_ID] = current_position
                                    flag_figure[ac_ID][0] = j

                                if flag1 != 0 and flag2 == 0 and distance(current_position, flag1).meters >= slow_distance :
                                    flagf[ac_ID] = ac.getSPEED() + 1
                                    flag_figure[ac_ID][1] = j
                                    if flagf[ac_ID] < reduced_speed :
                                        reduced_speed = flagf[ac_ID]
                                        flag_end_movement[ac_ID] = 1
                                        ac.show1(list_AI_speed[ac_ID], list_user_speed[ac_ID], list_target_speed[ac_ID], flag_figure[ac_ID])

                            elif ac_ID in intersections_dico :
                                infos = intersections_dico[ac_ID]
                                conflict_pos = infos[0]
                                offset = infos[1]

                                # target_speed is different before and after the intersection conflict
                                if flagf[ac_ID] == 0 :
                                    target_speed = ac.correct_speed2(conflict_pos, offset)
                                else :
                                    target_speed = wp_vel[ac_ID]

                                flag_speed_null[ac_ID] = ac.correct_speed(target_speed, flag_speed_null[ac_ID])

                                # check if the aircraft is before or after the intersection conflict
                                if flagf[ac_ID] == 0 and ac.reached_target(conflict_pos[0], conflict_pos[1]) == 1 :
                                    flagf[ac_ID] = 1

                            else:
                                target_speed = wp_vel[ac_ID]
                                flag_speed_null[ac_ID] = ac.correct_speed(target_speed, flag_speed_null[ac_ID])

                            # Stops simulation if an ai aircraft is not moving for 40 ms
                            if flag_speed_null[ac_ID] >= 4 :
                                print(f'Aircraft {ac_ID} not moving')
                                flag_speed_null[ac_ID] = 0
                                
                            ac.correct_heading(wp_lat[ac_ID], wp_lon[ac_ID])
                            flag = ac.reached_target(wp_lat[ac_ID], wp_lon[ac_ID])

                            if flag == 1 :
                                waypoint_numer = (index_waypoint[ac_ID] //3) + 1

                                index_waypoint[ac_ID] += 3
                                flag_end, wp_lat[ac_ID], wp_lon[ac_ID], wp_vel[ac_ID] = ac.next_waypoint(xml_list, index_waypoint[ac_ID])

                                if flag_end == 1 :
                                    print(f'end of trajectory : ac{ac_ID}')
                                    ac.set_breaks(1.0)
                                    flag_end_movement[ac_ID] = 1
                                    if ac_ID in followings_dico : ac.show1(list_AI_speed[ac_ID], list_user_speed[ac_ID], list_target_speed[ac_ID], flag_figure[ac_ID])
                            
                j += 1
                sleep(0.5)


            except TimeoutError:
                print ("TIMEOUT")
                pass
            except ConnectionResetError:
                print("CONNECTION RESET ERROR")
                pass
            except IndexError:
                print("INDEX")
                pass
        
        

