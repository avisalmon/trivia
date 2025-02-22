import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .game_manager import GameManager
from qasync import QEventLoop, QApplication as AsyncQApplication


async def main():
    app = AsyncQApplication.instance() or AsyncQApplication(sys.argv)
    
    # Create game manager and main window
    game_manager = GameManager()
    game_manager.start_game("Player1")
    
    window = MainWindow(game_manager)
    window.show()
    
    # Create event loop and run the application
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    try:
        # Run the event loop
        with loop:
            await loop.run_forever()
    finally:
        # Cleanup
        await game_manager.cleanup()
        await game_manager.question_generator.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error running game: {e}", file=sys.stderr)
        sys.exit(1) 