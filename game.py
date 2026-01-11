import pygame
import sys
import random
import math
import hmac
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Player settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
PLAYER_X = 100  # Fixed x position for scroller style
GRAVITY = 0.8
JUMP_STRENGTH = -15
GROUND_Y = SCREEN_HEIGHT - 50  # Ground level

# Obstacle settings
BASE_SCROLL_SPEED = 4
MAX_SCROLL_SPEED = 12
SPEED_INCREMENT = 0.05  # Speed increase per point scored
MIN_OBSTACLE_WIDTH = 60
MAX_OBSTACLE_WIDTH = 150
OBSTACLE_THICKNESS = 20  # Fixed thickness for all obstacles
MIN_GAP = 60   # Base minimum horizontal gap between obstacles
MAX_GAP = 130  # Maximum horizontal gap between obstacles
MIN_JUMP_FRAMES = 18  # Frames for minimum jump (tap) to complete
GAP_BUFFER = 20  # Extra buffer pixels for comfortable landing
MAX_JUMP_HEIGHT = 120  # Maximum height player can jump
MAX_HEIGHT_DIFF = 100  # Max height difference to ensure jumpability
MIN_PLATFORM_Y = 50   # Highest platforms can go (near top of screen)
MAX_PLATFORM_Y = GROUND_Y - 20  # Lowest platforms (near ground)
INITIAL_OBSTACLE_COUNT = 4  # Number of obstacles generated at game start
INITIAL_OBSTACLE_OFFSET_MIN = 100  # Minimum x offset for first obstacle
INITIAL_OBSTACLE_OFFSET_MAX = 300  # Maximum x offset for first obstacle

# Drawing settings
LINE_THICKNESS = 2
SCORE_PADDING = 20  # Padding from screen edge for score
SCORE_DIGIT_WIDTH = 16
SCORE_DIGIT_SIZE = 20
GAME_OVER_TEXT_SIZE = 32
GAME_OVER_SUBTEXT_SIZE = 16
LANDING_TOLERANCE = 5  # Extra pixels below obstacle for landing detection

# Debris/explosion settings
DEBRIS_COUNT = 16  # Number of pieces the player breaks into
DEBRIS_SIZE_MIN = 6  # Minimum debris piece size
DEBRIS_SIZE_MAX = 12  # Maximum debris piece size
DEBRIS_SPEED_MIN = 3  # Minimum initial velocity
DEBRIS_SPEED_MAX = 10  # Maximum initial velocity
DEBRIS_BOUNCE_DAMPING = 0.6  # Energy retained after bounce (0-1)
DEBRIS_FRICTION = 0.98  # Horizontal slowdown per frame
DEBRIS_GRAVITY = 0.5  # Gravity for debris (can differ from player)

# Frame rate
FPS = 60

# Jump mechanics
JUMP_CUT_MULTIPLIER = 0.5  # Velocity multiplier when releasing jump early
DEBRIS_UPWARD_BIAS = 5  # Upward velocity added to debris for better visual

# Asset paths
ASSETS_DIR = Path(__file__).parent / "assets"
BACKGROUND_MUSIC_PATH = ASSETS_DIR / "background_music.wav"
CRASH_SOUND_PATH = ASSETS_DIR / "crash.wav"

# High score settings
# I realize this won't prevent people from generating their own high scores, but it makes it way harder than just plain text
# Only prevents casual tampering
HIGH_SCORE_PATH = Path(__file__).parent / "highscore.json"
HIGH_SCORE_SECRET = b"jump_game_secret_key_2024"  # HMAC key for tamper protection

# FPS display settings
FPS_DISPLAY_PADDING = 10
FPS_DISPLAY_SIZE = 14

# Text outline settings
TEXT_OUTLINE_OFFSET = 2  # Pixels to offset for outline effect

# Pre-computed segment definitions for 7-segment digit display
# Segment positions are relative multipliers of (width, height)
# Format: (start_x_mult, start_y_mult, end_x_mult, end_y_mult)
DIGIT_SEGMENTS = {
    'top':    (0, 0, 1, 0),
    'mid':    (0, 0.5, 1, 0.5),
    'bot':    (0, 1, 1, 1),
    'tl':     (0, 0, 0, 0.5),
    'tr':     (1, 0, 1, 0.5),
    'bl':     (0, 0.5, 0, 1),
    'br':     (1, 0.5, 1, 1),
}

