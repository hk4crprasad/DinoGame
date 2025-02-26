from typing import List, Optional
import random
from player import Player
from genome import Genome

class Species:
    def __init__(self, player: Optional[Player] = None):
        self.players: List[Player] = []
        self.best_fitness = 0
        self.staleness = 0  # how many generations the species has gone without improvement
        self.champ: Optional[Player] = None
        self.average_fitness = 0
        
        if player:
            self.players.append(player)
            self.best_fitness = player.fitness
            self.champ = player.clone()

    def same_species(self, genome: Genome) -> bool:
        excess_coefficient = 1.0
        w_diff_coefficient = 0.5
        compatibility_threshold = 3
        
        if len(self.players) == 0:
            return False
            
        compatibility_distance = self.get_compatibility_distance(genome, self.players[0].brain)
        return compatibility_distance <= compatibility_threshold

    def get_compatibility_distance(self, genome1: Genome, genome2: Genome) -> float:
        """Calculate how similar two genomes are"""
        excess_coefficient = 1.0
        weight_diff_coefficient = 0.5
        
        if len(genome1.genes) == 0 or len(genome2.genes) == 0:
            return 0
            
        # Get innovation numbers for both genomes
        innovation_numbers1 = {g.innovation_no for g in genome1.genes}
        innovation_numbers2 = {g.innovation_no for g in genome2.genes}
        
        # Count excess and disjoint genes
        max_innovation1 = max(innovation_numbers1)
        max_innovation2 = max(innovation_numbers2)
        
        # Count disjoint and excess genes
        disjoint_excess = 0
        for inno in innovation_numbers1:
            if inno > max_innovation2 or inno not in innovation_numbers2:
                disjoint_excess += 1
                
        for inno in innovation_numbers2:
            if inno > max_innovation1 or inno not in innovation_numbers1:
                disjoint_excess += 1
        
        # Calculate average weight difference for matching genes
        weight_diff = 0
        matching_genes = 0
        
        for gene1 in genome1.genes:
            for gene2 in genome2.genes:
                if gene1.innovation_no == gene2.innovation_no:
                    matching_genes += 1
                    weight_diff += abs(gene1.weight - gene2.weight)
                    break
                    
        if matching_genes == 0:
            weight_diff = 100  # If no matching genes, make them very different
        else:
            weight_diff /= matching_genes
            
        # Calculate final compatibility distance
        n = max(len(genome1.genes), len(genome2.genes))
        if n < 20:  # Small genomes should be compatible
            n = 1
            
        compatibility = (excess_coefficient * disjoint_excess / n) + (weight_diff_coefficient * weight_diff)
        return compatibility

    def add_to_species(self, player: Player):
        self.players.append(player)

    def sort_species(self):
        self.players.sort(key=lambda x: x.fitness, reverse=True)
        
        if len(self.players) == 0:
            return
            
        if self.players[0].fitness > self.best_fitness:
            self.staleness = 0
            self.best_fitness = self.players[0].fitness
            self.champ = self.players[0].clone()
        else:
            self.staleness += 1

    def give_me_baby(self, innovation_history: List) -> Player:
        """Create a new baby from this species"""
        # Ensure we have players to breed from
        if not self.players:
            raise ValueError("Cannot create baby from empty species")
            
        if len(self.players) == 1:
            # If only one player, clone it
            baby = self.players[0].clone()
        elif random.random() < 0.25:  # 25% of the time clone the best player
            baby = self.players[0].clone()
        else:
            # Select parents from the better half of the species
            available_parents = self.players[:max(1, len(self.players)//2)]
            parent1 = random.choice(available_parents)
            parent2 = random.choice(available_parents)
            
            if parent1.fitness > parent2.fitness:
                baby = parent1.crossover(parent2)
            else:
                baby = parent2.crossover(parent1)
                
        baby.brain.mutate(innovation_history)
        return baby

    def fitness_sharing(self):
        for p in self.players:
            p.fitness /= len(self.players)

    def set_average(self):
        """Calculate the average fitness of the species"""
        if not self.players:
            self.average_fitness = 0
            return
            
        sum_fitness = sum(player.fitness for player in self.players)
        self.average_fitness = sum_fitness / len(self.players)

    def cull(self):
        """Kill the bottom half of the species"""
        if len(self.players) > 2:
            self.players = self.players[:len(self.players)//2]

