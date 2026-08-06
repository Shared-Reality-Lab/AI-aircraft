from PySide6.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit
from PySide6.QtCore import QPoint, Qt, QPointF, QRect, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QWheelEvent, QPalette, QPixmap, QBrush
from CoordConverter import utm_to_screen, screen_to_utm, utm_to_geo, geo_to_utm, geo_to_screen, screen_to_geo #, zoom_point , inv_zoom_point, 
import xml.etree.ElementTree as ET
from Aircraft import Aircraft
from AircraftItem import AircraftItem

class Map(QWidget):

    def __init__(self, apt, xml_class):

        super().__init__()

        self.setStyleSheet("background: lightgrey;")

        self.center = self.rect().center()
        self.airport = apt
        self.zoom = 0.1
        self.offset = QPointF()
        self.last_pos = QPointF(0,0)

        self.xml_class = xml_class

        self.waitingForIntersectionPoint = False
        self.waitingForFollowPoint = False
        self.waitingForEndFollow = False
        self.waitingForTrajectoryPoints = False
        self.hideConflicts = False

        self.allAircraft = []
        self.currentAircraft = Aircraft()
    
    def get_screen_size(self):
        return self.width(), self.height()

    def draw_start(self, position, acID, painter):
        icon = QPixmap(r"images\ai_position.png")
        iconSize = 30 + 5*self.zoom
        rect = QRect(position.x() - iconSize/2, position.y() - iconSize/2, iconSize, iconSize)
        painter.drawPixmap(rect, icon)

        if acID != 0:
            painter.setPen(Qt.white)
            painter.drawText(rect, Qt.AlignCenter, str(acID))
            
        pen = QPen(Qt.black)
        pen.setWidth(4 + 5*self.zoom)
        painter.setPen(pen)

    def draw_intersection(self, position, painter):
        screen_pos = geo_to_screen(position, self.zoom, self.offset, self.airport.center, self.get_screen_size())
        pen = QPen(Qt.red)
        pen.setWidth(10 + 5*self.zoom)
        painter.setPen(pen)
        painter.drawEllipse(screen_pos, 3, 3)

    def draw_follow(self, position, painter):
        screen_pos = geo_to_screen(position, self.zoom, self.offset, self.airport.center, self.get_screen_size())
        pen = QPen(Qt.darkRed)
        pen.setWidth(7 + 5*self.zoom)
        painter.setPen(pen)
        painter.drawEllipse(screen_pos, 3, 3)

    def draw_node(self, position, painter):
        pen = QPen(Qt.black)
        pen.setWidth(2 + 5*self.zoom)
        painter.setPen(pen)
        painter.drawEllipse(position, 3, 3)
        
        pen = QPen(Qt.darkYellow)
        pen.setWidth(4 + 5*self.zoom)
        painter.setPen(pen)

    def paintEvent(self, event):

        painter = QPainter(self)
        pen = QPen(Qt.darkBlue)
        pen.setWidth(13 + 7*self.zoom)
        painter.setPen(pen)

        for runway in self.airport.runways :
            ext1 = utm_to_screen(runway.side1[1], self.zoom, self.offset, self.airport.center, self.get_screen_size())
            ext1 = QPointF(ext1[0],ext1[1])
            ext2 = utm_to_screen(runway.side2[1], self.zoom, self.offset, self.airport.center, self.get_screen_size())
            ext2 = QPointF(ext2[0], ext2[1])
            painter.drawLine(ext1, ext2)
        
        pen.setWidth(2+ 5*self.zoom)
        painter.setPen(pen)

        for taxiSegment in self.airport.taxiSegments :
            ext1 = utm_to_screen(taxiSegment.node1.pos, self.zoom, self.offset, self.airport.center, self.get_screen_size())
            ext1 = QPointF(ext1[0],ext1[1])
            ext2 = utm_to_screen(taxiSegment.node2.pos, self.zoom, self.offset, self.airport.center, self.get_screen_size())
            ext2 = QPointF(ext2[0], ext2[1])
            painter.drawLine(ext1, ext2)
        
        pen.setWidth(4 + 5*self.zoom)
        painter.setPen(pen)
        
        if self.currentAircraft.ID != 0:
            currentTrajectory = self.currentAircraft.trajectory
            if len(currentTrajectory) != 0 :
                start = currentTrajectory[0]
                ext1 = geo_to_screen(start, self.zoom, self.offset, self.airport.center, self.get_screen_size())
                start = ext1

                self.draw_start(start, self.currentAircraft.ID, painter)

                if len(currentTrajectory)>=2:

                    for waypoint in currentTrajectory[1:]:
                        # point = waypoint
                        ext2 = geo_to_screen(waypoint, self.zoom, self.offset, self.airport.center, self.get_screen_size())
                        painter.drawLine(ext1, ext2)
                        ext1 = ext2
                
                self.draw_start(start, self.currentAircraft.ID, painter)
            
            currentConflicts = self.currentAircraft.intersections
            if len(currentConflicts) != 0:
                for conflict in currentConflicts:
                    geo_pos = conflict[0]
                    self.draw_intersection(geo_pos, painter)

            currentFollow = self.currentAircraft.follow
            if currentFollow['startFollowPosition'] != (0,0):
                self.draw_follow(currentFollow['startFollowPosition'], painter)

                if currentFollow['endFollowPosition'] != (0,0):
                    self.draw_follow(currentFollow['endFollowPosition'], painter)

        for aircraft in self.allAircraft:
            trajectory = aircraft.trajectory

            if aircraft.ID == 0:
                pen = QPen(Qt.red)
                pen.setWidth(4)
            elif aircraft is not self.currentAircraft :
                pen = QPen(Qt.black)
                pen.setWidth(4 + 5*self.zoom)
            else:
                pen = QPen(Qt.darkYellow)
                pen.setWidth(4 + 5*self.zoom)
            painter.setPen(pen)

            if aircraft.ID == 0:
                start = trajectory[0]
                ext1 = geo_to_screen(start, self.zoom, self.offset, self.airport.center, self.get_screen_size())
                start = ext1
                for waypoint in trajectory[1:]:
                    ext2 = geo_to_screen(waypoint, self.zoom, self.offset, self.airport.center, self.get_screen_size())
                    painter.drawLine(ext1, ext2)
                    ext1 = ext2
                icon = QPixmap(r"images\user_position.jpg")
                iconSize = 30 + 5*self.zoom
                painter.drawPixmap(start.x()-iconSize/2, start.y()-iconSize/2, iconSize, iconSize, icon)

            else:

                if len(trajectory)>=2:
                    start = trajectory[0]
                    ext1 = geo_to_screen(start, self.zoom, self.offset, self.airport.center, self.get_screen_size())
                    start = ext1

                    for waypoint in trajectory[1:]:
                        ext2 = geo_to_screen(waypoint, self.zoom, self.offset, self.airport.center, self.get_screen_size())
                        painter.drawLine(ext1, ext2)
                        if aircraft is self.currentAircraft:
                            self.draw_node(ext1, painter)

                        ext1 = ext2
                    self.draw_node(ext2, painter)
                    self.draw_start(start, aircraft.ID, painter)

                if not self.hideConflicts:

                    for conflict in aircraft.intersections:
                        geo_pos = conflict[0]
                        self.draw_intersection(geo_pos, painter)

                    follow = aircraft.follow
                    if follow['startFollowPosition'] != (0,0):
                        self.draw_follow(follow['startFollowPosition'], painter)

                        if follow['endFollowPosition'] != (0,0):
                            self.draw_follow(follow['endFollowPosition'], painter)

        painter.end()

    def wheelEvent(self, event: QWheelEvent):

        mousePos = event.position()
        mapPos = screen_to_utm(mousePos, self.zoom, self.offset, self.airport.center, self.get_screen_size())
        mapPos = (mapPos.x(), mapPos.y())
        
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom *= 0.9
        self.zoom = max(0.01, min(self.zoom, 10))

        newMousePos = utm_to_screen(mapPos, self.zoom, self.offset, self.airport.center, self.get_screen_size())
        newMousePos = QPointF(newMousePos[0], newMousePos[1])
        delta = mousePos - newMousePos
        self.offset += delta

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:

            if self.waitingForIntersectionPoint or self.waitingForFollowPoint or self.waitingForEndFollow:
                screen_pos = event.pos()
                geo_pos = screen_to_geo(screen_pos, self.zoom, self.offset, self.airport.center, self.get_screen_size(), self.airport.zoneNumber, self.airport.zoneLetter)

                self.edit = QLineEdit(self)
                self.edit.setGeometry(event.x(), event.y(), 40, 25)
                self.edit.setToolTip("Please enter the offset in meters")
                self.edit.show()
                self.edit.setFocus()
                self.edit.returnPressed.connect(lambda: self.validate(geo_pos))
                        
            if self.waitingForTrajectoryPoints:
                screen_pos = event.pos()
                geo_pos = screen_to_geo(screen_pos, self.zoom, self.offset, self.airport.center, self.get_screen_size(), self.airport.zoneNumber, self.airport.zoneLetter)
                waypoint = geo_pos
                self.currentAircraft.trajectory.append(waypoint)
                self.update()

        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()

    def validate(self, geo_pos):
        for aircraft in self.allAircraft:
            if aircraft.ID == self.currentAircraft.ID:
                if self.waitingForEndFollow:
                    reducedSpeed = int(self.edit.text())
                    aircraft.follow['endFollowPosition'] = geo_pos
                    aircraft.follow['reducedSpeed'] = reducedSpeed
                    self.waitingForEndFollow = False

                offset = int(self.edit.text())
                if self.waitingForFollowPoint:
                    aircraft.follow['startFollowPosition'] = geo_pos
                    aircraft.follow['offset'] = offset
                    self.waitingForFollowPoint = False
                    self.waitingForEndFollow = True

                if self.waitingForIntersectionPoint:
                    aircraft.intersections.append((geo_pos, offset))
                    self.waitingForIntersectionPoint = False                

        self.edit.hide()
        self.edit.deleteLater()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_pos
            self.offset += delta
            self.last_pos = event.pos()
            self.update()

    def read_trajectories(self):
        scenario = self.xml_class.currentFilename
        tree = ET.parse(scenario)
        root = tree.getroot()

        for aircraft in root.findall('ac'):
            
            # Get aircraft ID
            ac_id = int(aircraft.get('id'))
            currentAircraft = Aircraft(ac_id)
            
            # Analyze waypoints the aircraft will have to go to
            waypoints = aircraft.find('waypoints')
            
            # Go through every waypoint coordinates and store them in the local list
            if waypoints is not None:
                for waypoint in waypoints.findall('waypoint'):
                    lat = float(waypoint.get('lat'))
                    lon = float(waypoint.get('lon'))
                    speed = float(waypoint.get('speed')) #* 0.5144 #Conversion noeuds -> m/s

                    currentAircraft.trajectory.append((lat, lon))
                    currentAircraft.segmentSpeed[ac_id] = speed

            for conflict in aircraft.findall('conflict'):
                if conflict is not None:
                    typeConflict = conflict.get('type')
                    location = conflict.find('location')
                    offset = conflict.find('offset')
                    
                    lat = float(location.get('lat'))
                    lon = float(location.get('lon'))
                    offsetDist = float(offset.get('dist'))

                    if typeConflict == "lead-follow":
                        slowDown = conflict.find('slow-down')

                        endPosition = conflict.find('end-position')
                        endLat = float(endPosition.get('lat'))
                        endLon = float(endPosition.get('lon'))
                        reducedSpeed = int(slowDown.get('reduc'))

                        currentAircraft.follow['startFollowPosition'] = (lat, lon)
                        currentAircraft.follow['offset'] = offsetDist
                        currentAircraft.follow['reducedSpeed'] = reducedSpeed
                        currentAircraft.follow['endFollowPosition'] = (endLat, endLon)

                    else:
                        currentAircraft.intersections.append(((lat, lon), offsetDist))
                        
            self.allAircraft.append(currentAircraft)
