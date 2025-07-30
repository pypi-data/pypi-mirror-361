"""Entry point for retro-snake-game when run as a module or script."""

def main():
    """Main entry point that imports and runs the app."""
    # Import the app module, which runs the game
    from . import snake_game

if __name__ == "__main__":
    main()