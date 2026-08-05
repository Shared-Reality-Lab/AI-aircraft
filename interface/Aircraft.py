class Aircraft:

    def __init__(self, ID=0):
        self.ID = ID
        self.trajectory = []
        self.segmentSpeed = {}
        self.conflicts = []
        self.follow = {'startFollowPosition':(0,0), 'endFollowPosition':(0,0), 'offset':-999, 'reducedSpeed':-999}

    def __repr__(self):
        return f'Aircraft {self.ID}'