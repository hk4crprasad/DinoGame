# 🦖 NEAT Dino Game

A Chrome dinosaur game clone with NEAT (NeuroEvolution of Augmenting Topologies) AI implementation.

<div align="center">
  <img src="assets/dino0000.png" alt="Dino Game" width="200">
  <br>
  <em>Watch AI learn to play the classic Chrome dinosaur game!</em>
  <br><br>
  <a href="https://github.com/hk4crprasad/DinoGame-AI/stargazers"><img src="https://img.shields.io/github/stars/hk4crprasad/DinoGame-AI?style=for-the-badge&color=yellow" alt="Stars"></a>
  <a href="https://github.com/hk4crprasad/DinoGame-AI/network/members"><img src="https://img.shields.io/github/forks/hk4crprasad/DinoGame-AI?style=for-the-badge&color=orange" alt="Forks"></a>
  <a href="https://github.com/hk4crprasad/DinoGame-AI/issues"><img src="https://img.shields.io/github/issues/hk4crprasad/DinoGame-AI?style=for-the-badge&color=red" alt="Issues"></a>
  <a href="https://github.com/hk4crprasad/DinoGame-AI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/hk4crprasad/DinoGame-AI?style=for-the-badge&color=blue" alt="License"></a>
</div>

## 🎮 Overview

This project implements the classic Chrome dinosaur game with an AI that learns to play using the NEAT algorithm. The dinosaur learns to jump over cacti and duck under birds to achieve the highest score possible.

<div align="center">
  <img src="https://raw.githubusercontent.com/hk4crprasad/DinoGame-AI/main/assets/gameplay.gif" alt="Gameplay Demo" width="600">
</div>

## ✨ Features

- 🦖 Classic dinosaur game mechanics (jump, duck, obstacles)
- 🧠 NEAT algorithm implementation for AI learning
- 📊 Visual representation of neural networks
- 🧬 Species differentiation for genetic diversity
- 💾 Trained model included
- 📈 Real-time fitness tracking
- 🔄 Generation progression visualization

## 📋 Requirements

- Python 3.6+
- Pygame
- NumPy
- Pickle (for saving/loading trained models)

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hk4crprasad/DinoGame-AI.git
   cd DinoGame-AI
   ```

2. Install dependencies:
   ```bash
   pip install pygame numpy
   ```

3. Run the game:
   ```bash
   python game.py
   ```

## 🧠 How It Works

### NEAT Algorithm

The NEAT (NeuroEvolution of Augmenting Topologies) algorithm works by:
- 🌱 Creating a population of neural networks
- ⭐ Evaluating each network's fitness based on game performance
- 🏆 Selecting the best performers for reproduction
- 🧬 Applying mutations to create diversity
- 🌐 Speciation to protect innovation

<div align="center">
  <img src="https://raw.githubusercontent.com/hk4crprasad/DinoGame-AI/main/assets/network.png" alt="Neural Network" width="500">
  <br>
  <em>Example of a neural network evolving over time</em>
</div>

### Game Components

| File | Description |
|------|-------------|
| `game.py` | Main game loop and rendering |
| `player.py` | Dinosaur player logic |
| `obstacle.py` | Cactus and bird obstacles |
| `genome.py` | Neural network structure |
| `population.py` | Manages the population of neural networks |
| `species.py` | Handles speciation for the NEAT algorithm |
| `node.py` & `connection_gene.py` | Building blocks for neural networks |

## 🎮 Controls

- **Space/Up Arrow**: Jump
- **Down Arrow**: Duck
- **P**: Pause game
- **R**: Restart game
- **Esc**: Quit

## 🏋️ Training Your Own AI

The repository includes a pre-trained model, but you can train your own:

1. Run the game with training mode enabled
2. Watch as the AI learns through generations
3. The best model will be saved automatically

<div align="center">
  <table>
    <tr>
      <td align="center"><img src="assets/berd.png" alt="Bird Obstacle" width="100"></td>
      <td align="center"><img src="assets/cactusBig0000.png" alt="Cactus Obstacle" width="100"></td>
    </tr>
    <tr>
      <td align="center"><strong>Bird Obstacle</strong></td>
      <td align="center"><strong>Cactus Obstacle</strong></td>
    </tr>
  </table>
</div>

## 📊 Performance Metrics

<div align="center">
  <img src="https://raw.githubusercontent.com/hk4crprasad/DinoGame-AI/main/assets/performance.png" alt="Performance Graph" width="600">
  <br>
  <em>Fitness improvement over generations</em>
</div>

## 📝 License

MIT License

## 👏 Acknowledgments

- The NEAT algorithm by Kenneth O. Stanley
- The Chrome dinosaur game by Google

---

<div align="center">
  <p>Made with ❤️ by <a href="https://github.com/hk4crprasad">hk4crprasad</a></p>
  <a href="https://github.com/hk4crprasad/DinoGame-AI"><img src="https://img.shields.io/badge/Visit_Repository-DinoGame--AI-green?style=for-the-badge&logo=github" alt="Repository"></a>
</div>
