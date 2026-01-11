# Agent Guidelines for Jump Game

## Development Principles

### Always Test Your Work
- Run the game after every change to verify it works
- Test edge cases (e.g., rapid key presses, boundary conditions)
- Verify visual output matches expected behavior

### Automated Testing
- Write unit tests for all game logic functions
- Tests should cover:
  - Collision detection (including pass-through detection)
  - Obstacle generation (reachability constraints)
  - Score calculation
  - Physics (gravity, jump mechanics)
  - Game state management
- Run tests before considering any task complete
- Use `pytest` as the testing framework

### Test File Structure
```
fun_game/
├── game.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest config, sys.path setup
│   ├── test_collision.py   # Collision detection tests
│   ├── test_game_state.py  # Game state & reset tests
│   ├── test_obstacles.py   # Obstacle generation tests
│   ├── test_physics.py     # Physics mechanics tests
│   └── test_scoring.py     # Scoring system tests
```

### Test Import Pattern
All test imports are handled centrally in `conftest.py`. Test files should NOT include:
```python
# DON'T DO THIS - conftest.py handles it
import sys
sys.path.insert(0, '/path/to/project')
```

Instead, just import directly:
```python
# DO THIS
from game import check_obstacle_collision, PLAYER_WIDTH
```

## Code Patterns

### Game Constants
- Define all magic numbers as named constants at the top of the file
- Group related constants together with comments
- Use UPPER_SNAKE_CASE for constants
- Categories:
  - Screen settings (dimensions)
  - Colors
  - Player settings (size, physics)
  - Obstacle settings (dimensions, gaps, speeds)
  - Drawing settings (line thickness, padding)
  - Frame rate

### Game State
- Use the `GameState` dataclass for all mutable game state
- Access state via `state.field_name` pattern
- Reset creates a fresh GameState instance
- Avoid global variables for game state

```python
@dataclass
class GameState:
    player_y: float
    player_velocity_y: float
    is_jumping: bool
    # ... etc
```

### Functions
- Keep functions small and focused on a single responsibility
- Use descriptive names (e.g., `check_obstacle_collision`, `generate_obstacle`)
- Add docstrings explaining purpose and parameters
- Pure functions are preferred for testability

### Drawing
- Separate draw functions for each game element
- All drawing happens in the main game loop after state updates
- Use Pygame's built-in shape functions (no sprites)
- Use `LINE_THICKNESS` constant for consistent stroke widths

### Collision Detection
- Track previous frame position for pass-through detection
- Check both crossing detection (for high-speed falls) and zone detection (for slow falls)
- Always verify horizontal alignment before vertical checks

## Visual Style Guidelines
- Background: BLACK (0, 0, 0)
- All objects: WHITE (255, 255, 255)
- Player: outlined rectangle (stroke width from LINE_THICKNESS)
- Obstacles: solid filled rectangles
- UI text: white, positioned with SCORE_PADDING from screen edges

## Audio
- Background music plays during active gameplay
- Music stops on game over
- Music restarts on game reset
- Handle missing audio files gracefully

## Adding New Features

### Checklist
1. Update `product_requirements.md` with the new feature spec
2. Add any new constants at the top of `game.py`
3. Implement the feature
4. Write automated tests for the new functionality
5. Run all tests to ensure no regressions
6. Manually playtest the game
7. Verify the feature matches requirements

### Code Changes
- Add new constants at the top of the file in the appropriate group
- Update GameState dataclass if new state is needed
- Create dedicated functions for new logic
- Update the main loop to integrate new features

## Running the Game

### Requirements
- Python 3.12 (required for full pygame audio support)
- Pygame 2.x

### Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Run the game
python game.py

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_collision.py -v
```

## Common Issues

### Obstacles Unreachable
- Check `MIN_GAP` and `MAX_GAP` values
- Verify `MAX_JUMP_HEIGHT` matches actual jump physics
- Ensure `generate_obstacle()` properly constrains vertical positioning

### Collision Not Detecting
- Verify `LANDING_TOLERANCE` value
- Check that collision checks both pass-through and zone detection
- Ensure previous position is tracked for high-speed fall detection
- Check that collision is only checked when player is falling (velocity >= 0)

### Audio Not Working
- Ensure Python 3.12 is being used (not 3.14)
- Check that `background_music.mp3` exists in project root
- Verify pygame.mixer is initialized before loading music

### Performance
- Maintain 60 FPS target
- Remove off-screen obstacles promptly
- Avoid creating objects in the main loop unnecessarily
