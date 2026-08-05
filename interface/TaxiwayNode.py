class TaxiwayNode:

    def __init__(self, idNode, pos):
        self.id = idNode
        self.pos = pos

    def __repr__(self):
        return f"Node {self.id} : {self.pos}"