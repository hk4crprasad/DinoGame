import random
from node import Node

class ConnectionGene:
    def __init__(self, from_node: Node, to_node: Node, weight: float, innovation_no: int):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.enabled = True
        self.innovation_no = innovation_no

    def mutate_weight(self):
        if random.random() < 0.1:  # 10% chance to completely change weight
            self.weight = random.uniform(-1, 1)
        else:  # Otherwise slightly change it
            self.weight += random.gauss(0, 1)/50
            self.weight = max(-1, min(1, self.weight))  # Clamp between -1 and 1

    def clone(self, from_node: Node, to_node: Node):
        clone = ConnectionGene(from_node, to_node, self.weight, self.innovation_no)
        clone.enabled = self.enabled
        return clone
