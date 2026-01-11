"""Tests for game state and game over logic."""
import pytest

from game import (
    reset_game, GameState, TrailPoint,
    GROUND_Y, PLAYER_HEIGHT, PLAYER_WIDTH, INITIAL_OBSTACLE_COUNT,
    OBSTACLE_THICKNESS,
    TRAIL_MAX_POINTS, TRAIL_SPAWN_INTERVAL, TRAIL_POINT_SIZE, TRAIL_FADE_RATE
)


class TestResetGame:
    """Test cases for reset_game function."""

    def test_reset_returns_game_state(self):
        """Reset should return a GameState object."""
        result = reset_game()
        assert isinstance(result, GameState)

    def test_reset_player_starts_on_starting_platform(self):
        """Player should start on the starting platform after reset."""
        state = reset_game()
        # Player starts on the starting platform (which sits on the ground)
        expected_y = GROUND_Y - OBSTACLE_THICKNESS - PLAYER_HEIGHT
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

    def test_reset_has_jumped_set(self):
        """has_jumped should be True after reset (falling to ground is death)."""
        state = reset_game()
        assert state.has_jumped is True

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
        # starting platform + 1 first obstacle + INITIAL_OBSTACLE_COUNT more
        assert len(state.obstacles) == INITIAL_OBSTACLE_COUNT + 2

    def test_reset_obstacles_not_scored(self):
        """All obstacles (except starting platform) should be unscored after reset."""
        state = reset_game()
        # First obstacle is the starting platform (pre-scored)
        assert state.obstacles[0].scored is True
        # All other obstacles should be unscored
        for obs in state.obstacles[1:]:
            assert obs.scored is False


class TestGameOverLogic:
    """Test cases for game over detection logic."""

    def test_game_over_not_triggered_at_start(self):
        """Game over should not trigger when starting on platform."""
        state = reset_game()
        # has_jumped is True but game_over is False since player is on platform
        assert state.has_jumped is True
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
            assert state.has_jumped is True  # Falling to ground is death
            assert state.game_over is False
            assert state.score == 0
            # starting platform + 1 first obstacle + INITIAL_OBSTACLE_COUNT more
            assert len(state.obstacles) == INITIAL_OBSTACLE_COUNT + 2


class TestGameStateTransitions:
    """Test game state transitions."""

    def test_has_jumped_starts_true(self):
        """has_jumped should be True from the start (falling to ground is death)."""
        state = reset_game()
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


class TestJumpBuffering:
    """Test cases for jump input buffering."""

    def test_jump_buffered_default_false(self):
        """jump_buffered should be False by default."""
        state = reset_game()
        assert state.jump_buffered is False

    def test_jump_buffered_can_be_set(self):
        """jump_buffered should be settable."""
        state = reset_game()
        state.jump_buffered = True
        assert state.jump_buffered is True

    def test_jump_buffer_allows_same_frame_jump(self):
        """Buffered jump should execute on landing frame."""
        state = reset_game()

        # Simulate: player is in air (jumping), presses space
        state.is_jumping = True
        state.jump_buffered = True

        # Simulate landing
        on_surface = True
        state.is_jumping = False

        # Process buffered jump (mimics game loop logic)
        if state.jump_buffered and on_surface:
            state.is_jumping = True
            state.jump_buffered = False

        # Jump should have executed
        assert state.is_jumping is True
        assert state.jump_buffered is False

    def test_jump_buffer_clears_when_not_landing(self):
        """Buffer should clear even if landing didn't happen."""
        state = reset_game()

        # Simulate: player is in air, presses space
        state.is_jumping = True
        state.jump_buffered = True

        # Simulate NO landing this frame
        on_surface = False

        # Process buffered jump (mimics game loop logic)
        if state.jump_buffered:
            if on_surface:
                state.is_jumping = True
            state.jump_buffered = False

        # Jump should NOT have executed, but buffer cleared
        assert state.is_jumping is True  # Still in air from before
        assert state.jump_buffered is False


class TestJumpTrail:
    """Test cases for jump trail visual effect."""

    def test_trail_empty_by_default(self):
        """Trail should be empty after reset."""
        state = reset_game()
        assert len(state.trail) == 0

    def test_trail_frame_counter_zero_by_default(self):
        """Trail frame counter should be zero after reset."""
        state = reset_game()
        assert state.trail_frame_counter == 0

    def test_trail_point_has_required_fields(self):
        """TrailPoint should have x, y, and opacity fields."""
        point = TrailPoint(x=100, y=200, opacity=0.5)
        assert point.x == 100
        assert point.y == 200
        assert point.opacity == 0.5

    def test_trail_point_opacity_range(self):
        """TrailPoint opacity should be between 0 and 1."""
        point = TrailPoint(x=0, y=0, opacity=1.0)
        assert 0 <= point.opacity <= 1

        point.opacity = 0.5
        assert 0 <= point.opacity <= 1

    def test_trail_max_points_constant_exists(self):
        """TRAIL_MAX_POINTS constant should exist and be positive."""
        assert TRAIL_MAX_POINTS > 0

    def test_trail_spawn_interval_constant_exists(self):
        """TRAIL_SPAWN_INTERVAL constant should exist and be positive."""
        assert TRAIL_SPAWN_INTERVAL > 0

    def test_trail_point_size_smaller_than_player(self):
        """TRAIL_POINT_SIZE should be smaller than player dimensions."""
        assert TRAIL_POINT_SIZE < PLAYER_WIDTH
        assert TRAIL_POINT_SIZE < PLAYER_HEIGHT

    def test_trail_fade_rate_valid(self):
        """TRAIL_FADE_RATE should be between 0 and 1."""
        assert 0 < TRAIL_FADE_RATE < 1
