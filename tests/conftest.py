import pytest
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set SDL to use dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame once for all tests."""
    pygame.init()
    yield
    pygame.quit()
