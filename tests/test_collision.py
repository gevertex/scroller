"""Tests for collision detection."""
import pytest
import sys
sys.path.insert(0, '/Users/georgesapp/Documents/gitrepos/fun_game')

from game import check_obstacle_collision, PLAYER_WIDTH, PLAYER_HEIGHT


class TestObstacleCollision:
    """Test cases for check_obstacle_collision function."""

    def create_obstacle(self, x, y, width, height):
        """Helper to create an obstacle dict."""
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'scored': False
        }

    def test_landing_on_top_of_obstacle(self):
        """Player landing directly on top of obstacle should collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        # Player positioned so bottom is at obstacle top
        player_x = 100
        player_y = 200 - PLAYER_HEIGHT  # Player bottom at y=200

        assert check_obstacle_collision(player_x, player_y, obstacle) is True

    def test_player_above_obstacle(self):
        """Player well above obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        player_y = 100  # Well above obstacle

        assert check_obstacle_collision(player_x, player_y, obstacle) is False

    def test_player_below_obstacle(self):
        """Player below obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        player_y = 250  # Below obstacle

        assert check_obstacle_collision(player_x, player_y, obstacle) is False

    def test_player_left_of_obstacle(self):
        """Player to the left of obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 50  # Left of obstacle (player right edge at 90, obstacle starts at 100)
        player_y = 200 - PLAYER_HEIGHT

        assert check_obstacle_collision(player_x, player_y, obstacle) is False

    def test_player_right_of_obstacle(self):
        """Player to the right of obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 200  # Right of obstacle (obstacle ends at 180)
        player_y = 200 - PLAYER_HEIGHT

        assert check_obstacle_collision(player_x, player_y, obstacle) is False

    def test_player_partially_overlapping_left(self):
        """Player overlapping left edge of obstacle should collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        # Player right edge overlaps obstacle left edge
        player_x = 80  # Player right edge at 120, obstacle starts at 100
        player_y = 200 - PLAYER_HEIGHT

        assert check_obstacle_collision(player_x, player_y, obstacle) is True

    def test_player_partially_overlapping_right(self):
        """Player overlapping right edge of obstacle should collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        # Player left edge overlaps obstacle right edge
        player_x = 160  # Player left at 160, obstacle ends at 180
        player_y = 200 - PLAYER_HEIGHT

        assert check_obstacle_collision(player_x, player_y, obstacle) is True

    def test_collision_tolerance(self):
        """Player slightly below obstacle top (within tolerance) should collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Player bottom is 10 pixels below obstacle top (within 15px tolerance)
        player_y = 200 - PLAYER_HEIGHT + 10

        assert check_obstacle_collision(player_x, player_y, obstacle) is True

    def test_collision_outside_tolerance(self):
        """Player too far below obstacle top should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Player bottom is 20 pixels below obstacle top (outside 15px tolerance)
        player_y = 200 - PLAYER_HEIGHT + 20

        assert check_obstacle_collision(player_x, player_y, obstacle) is False
