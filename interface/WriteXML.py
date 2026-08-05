import xml.etree.ElementTree as ET
from xml.dom import minidom
from geopy.distance import distance

class WriteXML:

    def __init__(self):
        self.conflictsRoot = ET.Element('aircraft')
        self.trajectoriesRoot = ET.Element('trajectories')
        self.finishedRoot = ET.Element('aircraft')
        self.currentFilename = "trajTEST.xml"

    def intersection_type(self, pos, offset_value):
        root = self.conflictsRoot
        ac4 = ET.SubElement(root, 'ac')
        ac4.set('id', '4')
        type4 = ET.SubElement(ac4, 'conflict')
        type4.set('type', 'intersection')
        location = ET.SubElement(type4, 'location')
        location.set('lat', str(pos[0]))
        location.set('lon', str(pos[1]))
        offset = ET.SubElement(type4, 'offset')
        offset.set('dist', str(offset_value))
        self.write(root, "simulation.xml")

    def write(self, root, filename):
        xml_data = ET.tostring(root)
        dom = minidom.parseString(xml_data)
        with open(filename, "w", encoding="utf-8") as xml_file:
            xml_file.write(dom.toprettyxml(indent="  "))
            xml_file.flush()

    def write_trajectory(self, aircraft):
        root = self.trajectoriesRoot
        ac = ET.SubElement(root, 'trajectory')
        ac.set('ac-id', str(aircraft.ID))
        waypoints = ET.SubElement(ac, 'waypoints')
        for point in aircraft.trajectory:
            waypoint = ET.SubElement(waypoints, 'waypoint')
            waypoint.set('lat', str(point.x()))
            waypoint.set('lon', str(point.y()))
            waypoint.set('speed', '5')

        self.write(root, "trajTEST.xml")

    def write_all(self, allAircraft, filename = None):
        if filename is not None :
            self.currentFilename = filename
        self.finishedRoot = ET.Element('aircraft')
        root = self.finishedRoot

        for aircraft in allAircraft:

            ac = ET.SubElement(root, 'ac')
            ac.set('id', str(aircraft.ID))
            waypoints = ET.SubElement(ac, 'waypoints')
            indexSpeed = 0
            for point in aircraft.trajectory:
                waypoint = ET.SubElement(waypoints, 'waypoint')
                waypoint.set('lat', str(point[0]))
                waypoint.set('lon', str(point[1]))
                if aircraft.ID != 0:
                    if indexSpeed != 0:
                        waypoint.set('speed', aircraft.segmentSpeed[indexSpeed])
                    else:
                        waypoint.set('speed', "-99")
                    indexSpeed += 1
                else:
                    waypoint.set('speed', "10")

            for conflict in aircraft.conflicts:
                position = conflict[0]
                offset_value = conflict[1]

                conflictXML = ET.SubElement(ac, 'conflict')
                conflictXML.set('type', 'intersection')
                location = ET.SubElement(conflictXML, 'location')
                location.set('lat', str(position[0]))
                location.set('lon', str(position[1]))
                offset = ET.SubElement(conflictXML, 'offset')
                offset.set('dist', str(offset_value))
            
            leadFollowDico = aircraft.follow
            if leadFollowDico['offset'] != -999:
                startPosition = leadFollowDico['startFollowPosition']
                offset_value = leadFollowDico['offset']
                reducedSpeed = leadFollowDico['reducedSpeed']
                endPosition = leadFollowDico['endFollowPosition']
                slowDistance = distance(startPosition, endPosition).meters

                conflictXML = ET.SubElement(ac, 'conflict')
                conflictXML.set('type', 'lead-follow')
                location = ET.SubElement(conflictXML, 'location')
                location.set('lat', str(startPosition[0]))
                location.set('lon', str(startPosition[1]))
                offset = ET.SubElement(conflictXML, 'offset')
                offset.set('dist', str(offset_value))
                slowDown = ET.SubElement(conflictXML, 'slow-down')
                slowDown.set('dist', str(int(slowDistance)))
                slowDown.set('reduc', str(reducedSpeed))

                endLocation = ET.SubElement(conflictXML, 'end-position')
                endLocation.set('lat', str(endPosition[0]))
                endLocation.set('lon', str(endPosition[1]))
        print({self.currentFilename})
        self.write(root, self.currentFilename)
        