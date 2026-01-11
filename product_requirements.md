# Jump Game - Product Requirements

## Overview
A simple side-scrolling jumping game built with Python and Pygame. The game uses vector graphics (shapes) instead of sprites, with a black background and white objects.

## Technical Stack
- Python
- Pygame
- Vector graphics only (no sprites/art assets)

## Visual Style
- Black background
- White objects (outlines and filled shapes)
- Minimalist aesthetic

## Player
- White outlined rectangle (40x40 pixels)
- Fixed horizontal position (scroller style)
- Single control: spacebar to jump

## Jump Mechanics
- Variable jump height based on spacebar hold duration
  - Quick tap: short hop (velocity reduced by 50% on release)
  - Hold longer: higher jump (full jump strength)
- Gravity pulls player down
- Player can only jump when on a surface (ground or obstacle)

## Obstacles
- Solid white rectangles (filled)
- Floating platforms in the air (not extending to ground)
- Random dimensions:
  - Width: 60-150 pixels
  - Height: 15-40 pixels
- Random positioning with constraints:
  - Horizontal gap between platforms: 60-130 pixels
  - Each platform must be reachable by jumping from the previous one
  - First platform must be reachable from the ground
- Platforms scroll from right to left at constant speed
- Player can land on top of platforms

## Scoring
- Score displayed in top right corner
- Player earns 1 point per obstacle landed on
- Each obstacle can only be scored once
- Score resets on game restart

## Controls
- **Spacebar**: Jump (hold for higher jump)
- **ESC**: Quit game

## Future Considerations
- Game over condition (falling off screen)
- Increasing difficulty/speed over time
- Collectible items
- High score tracking
