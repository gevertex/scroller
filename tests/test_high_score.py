"""Tests for high score save/load with tamper protection."""
import json
import os
import pytest

from game import (
    save_high_score,
    load_high_score,
    reset_game,
    _compute_score_signature,
    HIGH_SCORE_PATH,
    HIGH_SCORE_SECRET,
)


@pytest.fixture
def clean_high_score_file():
    """Remove high score file before and after test."""
    if HIGH_SCORE_PATH.exists():
        os.remove(HIGH_SCORE_PATH)
    yield
    if HIGH_SCORE_PATH.exists():
        os.remove(HIGH_SCORE_PATH)


class TestHighScoreSaveLoad:
    """Test cases for high score persistence."""

    def test_save_and_load_high_score(self, clean_high_score_file):
        """Saving and loading should return the same score."""
        assert save_high_score(42)
        assert load_high_score() == 42

    def test_load_returns_zero_when_no_file(self, clean_high_score_file):
        """Loading without a file should return 0."""
        assert load_high_score() == 0

    def test_save_overwrites_previous_score(self, clean_high_score_file):
        """Saving a new score should overwrite the previous one."""
        save_high_score(10)
        save_high_score(20)
        assert load_high_score() == 20

    def test_save_returns_true_on_success(self, clean_high_score_file):
        """save_high_score should return True on success."""
        assert save_high_score(100) is True


class TestTamperProtection:
    """Test cases for tamper detection."""

    def test_tampered_score_returns_zero(self, clean_high_score_file):
        """Modifying the score without updating signature returns 0."""
        save_high_score(50)

        # Tamper with the score
        with open(HIGH_SCORE_PATH, "r") as f:
            data = json.load(f)
        data["high_score"] = 9999
        with open(HIGH_SCORE_PATH, "w") as f:
            json.dump(data, f)

        assert load_high_score() == 0

    def test_tampered_signature_returns_zero(self, clean_high_score_file):
        """Modifying the signature returns 0."""
        save_high_score(50)

        # Tamper with the signature
        with open(HIGH_SCORE_PATH, "r") as f:
            data = json.load(f)
        data["signature"] = "invalid_signature"
        with open(HIGH_SCORE_PATH, "w") as f:
            json.dump(data, f)

        assert load_high_score() == 0

    def test_missing_signature_returns_zero(self, clean_high_score_file):
        """File without signature returns 0."""
        with open(HIGH_SCORE_PATH, "w") as f:
            json.dump({"high_score": 100}, f)

        assert load_high_score() == 0

    def test_invalid_json_returns_zero(self, clean_high_score_file):
        """Invalid JSON file returns 0."""
        with open(HIGH_SCORE_PATH, "w") as f:
            f.write("not valid json")

        assert load_high_score() == 0

    def test_valid_signature_verification(self, clean_high_score_file):
        """Valid signature should pass verification."""
        score = 75
        signature = _compute_score_signature(score)
        data = {"high_score": score, "signature": signature}

        with open(HIGH_SCORE_PATH, "w") as f:
            json.dump(data, f)

        assert load_high_score() == 75


class TestSignatureComputation:
    """Test cases for HMAC signature computation."""

    def test_signature_is_deterministic(self):
        """Same score should produce same signature."""
        sig1 = _compute_score_signature(100)
        sig2 = _compute_score_signature(100)
        assert sig1 == sig2

    def test_different_scores_different_signatures(self):
        """Different scores should produce different signatures."""
        sig1 = _compute_score_signature(100)
        sig2 = _compute_score_signature(101)
        assert sig1 != sig2

    def test_signature_is_hex_string(self):
        """Signature should be a hexadecimal string."""
        sig = _compute_score_signature(42)
        assert isinstance(sig, str)
        # SHA256 produces 64 hex characters
        assert len(sig) == 64
        assert all(c in "0123456789abcdef" for c in sig)


class TestHighScoreIntegration:
    """Integration tests for high score across game sessions."""

    def test_reset_game_loads_high_score_from_disk(self, clean_high_score_file):
        """reset_game should load the persisted high score."""
        save_high_score(150)
        state = reset_game()
        assert state.high_score == 150

    def test_save_restart_load_flow(self, clean_high_score_file):
        """Full flow: save score, simulate restart, verify loaded."""
        # First "session" - save a high score
        save_high_score(88)

        # Simulate game restart by calling reset_game
        state = reset_game()

        # Verify the high score persisted across "sessions"
        assert state.high_score == 88
        assert state.score == 0  # Current score should be fresh

    def test_reset_game_with_no_high_score_file(self, clean_high_score_file):
        """reset_game should handle missing high score file gracefully."""
        state = reset_game()
        assert state.high_score == 0

    def test_reset_game_with_tampered_file(self, clean_high_score_file):
        """reset_game should return 0 for tampered high score file."""
        # Create a tampered file
        with open(HIGH_SCORE_PATH, "w") as f:
            json.dump({"high_score": 9999, "signature": "fake"}, f)

        state = reset_game()
        assert state.high_score == 0
