# Copilot Code Review Instructions

When reviewing code for this project, follow these guidelines and reference the project documentation.

## Project Context

This is a minimalist side-scrolling jumping game built with Python and Pygame. The game uses vector graphics (shapes, not sprites) with a black background and white objects.

## Key Documentation

Before reviewing, familiarize yourself with:
- **[AGENTS.md](../AGENTS.md)** - Development guidelines and code patterns
- **[product_requirements.md](../product_requirements.md)** - Product specifications and feature requirements

## Code Review Checklist

### Architecture & Patterns

- [ ] **GameState dataclass** - All mutable state should be in the `GameState` dataclass, not global variables
- [ ] **Constants** - Magic numbers should be defined as UPPER_SNAKE_CASE constants at the top of the file
- [ ] **Function design** - Functions should be small, focused, and have descriptive names
- [ ] **Pure functions** - Prefer pure functions for testability where possible

### Testing Requirements

All code changes must have corresponding tests. Check that:

- [ ] **Unit tests exist** for new game logic functions
- [ ] **Tests cover edge cases** (boundary conditions, rapid inputs, etc.)
- [ ] **No test regressions** - Existing tests should still pass
- [ ] **Tests follow project patterns** - Import from `game.py` directly (conftest.py handles path setup)

Test coverage areas:
- Collision detection (including pass-through detection)
- Obstacle generation (reachability constraints)
- Score calculation
- Physics (gravity, jump mechanics)
- Game state management
- High score save/load with tamper protection

### Visual Style

- [ ] Background must be BLACK (0, 0, 0)
- [ ] All objects must be WHITE (255, 255, 255)
- [ ] Player: outlined rectangle using `LINE_THICKNESS`
- [ ] Obstacles: solid filled rectangles
- [ ] Text: vector graphics (7-segment digits, line-based letters)

### Audio Handling

- [ ] Music plays during active gameplay, stops on game over
- [ ] Music restarts on game reset
- [ ] Missing audio files handled gracefully (no crashes)

### Security

- [ ] High score uses HMAC signature for tamper protection
- [ ] No hardcoded sensitive data (API keys, credentials)
- [ ] File I/O has proper error handling

### Performance

- [ ] Maintain 60 FPS target
- [ ] Off-screen obstacles are removed promptly
- [ ] Avoid object creation in the main loop

## Common Issues to Flag

### Collision Detection
- Missing pass-through detection for high-speed falls
- Not tracking previous frame position
- Collision checked when player is ascending (should only check when falling)

### Obstacle Generation
- Platforms not reachable from previous platform
- First platform not reachable from ground
- Gap constraints not enforced (MIN_GAP, MAX_GAP)

### Game State
- Global mutable state outside GameState dataclass
- State not properly reset on game restart
- Missing state fields for new features

## PR Requirements

Before approving a PR, verify:

1. **CI passes** - All tests pass in the GitHub Actions workflow
2. **Tests added** - New functionality has corresponding tests
3. **Documentation updated** - AGENTS.md or product_requirements.md updated if needed
4. **No regressions** - Manual playtest confirms game still works correctly

## Running Tests Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_collision.py -v
```

## Test File Structure

```
tests/
├── conftest.py         # Pytest config (handles imports)
├── test_collision.py   # Collision detection tests
├── test_game_state.py  # Game state & reset tests
├── test_high_score.py  # High score persistence & tamper protection
├── test_obstacles.py   # Obstacle generation tests
├── test_physics.py     # Physics mechanics tests
├── test_rendering.py   # Rendering constants & text segments
└── test_scoring.py     # Scoring system tests
```
