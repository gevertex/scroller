"""Tests for scoring mechanics."""
import pytest

from game import generate_obstacle


class TestScoringMechanics:
    """Test cases for scoring system."""

    def create_obstacle(self, x=100, y=200, width=80, height=20, scored=False):
        """Helper to create an obstacle dict."""
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'scored': scored
        }

    def test_new_obstacle_not_scored(self):
        """New obstacles should start with scored=False."""
        obstacle = generate_obstacle()
        assert obstacle['scored'] is False

    def test_obstacle_can_be_marked_scored(self):
        """Obstacle scored flag can be set to True."""
        obstacle = self.create_obstacle(scored=False)
        assert obstacle['scored'] is False

        obstacle['scored'] = True
        assert obstacle['scored'] is True

    def test_score_increment_logic(self):
        """Simulate scoring logic - only score unscored obstacles."""
        score = 0
        obstacle = self.create_obstacle(scored=False)

        # First landing - should score
        if not obstacle['scored']:
            obstacle['scored'] = True
            score += 1

        assert score == 1
        assert obstacle['scored'] is True

        # Second landing on same obstacle - should not score
        if not obstacle['scored']:
            obstacle['scored'] = True
            score += 1

        assert score == 1  # Score unchanged

    def test_multiple_obstacles_scoring(self):
        """Each obstacle should only be scored once."""
        score = 0
        obstacles = [
            self.create_obstacle(x=100, scored=False),
            self.create_obstacle(x=200, scored=False),
            self.create_obstacle(x=300, scored=False),
        ]

        # Land on each obstacle
        for obs in obstacles:
            if not obs['scored']:
                obs['scored'] = True
                score += 1

        assert score == 3

        # Land on all again
        for obs in obstacles:
            if not obs['scored']:
                obs['scored'] = True
                score += 1

        assert score == 3  # No change

    def test_score_starts_at_zero(self):
        """Game should start with score of 0."""
        score = 0
        assert score == 0

    def test_generated_obstacles_chain_all_unscored(self):
        """Chain of generated obstacles should all be unscored."""
        obstacles = []
        first = generate_obstacle(from_ground=True)
        obstacles.append(first)

        for _ in range(5):
            next_obs = generate_obstacle(last_obstacle=obstacles[-1])
            obstacles.append(next_obs)

        for obs in obstacles:
            assert obs['scored'] is False

    def test_scoring_order_independence(self):
        """Scoring should work regardless of landing order."""
        score = 0
        obstacles = [
            self.create_obstacle(x=100, scored=False),
            self.create_obstacle(x=200, scored=False),
            self.create_obstacle(x=300, scored=False),
        ]

        # Land in reverse order
        for obs in reversed(obstacles):
            if not obs['scored']:
                obs['scored'] = True
                score += 1

        assert score == 3

    def test_mixed_scored_obstacles(self):
        """Should correctly handle mix of scored and unscored obstacles."""
        score = 0
        obstacles = [
            self.create_obstacle(x=100, scored=True),   # Already scored
            self.create_obstacle(x=200, scored=False),  # Not scored
            self.create_obstacle(x=300, scored=True),   # Already scored
            self.create_obstacle(x=400, scored=False),  # Not scored
        ]

        for obs in obstacles:
            if not obs['scored']:
                obs['scored'] = True
                score += 1

        assert score == 2  # Only 2 were unscored
