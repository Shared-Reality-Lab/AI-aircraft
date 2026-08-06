from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QLabel, QPushButton, QListWidgetItem, QFileDialog, QMessageBox
from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from Map import Map
from AircraftItem import AircraftItem
from Aircraft import Aircraft

class Interface(QWidget):

    endTrajectorySignal = Signal(QWidget)

    def __init__(self, apt, xml_class):
        super().__init__()

        self.setWindowTitle("Experiment configuration")
        self.showMaximized()

        self.mapWidget = Map(apt, xml_class)
        self.aircraftList = QListWidget()
        self.aircraftList.currentItemChanged.connect(self.on_list_selection)
        self.aircraftList.itemClicked.connect(self.on_item_clicked)
        self._lastSelectedItem = None

        rightPanel = QVBoxLayout()
        rightPanel.addWidget(QLabel("Aircraft list"))
        rightPanel.addWidget(self.aircraftList)

        self.endTrajectoryButton = QPushButton('OK')
        self.endTrajectoryButton.setCheckable(True)
        self.endTrajectoryButton.setStyleSheet("""QPushButton:checked {
                                        background-color: yellow;
                                        border: 2px solid black;}""")
        self.endTrajectoryButton.clicked.connect(self.end_trajectory)
        rightPanel.addWidget(self.endTrajectoryButton)

        self.addPlaneButton = QPushButton('+')
        self.addPlaneButton.clicked.connect(self.add_plane)
        rightPanel.addWidget(self.addPlaneButton)

        self.hideConflictsButton = QPushButton('Hide conflicts')
        self.hideConflictsButton.clicked.connect(self.hide_conflicts)
        rightPanel.addWidget(self.hideConflictsButton)

        loadLayout = QHBoxLayout()
        loadButton = QPushButton('Load file')
        saveButton = QPushButton('Save')
        saveAsButton = QPushButton('Save as')
        loadLayout.addWidget(loadButton)
        loadLayout.addWidget(saveButton)
        loadLayout.addWidget(saveAsButton)
        rightPanel.addLayout(loadLayout)

        saveButton.clicked.connect(self.save)
        loadButton.clicked.connect(self.loadScenario)
        saveAsButton.clicked.connect(self.save_as)

        layout = QHBoxLayout(self)
        layout.addWidget(self.mapWidget, 6)
        layout.addLayout(rightPanel, 2)

    def end_trajectory(self):
        self.mapWidget.waitingForTrajectoryPoints = False
        self.updateOKButton()

        currentAircraft = self.mapWidget.currentAircraft
        currentAircraftItem = self.getAircraftItem(currentAircraft)

        if currentAircraft not in self.mapWidget.allAircraft and currentAircraft.ID != 0:
            self.mapWidget.allAircraft.append(currentAircraft)
            
            if currentAircraftItem is not None:
                currentAircraftItem.setSpeedChoice()
            
        if currentAircraftItem is not None:
            currentAircraftItem.setSelected(False)
            
        self.setSize()
        self.mapWidget.currentAircraft = Aircraft()
        self.update()

    def add_plane(self):
        if len(self.mapWidget.currentAircraft.trajectory) > 1:
            self.end_trajectory()

        ids = [aircraft.ID for aircraft in self.mapWidget.allAircraft]
        for i in range(1,20):
            if i not in ids:
                firstAvailableId = i
                break

        self.mapWidget.currentAircraft = Aircraft(firstAvailableId)

        card = AircraftItem(self.mapWidget.currentAircraft)
        self.add_item(card)

        self.mapWidget.waitingForTrajectoryPoints = True
        self.updateOKButton()

    def add_item(self, card):
        item = QListWidgetItem()
        item.setSizeHint(card.sizeHint())
        self.aircraftList.setCurrentItem(item)

        card.deleteRequested.connect(lambda w=card, i=item: self.remove_plane(i, w))
        card.intersectionRequested.connect(lambda w=card, i=item: self.add_intersection(i,w))
        card.followRequested.connect(lambda w=card, i=item: self.add_follow(i,w))

        self.aircraftList.addItem(item)
        self.aircraftList.setItemWidget(item, card)

    def remove_plane(self, item, card):
        row = self.aircraftList.row(item)
        self.aircraftList.takeItem(row)

        if self.mapWidget.waitingForTrajectoryPoints:
            self.end_trajectory()
        if card.aircraft in self.mapWidget.allAircraft:
            self.mapWidget.allAircraft.remove(card.aircraft)
        if len(self.mapWidget.allAircraft) <= 1:
            self.mapWidget.currentAircraft = Aircraft() 

        self.update()
        card.deleteLater()

    def add_intersection(self, item, card):
        self.mapWidget.waitingForIntersectionPoint = True
        self.mapWidget.waitingForTrajectoryPoints = False
        self.mapWidget.waitingForFollowPoint = False
        self.aircraftList.setCurrentItem(item)

    def add_follow(self, item, card):
        self.mapWidget.waitingForFollowPoint = True
        self.mapWidget.waitingForTrajectoryPoints = False
        self.mapWidget.waitingForIntersectionPoint = False
        self.aircraftList.setCurrentItem(item)

    def on_list_selection(self, current, previous):
        if previous:
            previousAircraftItem = self.aircraftList.itemWidget(previous)
            if previousAircraftItem is not None:
                previousAircraftItem.setSelected(False)
        if current:
            if len(self.mapWidget.allAircraft) != 0:
                self.end_trajectory()
                currentAircraftItem = self.aircraftList.itemWidget(current)
                self.mapWidget.currentAircraft = currentAircraftItem.aircraft
                currentAircraftItem.setSelected(True)
        self._lastSelectedItem = current
        self.setSize()
        self.update()

    def on_item_clicked(self, item):
        if item is self._lastSelectedItem:
            aircraftItem = self.aircraftList.itemWidget(item)
            if aircraftItem is not None:
                self.mapWidget.currentAircraft = aircraftItem.aircraft
                aircraftItem.setSelected(True)
                self.setSize()
                self.update()

    def updateOKButton(self):
        self.endTrajectoryButton.setChecked(self.mapWidget.waitingForTrajectoryPoints)

    def save(self):
        self.mapWidget.xml_class.write_all(self.mapWidget.allAircraft)

    def save_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save as",
            "",
            "XML files (*.xml)"
        )
        if filename:
            if not filename.endswith(".xml"):
                filename += ".xml"
            self.mapWidget.xml_class.write_all(self.mapWidget.allAircraft, filename)
        return bool(filename)

    def loadScenario(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open scenario", "", "XML files (*.xml);;All files (*)")
        self.mapWidget.xml_class.currentFilename = filename

        if filename:
            self.mapWidget.allAircraft = []
            self.mapWidget.xml_class.currentFilename = filename
            self.mapWidget.read_trajectories()
            for aircraft in self.mapWidget.allAircraft:
                if aircraft.ID != 0:
                    aircraftItem = AircraftItem(aircraft)
                    aircraftItem.setSpeedChoice()
                    aircraftItem.setSelected(False)
                    self.add_item(aircraftItem)


    def closeEvent(self, event: QCloseEvent):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Quit")
        msgBox.setText("Save before exiting ?")

        overwriteBtn = msgBox.addButton("Save", QMessageBox.AcceptRole)
        saveAsBtn = msgBox.addButton("Save as", QMessageBox.ActionRole)
        discardBtn = msgBox.addButton("Discard", QMessageBox.DestructiveRole)
        cancelBtn = msgBox.addButton("Cancel", QMessageBox.RejectRole)

        msgBox.setDefaultButton(overwriteBtn)
        msgBox.exec_()
        clicked = msgBox.clickedButton()

        if clicked == overwriteBtn:
            self.save()
            event.accept()
        elif clicked == saveAsBtn:
            saved = self.save_as()
            if saved:
                event.accept()
            else:
                event.ignore()
        elif clicked == discardBtn:
            event.accept()
        else: 
            event.ignore()

    def getAircraftItem(self, aircraft):
        for i in range(self.aircraftList.count()):
            item = self.aircraftList.item(i)
            widget = self.aircraftList.itemWidget(item)

            if widget.aircraft.ID == aircraft.ID:
                return widget
        return None

    def setSize(self):
        for i in range(self.aircraftList.count()):
            item = self.aircraftList.item(i)
            widget = self.aircraftList.itemWidget(item)
            if widget is not None:
                item.setSizeHint(widget.sizeHint())

    def hide_conflicts(self):
        isHidden = self.mapWidget.hideConflicts
        if isHidden:
            self.mapWidget.hideConflicts = False
            self.hideConflictsButton.setText("Hide conflicts")
        else:
            self.mapWidget.hideConflicts = True
            self.hideConflictsButton.setText("Show conflicts")