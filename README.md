# Jump Game

A minimalist side-scrolling platform game built with Python and Pygame. Features vector graphics with a black and white aesthetic.

## Gameplay

- Jump between floating platforms to score points
- Each platform landed on earns 1 point
- Don't fall to the ground or it's game over
- Hold spacebar longer for higher jumps, tap for short hops

## Requirements

- Python 3.12 (recommended for full audio support)
- Pygame 2.x

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd fun_game
```

2. Create and activate a virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python game.py
```

## Controls

| Key | Action |
|-----|--------|
| **Spacebar** | Jump (hold for higher jump) |
| **Enter** | Reset game (after game over) |
| **ESC** | Quit game |

## Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_collision.py -v
pytest tests/test_obstacles.py -v
pytest tests/test_physics.py -v
pytest tests/test_scoring.py -v
pytest tests/test_game_state.py -v
```

## Project Structure

```
fun_game/
├── game.py                 # Main game code
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── AGENTS.md               # Development guidelines
├── product_requirements.md # Product specifications
└── tests/
    ├── __init__.py
    ├── conftest.py         # Pytest configuration
    ├── test_collision.py   # Collision detection tests
    ├── test_game_state.py  # Game state & game over tests
    ├── test_obstacles.py   # Obstacle generation tests
    ├── test_physics.py     # Physics mechanics tests
    └── test_scoring.py     # Scoring system tests
```

## Features

- **Variable jump height** - Hold spacebar longer for higher jumps
- **Procedural platforms** - Randomly generated but always reachable
- **Vector graphics** - All visuals rendered with shapes and lines
- **Game over & reset** - Fall to the ground and press Enter to retry