# Which segments are active for each digit 0-9
DIGIT_SEGMENT_MAP = {
    0: ('top', 'bot', 'tl', 'tr', 'bl', 'br'),
    1: ('tr', 'br'),
    2: ('top', 'mid', 'bot', 'tr', 'bl'),
    3: ('top', 'mid', 'bot', 'tr', 'br'),
    4: ('mid', 'tl', 'tr', 'br'),
    5: ('top', 'mid', 'bot', 'tl', 'br'),
    6: ('top', 'mid', 'bot', 'tl', 'bl', 'br'),
    7: ('top', 'tr', 'br'),
    8: ('top', 'mid', 'bot', 'tl', 'tr', 'bl', 'br'),
    9: ('top', 'mid', 'bot', 'tl', 'tr', 'br'),
}

# Pre-computed letter segment definitions for vector text
# Format: list of (start_x_mult, start_y_mult, end_x_mult, end_y_mult)
LETTER_SEGMENTS = {
    'A': ((0, 1, 0, 0.33), (0, 0.33, 0.5, 0), (0.5, 0, 1, 0.33), (1, 0.33, 1, 1), (0, 0.5, 1, 0.5)),
    'C': ((1, 0.25, 0.5, 0), (0.5, 0, 0, 0.25), (0, 0.25, 0, 0.75), (0, 0.75, 0.5, 1), (0.5, 1, 1, 0.75)),
    'E': ((0, 0, 0, 1), (0, 0, 1, 0), (0, 0.5, 0.66, 0.5), (0, 1, 1, 1)),
    'F': ((0, 1, 0, 0), (0, 0, 1, 0), (0, 0.5, 0.66, 0.5)),
    'G': ((1, 0.33, 0.5, 0), (0.5, 0, 0, 0.33), (0, 0.33, 0, 0.66), (0, 0.66, 0.5, 1), (0.5, 1, 1, 0.66), (1, 0.66, 1, 0.5), (1, 0.5, 0.5, 0.5)),
    'H': ((0, 0, 0, 1), (0, 0.5, 1, 0.5), (1, 0, 1, 1)),
    'I': ((0.25, 0, 0.75, 0), (0.5, 0, 0.5, 1), (0.25, 1, 0.75, 1)),
    'M': ((0, 1, 0, 0), (0, 0, 0.5, 0.5), (0.5, 0.5, 1, 0), (1, 0, 1, 1)),
    'N': ((0, 1, 0, 0), (0, 0, 1, 1), (1, 1, 1, 0)),
    'O': ((0, 0.25, 0, 0.75), (0, 0.25, 0.5, 0), (0.5, 0, 1, 0.25), (1, 0.25, 1, 0.75), (1, 0.75, 0.5, 1), (0.5, 1, 0, 0.75)),
    'P': ((0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 1, 0.5), (1, 0.5, 0, 0.5)),
    'R': ((0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 1, 0.5), (1, 0.5, 0, 0.5), (0, 0.5, 1, 1)),
    'S': ((1, 0.25, 0.5, 0), (0.5, 0, 0, 0.25), (0, 0.25, 0, 0.5), (0, 0.5, 1, 0.5), (1, 0.5, 1, 0.75), (1, 0.75, 0.5, 1), (0.5, 1, 0, 0.75)),
    'T': ((0, 0, 1, 0), (0.5, 0, 0.5, 1)),
    'V': ((0, 0, 0.5, 1), (0.5, 1, 1, 0)),
    'W': ((0, 0, 0.25, 1), (0.25, 1, 0.5, 0.5), (0.5, 0.5, 0.75, 1), (0.75, 1, 1, 0)),
}


@dataclass
class Obstacle:
    """Represents a floating platform obstacle."""
    x: float
    y: float
    width: float
    height: float
    scored: bool = False


