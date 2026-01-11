import pygame
import sys
import random

# Screen settings (constants)
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
SCROLL_SPEED = 4
MIN_OBSTACLE_WIDTH = 60
MAX_OBSTACLE_WIDTH = 150
MIN_OBSTACLE_HEIGHT = 15
MAX_OBSTACLE_HEIGHT = 40
MIN_GAP = 60   # Minimum horizontal gap between obstacles
MAX_GAP = 130  # Maximum horizontal gap between obstacles
MAX_JUMP_HEIGHT = 120  # Maximum height player can jump
MAX_HEIGHT_DIFF = 80  # Max height difference to ensure jumpability
MIN_PLATFORM_Y = 150  # Highest platforms can go (from top of screen)
MAX_PLATFORM_Y = GROUND_Y - 60  # Lowest platforms can be

# Frame rate
FPS = 60

# Pygame objects (initialized at runtime)
screen = None
font = None
clock = None


def init_pygame():
    """Initialize pygame and create display objects."""
    global screen, font, clock
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jump Game")
    # Try to load font, but handle if unavailable (Python 3.14 compatibility)
    try:
        font = pygame.font.Font(None, 36)
    except (NotImplementedError, ImportError):
        font = None
    clock = pygame.time.Clock()


def generate_obstacle(last_obstacle=None, from_ground=False):
    """Generate a new floating obstacle that is reachable from the last one."""
    width = random.randint(MIN_OBSTACLE_WIDTH, MAX_OBSTACLE_WIDTH)
    height = random.randint(MIN_OBSTACLE_HEIGHT, MAX_OBSTACLE_HEIGHT)

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
        x = SCREEN_WIDTH + random.randint(100, 300)
        y = random.randint(GROUND_Y - MAX_JUMP_HEIGHT, MAX_PLATFORM_Y)
    else:
        x = SCREEN_WIDTH + random.randint(100, 300)
        y = random.randint(MIN_PLATFORM_Y, MAX_PLATFORM_Y)

    return {
        'x': x,
        'y': y,
        'width': width,
        'height': height,  # Fixed height, floating platform
        'scored': False  # Track if player has landed on this
    }


def draw_player(x, y):
    """Draw the player as a white outlined rectangle."""
    pygame.draw.rect(screen, WHITE, (x, y, PLAYER_WIDTH, PLAYER_HEIGHT), 2)


def draw_ground():
    """Draw the ground line."""
    pygame.draw.line(screen, WHITE, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)


def draw_digit(x, y, digit, size=20):
    """Draw a single digit using vector lines (7-segment style)."""
    w = size // 2  # Width
    h = size       # Height
    t = 2          # Thickness

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
        text_rect = text_surface.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(text_surface, text_rect)
    else:
        # Draw score using vector digit rendering
        score_str = str(score)
        digit_width = 16
        total_width = len(score_str) * digit_width
        start_x = SCREEN_WIDTH - 20 - total_width

        for i, char in enumerate(score_str):
            draw_digit(start_x + i * digit_width, 15, int(char), size=20)


def draw_obstacle(obstacle):
    """Draw an obstacle as a solid white rectangle."""
    pygame.draw.rect(screen, WHITE, (obstacle['x'], obstacle['y'],
                                      obstacle['width'], obstacle['height']))


def check_obstacle_collision(player_x, player_y, obstacle):
    """Check if player is landing on top of a floating obstacle."""
    player_bottom = player_y + PLAYER_HEIGHT
    player_right = player_x + PLAYER_WIDTH
    player_left = player_x

    obs_top = obstacle['y']
    obs_left = obstacle['x']
    obs_right = obstacle['x'] + obstacle['width']

    # Check if player is horizontally aligned with obstacle
    if player_right > obs_left and player_left < obs_right:
        # Check if player is landing on top (feet near platform top)
        if player_bottom >= obs_top and player_bottom <= obs_top + 15:
            return True
    return False


def main():
    # Initialize pygame
    init_pygame()

    # Game state
    player_y = SCREEN_HEIGHT - PLAYER_HEIGHT - 50  # Start on ground
    player_velocity_y = 0
    is_jumping = False
    jump_held = False
    score = 0

    # Generate initial obstacles
    obstacles = []
    # First obstacle must be reachable from the ground
    first_obs = generate_obstacle(from_ground=True)
    obstacles.append(first_obs)
    last_obs = first_obs
    for _ in range(4):
        new_obs = generate_obstacle(last_obs)
        obstacles.append(new_obs)
        last_obs = new_obs

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Only jump if on the ground or on an obstacle
                    if not is_jumping:
                        player_velocity_y = JUMP_STRENGTH
                        is_jumping = True
                        jump_held = True

                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    jump_held = False
                    # Cut the jump short if still moving upward
                    if player_velocity_y < 0:
                        player_velocity_y *= 0.5  # Reduce upward velocity

        # Apply gravity
        player_velocity_y += GRAVITY
        player_y += player_velocity_y

        # Check ground collision
        on_surface = False
        if player_y >= GROUND_Y - PLAYER_HEIGHT:
            player_y = GROUND_Y - PLAYER_HEIGHT
            player_velocity_y = 0
            is_jumping = False
            on_surface = True

        # Check obstacle collisions (landing on top)
        if not on_surface and player_velocity_y >= 0:  # Only check when falling
            for obstacle in obstacles:
                if check_obstacle_collision(PLAYER_X, player_y, obstacle):
                    player_y = obstacle['y'] - PLAYER_HEIGHT
                    player_velocity_y = 0
                    is_jumping = False
                    on_surface = True
                    # Award point if first time landing on this obstacle
                    if not obstacle['scored']:
                        obstacle['scored'] = True
                        score += 1
                    break

        # Move obstacles
        for obstacle in obstacles:
            obstacle['x'] -= SCROLL_SPEED

        # Remove off-screen obstacles and generate new ones
        if obstacles and obstacles[0]['x'] + obstacles[0]['width'] < 0:
            obstacles.pop(0)

        # Generate new obstacle if needed
        if obstacles:
            last_obs = obstacles[-1]
            if last_obs['x'] < SCREEN_WIDTH:
                new_obs = generate_obstacle(last_obs)
                obstacles.append(new_obs)

        # Clear screen
        screen.fill(BLACK)

        # Draw game objects
        draw_ground()
        for obstacle in obstacles:
            draw_obstacle(obstacle)
        draw_player(PLAYER_X, player_y)
        draw_score(score)

        # Update display
        pygame.display.flip()

        # Cap frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
