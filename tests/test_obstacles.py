"""Tests for obstacle generation."""
import pytest

from game import (
    generate_obstacle, Obstacle, get_min_gap,
    MIN_OBSTACLE_WIDTH, MAX_OBSTACLE_WIDTH,
    OBSTACLE_THICKNESS,
    MIN_GAP, MAX_GAP,
    MIN_JUMP_FRAMES, GAP_BUFFER,
    BASE_SCROLL_SPEED, MAX_SCROLL_SPEED,
    MAX_JUMP_HEIGHT, MAX_HEIGHT_DIFF,
    MIN_PLATFORM_Y, MAX_PLATFORM_Y,
    GROUND_Y, SCREEN_WIDTH
)


class TestObstacleGeneration:
    """Test cases for generate_obstacle function."""

    def test_obstacle_has_required_attributes(self):
        """Generated obstacle should have all required attributes."""
        obstacle = generate_obstacle()

        assert hasattr(obstacle, 'x')
        assert hasattr(obstacle, 'y')
        assert hasattr(obstacle, 'width')
        assert hasattr(obstacle, 'height')
        assert hasattr(obstacle, 'scored')

    def test_obstacle_is_dataclass(self):
        """Generated obstacle should be an Obstacle dataclass."""
        obstacle = generate_obstacle()
        assert isinstance(obstacle, Obstacle)

    def test_obstacle_width_in_range(self):
        """Obstacle width should be within defined range."""
        for _ in range(50):
            obstacle = generate_obstacle()
            assert MIN_OBSTACLE_WIDTH <= obstacle.width <= MAX_OBSTACLE_WIDTH

    def test_obstacle_height_is_fixed(self):
        """Obstacle height should be fixed thickness."""
        for _ in range(50):
            obstacle = generate_obstacle()
            assert obstacle.height == OBSTACLE_THICKNESS

    def test_obstacle_starts_offscreen(self):
        """First obstacle should start off-screen to the right."""
        obstacle = generate_obstacle()
        assert obstacle.x >= SCREEN_WIDTH

    def test_obstacle_scored_initially_false(self):
        """New obstacle should have scored set to False."""
        obstacle = generate_obstacle()
        assert obstacle.scored is False

    def test_from_ground_y_position(self):
        """Obstacle from ground should be reachable by jumping."""
        for _ in range(50):
            obstacle = generate_obstacle(from_ground=True)
            # Should be within jump range from ground
            assert obstacle.y <= GROUND_Y
            assert obstacle.y >= MIN_PLATFORM_Y

    def test_chained_obstacle_horizontal_gap_base_speed(self):
        """Chained obstacle at base speed should use MIN_GAP."""
        first = generate_obstacle(from_ground=True)

        for _ in range(50):
            second = generate_obstacle(last_obstacle=first, speed=BASE_SCROLL_SPEED)
            gap = second.x - (first.x + first.width)
            assert MIN_GAP <= gap <= MAX_GAP

    def test_chained_obstacle_reachable_height(self):
        """Chained obstacle should be reachable from previous one."""
        first = generate_obstacle(from_ground=True)

        for _ in range(50):
            second = generate_obstacle(last_obstacle=first)
            height_diff = second.y - first.y

            # Player can jump up MAX_JUMP_HEIGHT or fall down
            # Going up (negative diff) should be within jump range
            if height_diff < 0:
                assert abs(height_diff) <= MAX_JUMP_HEIGHT
            # Going down (positive diff) should be within reasonable range
            else:
                assert height_diff <= MAX_HEIGHT_DIFF

    def test_obstacle_chain_generation(self):
        """Should be able to generate a chain of reachable obstacles."""
        obstacles = []

        # Generate first obstacle from ground
        first = generate_obstacle(from_ground=True)
        obstacles.append(first)

        # Generate chain of 10 obstacles
        for _ in range(10):
            next_obs = generate_obstacle(last_obstacle=obstacles[-1])
            obstacles.append(next_obs)

        assert len(obstacles) == 11

        # Verify each obstacle has valid properties
        for obs in obstacles:
            assert MIN_OBSTACLE_WIDTH <= obs.width <= MAX_OBSTACLE_WIDTH
            assert obs.height == OBSTACLE_THICKNESS
            assert obs.scored is False

    def test_obstacle_y_within_bounds(self):
        """Obstacle Y position should stay within screen bounds."""
        first = generate_obstacle(from_ground=True)

        for _ in range(100):
            obstacle = generate_obstacle(last_obstacle=first)
            assert obstacle.y >= MIN_PLATFORM_Y
            assert obstacle.y <= MAX_PLATFORM_Y
            first = obstacle  # Chain them


class TestGapScaling:
    """Test cases for dynamic gap scaling based on speed."""

    def test_get_min_gap_at_base_speed(self):
        """At base speed, min gap should equal MIN_GAP."""
        assert get_min_gap(BASE_SCROLL_SPEED) == MIN_GAP

    def test_get_min_gap_increases_with_speed(self):
        """Min gap should increase as speed increases."""
        gap_at_base = get_min_gap(BASE_SCROLL_SPEED)
        gap_at_max = get_min_gap(MAX_SCROLL_SPEED)
        assert gap_at_max > gap_at_base

    def test_get_min_gap_at_max_speed(self):
        """At max speed, min gap should ensure jumpability."""
        min_gap = get_min_gap(MAX_SCROLL_SPEED)
        # Gap + min obstacle width should exceed scroll distance during jump
        scroll_distance = MAX_SCROLL_SPEED * MIN_JUMP_FRAMES
        assert min_gap + MIN_OBSTACLE_WIDTH >= scroll_distance

    def test_get_min_gap_never_below_min(self):
        """Min gap should never go below MIN_GAP constant."""
        for speed in [1, 2, 3, 4, 5]:
            assert get_min_gap(speed) >= MIN_GAP

    def test_get_min_gap_formula(self):
        """Verify the gap calculation formula."""
        speed = 10
        expected = max(MIN_GAP, int((speed * MIN_JUMP_FRAMES) - MIN_OBSTACLE_WIDTH + GAP_BUFFER))
        assert get_min_gap(speed) == expected

    def test_chained_obstacle_gap_at_max_speed(self):
        """At max speed, obstacles should have larger gaps."""
        first = generate_obstacle(from_ground=True)
        min_gap_at_max = get_min_gap(MAX_SCROLL_SPEED)
        # At high speeds, max_gap scales up to match min_gap
        max_gap_at_max = max(min_gap_at_max, MAX_GAP)

        for _ in range(50):
            second = generate_obstacle(last_obstacle=first, speed=MAX_SCROLL_SPEED)
            gap = second.x - (first.x + first.width)
            assert gap >= min_gap_at_max
            assert gap <= max_gap_at_max

    def test_obstacles_landable_at_max_speed(self):
        """Obstacles generated at max speed should be theoretically landable."""
        first = generate_obstacle(from_ground=True)

        for _ in range(50):
            second = generate_obstacle(last_obstacle=first, speed=MAX_SCROLL_SPEED)
            gap = second.x - (first.x + first.width)

            # During a minimum jump, the world scrolls this distance
            scroll_distance = MAX_SCROLL_SPEED * MIN_JUMP_FRAMES

            # For the player to land: gap + obstacle_width > scroll_distance
            # (approximately, with some buffer for the landing window)
            assert gap + second.width > scroll_distance - GAP_BUFFER
