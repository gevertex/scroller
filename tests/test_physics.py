"""Tests for physics mechanics."""
import pytest
import sys
sys.path.insert(0, '/Users/georgesapp/Documents/gitrepos/fun_game')

from game import (
    GRAVITY, JUMP_STRENGTH, GROUND_Y,
    PLAYER_HEIGHT, PLAYER_WIDTH,
    MAX_JUMP_HEIGHT
)


class TestPhysicsConstants:
    """Test that physics constants are properly configured."""

    def test_gravity_is_positive(self):
        """Gravity should pull player down (positive value)."""
        assert GRAVITY > 0

    def test_jump_strength_is_negative(self):
        """Jump strength should be negative (upward velocity)."""
        assert JUMP_STRENGTH < 0

    def test_ground_y_is_reasonable(self):
        """Ground should be near bottom of screen."""
        assert GROUND_Y > 200  # Should be in lower half

    def test_player_dimensions_positive(self):
        """Player dimensions should be positive."""
        assert PLAYER_WIDTH > 0
        assert PLAYER_HEIGHT > 0


class TestJumpPhysics:
    """Test jump physics calculations."""

    def test_jump_reaches_expected_height(self):
        """Jump should reach approximately MAX_JUMP_HEIGHT."""
        # Simulate a jump
        velocity = JUMP_STRENGTH
        position = 0  # Start at 0 for calculation
        max_height = 0

        # Simulate until falling back down
        while velocity < 0 or position < 0:
            velocity += GRAVITY
            position += velocity
            if position < max_height:
                max_height = position

        # Max height reached (negative because going up)
        actual_height = abs(max_height)

        # Should be within reasonable range of MAX_JUMP_HEIGHT
        # Allow some tolerance since physics are discrete
        assert actual_height >= MAX_JUMP_HEIGHT * 0.8
        assert actual_height <= MAX_JUMP_HEIGHT * 1.5

    def test_player_returns_to_ground(self):
        """Player should return to starting position after jump."""
        velocity = JUMP_STRENGTH
        position = 0
        frames = 0
        max_frames = 200  # Safety limit

        # Simulate until back at or below starting position
        while frames < max_frames:
            velocity += GRAVITY
            position += velocity
            frames += 1
            if position >= 0:
                break

        assert position >= 0, "Player should return to ground"
        assert frames < max_frames, "Jump should complete in reasonable time"

    def test_short_jump_mechanics(self):
        """Releasing jump early should result in shorter jump."""
        # Full jump
        velocity_full = JUMP_STRENGTH
        position_full = 0
        max_height_full = 0

        for _ in range(100):
            velocity_full += GRAVITY
            position_full += velocity_full
            if position_full < max_height_full:
                max_height_full = position_full

        # Short jump (velocity cut after 5 frames)
        velocity_short = JUMP_STRENGTH
        position_short = 0
        max_height_short = 0

        for i in range(100):
            velocity_short += GRAVITY
            # Simulate early release at frame 5
            if i == 5 and velocity_short < 0:
                velocity_short *= 0.5
            position_short += velocity_short
            if position_short < max_height_short:
                max_height_short = position_short

        # Short jump should reach less height
        assert abs(max_height_short) < abs(max_height_full)

    def test_gravity_accumulates(self):
        """Gravity should accelerate falling speed."""
        velocity = 0
        velocities = []

        for _ in range(10):
            velocity += GRAVITY
            velocities.append(velocity)

        # Each velocity should be greater than the last
        for i in range(1, len(velocities)):
            assert velocities[i] > velocities[i-1]

    def test_jump_arc_is_parabolic(self):
        """Jump should follow a parabolic arc (up then down)."""
        velocity = JUMP_STRENGTH
        position = 0
        positions = []

        for _ in range(60):
            velocity += GRAVITY
            position += velocity
            positions.append(position)

        # Find the peak (minimum position since up is negative)
        peak_index = positions.index(min(positions))

        # Peak should be somewhere in the middle, not at start or end
        assert peak_index > 5
        assert peak_index < len(positions) - 5

        # Before peak, positions should decrease (going up)
        for i in range(1, peak_index):
            assert positions[i] <= positions[i-1] or positions[i-1] < -50

        # After peak, positions should increase (going down)
        for i in range(peak_index + 1, len(positions)):
            if positions[i-1] < 0:  # Still in the air
                assert positions[i] >= positions[i-1]
