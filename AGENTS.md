# Agent Guidelines for Jump Game

## Development Principles

### Always Test Your Work
- Run the game after every change to verify it works
- Test edge cases (e.g., rapid key presses, boundary conditions)
- Verify visual output matches expected behavior

### Automated Testing
- Write unit tests for all game logic functions
- Tests should cover:
  - Collision detection
  - Obstacle generation (reachability constraints)
  - Score calculation
  - Physics (gravity, jump mechanics)
- Run tests before considering any task complete
- Use `pytest` as the testing framework

### Test File Structure
```
fun_game/
├── game.py
├── tests/
│   ├── __init__.py
│   ├── test_collision.py
│   ├── test_obstacles.py
│   ├── test_physics.py
│   └── test_scoring.py
```

## Code Patterns

### Game Constants
- Define all magic numbers as named constants at the top of the file
- Group related constants together with comments
- Use UPPER_SNAKE_CASE for constants

### Game State
- Use global variables sparingly, only for core game state
- Document what each state variable tracks

### Functions
- Keep functions small and focused on a single responsibility
- Use descriptive names (e.g., `check_obstacle_collision`, `generate_obstacle`)
- Add docstrings explaining purpose and parameters

### Drawing
- Separate draw functions for each game element
- All drawing happens in the main game loop after state updates
- Use Pygame's built-in shape functions (no sprites)

## Visual Style Guidelines
- Background: BLACK (0, 0, 0)
- All objects: WHITE (255, 255, 255)
- Player: outlined rectangle (stroke width 2)
- Obstacles: solid filled rectangles
- UI text: white, positioned with padding from screen edges

## Adding New Features

### Checklist
1. Update `product_requirements.md` with the new feature spec
2. Implement the feature in `game.py`
3. Write automated tests for the new functionality
4. Run all tests to ensure no regressions
5. Manually playtest the game
6. Verify the feature matches requirements

### Code Changes
- Add new constants at the top of the file
- Add new state variables with the existing game state
- Create dedicated functions for new logic
- Update the main loop to integrate new features

## Running the Game
```bash
# Activate virtual environment
source venv/bin/activate

# Run the game
python game.py

# Run tests
pytest tests/
```

## Common Issues

### Obstacles Unreachable
- Check `MIN_GAP` and `MAX_GAP` values
- Verify `MAX_JUMP_HEIGHT` matches actual jump physics
- Ensure `generate_obstacle()` properly constrains vertical positioning

### Collision Not Detecting
- Verify collision tolerance values (currently 15px for landing)
- Check that collision is only checked when player is falling (velocity >= 0)
- Ensure obstacle coordinates are being updated correctly

### Performance
- Maintain 60 FPS target
- Remove off-screen obstacles promptly
- Avoid creating objects in the main loop unnecessarily
