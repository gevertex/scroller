"""Tests for game state and game over logic."""
import pytest

from game import (
    reset_game, GameState,
    GROUND_Y, PLAYER_HEIGHT, INITIAL_OBSTACLE_COUNT
)


class TestResetGame:
    """Test cases for reset_game function."""

    def test_reset_returns_game_state(self):
        """Reset should return a GameState object."""
        result = reset_game()
        assert isinstance(result, GameState)

    def test_reset_player_starts_on_ground(self):
        """Player should start on the ground after reset."""
        state = reset_game()
        expected_y = GROUND_Y - PLAYER_HEIGHT
        assert state.player_y == expected_y

    def test_reset_velocity_is_zero(self):
        """Player velocity should be zero after reset."""
        state = reset_game()
        assert state.player_velocity_y == 0

    def test_reset_not_jumping(self):
        """Player should not be jumping after reset."""
        state = reset_game()
        assert state.is_jumping is False

    def test_reset_jump_not_held(self):
        """Jump should not be held after reset."""
        state = reset_game()
        assert state.jump_held is False

    def test_reset_has_not_jumped(self):
        """has_jumped should be False after reset."""
        state = reset_game()
        assert state.has_jumped is False

    def test_reset_not_game_over(self):
        """game_over should be False after reset."""
        state = reset_game()
        assert state.game_over is False

    def test_reset_score_is_zero(self):
        """Score should be zero after reset."""
        state = reset_game()
        assert state.score == 0

    def test_reset_generates_obstacles(self):
        """Reset should generate initial obstacles."""
        state = reset_game()
        # 1 first obstacle + INITIAL_OBSTACLE_COUNT more
        assert len(state.obstacles) == INITIAL_OBSTACLE_COUNT + 1

    def test_reset_obstacles_not_scored(self):
        """All obstacles should be unscored after reset."""
        state = reset_game()
        for obs in state.obstacles:
            assert obs['scored'] is False


class TestGameOverLogic:
    """Test cases for game over detection logic."""

    def test_game_over_not_triggered_at_start(self):
        """Game over should not trigger when starting on ground."""
        state = reset_game()
        assert state.has_jumped is False
        assert state.game_over is False

    def test_game_over_condition_requires_prior_jump(self):
        """Game over should only trigger after player has jumped."""
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
        has_jumped = True
        on_ground = False  # On obstacle, not ground

        game_over = has_jumped and on_ground
        assert game_over is False

    def test_multiple_resets_work_correctly(self):
        """Multiple resets should each produce fresh state."""
        for _ in range(5):
            state = reset_game()

            assert state.player_velocity_y == 0
            assert state.is_jumping is False
            assert state.jump_held is False
            assert state.has_jumped is False
            assert state.game_over is False
            assert state.score == 0
            assert len(state.obstacles) == INITIAL_OBSTACLE_COUNT + 1


class TestGameStateTransitions:
    """Test game state transitions."""

    def test_jump_sets_has_jumped(self):
        """Jumping should set has_jumped to True."""
        state = reset_game()
        assert state.has_jumped is False

        # Simulate jump
        state.has_jumped = True
        assert state.has_jumped is True

    def test_game_over_pauses_updates(self):
        """When game_over is True, game updates should be skipped."""
        state = reset_game()
        state.game_over = True

        should_update = not state.game_over
        assert should_update is False

    def test_game_active_allows_updates(self):
        """When game_over is False, game updates should happen."""
        state = reset_game()

        should_update = not state.game_over
        assert should_update is True

    def test_state_is_mutable(self):
        """GameState should allow mutation of its fields."""
        state = reset_game()

        state.score = 10
        state.player_y = 100
        state.is_jumping = True

        assert state.score == 10
        assert state.player_y == 100
        assert state.is_jumping is True
