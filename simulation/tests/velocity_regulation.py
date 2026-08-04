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
        table_override_ai = [True, True, True]
        client.sendDREF(dref_override_ai, table_override_ai)

        dref_override_planepath = "sim/operation/override/override_planepath"
        table_override_planepath = [True, True, True]
        client.sendDREF(dref_override_planepath, table_override_planepath)

        dreff = "sim/flightmodel/position/groundspeed"
        
        # MAIN
        ac1 = Aircraft(client, 1)
        ac1.setPOST([49.018086, 2.541438, 110.20504630126953, -1.0, 0.6105514168739319, 90, 1.0])
        ac1.setCTRL([0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0])

        ac0 = Aircraft(client, 0)
        ac0.setPOST([49.018086, 2.541438, 110.20504630126953, -1.0, 0.6105514168739319, 90, 1.0])
        ac0.setCTRL([0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0])
        sleep(1)

        table_override_planepath = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        client.sendDREF(dref_override_planepath, table_override_planepath)

        ac0.set_breaks(1.0)
        ac1.set_breaks(0.0)
        
        i = 0
        while i < 100 :
            ac1.correct_speed(10)
            res = ac1.getSPEED()
            print(f"avion 1 : {res}")   
            # res2 = ac0.getSPEED() 
            # print(f'avion 0 : {res2}')
            
            i +=1
            sleep(0.1)

    
        ac1.set_breaks(1.0)
        ac1.setCTRL([0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        ac0.set_breaks(1.0)
        ac0.setCTRL([0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        
        

        input("Press any key to exit...")


if __name__ == "__main__": 
    main()