class Runway:

    def __init__(self, width, surfaceCode, side1, side2):
        self.width = width
        self.surfaceCode = surfaceCode
        self.side1 = side1
        self.side2 = side2

    def __repr__(self):
        return f"Runway({self.side1}, {self.side2})"