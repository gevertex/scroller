# Jump Game - Product Requirements

## Overview
A simple side-scrolling jumping game built with Python and Pygame. The game uses vector graphics (shapes) instead of sprites, with a black background and white objects.

## Technical Stack
- Python 3.12 (required for full audio/mixer support)
- Pygame 2.x
- Vector graphics only (no sprites/art assets)

## Visual Style
- Black background
- White objects (outlines and filled shapes)
- Minimalist aesthetic
- All text rendered using vector graphics (7-segment style digits, line-based letters)

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
- Dimensions:
  - Width: 60-150 pixels (random)
  - Height: 20 pixels (fixed thickness)
- Vertical positioning:
  - Platforms can appear from near the top of the screen (y=50) to near the ground
  - Full vertical range utilized for variety
- Random positioning with constraints:
  - Horizontal gap between platforms: 60-130 pixels
  - Each platform must be reachable by jumping from the previous one
  - First platform must be reachable from the ground
- Platforms scroll from right to left
- Scroll speed increases with score (progressive difficulty)
  - Base speed: 4 pixels/frame
  - Increases by 0.05 pixels/frame per point scored
  - Maximum speed: 12 pixels/frame (reached at 160 points)
- Player can land on top of platforms

## Scoring
- Score displayed in top right corner using 7-segment style vector numbers
- Player earns 1 point per obstacle landed on
- Each obstacle can only be scored once
- Score resets on game restart

## Game Over
- Condition: Player touches the ground after having jumped at least once
  - Starting on the ground does not trigger game over
  - Only triggered after player has left the ground and returns to it
- When game over is triggered:
  - All motion pauses (obstacles stop scrolling, player stops moving)
  - "GAME OVER" displayed in large vector text (centered)
  - "PRESS ENTER TO RESET" displayed below in smaller text
- Press Enter to restart the game with fresh state

## Controls
- **Spacebar**: Jump (hold for higher jump)
- **Enter**: Reset game (when game over)
- **ESC**: Quit game

## Audio
- Background music plays during gameplay (background_music.mp3)
- Music loops continuously while game is active
- Music stops when game over is triggered
- Crash sound effect plays on game over (crash.wav)
- Music restarts when game is reset

## Future Considerations
- Collectible items
- High score tracking
- Sound effects
