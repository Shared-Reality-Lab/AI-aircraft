import xpc

elevation_offset = 2.5

def terrain_elevation(client, terrain_coordinates):
    """Returns terrain elevation

        Args : 
            client : client
            terrain_coordinates : coordinates where to compute terrain elevation [lat, lon, elev]
                                  elev must be set at 0 
    """

    # Ensures that terrain_coordinates is in the correct format
    if len(terrain_coordinates) != 3 :
        print('terrain_coordinates must be an array of lenght 3')
        return
    
    # Retrieves terrain elevation
    terrain_info = client.getTERR(terrain_coordinates)
    terrain_elevation = terrain_info[2]

    return terrain_elevation

def sendPOST(client, pos, aircraft_number):
    """sendPOSI at ground level

        Args : 
            client : client
            terrain_coordinates : coordinates where to compute terrain elevation [lat, lon, elev]
                                  elev must be set at 0 
            aircraft_number : 0 for user aircraft, [1-20] for ai aircraft
    """
    # Retrieve terrain elevation at specified coordinates [lat, lon, elev = 0]
    terrain_coordinates = [pos[0], pos[1], 0]
    elevation = terrain_elevation(client, terrain_coordinates) 

    # Send fixed elevation (ground level + landing gear height)
    pos[2] = elevation + elevation_offset
    client.sendPOSI(pos, aircraft_number)

