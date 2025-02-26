from typing import List
import random
from player import Player
from species import Species
from connection_history import ConnectionHistory
from globals import next_connection_no
from game_state import state

class Population:
    def __init__(self, size: int):
        self.pop: List[Player] = []
        self.best_player = None
        self.best_score = 0
        self.gen = 0
        self.innovation_history: List[ConnectionHistory] = []
        self.gen_players: List[Player] = []
        self.species: List[Species] = []
        
        self.mass_extinction_event = False
        self.new_stage = False
        self.population_life = 0
        
        # Initialize population
        for _ in range(size):
            player = Player()
            player.brain.generate_network()
            player.brain.mutate(self.innovation_history)
            self.pop.append(player)

    def update_alive(self):
        """Update all alive players"""
        from game_state import state
        game = state.game
        
        self.population_life += 1
        for player in self.pop:
            if not player.dead:
                # First look at environment
                player.look(game.obstacles, game.birds, game.speed)
                # Then think and make decisions
                player.think()
                # Finally update physics and state
                player.update()

    def done(self) -> bool:
        return all(player.dead for player in self.pop)

    def natural_selection(self):
        """Perform natural selection on the population"""
        self.speciate()
        self.calculate_fitness()
        
        if not self.species:
            # If no species, create a new one with the best player
            best_player = max(self.pop, key=lambda x: x.fitness)
            self.species.append(Species(best_player))
            
        self.sort_species()
        
        if self.mass_extinction_event:
            self.mass_extinction()
            self.mass_extinction_event = False
            
        self.cull_species()
        self.set_best_player()
        self.kill_stale_species()
        self.kill_bad_species()
        
        # Ensure we still have at least one species
        if not self.species:
            best_player = max(self.pop, key=lambda x: x.fitness)
            self.species.append(Species(best_player))
        
        average_sum = self.get_avg_fitness_sum()
        if average_sum == 0:
            # If all species have 0 fitness, start fresh with best player
            best_player = max(self.pop, key=lambda x: x.fitness)
            self.species = [Species(best_player)]
            average_sum = self.get_avg_fitness_sum()
            
        children = []
        
        # Add champion from each species
        for species in self.species:
            try:
                children.append(species.champ.clone())
                
                # Calculate number of children this species gets
                no_of_children = max(0, int(species.average_fitness/average_sum * len(self.pop)) - 1)
                for _ in range(no_of_children):
                    try:
                        children.append(species.give_me_baby(self.innovation_history))
                    except (ValueError, IndexError):
                        # If can't create baby, add clone of best player
                        children.append(species.champ.clone())
            except (AttributeError, IndexError):
                continue
                
        # Fill remaining population slots with children from best species
        while len(children) < len(self.pop):
            try:
                children.append(self.species[0].give_me_baby(self.innovation_history))
            except (ValueError, IndexError, AttributeError):
                # If can't create baby, clone best overall player
                children.append(self.best_player.clone() if self.best_player else self.pop[0].clone())
            
        self.pop = children
        self.gen += 1
        
        # Generate networks for all new children
        for player in self.pop:
            player.brain.generate_network()
            
        self.population_life = 0

    def speciate(self):
        """Separate population into species based on how similar they are"""
        # Empty species
        for s in self.species:
            s.players.clear()
        
        # For each player, add it to a species
        for player in self.pop:
            species_found = False
            
            # Check if player belongs to an existing species
            for s in self.species:
                if s.same_species(player.brain):
                    s.add_to_species(player)
                    species_found = True
                    break
                    
            # If no species found, create a new species
            if not species_found:
                self.species.append(Species(player))
                
        # Remove empty species
        self.species = [s for s in self.species if s.players]

    def calculate_fitness(self):
        """Calculate the fitness of each player"""
        for player in self.pop[1:]:  # Skip first player as it's already calculated
            player.calculate_fitness()

    def sort_species(self):
        """Sort the players within a species and the species by fitness"""
        if not self.species:
            return
            
        # Sort players within each species
        for s in self.species:
            s.sort_species()

        # Sort species by fitness of its best player
        self.species.sort(key=lambda s: s.best_fitness, reverse=True)

    def kill_stale_species(self):
        """Remove species that haven't improved in 15 generations"""
        for i in range(len(self.species)-1, 1, -1):  # Skip first 2 species
            if self.species[i].staleness >= 15:
                self.species.pop(i)

    def kill_bad_species(self):
        """Remove species that are so bad they won't be allocated any children"""
        avg_sum = self.get_avg_fitness_sum()
        
        for i in range(len(self.species)-1, 0, -1):  # Skip first species
            if self.species[i].average_fitness / avg_sum * len(self.pop) < 1:
                self.species.pop(i)

    def get_avg_fitness_sum(self) -> float:
        """Calculate sum of average fitnesses of all species"""
        return sum(s.average_fitness for s in self.species)

    def cull_species(self):
        """Kill bottom half of each species"""
        for s in self.species:
            s.cull()  # Kill bottom half
            s.fitness_sharing()  # Share fitness within species
            s.set_average()  # Reset averages

    def mass_extinction(self):
        """Kill all species except the top 5"""
        while len(self.species) > 5:
            self.species.pop()

    def set_best_player(self):
        """Set the best player globally and for this generation"""
        if not self.species or not self.species[0].players:
            # If no valid species/players, find best from population
            temp_best = max(self.pop, key=lambda x: x.fitness)
        else:
            temp_best = self.species[0].players[0]
            
        temp_best.gen = self.gen

        if temp_best.score > self.best_score:
            self.gen_players.append(temp_best.clone_for_replay())
            print(f"old best: {self.best_score}")
            print(f"new best: {temp_best.score}")
            self.best_score = temp_best.score
            self.best_player = temp_best.clone_for_replay()
