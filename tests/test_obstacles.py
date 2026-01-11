"""Tests for obstacle generation."""
import pytest

from game import (
    generate_obstacle,
    MIN_OBSTACLE_WIDTH, MAX_OBSTACLE_WIDTH,
    OBSTACLE_THICKNESS,
    MIN_GAP, MAX_GAP,
    MAX_JUMP_HEIGHT, MAX_HEIGHT_DIFF,
    MIN_PLATFORM_Y, MAX_PLATFORM_Y,
    GROUND_Y, SCREEN_WIDTH
)


class TestObstacleGeneration:
    """Test cases for generate_obstacle function."""

    def test_obstacle_has_required_keys(self):
        """Generated obstacle should have all required keys."""
        obstacle = generate_obstacle()

        assert 'x' in obstacle
        assert 'y' in obstacle
        assert 'width' in obstacle
        assert 'height' in obstacle
        assert 'scored' in obstacle

    def test_obstacle_width_in_range(self):
        """Obstacle width should be within defined range."""
        for _ in range(50):
            obstacle = generate_obstacle()
            assert MIN_OBSTACLE_WIDTH <= obstacle['width'] <= MAX_OBSTACLE_WIDTH

    def test_obstacle_height_is_fixed(self):
        """Obstacle height should be fixed thickness."""
        for _ in range(50):
            obstacle = generate_obstacle()
            assert obstacle['height'] == OBSTACLE_THICKNESS

    def test_obstacle_starts_offscreen(self):
        """First obstacle should start off-screen to the right."""
        obstacle = generate_obstacle()
        assert obstacle['x'] >= SCREEN_WIDTH

    def test_obstacle_scored_initially_false(self):
        """New obstacle should have scored set to False."""
        obstacle = generate_obstacle()
        assert obstacle['scored'] is False

    def test_from_ground_y_position(self):
        """Obstacle from ground should be reachable by jumping."""
        for _ in range(50):
            obstacle = generate_obstacle(from_ground=True)
            # Should be within jump range from ground
            assert obstacle['y'] <= GROUND_Y
            assert obstacle['y'] >= MIN_PLATFORM_Y

    def test_chained_obstacle_horizontal_gap(self):
        """Chained obstacle should maintain proper horizontal gap."""
        first = generate_obstacle(from_ground=True)

        for _ in range(50):
            second = generate_obstacle(last_obstacle=first)
            gap = second['x'] - (first['x'] + first['width'])
            assert MIN_GAP <= gap <= MAX_GAP

    def test_chained_obstacle_reachable_height(self):
        """Chained obstacle should be reachable from previous one."""
        first = generate_obstacle(from_ground=True)

        for _ in range(50):
            second = generate_obstacle(last_obstacle=first)
            height_diff = second['y'] - first['y']

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
            assert MIN_OBSTACLE_WIDTH <= obs['width'] <= MAX_OBSTACLE_WIDTH
            assert obs['height'] == OBSTACLE_THICKNESS
            assert obs['scored'] is False

    def test_obstacle_y_within_bounds(self):
        """Obstacle Y position should stay within screen bounds."""
        first = generate_obstacle(from_ground=True)

        for _ in range(100):
            obstacle = generate_obstacle(last_obstacle=first)
            assert obstacle['y'] >= MIN_PLATFORM_Y
            assert obstacle['y'] <= MAX_PLATFORM_Y
            first = obstacle  # Chain them