@dataclass
class Debris:
    """Represents a debris particle from player explosion."""
    x: float
    y: float
    vel_x: float
    vel_y: float
    size: int
    bounces: int = 0


@dataclass
class GameState:
    """Holds all mutable game state."""
    player_y: float
    player_velocity_y: float
    is_jumping: bool
    jump_held: bool
    has_jumped: bool
    game_over: bool
    score: int
    high_score: int
    high_score_beaten: bool = False
    jump_buffered: bool = False  # Buffer jump input for same-frame landing
    obstacles: List[Obstacle] = field(default_factory=list)
    debris: List[Debris] = field(default_factory=list)


@dataclass
class Game:
    """Encapsulates pygame runtime objects."""
    screen: pygame.Surface
    font: Optional[pygame.font.Font]
    clock: pygame.time.Clock
    crash_sound: Optional[pygame.mixer.Sound]


# Global game instance (initialized at runtime)
_game: Optional[Game] = None


def _compute_score_signature(score: int) -> str:
    """Compute HMAC signature for a score value."""
    message = str(score).encode()
    return hmac.new(HIGH_SCORE_SECRET, message, hashlib.sha256).hexdigest()


def save_high_score(score: int) -> bool:
    """Save high score to file with tamper protection.

    Args:
        score: The high score to save.

    Returns:
        True if saved successfully.
        False if file could not be written (IOError/OSError).
    """
    data = {
        "high_score": score,
        "signature": _compute_score_signature(score)
    }
    try:
        with open(HIGH_SCORE_PATH, "w") as f:
            json.dump(data, f)
        return True
    except (IOError, OSError):
        return False


def load_high_score() -> int:
    """Load high score from file with tamper detection.

    Returns:
        The high score if valid, 0 if file doesn't exist or is tampered.
    """
    if not HIGH_SCORE_PATH.exists():
        return 0

    try:
        with open(HIGH_SCORE_PATH, "r") as f:
            data = json.load(f)

        score = data.get("high_score", 0)
        signature = data.get("signature", "")

        # Verify signature matches
        expected_signature = _compute_score_signature(score)
        if hmac.compare_digest(signature, expected_signature):
            return score
        else:
            # Tampered file - return 0
            return 0
    except (IOError, OSError, json.JSONDecodeError, TypeError):
        return 0


def init_pygame() -> Game:
    """Initialize pygame and create display objects.

    Returns:
        Game: Initialized game instance with pygame objects.
    """
    global _game
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF, vsync=1
    )
    pygame.display.set_caption("Jump Game")

    # Try to load font, but handle if unavailable (Python 3.14 compatibility)
    try:
        font = pygame.font.Font(None, 36)
    except (NotImplementedError, ImportError):
        font = None

    clock = pygame.time.Clock()

    # Initialize audio
    pygame.mixer.init()

    # Load and play background music
    try:
        pygame.mixer.music.load(str(BACKGROUND_MUSIC_PATH))
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    except pygame.error:
        pass  # Music file not found

    # Load crash sound effect
    try:
        crash_sound = pygame.mixer.Sound(str(CRASH_SOUND_PATH))
    except pygame.error:
        crash_sound = None  # Sound file not found

    _game = Game(screen=screen, font=font, clock=clock, crash_sound=crash_sound)
    return _game


