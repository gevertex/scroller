import pytest
import os

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
