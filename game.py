import pygame
import sys
import random
import math
from dataclasses import dataclass, field
from typing import List, Dict

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
MIN_GAP = 60   # Minimum horizontal gap between obstacles
MAX_GAP = 130  # Maximum horizontal gap between obstacles
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
    obstacles: List[Dict] = field(default_factory=list)
    debris: List[Dict] = field(default_factory=list)  # Explosion particles


# Pygame objects (initialized at runtime)
screen = None
font = None
clock = None
crash_sound = None


def init_pygame():
    """Initialize pygame and create display objects."""
    global screen, font, clock, crash_sound
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        pygame.mixer.music.load("background_music.mp3")
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    except pygame.error:
        pass  # Music file not found

    # Load crash sound effect
    try:
        crash_sound = pygame.mixer.Sound("crash.wav")
    except pygame.error:
        crash_sound = None  # Sound file not found


def generate_obstacle(last_obstacle=None, from_ground=False):
    """Generate a new floating obstacle that is reachable from the last one."""
    width = random.randint(MIN_OBSTACLE_WIDTH, MAX_OBSTACLE_WIDTH)

    # Position obstacle off-screen to the right
    if last_obstacle and not from_ground:
        x = last_obstacle['x'] + last_obstacle['width'] + random.randint(MIN_GAP, MAX_GAP)
        # Ensure platform is reachable from last obstacle
        last_top = last_obstacle['y']
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

    return {
        'x': x,
        'y': y,
        'width': width,
        'height': OBSTACLE_THICKNESS,  # Fixed thickness for all platforms
        'scored': False  # Track if player has landed on this
    }


def draw_player(x, y):
    """Draw the player as a white outlined rectangle."""
    pygame.draw.rect(screen, WHITE, (x, y, PLAYER_WIDTH, PLAYER_HEIGHT), LINE_THICKNESS)


def draw_ground():
    """Draw the ground line."""
    pygame.draw.line(screen, WHITE, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), LINE_THICKNESS)