def generate_obstacle(
    last_obstacle: Optional[Obstacle] = None,
    from_ground: bool = False,
    speed: float = BASE_SCROLL_SPEED
) -> Obstacle:
    """Generate a new floating obstacle that is reachable from the last one.

    Args:
        last_obstacle: Previous obstacle to chain from (for reachability).
        from_ground: If True, generate obstacle reachable from ground level.
        speed: Current scroll speed, used to scale minimum gap for jumpability.

    Returns:
        Obstacle: New obstacle instance.
    """
    width = random.randint(MIN_OBSTACLE_WIDTH, MAX_OBSTACLE_WIDTH)
    min_gap = get_min_gap(speed)
    # At high speeds, min_gap may exceed MAX_GAP, so use max of both for upper bound
    max_gap = max(min_gap, MAX_GAP)

    # Position obstacle off-screen to the right
    if last_obstacle and not from_ground:
        x = last_obstacle.x + last_obstacle.width + random.randint(min_gap, max_gap)
        # Ensure platform is reachable from last obstacle
        last_top = last_obstacle.y
        # Player can jump up MAX_JUMP_HEIGHT or fall down any distance
        # New platform top should be within jumpable range (can go up or down)
        min_y = max(MIN_PLATFORM_Y, last_top - MAX_JUMP_HEIGHT)  # Can jump up this much
        max_y = min(MAX_PLATFORM_Y, last_top + MAX_HEIGHT_DIFF)  # Don't drop too far
        if min_y > max_y:
            min_y, max_y = max_y, min_y
        y = random.randint(int(min_y), int(max_y))
    elif from_ground:
        # First platform should be reachable from ground
        x = SCREEN_WIDTH + random.randint(INITIAL_OBSTACLE_OFFSET_MIN, INITIAL_OBSTACLE_OFFSET_MAX)
        y = random.randint(GROUND_Y - MAX_JUMP_HEIGHT, MAX_PLATFORM_Y)
    else:
        x = SCREEN_WIDTH + random.randint(INITIAL_OBSTACLE_OFFSET_MIN, INITIAL_OBSTACLE_OFFSET_MAX)
        y = random.randint(MIN_PLATFORM_Y, MAX_PLATFORM_Y)

    return Obstacle(
        x=x,
        y=y,
        width=width,
        height=OBSTACLE_THICKNESS,
        scored=False
    )


def draw_player(x: float, y: float) -> None:
    """Draw the player as a white outlined rectangle."""
    pygame.draw.rect(_game.screen, WHITE, (x, y, PLAYER_WIDTH, PLAYER_HEIGHT), LINE_THICKNESS)


def draw_ground() -> None:
    """Draw the ground line."""
    pygame.draw.line(_game.screen, WHITE, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), LINE_THICKNESS)


def draw_digit_raw(x: float, y: float, digit: int, color: tuple, size: int = SCORE_DIGIT_SIZE) -> None:
    """Draw a single digit using vector lines (7-segment style).

    Uses pre-computed DIGIT_SEGMENTS and DIGIT_SEGMENT_MAP constants.

    Args:
        x: X position.
        y: Y position.
        digit: Digit 0-9 to draw.
        color: RGB tuple for the color.
        size: Size of the digit.
    """
    w = size // 2  # Width
    h = size       # Height

    for seg_name in DIGIT_SEGMENT_MAP.get(digit, ()):
        seg = DIGIT_SEGMENTS[seg_name]
        pygame.draw.line(_game.screen, color,
                        (x + seg[0] * w, y + seg[1] * h),
                        (x + seg[2] * w, y + seg[3] * h), LINE_THICKNESS)


def draw_digit(x: float, y: float, digit: int, size: int = SCORE_DIGIT_SIZE) -> None:
    """Draw a digit with black outline for readability."""
    # Draw black outline at offsets
    for dx, dy in [(-TEXT_OUTLINE_OFFSET, 0), (TEXT_OUTLINE_OFFSET, 0),
                   (0, -TEXT_OUTLINE_OFFSET), (0, TEXT_OUTLINE_OFFSET)]:
        draw_digit_raw(x + dx, y + dy, digit, BLACK, size)
    # Draw white digit on top
    draw_digit_raw(x, y, digit, WHITE, size)


