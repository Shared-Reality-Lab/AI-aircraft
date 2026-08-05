from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class ScenarioDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Scenario choice")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Please choose a scenario :"))

        self.combo = QComboBox()
        self.combo.addItems(["Scenario 1", "Scenario 2"])
        layout.addWidget(self.combo)

        bouton = QPushButton("Validate")
        bouton.clicked.connect(self.accept)
        layout.addWidget(bouton)

    def getScenario(self):
        pass
        # text_input = self.combo.currentText()
        # i = int(text_input[-1])
        # return f"scenarios\sc{i}.xml"
    
