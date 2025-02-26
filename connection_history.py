from typing import List
#from genome import Genome
from node import Node

class ConnectionHistory:
    def __init__(self, from_node: int, to_node: int, innovation_no: int, innovation_numbers: List[int]):
        self.from_node = from_node
        self.to_node = to_node
        self.innovation_number = innovation_no
        self.innovation_numbers = innovation_numbers.copy()

    def matches(self, genome: 'Genome', from_node: Node, to_node: Node) -> bool:
        if len(genome.genes) != len(self.innovation_numbers):
            return False
            
        if from_node.number == self.from_node and to_node.number == self.to_node:
            for gene in genome.genes:
                if gene.innovation_no not in self.innovation_numbers:
                    return False
            return True
            
        return False