def draw_score(score: int, high_score: int) -> None:
    """Draw the score and high score in the top right corner with black outline."""
    if _game.font:
        # Draw current score
        text = f"Score: {score}"
        text_rect = _game.font.render(text, True, WHITE).get_rect(
            topright=(SCREEN_WIDTH - SCORE_PADDING, SCORE_PADDING))
        # Draw black outline at offsets
        outline_surface = _game.font.render(text, True, BLACK)
        for dx, dy in [(-TEXT_OUTLINE_OFFSET, 0), (TEXT_OUTLINE_OFFSET, 0),
                       (0, -TEXT_OUTLINE_OFFSET), (0, TEXT_OUTLINE_OFFSET)]:
            _game.screen.blit(outline_surface, text_rect.move(dx, dy))
        # Draw white text on top
        text_surface = _game.font.render(text, True, WHITE)
        _game.screen.blit(text_surface, text_rect)

        # Draw high score below current score
        if high_score > 0:
            hi_text = f"Best: {high_score}"
            hi_rect = _game.font.render(hi_text, True, WHITE).get_rect(
                topright=(SCREEN_WIDTH - SCORE_PADDING, SCORE_PADDING + 25))
            hi_outline = _game.font.render(hi_text, True, BLACK)
            for dx, dy in [(-TEXT_OUTLINE_OFFSET, 0), (TEXT_OUTLINE_OFFSET, 0),
                           (0, -TEXT_OUTLINE_OFFSET), (0, TEXT_OUTLINE_OFFSET)]:
                _game.screen.blit(hi_outline, hi_rect.move(dx, dy))
            hi_surface = _game.font.render(hi_text, True, WHITE)
            _game.screen.blit(hi_surface, hi_rect)
    else:
        # Draw score using vector digit rendering (already has outline)
        score_str = str(score)
        total_width = len(score_str) * SCORE_DIGIT_WIDTH
        start_x = SCREEN_WIDTH - SCORE_PADDING - total_width

        for i, char in enumerate(score_str):
            draw_digit(start_x + i * SCORE_DIGIT_WIDTH, SCORE_PADDING - 5, int(char))

        # Draw high score below current score using vector rendering
        if high_score > 0:
            hi_str = str(high_score)
            hi_width = len(hi_str) * SCORE_DIGIT_WIDTH
            hi_start_x = SCREEN_WIDTH - SCORE_PADDING - hi_width
            for i, char in enumerate(hi_str):
                draw_digit(hi_start_x + i * SCORE_DIGIT_WIDTH, SCORE_PADDING + 20, int(char))


def draw_obstacle(obstacle: Obstacle) -> None:
    """Draw an obstacle as a solid white rectangle."""
    pygame.draw.rect(_game.screen, WHITE, (obstacle.x, obstacle.y,
                                           obstacle.width, obstacle.height))


def draw_text(text: str, y_position: float, size: int = 20) -> None:
    """Draw text centered on screen using vector digits."""
    # Calculate total width
    char_width = size // 2 + 6
    total_width = len(text) * char_width
    start_x = (SCREEN_WIDTH - total_width) // 2

    for i, char in enumerate(text):
        x = start_x + i * char_width
        if char.isdigit():
            draw_digit(x, y_position, int(char), size=size)
        elif char.isalpha():
            draw_letter(x, y_position, char.upper(), size=size)
        # Spaces and other characters are skipped (just add spacing)


def draw_letter_raw(x: float, y: float, letter: str, color: tuple, size: int = SCORE_DIGIT_SIZE) -> None:
    """Draw a letter using vector lines.

    Uses pre-computed LETTER_SEGMENTS constant.

    Args:
        x: X position.
        y: Y position.
        letter: Uppercase letter to draw.
        color: RGB tuple for the color.
        size: Size of the letter.
    """
    w = size // 2
    h = size

    if letter in LETTER_SEGMENTS:
        for seg in LETTER_SEGMENTS[letter]:
            pygame.draw.line(_game.screen, color,
                           (x + seg[0] * w, y + seg[1] * h),
                           (x + seg[2] * w, y + seg[3] * h), LINE_THICKNESS)


def draw_letter(x: float, y: float, letter: str, size: int = SCORE_DIGIT_SIZE) -> None:
    """Draw a letter with black outline for readability."""
    # Draw black outline at offsets
    for dx, dy in [(-TEXT_OUTLINE_OFFSET, 0), (TEXT_OUTLINE_OFFSET, 0),
                   (0, -TEXT_OUTLINE_OFFSET), (0, TEXT_OUTLINE_OFFSET)]:
        draw_letter_raw(x + dx, y + dy, letter, BLACK, size)
    # Draw white letter on top
    draw_letter_raw(x, y, letter, WHITE, size)


