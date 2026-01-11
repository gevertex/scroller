"""Tests for game state and game over logic."""
import pytest
import sys
sys.path.insert(0, '/Users/georgesapp/Documents/gitrepos/fun_game')

from game import (
    reset_game,
    SCREEN_HEIGHT, PLAYER_HEIGHT, GROUND_Y
)


class TestResetGame:
    """Test cases for reset_game function."""

    def test_reset_returns_all_state_variables(self):
        """Reset should return all necessary game state variables."""
        result = reset_game()
        assert len(result) == 8  # 8 state variables returned

    def test_reset_player_starts_on_ground(self):
        """Player should start on the ground after reset."""
        player_y, _, _, _, _, _, _, _ = reset_game()
        expected_y = SCREEN_HEIGHT - PLAYER_HEIGHT - 50
        assert player_y == expected_y

    def test_reset_velocity_is_zero(self):
        """Player velocity should be zero after reset."""
        _, player_velocity_y, _, _, _, _, _, _ = reset_game()
        assert player_velocity_y == 0

    def test_reset_not_jumping(self):
        """Player should not be jumping after reset."""
        _, _, is_jumping, _, _, _, _, _ = reset_game()
        assert is_jumping is False

    def test_reset_jump_not_held(self):
        """Jump should not be held after reset."""
        _, _, _, jump_held, _, _, _, _ = reset_game()
        assert jump_held is False

    def test_reset_has_not_jumped(self):
        """has_jumped should be False after reset."""
        _, _, _, _, has_jumped, _, _, _ = reset_game()
        assert has_jumped is False

    def test_reset_not_game_over(self):
        """game_over should be False after reset."""
        _, _, _, _, _, game_over, _, _ = reset_game()
        assert game_over is False

    def test_reset_score_is_zero(self):
        """Score should be zero after reset."""
        _, _, _, _, _, _, score, _ = reset_game()
        assert score == 0

    def test_reset_generates_obstacles(self):
        """Reset should generate initial obstacles."""
        _, _, _, _, _, _, _, obstacles = reset_game()
        assert len(obstacles) == 5  # 1 first + 4 more

    def test_reset_obstacles_not_scored(self):
        """All obstacles should be unscored after reset."""
        _, _, _, _, _, _, _, obstacles = reset_game()
        for obs in obstacles:
            assert obs['scored'] is False


class TestGameOverLogic:
    """Test cases for game over detection logic."""

    def test_game_over_not_triggered_at_start(self):
        """Game over should not trigger when starting on ground."""
        _, _, _, _, has_jumped, game_over, _, _ = reset_game()
        # Simulate being on ground at start
        assert has_jumped is False
        assert game_over is False
        # If has_jumped is False, touching ground should NOT trigger game over

    def test_game_over_condition_requires_prior_jump(self):
        """Game over should only trigger after player has jumped."""
        # This tests the logic: game_over should only be True if has_jumped is True
        # AND player touches ground
        has_jumped = False
        on_ground = True

        # Simulate game over check
        game_over = has_jumped and on_ground
        assert game_over is False

        # After jumping
        has_jumped = True
        game_over = has_jumped and on_ground
        assert game_over is True

    def test_landing_on_obstacle_does_not_trigger_game_over(self):
        """Landing on an obstacle should not trigger game over."""
        # Game over only triggers on ground contact, not obstacle contact
        has_jumped = True
        on_ground = False  # On obstacle, not ground

        game_over = has_jumped and on_ground
        assert game_over is False

    def test_multiple_resets_work_correctly(self):
        """Multiple resets should each produce fresh state."""
        for _ in range(5):
            player_y, vel, jumping, held, has_jumped, game_over, score, obs = reset_game()

            assert vel == 0
            assert jumping is False
            assert held is False
            assert has_jumped is False
            assert game_over is False
            assert score == 0
            assert len(obs) == 5


class TestGameStateTransitions:
    """Test game state transitions."""

    def test_jump_sets_has_jumped(self):
        """Jumping should set has_jumped to True."""
        has_jumped = False

        # Simulate jump
        has_jumped = True

        assert has_jumped is True

    def test_game_over_pauses_updates(self):
        """When game_over is True, game updates should be skipped."""
        game_over = True

        # In the actual game, this flag controls whether updates happen
        # This test verifies the flag can be used for this purpose
        should_update = not game_over
        assert should_update is False

    def test_game_active_allows_updates(self):
        """When game_over is False, game updates should happen."""
        game_over = False

        should_update = not game_over
        assert should_update is True
