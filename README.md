# Bagh-Chal (Tiger and Goats Game)

This project is a Python implementation of **Bagh-Chal**, a traditional Nepali strategy board game.  
The game is built using **Pygame** with a clear separation between UI and the game logic.

This implementation supports:
- Goat placement phase
- Tiger and goat movement phase
- Tiger capture mechanics
- Turn management
- Win condition detection

The goal was to create a functional, clean, and readable version of the game.


## 1. Gameplay Summary

Bagh-Chal is a two-player asymmetric strategy game:

- One player controls **4 tigers**.
- The other controls **20 goats**.

### Objectives
- Tigers win by capturing **5 goats**.
- Goats win by restricting all tiger movement (no legal moves available).

### Rules Implemented in This Version
- Tigers start at the four corners.
- Goats are placed one per turn until all 20 are placed.
- After placement, goats can move.
- Both players move one step along the valid board lines.
- Tigers can capture goats by jumping over them to an empty point.
- Only single jumps are implemented (no multi-jumps).

Movement is restricted according to the Bagh-Chal board graph:
- Orthogonal moves from all points
- Diagonal moves only from valid positions


## 2. Installation

### Requirements
- Python 3.8+
- Pygame

### Setup

```bash
git clone https://github.com/RonanVaz05/bhagchal
cd bhagchal
pip install pygame
python main.py
