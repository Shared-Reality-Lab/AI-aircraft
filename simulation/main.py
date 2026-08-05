from time import sleep
import sys
from PySide6.QtWidgets import QApplication, QFileDialog
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
        table_override_planepath = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        client.sendDREF(dref_override_planepath, table_override_planepath)

        app = QApplication(sys.argv)
        scenario, _ = QFileDialog.getOpenFileName(None, "Open scenario", "", "XML files (*.xml);;All files (*)")

        if scenario:

             # SIMULATION
            sim = Simulation(client, scenario)

            aircraft_list, xml_list, test_follow, test_intersec = sim.Initialize()
            print('Starting main loop...')
            sleep(2)
            sim.main_loop(aircraft_list, xml_list, test_follow, test_intersec)
            
            input("End of simulation, press any key to exit...")
        
        else :
            print("Please choose your scenario")
            sys.exit()

        sys.exit(app.exec())


if __name__ == "__main__": 
    main()