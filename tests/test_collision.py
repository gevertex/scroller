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
        prev_player_y = player_y - 5  # Was slightly above

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is True

    def test_player_above_obstacle(self):
        """Player well above obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        player_y = 100  # Well above obstacle
        prev_player_y = 95  # Was even higher

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False

    def test_player_below_obstacle(self):
        """Player below obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        player_y = 250  # Below obstacle
        prev_player_y = 245  # Was also below

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False

    def test_player_left_of_obstacle(self):
        """Player to the left of obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 50  # Left of obstacle (player right edge at 90, obstacle starts at 100)
        player_y = 200 - PLAYER_HEIGHT
        prev_player_y = player_y - 5

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False

    def test_player_right_of_obstacle(self):
        """Player to the right of obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 200  # Right of obstacle (obstacle ends at 180)
        player_y = 200 - PLAYER_HEIGHT
        prev_player_y = player_y - 5

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False

    def test_player_partially_overlapping_left(self):
        """Player overlapping left edge of obstacle should collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        # Player right edge overlaps obstacle left edge
        player_x = 80  # Player right edge at 120, obstacle starts at 100
        player_y = 200 - PLAYER_HEIGHT
        prev_player_y = player_y - 5

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is True

    def test_player_partially_overlapping_right(self):
        """Player overlapping right edge of obstacle should collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        # Player left edge overlaps obstacle right edge
        player_x = 160  # Player left at 160, obstacle ends at 180
        player_y = 200 - PLAYER_HEIGHT
        prev_player_y = player_y - 5

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is True

    def test_collision_tolerance(self):
        """Player slightly below obstacle top (within tolerance) should collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Player bottom is 10 pixels below obstacle top (within obstacle height + 5)
        player_y = 200 - PLAYER_HEIGHT + 10
        prev_player_y = player_y - 5

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is True

    def test_collision_outside_tolerance(self):
        """Player too far below obstacle should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Player bottom is 30 pixels below obstacle top (outside obstacle height + 5)
        player_y = 200 - PLAYER_HEIGHT + 30
        prev_player_y = player_y - 5  # Was also below obstacle

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False


class TestPassThroughDetection:
    """Test cases for detecting when player passes through obstacle at high speed."""

    def create_obstacle(self, x, y, width, height):
        """Helper to create an obstacle dict."""
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'scored': False
        }

    def test_high_speed_pass_through_detected(self):
        """Player falling fast enough to skip past obstacle should still collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Previous frame: player bottom at 180 (above obstacle top at 200)
        prev_player_y = 180 - PLAYER_HEIGHT
        # Current frame: player bottom at 230 (below obstacle bottom at 220)
        player_y = 230 - PLAYER_HEIGHT

        # Should detect the pass-through
        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is True

    def test_very_high_speed_pass_through(self):
        """Player falling extremely fast should still be caught."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Previous frame: player bottom at 100 (well above)
        prev_player_y = 100 - PLAYER_HEIGHT
        # Current frame: player bottom at 300 (well below)
        player_y = 300 - PLAYER_HEIGHT

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is True

    def test_no_false_positive_when_starting_below(self):
        """Player who was already below obstacle should not trigger collision."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Previous frame: player bottom at 250 (already below obstacle)
        prev_player_y = 250 - PLAYER_HEIGHT
        # Current frame: player bottom at 260 (still below, falling further)
        player_y = 260 - PLAYER_HEIGHT

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False

    def test_no_collision_when_rising(self):
        """Player moving upward through obstacle position should not collide."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        player_x = 100
        # Previous frame: player bottom at 210 (below obstacle top)
        prev_player_y = 210 - PLAYER_HEIGHT
        # Current frame: player bottom at 190 (above obstacle top, moving up)
        player_y = 190 - PLAYER_HEIGHT

        # Rising through should not count as landing
        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False

    def test_pass_through_requires_horizontal_alignment(self):
        """Pass-through detection should still require horizontal overlap."""
        obstacle = self.create_obstacle(100, 200, 80, 20)
        # Player to the left of obstacle
        player_x = 20  # Player right edge at 60, obstacle starts at 100
        prev_player_y = 180 - PLAYER_HEIGHT
        player_y = 230 - PLAYER_HEIGHT

        assert check_obstacle_collision(player_x, player_y, prev_player_y, obstacle) is False