def draw_game_over(high_score_beaten: bool = False) -> None:
    """Draw game over overlay.

    Args:
        high_score_beaten: If True, display "NEW HIGH SCORE" message.
    """
    draw_text("GAME OVER", SCREEN_HEIGHT // 3, size=GAME_OVER_TEXT_SIZE)
    if high_score_beaten:
        draw_text("NEW HIGH SCORE", SCREEN_HEIGHT // 3 + 45, size=GAME_OVER_SUBTEXT_SIZE)
        draw_text("PRESS ENTER TO RESET", SCREEN_HEIGHT // 3 + 75, size=GAME_OVER_SUBTEXT_SIZE)
    else:
        draw_text("PRESS ENTER TO RESET", SCREEN_HEIGHT // 3 + 50, size=GAME_OVER_SUBTEXT_SIZE)


def draw_fps(fps: float) -> None:
    """Draw FPS counter in the top-left corner with black outline.

    Args:
        fps: Current frames per second from clock.get_fps().
    """
    fps_int = int(fps)

    if _game.font:
        text = f"FPS: {fps_int}"
        pos = (FPS_DISPLAY_PADDING, FPS_DISPLAY_PADDING)
        # Draw black outline at offsets
        outline_surface = _game.font.render(text, True, BLACK)
        for dx, dy in [(-TEXT_OUTLINE_OFFSET, 0), (TEXT_OUTLINE_OFFSET, 0),
                       (0, -TEXT_OUTLINE_OFFSET), (0, TEXT_OUTLINE_OFFSET)]:
            _game.screen.blit(outline_surface, (pos[0] + dx, pos[1] + dy))
        # Draw white text on top
        text_surface = _game.font.render(text, True, WHITE)
        _game.screen.blit(text_surface, pos)
    else:
        # Draw "FPS" text using vector letters (already has outline)
        draw_letter(FPS_DISPLAY_PADDING, FPS_DISPLAY_PADDING, 'F', size=FPS_DISPLAY_SIZE)
        draw_letter(FPS_DISPLAY_PADDING + 12, FPS_DISPLAY_PADDING, 'P', size=FPS_DISPLAY_SIZE)
        draw_letter(FPS_DISPLAY_PADDING + 24, FPS_DISPLAY_PADDING, 'S', size=FPS_DISPLAY_SIZE)

        # Draw FPS digits
        fps_str = str(fps_int)
        digit_start_x = FPS_DISPLAY_PADDING + 42
        for i, char in enumerate(fps_str):
            draw_digit(digit_start_x + i * 12, FPS_DISPLAY_PADDING, int(char), size=FPS_DISPLAY_SIZE)


def generate_debris(player_x: float, player_y: float) -> List[Debris]:
    """Generate debris particles from player position for explosion effect.

    Args:
        player_x: Player's x position
        player_y: Player's y position

    Returns:
        List of Debris instances.
    """
    debris_list = []

    for _ in range(DEBRIS_COUNT):
        # Random angle for explosion direction
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(DEBRIS_SPEED_MIN, DEBRIS_SPEED_MAX)

        # Calculate velocity components
        vel_x = math.cos(angle) * speed
        vel_y = math.sin(angle) * speed - DEBRIS_UPWARD_BIAS

        # Random starting position within the player bounds
        start_x = player_x + random.randint(0, PLAYER_WIDTH)
        start_y = player_y + random.randint(0, PLAYER_HEIGHT)

        debris_list.append(Debris(
            x=start_x,
            y=start_y,
            vel_x=vel_x,
            vel_y=vel_y,
            size=random.randint(DEBRIS_SIZE_MIN, DEBRIS_SIZE_MAX),
            bounces=0
        ))

    return debris_list


def update_debris(debris_list: List[Debris]) -> None:
    """Update debris physics - gravity, movement, and ground bouncing.

    Args:
        debris_list: List of Debris instances.
    """
    for debris in debris_list:
        # Apply gravity
        debris.vel_y += DEBRIS_GRAVITY

        # Apply friction to horizontal movement
        debris.vel_x *= DEBRIS_FRICTION

        # Update position
        debris.x += debris.vel_x
        debris.y += debris.vel_y

        # Ground collision and bounce
        if debris.y + debris.size >= GROUND_Y:
            debris.y = GROUND_Y - debris.size
            debris.vel_y = -debris.vel_y * DEBRIS_BOUNCE_DAMPING
            debris.bounces += 1

            # Stop bouncing if velocity is very small
            if abs(debris.vel_y) < 1:
                debris.vel_y = 0


def draw_debris(debris_list: List[Debris]) -> None:
    """Draw all debris particles.

    Args:
        debris_list: List of Debris instances.
    """
    for debris in debris_list:
        pygame.draw.rect(
            _game.screen, WHITE,
            (int(debris.x), int(debris.y), debris.size, debris.size),
            LINE_THICKNESS
        )


def check_obstacle_collision(player_x: float, player_y: float, prev_player_y: float, obstacle: Obstacle) -> bool:
    """Check if player is landing on top of a floating obstacle.

    Uses both current and previous position to detect if player passed through
    the obstacle between frames (prevents falling through at high velocities).

    Args:
        player_x: Player's current x position.
        player_y: Player's current y position.
        prev_player_y: Player's previous y position.
        obstacle: Obstacle to check collision with.

    Returns:
        True if player is landing on the obstacle, False otherwise.
    """
    player_bottom = player_y + PLAYER_HEIGHT
    prev_player_bottom = prev_player_y + PLAYER_HEIGHT
    player_right = player_x + PLAYER_WIDTH
    player_left = player_x

    obs_top = obstacle.y
    obs_bottom = obstacle.y + obstacle.height
    obs_left = obstacle.x
    obs_right = obstacle.x + obstacle.width

    # Check if player is horizontally aligned with obstacle
    if player_right > obs_left and player_left < obs_right:
        # Check if player crossed through the obstacle top between frames
        # Previous bottom was above obstacle top, current bottom is at or below it
        if prev_player_bottom <= obs_top and player_bottom >= obs_top:
            return True
        # Also check if player is currently in the landing zone (for slow falls)
        if player_bottom >= obs_top and player_bottom <= obs_bottom + LANDING_TOLERANCE:
            return True
    return False


def get_scroll_speed(score: int) -> float:
    """Calculate scroll speed based on current score.

    Args:
        score: Current game score.

    Returns:
        Scroll speed capped at MAX_SCROLL_SPEED.
    """
    speed = BASE_SCROLL_SPEED + (score * SPEED_INCREMENT)
    return min(speed, MAX_SCROLL_SPEED)


def get_min_gap(speed: float) -> int:
    """Calculate minimum gap between obstacles based on scroll speed.

    At higher speeds, obstacles need larger gaps to ensure the player
    can complete a minimum jump and still land on the next platform.

    Args:
        speed: Current scroll speed in pixels per frame.

    Returns:
        Minimum gap in pixels, scaled to ensure jumpability.
    """
    # During a minimum jump, obstacles scroll: speed * MIN_JUMP_FRAMES
    # For landing: gap + obstacle_width > scroll_distance
    # So: gap > scroll_distance - MIN_OBSTACLE_WIDTH
    required_gap = (speed * MIN_JUMP_FRAMES) - MIN_OBSTACLE_WIDTH + GAP_BUFFER
    return max(MIN_GAP, int(required_gap))


def reset_game() -> GameState:
    """Reset game state for a new game.

    Returns:
        Fresh game state with player on ground and initial obstacles.
    """
    # Generate initial obstacles
    obstacles: List[Obstacle] = []
    first_obs = generate_obstacle(from_ground=True)
    obstacles.append(first_obs)
    last_obs = first_obs
    for _ in range(INITIAL_OBSTACLE_COUNT):
        new_obs = generate_obstacle(last_obs)
        obstacles.append(new_obs)
        last_obs = new_obs

    return GameState(
        player_y=GROUND_Y - PLAYER_HEIGHT,  # Start on ground
        player_velocity_y=0,
        is_jumping=False,
        jump_held=False,
        has_jumped=False,
        game_over=False,
        score=0,
        high_score=load_high_score(),
        obstacles=obstacles
    )


def main() -> None:
    """Main game loop."""
    # Initialize pygame
    game = init_pygame()

    # Initialize game state
    state = reset_game()

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not state.game_over:
                    # Only jump if on the ground or on an obstacle
                    if not state.is_jumping:
                        state.player_velocity_y = JUMP_STRENGTH
                        state.is_jumping = True
                        state.jump_held = True
                        state.has_jumped = True
                    else:
                        # Buffer jump for same-frame landing
                        state.jump_buffered = True

                if event.key == pygame.K_RETURN and state.game_over:
                    # Reset the game
                    state = reset_game()
                    # Restart background music
                    pygame.mixer.music.play(-1)

                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    state.jump_held = False
                    # Cut the jump short if still moving upward
                    if state.player_velocity_y < 0:
                        state.player_velocity_y *= JUMP_CUT_MULTIPLIER

        # Only update game if not game over
        if not state.game_over:
            # Store previous position for collision detection
            prev_player_y = state.player_y

            # Apply gravity
            state.player_velocity_y += GRAVITY
            state.player_y += state.player_velocity_y

            # Check ground collision
            on_surface = False
            if state.player_y >= GROUND_Y - PLAYER_HEIGHT:
                state.player_y = GROUND_Y - PLAYER_HEIGHT
                state.player_velocity_y = 0
                state.is_jumping = False
                on_surface = True

                # Game over if player has jumped before and touches ground
                if state.has_jumped:
                    state.game_over = True
                    state.debris = generate_debris(PLAYER_X, state.player_y)
                    pygame.mixer.music.stop()
                    if game.crash_sound:
                        game.crash_sound.play()
                    # Check and save high score
                    if state.score > state.high_score:
                        state.high_score = state.score
                        state.high_score_beaten = True
                        save_high_score(state.score)

            # Check obstacle collisions (landing on top)
            if not on_surface and state.player_velocity_y >= 0:
                for obstacle in state.obstacles:
                    if check_obstacle_collision(PLAYER_X, state.player_y, prev_player_y, obstacle):
                        state.player_y = obstacle.y - PLAYER_HEIGHT
                        state.player_velocity_y = 0
                        state.is_jumping = False
                        on_surface = True
                        # Award point if first time landing on this obstacle
                        if not obstacle.scored:
                            obstacle.scored = True
                            state.score += 1
                        break

            # Process buffered jump (for same-frame landing)
            if state.jump_buffered:
                if on_surface:
                    # Execute the buffered jump
                    state.player_velocity_y = JUMP_STRENGTH
                    state.is_jumping = True
                    state.jump_held = True
                    state.has_jumped = True
                # Clear buffer regardless (don't persist across frames)
                state.jump_buffered = False

            # Move obstacles (speed increases with score)
            current_speed = get_scroll_speed(state.score)
            for obstacle in state.obstacles:
                obstacle.x -= current_speed

            # Remove off-screen obstacles and generate new ones
            if state.obstacles and state.obstacles[0].x + state.obstacles[0].width < 0:
                state.obstacles.pop(0)

            # Generate new obstacle if needed
            if state.obstacles:
                last_obs = state.obstacles[-1]
                if last_obs.x < SCREEN_WIDTH:
                    new_obs = generate_obstacle(last_obs, speed=current_speed)
                    state.obstacles.append(new_obs)

        # Update debris physics during game over
        if state.game_over and state.debris:
            update_debris(state.debris)

        # Clear screen
        game.screen.fill(BLACK)

        # Draw game objects
        draw_ground()
        for obstacle in state.obstacles:
            draw_obstacle(obstacle)

        # Draw player or debris depending on game state
        if state.game_over:
            draw_debris(state.debris)
        else:
            draw_player(PLAYER_X, state.player_y)

        draw_score(state.score, state.high_score)

        # Draw FPS counter
        draw_fps(game.clock.get_fps())

        # Draw game over overlay if game is over
        if state.game_over:
            draw_game_over(state.high_score_beaten)

        # Update display
        pygame.display.flip()

        # Cap frame rate
        game.clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
