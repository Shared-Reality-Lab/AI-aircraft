from CoordConverter import geo_to_utm, get_geo_zone
from Runway import Runway
from TaxiwayNode import TaxiwayNode
from TaxiwaySegment import TaxiwaySegment
from pathlib import Path

class Airport:

    # CONSTRUCTOR ****************************************
    def __init__(self, icaoCode):
        self.icaoCode = icaoCode
        self.elevASM = 0
        self.runways = []
        self.taxiNodes = {}
        self.taxiSegments = []
        self.center = [0,0]
        self.zoneNumber = 0
        self.zoneLetter = ''

    def readApt(self):

        isFound = False # to know if we found airport
        isEmpty = False
        isFinished = False
        print("Looking for airport " + self.icaoCode + "...")

        pathToAptData = Path(__file__).parent.parent/'data'/'apt.dat'
        with open(pathToAptData, 'r', encoding="latin-1") as aptFile :

            for line in aptFile :
                line = line.split()
                isEmpty = (len(line) == 0)
                if not isEmpty and not isFinished :
                    
                    if isFound :
                        elmt0 = line[0]

                        if elmt0 == "1302":
                            if line[1] == "datum_lat" :
                                center_lat = float(line[2])
                            elif line[1] == "datum_lon" :
                                center_lon = float(line[2])
                                utm_pos = geo_to_utm(center_lat, center_lon)
                                self.center[0] = utm_pos[0]
                                self.center[1] = utm_pos[1]

                                geo_zone = get_geo_zone(center_lat, center_lon)
                                self.zoneNumber = geo_zone[0]
                                self.zoneLetter = geo_zone[1]


                        elif elmt0 == "100":
                            width = float(line[1])
                            surfaceCode = int(line[2])

                            runwayNumber1 = line[8] #str
                            lat1 = float(line[9])
                            lon1 = float(line[10])

                            runwayNumber2 = line[17]
                            lat2 = float(line[18])
                            lon2 = float(line[19])

                            side1 = [runwayNumber1, geo_to_utm(lat1, lon1)]
                            side2 = [runwayNumber2, geo_to_utm(lat2, lon2)]

                            runway = Runway(width, surfaceCode, side1, side2)
                            self.runways.append(runway)

                        elif elmt0 == "1201":
                            idNode = int(line[4])
                            lat = float(line[1])
                            lon = float(line[2])
                            pos = geo_to_utm(lat, lon)
                            taxiwayNode = TaxiwayNode(idNode, pos)
                            self.taxiNodes[idNode] = taxiwayNode

                        elif elmt0 == "1202":
                            idNode1 = int(line[1])
                            node1 = self.taxiNodes[idNode1]
                            idNode2 = int(line[2])
                            node2 = self.taxiNodes[idNode2]

                            taxiwaySegment = TaxiwaySegment(node1, node2)
                            self.taxiSegments.append(taxiwaySegment)
                        
                        elif elmt0 == "1":
                            isFinished = True

                    else :
                        if line[0] == "1" and self.icaoCode.upper() == line[4]:
                            isFound = True
                            self.elevASM = line[1]
            if not isFound :
                print("Airport not found")
