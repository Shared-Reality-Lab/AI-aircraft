from Airport import Airport
from PySide6.QtWidgets import QApplication
from Interface import Interface
from WriteXML import WriteXML
import sys

def main():

    icaoCode = input("Please enter the icao code of your airport ")
    airport = Airport(icaoCode)

    app = QApplication(sys.argv)
    airport.readApt()

    xml_class = WriteXML()

    interface = Interface(airport, xml_class)
    interface.show()
        
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()