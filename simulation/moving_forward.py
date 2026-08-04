from time import sleep
import xpc
import CoordConverter
import Terrain
from Simulation import Simulation
from Aircraft import Aircraft

def main():
        
    # Verify connection with xplane
    with xpc.XPlaneConnect() as client: 
        try:
            client.getDREF("sim/test/test_float")
        except:
            print("Error establishing connection to X-Plane.")
            print("Exiting...")
            return
        sleep(2)

        # Override AI automatic control over aircrafts
        dref_override_ai = "sim/operation/override/override_plane_ai_autopilot"
        table_override_ai = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        client.sendDREF(dref_override_ai, table_override_ai)

        dref_override_planepath = "sim/operation/override/override_planepath"
        table_override_planepath = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        client.sendDREF(dref_override_planepath, table_override_planepath)

        ac2 = Aircraft(client, 0)
        ac2.setPOST([49.022314, 2.548358, 110.20504630126953, -1.0, 0.6105514168739319, 190, 1.0])
        ac2.setCTRL([0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0])
        
        ac1 = Aircraft(client, 2)
        ac1.setPOST([49.022314, 2.548358, 110.20504630126953, -1.0, 0.6105514168739319, 190, 1.0])
        ac1.setCTRL([0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0])

        sleep(1)
        table_override_planepath = [0, 0, 0, 0, 0]
        client.sendDREF(dref_override_planepath, table_override_planepath)

        sleep(1)
        ac2.set_breaks(0.0)
        ac1.set_breaks(0.0)
        sleep(2)
        drefprint = 'sim/multiplayer/combat/team_status'
        drefprint2 = 'sim/multiplayer/combat/team_status'
        res = client.getDREF(drefprint)
        res2 = client.getDREF(drefprint2)
        print(res)
        print(res2)
        sleep(1)
        ac2.set_breaks(1.0)
        ac1.set_breaks(1.0)

        
        

        input("End of simulation, press any key to exit...")


if __name__ == "__main__": 
    main()