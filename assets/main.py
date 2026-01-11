"""Web entry point for pygbag (in assets folder where template expects it)."""
import sys
import asyncio

print("=== Starting scroller ===")

# Add parent directory to path so we can import game
# In pygbag, __file__ is set after the template runs
try:
    from pathlib import Path
    parent = Path(__file__).parent.parent
    print(f"Adding to path: {parent}")
    sys.path.insert(0, str(parent))
except Exception as e:
    print(f"Path setup error: {e}")
    # Fallback: try adding common locations
    sys.path.insert(0, "/data/data/scroller")

print(f"sys.path: {sys.path[:3]}")

try:
    import game
    print("game module imported successfully")
except Exception as e:
    print(f"Failed to import game: {e}")
    import traceback
    traceback.print_exc()
    raise


async def main():
    """Run the game."""
    print("Starting main()")
    try:
        await game.main()
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
