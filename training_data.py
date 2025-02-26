import os
import pickle
from typing import Dict, Any
from genome import Genome

class TrainingData:
    def __init__(self):
        self.data = {}  # generation -> generation data
        self.file_path = os.path.join(os.path.dirname(__file__), 'training_data', 'trained_model.pkl')
        
    def add_generation_data(self, gen: int, best_score: float, avg_score: float, 
                          best_genome: Genome, num_species: int, vision_history=None, decision_history=None):
        """Store training data including vision inputs and decisions made"""
        self.data[gen] = {
            'best_score': best_score,
            'avg_score': avg_score,
            'best_genome': best_genome,
            'num_species': num_species,
            'vision_history': vision_history or [],  # Store what AI saw
            'decision_history': decision_history or []  # Store what AI decided to do
        }
    
    def save_to_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'wb') as f:
            pickle.dump(self.data, f)
            
    def load_from_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'rb') as f:
                self.data = pickle.load(f)
        else:
            raise FileNotFoundError("No training data found")