def draw_digit(x, y, digit, size=SCORE_DIGIT_SIZE):
    """Draw a single digit using vector lines (7-segment style)."""
    w = size // 2  # Width
    h = size       # Height
    t = LINE_THICKNESS

    # Segment definitions: (start_x, start_y, end_x, end_y) relative to top-left
    segments = {
        'top':    (0, 0, w, 0),
        'mid':    (0, h//2, w, h//2),
        'bot':    (0, h, w, h),
        'tl':     (0, 0, 0, h//2),
        'tr':     (w, 0, w, h//2),
        'bl':     (0, h//2, 0, h),
        'br':     (w, h//2, w, h),
    }

    # Which segments are on for each digit
    digit_segments = {
        0: ['top', 'bot', 'tl', 'tr', 'bl', 'br'],
        1: ['tr', 'br'],
        2: ['top', 'mid', 'bot', 'tr', 'bl'],
        3: ['top', 'mid', 'bot', 'tr', 'br'],
        4: ['mid', 'tl', 'tr', 'br'],
        5: ['top', 'mid', 'bot', 'tl', 'br'],
        6: ['top', 'mid', 'bot', 'tl', 'bl', 'br'],
        7: ['top', 'tr', 'br'],
        8: ['top', 'mid', 'bot', 'tl', 'tr', 'bl', 'br'],
        9: ['top', 'mid', 'bot', 'tl', 'tr', 'br'],
    }

    for seg_name in digit_segments.get(digit, []):
        seg = segments[seg_name]
        pygame.draw.line(screen, WHITE,
                        (x + seg[0], y + seg[1]),
                        (x + seg[2], y + seg[3]), t)


def draw_score(score):
    """Draw the score in the top right corner."""
    if font:
        text_surface = font.render(f"Score: {score}", True, WHITE)
        text_rect = text_surface.get_rect(topright=(SCREEN_WIDTH - SCORE_PADDING, SCORE_PADDING))
        screen.blit(text_surface, text_rect)
    else:
        # Draw score using vector digit rendering
        score_str = str(score)
        total_width = len(score_str) * SCORE_DIGIT_WIDTH
        start_x = SCREEN_WIDTH - SCORE_PADDING - total_width

        for i, char in enumerate(score_str):
            draw_digit(start_x + i * SCORE_DIGIT_WIDTH, SCORE_PADDING - 5, int(char))


def draw_obstacle(obstacle):
    """Draw an obstacle as a solid white rectangle."""
    pygame.draw.rect(screen, WHITE, (obstacle['x'], obstacle['y'],
                                      obstacle['width'], obstacle['height']))


def draw_text(text, y_position, size=20):
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


def draw_letter(x, y, letter, size=SCORE_DIGIT_SIZE):
    """Draw a letter using vector lines."""
    w = size // 2
    h = size
    t = LINE_THICKNESS

    # Simple segment-based letters
    letter_segments = {
        'A': [(0, h, 0, h//3), (0, h//3, w//2, 0), (w//2, 0, w, h//3), (w, h//3, w, h), (0, h//2, w, h//2)],
        'E': [(0, 0, 0, h), (0, 0, w, 0), (0, h//2, w*2//3, h//2), (0, h, w, h)],
        'G': [(w, h//3, w//2, 0), (w//2, 0, 0, h//3), (0, h//3, 0, h*2//3), (0, h*2//3, w//2, h), (w//2, h, w, h*2//3), (w, h*2//3, w, h//2), (w, h//2, w//2, h//2)],
        'M': [(0, h, 0, 0), (0, 0, w//2, h//2), (w//2, h//2, w, 0), (w, 0, w, h)],
        'O': [(0, h//4, 0, h*3//4), (0, h//4, w//2, 0), (w//2, 0, w, h//4), (w, h//4, w, h*3//4), (w, h*3//4, w//2, h), (w//2, h, 0, h*3//4)],
        'P': [(0, h, 0, 0), (0, 0, w, 0), (w, 0, w, h//2), (w, h//2, 0, h//2)],
        'R': [(0, h, 0, 0), (0, 0, w, 0), (w, 0, w, h//2), (w, h//2, 0, h//2), (0, h//2, w, h)],
        'S': [(w, h//4, w//2, 0), (w//2, 0, 0, h//4), (0, h//4, 0, h//2), (0, h//2, w, h//2), (w, h//2, w, h*3//4), (w, h*3//4, w//2, h), (w//2, h, 0, h*3//4)],
        'T': [(0, 0, w, 0), (w//2, 0, w//2, h)],
        'V': [(0, 0, w//2, h), (w//2, h, w, 0)],
        'N': [(0, h, 0, 0), (0, 0, w, h), (w, h, w, 0)],
        'I': [(w//4, 0, w*3//4, 0), (w//2, 0, w//2, h), (w//4, h, w*3//4, h)],
    }

    if letter in letter_segments:
        for seg in letter_segments[letter]:
            pygame.draw.line(screen, WHITE, (x + seg[0], y + seg[1]), (x + seg[2], y + seg[3]), t)


def draw_game_over():
    """Draw game over overlay."""
    draw_text("GAME OVER", SCREEN_HEIGHT // 3, size=GAME_OVER_TEXT_SIZE)
    draw_text("PRESS ENTER TO RESET", SCREEN_HEIGHT // 3 + 50, size=GAME_OVER_SUBTEXT_SIZE)


def generate_debris(player_x, player_y):
    """Generate debris particles from player position for explosion effect.

    Args:
        player_x: Player's x position
        player_y: Player's y position

    Returns:
        List of debris particle dictionaries
    """
    debris = []
    center_x = player_x + PLAYER_WIDTH // 2
    center_y = player_y + PLAYER_HEIGHT // 2

    for _ in range(DEBRIS_COUNT):
        # Random angle for explosion direction
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(DEBRIS_SPEED_MIN, DEBRIS_SPEED_MAX)

        # Calculate velocity components
        vel_x = math.cos(angle) * speed
        vel_y = math.sin(angle) * speed - 5  # Bias upward for better visual

        # Random starting position within the player bounds
        start_x = player_x + random.randint(0, PLAYER_WIDTH)
        start_y = player_y + random.randint(0, PLAYER_HEIGHT)

        debris.append({
            'x': start_x,
            'y': start_y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'size': random.randint(DEBRIS_SIZE_MIN, DEBRIS_SIZE_MAX),
            'bounces': 0  # Track number of bounces
        })

    return debris


def update_debris(debris_list):
    """Update debris physics - gravity, movement, and ground bouncing.

    Args:
        debris_list: List of debris particle dictionaries
    """
    for debris in debris_list:
        # Apply gravity
        debris['vel_y'] += DEBRIS_GRAVITY

        # Apply friction to horizontal movement
        debris['vel_x'] *= DEBRIS_FRICTION

        # Update position
        debris['x'] += debris['vel_x']
        debris['y'] += debris['vel_y']

        # Ground collision and bounce
        if debris['y'] + debris['size'] >= GROUND_Y:
            debris['y'] = GROUND_Y - debris['size']
            debris['vel_y'] = -debris['vel_y'] * DEBRIS_BOUNCE_DAMPING
            debris['bounces'] += 1

            # Stop bouncing if velocity is very small
            if abs(debris['vel_y']) < 1:
                debris['vel_y'] = 0


def draw_debris(debris_list):
    """Draw all debris particles.

    Args:
        debris_list: List of debris particle dictionaries
    """
    for debris in debris_list:
        pygame.draw.rect(
            screen, WHITE,
            (int(debris['x']), int(debris['y']), debris['size'], debris['size']),
            LINE_THICKNESS
        )


def check_obstacle_collision(player_x, player_y, prev_player_y, obstacle):
    """Check if player is landing on top of a floating obstacle.

    Uses both current and previous position to detect if player passed through
    the obstacle between frames (prevents falling through at high velocities).
    """
    player_bottom = player_y + PLAYER_HEIGHT
    prev_player_bottom = prev_player_y + PLAYER_HEIGHT
    player_right = player_x + PLAYER_WIDTH
    player_left = player_x

    obs_top = obstacle['y']
    obs_bottom = obstacle['y'] + obstacle['height']
    obs_left = obstacle['x']
    obs_right = obstacle['x'] + obstacle['width']

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


def get_scroll_speed(score):
    """Calculate scroll speed based on current score."""
    speed = BASE_SCROLL_SPEED + (score * SPEED_INCREMENT)
    return min(speed, MAX_SCROLL_SPEED)


def reset_game():
    """Reset game state for a new game.

    Returns:
        GameState: Fresh game state with player on ground and initial obstacles.
    """
    # Generate initial obstacles
    obstacles = []
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
        obstacles=obstacles
    )


def main():
    # Initialize pygame
    init_pygame()

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
                        state.player_velocity_y *= 0.5

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
                    if crash_sound:
                        crash_sound.play()

            # Check obstacle collisions (landing on top)
            if not on_surface and state.player_velocity_y >= 0:
                for obstacle in state.obstacles:
                    if check_obstacle_collision(PLAYER_X, state.player_y, prev_player_y, obstacle):
                        state.player_y = obstacle['y'] - PLAYER_HEIGHT
                        state.player_velocity_y = 0
                        state.is_jumping = False
                        on_surface = True
                        # Award point if first time landing on this obstacle
                        if not obstacle['scored']:
                            obstacle['scored'] = True
                            state.score += 1
                        break

            # Move obstacles (speed increases with score)
            current_speed = get_scroll_speed(state.score)
            for obstacle in state.obstacles:
                obstacle['x'] -= current_speed

            # Remove off-screen obstacles and generate new ones
            if state.obstacles and state.obstacles[0]['x'] + state.obstacles[0]['width'] < 0:
                state.obstacles.pop(0)

            # Generate new obstacle if needed
            if state.obstacles:
                last_obs = state.obstacles[-1]
                if last_obs['x'] < SCREEN_WIDTH:
                    new_obs = generate_obstacle(last_obs)
                    state.obstacles.append(new_obs)

        # Update debris physics during game over
        if state.game_over and state.debris:
            update_debris(state.debris)

        # Clear screen
        screen.fill(BLACK)

        # Draw game objects
        draw_ground()
        for obstacle in state.obstacles:
            draw_obstacle(obstacle)

        # Draw player or debris depending on game state
        if state.game_over:
            draw_debris(state.debris)
        else:
            draw_player(PLAYER_X, state.player_y)

        draw_score(state.score)

        # Draw game over overlay if game is over
        if state.game_over:
            draw_game_over()

        # Update display
        pygame.display.flip()

        # Cap frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
