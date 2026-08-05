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

        # self.setStyleSheet("""QFrame {
        #                         background-color: white;
        #                         border: 2px solid #999;
        #                         border-radius: 8px;}

        #                     QPushButton {
        #                         padding: 4px;}

        #                     QLabel {
        #                         font-size: 12pt;
        #                         font-weight: bold;}
        #                     """)

        self.formWidget = None
        self.speedLayout = None
        # self.editsSpeed = []

    def ask_delete(self):
        self.deleteRequested.emit(self)

    def ask_intersection(self):
        self.intersectionRequested.emit(self)

    def ask_follow(self):
        self.followRequested.emit(self)

    def setSelected(self, isSelected):
        if len(self.aircraft.trajectory) >=2 and self.aircraft.ID != 0:
            self.formWidget.show() if isSelected else self.formWidget.hide()
            self.update()

    def setSpeedChoice(self):
        trajectory = self.aircraft.trajectory
        if len(trajectory) >= 2:
            self.formWidget = QWidget()
            self.speedLayout = QFormLayout(self.formWidget)
            for segmentID in range(1, len(trajectory)):
                edit = QLineEdit()
                edit.setPlaceholderText("in knots")
                edit.setText("10")
                label = f"Speed {segmentID}"
                self.speedLayout.addRow(label, edit)

                self.aircraft.segmentSpeed[segmentID] = "10"
                edit.textChanged.connect(lambda speed, index=segmentID: self.updateSegmentValue(speed, index))
            self.mainLayout.addWidget(self.formWidget)

        self.update()

    def updateSegmentValue(self, speed, index):
        if self.aircraft.ID != 0:
            self.aircraft.segmentSpeed[index] = speed

    def __repr__(self):
        return f'Aircraft Item {self.aircraft.ID}'
