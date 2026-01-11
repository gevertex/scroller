"""Web entry point for pygbag.

Pygbag requires a main.py with an async main() function.
This file imports and runs the game module.
"""
import asyncio
import game


async def main():
    """Run the game (delegates to game.main)."""
    await game.main()


if __name__ == "__main__":
    asyncio.run(main())
