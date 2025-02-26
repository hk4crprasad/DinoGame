import math
import pygame
from typing import List

class Node:
    def __init__(self, number: int):
        self.number = number
        self.input_sum = 0
        self.output_value = 0
        self.output_connections = []
        self.layer = 0
        self.draw_pos = pygame.math.Vector2()

    def engage(self):
        if self.layer != 0:  # No sigmoid for inputs and bias
            self.output_value = self.sigmoid(self.input_sum)

        for conn in self.output_connections:
            if conn.enabled:
                conn.to_node.input_sum += conn.weight * self.output_value

    def sigmoid(self, x: float) -> float:
        # Clamp the input to avoid overflow
        x = max(-60, min(60, x))
        return 1 / (1 + math.exp(-4.9 * x))

    def is_connected_to(self, node) -> bool:
        if node.layer == self.layer:
            return False

        if node.layer < self.layer:
            return any(conn.to_node == self for conn in node.output_connections)
        else:
            return any(conn.to_node == node for conn in self.output_connections)

    def clone(self):
        clone_node = Node(self.number)
        clone_node.layer = self.layer
        return clone_node
