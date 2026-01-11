"""Tests for rendering constants and text segment definitions."""
import pytest

from game import (
    # Segment definitions
    DIGIT_SEGMENTS,
    DIGIT_SEGMENT_MAP,
    LETTER_SEGMENTS,
    # Display constants
    TEXT_OUTLINE_OFFSET,
    FPS_DISPLAY_PADDING,
    FPS_DISPLAY_SIZE,
    SCORE_DIGIT_SIZE,
    SCORE_DIGIT_WIDTH,
    LINE_THICKNESS,
)


class TestDigitSegments:
    """Test cases for digit segment definitions."""

    def test_digit_segment_map_has_all_digits(self):
        """DIGIT_SEGMENT_MAP should have entries for digits 0-9."""
        for digit in range(10):
            assert digit in DIGIT_SEGMENT_MAP, f"Missing digit {digit}"

    def test_digit_segment_map_values_are_tuples(self):
        """Each digit's segments should be a tuple of segment names."""
        for digit, segments in DIGIT_SEGMENT_MAP.items():
            assert isinstance(segments, tuple), f"Digit {digit} segments should be tuple"
            assert len(segments) > 0, f"Digit {digit} should have at least one segment"

    def test_digit_segment_map_references_valid_segments(self):
        """All segment names in DIGIT_SEGMENT_MAP should exist in DIGIT_SEGMENTS."""
        for digit, segments in DIGIT_SEGMENT_MAP.items():
            for seg_name in segments:
                assert seg_name in DIGIT_SEGMENTS, \
                    f"Digit {digit} references unknown segment '{seg_name}'"

    def test_digit_segments_has_seven_segments(self):
        """DIGIT_SEGMENTS should define all 7 segments."""
        expected_segments = {'top', 'mid', 'bot', 'tl', 'tr', 'bl', 'br'}
        assert set(DIGIT_SEGMENTS.keys()) == expected_segments

    def test_digit_segments_are_valid_tuples(self):
        """Each segment should be a 4-tuple of coordinates."""
        for name, coords in DIGIT_SEGMENTS.items():
            assert isinstance(coords, tuple), f"Segment '{name}' should be tuple"
            assert len(coords) == 4, f"Segment '{name}' should have 4 values"
            for val in coords:
                assert 0 <= val <= 1, f"Segment '{name}' values should be 0-1 multipliers"


class TestLetterSegments:
    """Test cases for letter segment definitions."""

    def test_letter_segments_has_game_over_letters(self):
        """LETTER_SEGMENTS should have all letters needed for 'GAME OVER'."""
        required = set('GAMEOVER')
        for letter in required:
            assert letter in LETTER_SEGMENTS, f"Missing letter '{letter}' for GAME OVER"

    def test_letter_segments_has_reset_text_letters(self):
        """LETTER_SEGMENTS should have all letters needed for 'PRESS ENTER TO RESET'."""
        required = set('PRESSENTERTOREST')  # Unique letters only
        for letter in required:
            assert letter in LETTER_SEGMENTS, f"Missing letter '{letter}' for reset text"

    def test_letter_segments_has_fps_letters(self):
        """LETTER_SEGMENTS should have letters needed for 'FPS'."""
        required = set('FPS')
        for letter in required:
            assert letter in LETTER_SEGMENTS, f"Missing letter '{letter}' for FPS display"

    def test_letter_segments_has_high_score_letters(self):
        """LETTER_SEGMENTS should have letters needed for 'NEW HIGH SCORE'."""
        required = set('NEWHIGHSCOR')  # Unique letters only
        for letter in required:
            assert letter in LETTER_SEGMENTS, f"Missing letter '{letter}' for high score text"

    def test_letter_segments_values_are_tuples(self):
        """Each letter's segments should be a tuple of line definitions."""
        for letter, segments in LETTER_SEGMENTS.items():
            assert isinstance(segments, tuple), f"Letter '{letter}' segments should be tuple"
            assert len(segments) > 0, f"Letter '{letter}' should have at least one segment"

    def test_letter_segments_line_definitions_valid(self):
        """Each line segment should be a 4-tuple of coordinate multipliers."""
        for letter, segments in LETTER_SEGMENTS.items():
            for i, seg in enumerate(segments):
                assert isinstance(seg, tuple), \
                    f"Letter '{letter}' segment {i} should be tuple"
                assert len(seg) == 4, \
                    f"Letter '{letter}' segment {i} should have 4 values"


class TestDisplayConstants:
    """Test cases for display-related constants."""

    def test_text_outline_offset_positive(self):
        """TEXT_OUTLINE_OFFSET should be positive."""
        assert TEXT_OUTLINE_OFFSET > 0

    def test_text_outline_offset_reasonable(self):
        """TEXT_OUTLINE_OFFSET should be small (1-5 pixels)."""
        assert 1 <= TEXT_OUTLINE_OFFSET <= 5

    def test_fps_display_padding_positive(self):
        """FPS_DISPLAY_PADDING should be positive."""
        assert FPS_DISPLAY_PADDING > 0

    def test_fps_display_size_positive(self):
        """FPS_DISPLAY_SIZE should be positive."""
        assert FPS_DISPLAY_SIZE > 0

    def test_score_digit_size_positive(self):
        """SCORE_DIGIT_SIZE should be positive."""
        assert SCORE_DIGIT_SIZE > 0

    def test_score_digit_width_positive(self):
        """SCORE_DIGIT_WIDTH should be positive."""
        assert SCORE_DIGIT_WIDTH > 0

    def test_line_thickness_positive(self):
        """LINE_THICKNESS should be positive."""
        assert LINE_THICKNESS > 0

    def test_fps_size_smaller_than_score_size(self):
        """FPS display should be smaller than score display."""
        assert FPS_DISPLAY_SIZE <= SCORE_DIGIT_SIZE
