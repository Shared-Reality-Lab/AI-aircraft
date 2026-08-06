from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFormLayout, QLineEdit, QComboBox
from PySide6.QtCore import Qt, Signal

class AircraftItem(QFrame):

    deleteRequested = Signal(QWidget)
    intersectionRequested = Signal(QWidget)
    followRequested = Signal(QWidget)

    def __init__(self, aircraft):
        super().__init__()

        self.aircraft = aircraft

        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)

        title = QLabel(f"Aircraft {self.aircraft.ID}")
        title.setStyleSheet("font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.deleteButton = QPushButton("Delete")
        self.intersectionButton = QPushButton("Intersection")
        self.followButton = QPushButton("Follow")

        self.deleteButton.clicked.connect(self.ask_delete)
        self.intersectionButton.clicked.connect(self.ask_intersection)
        self.followButton.clicked.connect(self.ask_follow)

        buttons = QHBoxLayout()
        buttons.addWidget(self.deleteButton)
        buttons.addWidget(self.intersectionButton)
        buttons.addWidget(self.followButton)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(title)
        self.mainLayout.addLayout(buttons)

        self.formWidget = None
        self.speedLayout = None
        self.conflictsWidget = None
        self.speedLabel = QLabel("Speed")
        self.speedLabel.setStyleSheet("font-weight: bold;")
        self.conflictID = 1

    def ask_delete(self):
        self.deleteRequested.emit(self)

    def ask_intersection(self):
        self.intersectionRequested.emit(self)

    def ask_follow(self):
        self.followRequested.emit(self)

    def setSelected(self, isSelected):
        if len(self.aircraft.trajectory) >=2 and self.aircraft.ID != 0:
            if isSelected:
                self.speedLabel.show()
                self.formWidget.show()
                self.updateConflictsInformation()
            else:
                self.speedLabel.hide()
                self.formWidget.hide()
                if self.conflictsWidget is not None:
                    self.conflictsWidget.hide()

            self.update()

    def setSpeedChoice(self):
        trajectory = self.aircraft.trajectory
        
        if len(trajectory) >= 2:
            self.formWidget = QWidget()
            self.speedLayout = QFormLayout(self.formWidget)
            self.speedLayout.setContentsMargins(0, 0, 0, 0)

            for segmentID in range(1, len(trajectory)):
                edit = QLineEdit()
                edit.setPlaceholderText("in knots")
                edit.setText("10")
                label = f"Segment {segmentID}"
                self.speedLayout.addRow(label, edit)
                self.aircraft.segmentSpeed[segmentID] = "10"
                edit.textChanged.connect(lambda speed, index=segmentID: self.updateSegmentValue(speed, index))

            self.mainLayout.addWidget(self.speedLabel)
            self.mainLayout.addWidget(self.formWidget)
        self.update()

    def intersectionInformation(self, conflict):
        text = f"Conflict {self.conflictID}: Intersection | Offset: {conflict[1]}m"
        return text

    def followInformation(self):
        follow = self.aircraft.follow
        text = f"Conflict {self.conflictID}: Lead-follow | Offset: {follow['offset']}m | Reduced speed: {follow['reducedSpeed']}kt"
        return text

    def updateConflictsInformation(self):
        if self.conflictsWidget is not None:
            self.mainLayout.removeWidget(self.conflictsWidget)
            self.conflictsWidget.deleteLater()
            self.conflictsWidget = None
        
        if len(self.aircraft.intersections) == 0 and self.aircraft.follow['offset'] == -999:
            return

        self.conflictsWidget = QWidget()
        conflictsLayout = QVBoxLayout(self.conflictsWidget)
        conflictsLayout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Conflicts:")
        header.setStyleSheet("font-weight: bold;")
        conflictsLayout.addWidget(header)

        if len(self.aircraft.conflicts) != 0:
            for conflict in self.aircraft.intersections:
                text = self.intersectionInformation(conflict)
                conflictsLayout.addWidget(QLabel(text))

                self.conflictID += 1

        if self.aircraft.follow['offset'] != -999:
            text = self.followInformation()
            conflictsLayout.addWidget(QLabel(text))
            
            self.conflictID += 1

        self.mainLayout.addWidget(self.conflictsWidget)
        self.conflictsWidget.show()

    def updateSegmentValue(self, speed, index):
        if self.aircraft.ID != 0:
            self.aircraft.segmentSpeed[index] = speed

    def __repr__(self):
        return f'Aircraft Item {self.aircraft.ID}'