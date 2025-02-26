import random
from typing import List, Optional
from node import Node
from connection_gene import ConnectionGene
from connection_history import ConnectionHistory
from globals import next_connection_no

class Genome:
    def __init__(self, inputs: int, outputs: int, clone: bool = False):
        self.genes: List[ConnectionGene] = []
        self.nodes: List[Node] = []
        self.inputs = inputs
        self.outputs = outputs
        self.layers = 2
        self.next_node = 0
        self.network: List[Node] = []

        if not clone:
            # Create input nodes
            for i in range(inputs):
                self.nodes.append(Node(i))
                self.next_node += 1
                self.nodes[-1].layer = 0

            # Create output nodes
            for i in range(outputs):
                self.nodes.append(Node(i + inputs))
                self.nodes[-1].layer = 1
                self.next_node += 1

            # Create bias node
            self.nodes.append(Node(self.next_node))
            self.bias_node = self.next_node
            self.next_node += 1
            self.nodes[-1].layer = 0

    def connect_nodes(self):
        for node in self.nodes:
            node.output_connections.clear()
        
        for gene in self.genes:
            gene.from_node.output_connections.append(gene)

    def feed_forward(self, input_values: List[float]) -> List[float]:
        # Set input values
        for i in range(self.inputs):
            self.nodes[i].output_value = input_values[i]
        
        self.nodes[self.bias_node].output_value = 1

        # Engage all nodes in order
        for node in self.network:
            node.engage()

        # Collect outputs
        outputs = []
        for i in range(self.outputs):
            outputs.append(self.nodes[self.inputs + i].output_value)

        # Reset node inputs for next feed forward
        for node in self.nodes:
            node.input_sum = 0

        return outputs

    def get_innovation_number(self, innovation_history: List[ConnectionHistory], 
                            from_node: Node, to_node: Node) -> int:
        is_new = True
        global next_connection_no

        # Check if this mutation has happened before
        for hist in innovation_history:
            if hist.matches(self, from_node, to_node):
                is_new = False
                return hist.innovation_number

        if is_new:
            # Create new innovation
            inno_numbers = [gene.innovation_no for gene in self.genes]
            innovation_history.append(ConnectionHistory(
                from_node.number, to_node.number, next_connection_no, inno_numbers))
            next_connection_no += 1
            return next_connection_no - 1

    def fully_connected(self) -> bool:
        max_connections = 0
        nodes_in_layers = [0] * self.layers

        # Count nodes in each layer
        for node in self.nodes:
            nodes_in_layers[node.layer] += 1

        # Calculate max possible connections
        for i in range(self.layers - 1):
            nodes_in_front = sum(nodes_in_layers[i+1:])
            max_connections += nodes_in_layers[i] * nodes_in_front

        return len(self.genes) == max_connections

    def mutate(self, innovation_history: List[ConnectionHistory]):
        if not self.genes:
            self.add_connection(innovation_history)
            return

        # 80% chance to mutate weights
        if random.random() < 0.8:
            for gene in self.genes:
                gene.mutate_weight()

        # 5% chance to add connection
        if random.random() < 0.05:
            self.add_connection(innovation_history)

        # 1% chance to add node
        if random.random() < 0.01:
            self.add_node(innovation_history)

    def crossover(self, parent2: 'Genome') -> 'Genome':
        child = Genome(self.inputs, self.outputs, True)
        child.genes = []
        child.nodes = []
        child.layers = self.layers
        child.next_node = self.next_node
        child.bias_node = self.bias_node

        for node in self.nodes:
            child.nodes.append(node.clone())

        for gene in self.genes:
            set_enabled = True
            parent2_gene = self.matching_gene(parent2, gene.innovation_no)

            if parent2_gene != -1:  # Matching gene found
                if not gene.enabled or not parent2.genes[parent2_gene].enabled:
                    if random.random() < 0.75:  # 75% chance to disable
                        set_enabled = False
                        
                # Randomly choose which parent's gene to inherit
                chosen_gene = gene if random.random() < 0.5 else parent2.genes[parent2_gene]
            else:  # Disjoint or excess gene
                chosen_gene = gene
                set_enabled = gene.enabled

            # Clone the chosen gene
            child_gene = chosen_gene.clone(
                child.get_node(chosen_gene.from_node.number),
                child.get_node(chosen_gene.to_node.number))
            child_gene.enabled = set_enabled
            child.genes.append(child_gene)

        child.connect_nodes()
        return child

    def clone(self) -> 'Genome':
        clone = Genome(self.inputs, self.outputs, True)
        
        for node in self.nodes:
            clone.nodes.append(node.clone())

        for gene in self.genes:
            clone.genes.append(gene.clone(
                clone.get_node(gene.from_node.number),
                clone.get_node(gene.to_node.number)))

        clone.layers = self.layers
        clone.next_node = self.next_node
        clone.bias_node = self.bias_node
        clone.connect_nodes()
        return clone

    def get_node(self, node_number: int) -> Optional[Node]:
        """Returns the node with a matching number"""
        for node in self.nodes:
            if node.number == node_number:
                return node
        return None

    def generate_network(self):
        """Sets up the neural network as a list of nodes in order to be engaged"""
        self.connect_nodes()
        self.network.clear()
        
        # For each layer add the nodes in that layer
        # Since layers cannot connect to themselves there is no need to order the nodes within a layer
        for layer in range(self.layers):
            for node in self.nodes:
                if node.layer == layer:
                    self.network.append(node)

    def add_node(self, innovation_history: List[ConnectionHistory]):
        """Mutate the network by adding a new node"""
        # If there are no connections, add one
        if not self.genes:
            self.add_connection(innovation_history)
            return

        # Pick a random connection to split
        random_connection = random.randrange(len(self.genes))
        
        # Don't disconnect bias if possible
        while (self.genes[random_connection].from_node == self.nodes[self.bias_node] 
               and len(self.genes) != 1):
            random_connection = random.randrange(len(self.genes))

        self.genes[random_connection].enabled = False  # Disable it

        # Create new node
        new_node = Node(self.next_node)
        self.nodes.append(new_node)
        self.next_node += 1

        # Add a new connection to the new node with a weight of 1
        connection_innovation_number = self.get_innovation_number(
            innovation_history,
            self.genes[random_connection].from_node,
            new_node
        )
        
        self.genes.append(ConnectionGene(
            self.genes[random_connection].from_node,
            new_node,
            1,
            connection_innovation_number
        ))

        # Add a new connection from the new node with a weight the same as the disabled connection
        connection_innovation_number = self.get_innovation_number(
            innovation_history,
            new_node,
            self.genes[random_connection].to_node
        )
        
        self.genes.append(ConnectionGene(
            new_node,
            self.genes[random_connection].to_node,
            self.genes[random_connection].weight,
            connection_innovation_number
        ))

        # Connect the bias to the new node
        connection_innovation_number = self.get_innovation_number(
            innovation_history,
            self.nodes[self.bias_node],
            new_node
        )
        
        self.genes.append(ConnectionGene(
            self.nodes[self.bias_node],
            new_node,
            0,
            connection_innovation_number
        ))

        # Set layer of new node
        new_node.layer = self.genes[random_connection].from_node.layer + 1

        # If the layer of the new node is equal to the layer of the output node of the old connection
        # then a new layer needs to be created
        if new_node.layer == self.genes[random_connection].to_node.layer:
            # Increment the layer numbers of all layers >= this new node
            for node in self.nodes[:-1]:  # Don't include this newest node
                if node.layer >= new_node.layer:
                    node.layer += 1
            self.layers += 1

        self.connect_nodes()

    def add_connection(self, innovation_history: List[ConnectionHistory]):
        """Adds a connection between 2 nodes that aren't currently connected"""
        if self.fully_connected():
            return

        # Get random nodes
        while True:
            random_node1 = random.randrange(len(self.nodes))
            random_node2 = random.randrange(len(self.nodes))
            
            if not self.random_connection_nodes_are_bad(random_node1, random_node2):
                break

        # Ensure node1 is before node2 in the network
        if self.nodes[random_node1].layer > self.nodes[random_node2].layer:
            random_node1, random_node2 = random_node2, random_node1

        # Add the connection with a random weight
        connection_innovation_number = self.get_innovation_number(
            innovation_history,
            self.nodes[random_node1],
            self.nodes[random_node2]
        )
        
        self.genes.append(ConnectionGene(
            self.nodes[random_node1],
            self.nodes[random_node2],
            random.uniform(-1, 1),
            connection_innovation_number
        ))
        
        self.connect_nodes()

    def random_connection_nodes_are_bad(self, r1: int, r2: int) -> bool:
        """Check if the random nodes selected for a new connection are valid"""
        if self.nodes[r1].layer == self.nodes[r2].layer:
            return True
        if self.nodes[r1].is_connected_to(self.nodes[r2]):
            return True
        return False

    def draw_genome(self, screen, start_x: int, start_y: int, width: int, height: int):
        """Draw the genome as a neural network visualization"""
        import pygame
        
        # Calculate node positions for each layer
        node_positions = []  # [(x, y, node_number)]
        layer_nodes = [[] for _ in range(self.layers)]
        
        # Group nodes by layer
        for node in self.nodes:
            layer_nodes[node.layer].append(node)
        
        # Calculate positions for each node
        for layer in range(self.layers):
            nodes_in_layer = layer_nodes[layer]
            layer_x = start_x + (layer * width) / (self.layers - 1)
            
            for i, node in enumerate(nodes_in_layer):
                layer_y = start_y + ((i + 1) * height) / (len(nodes_in_layer) + 1)
                node_positions.append((layer_x, layer_y, node.number))
                node.draw_pos.x = layer_x
                node.draw_pos.y = layer_y

        # Draw connections
        for gene in self.genes:
            if gene.enabled:
                color = (255, 0, 0) if gene.weight > 0 else (0, 0, 255)  # Red for positive, blue for negative
                weight_thickness = abs(int(gene.weight * 5))  # Thickness based on weight
                
                pygame.draw.line(screen, color,
                               (gene.from_node.draw_pos.x, gene.from_node.draw_pos.y),
                               (gene.to_node.draw_pos.x, gene.to_node.draw_pos.y),
                               max(1, weight_thickness))

        # Draw nodes
        for x, y, node_num in node_positions:
            # Draw node circle
            pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 10)
            pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 10, 1)
            
            # Draw node number
            font = pygame.font.Font(None, 20)
            text = font.render(str(node_num), True, (0, 0, 0))
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)

    def matching_gene(self, parent2: 'Genome', innovation_number: int) -> int:
        """Returns the index of the gene in parent2 with the matching innovation number, or -1 if not found"""
        for i, gene in enumerate(parent2.genes):
            if gene.innovation_no == innovation_number:
                return i
        return -1  # No matching gene found
