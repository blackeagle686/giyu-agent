"""
Giyu Agent — Main launcher.
Boots the Textual TUI, routing to the setup wizard when config is missing,
or directly to the full-screen chat interface otherwise.
"""

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.binding import Binding
from .cli.theme import GIYU_THEME
from .cli.splash_screen import SplashScreen


# ── Configuration Path ────────────────────────────────────────────────────────
# Default to local .env, fallback to ~/.giyu/.env for global use
ENV_PATH = Path(".env")
GLOBAL_CONFIG_DIR = Path.home() / ".giyu"
GLOBAL_ENV_PATH = GLOBAL_CONFIG_DIR / ".env"


def _has_valid_config() -> bool:
    """Return True if any .env has a non-empty API key."""
    # Check local first, then global
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=True)
    elif GLOBAL_ENV_PATH.exists():
        load_dotenv(GLOBAL_ENV_PATH, override=True)
    
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(key)


class GiyuApp(App):
    """Root Textual application for the Giyu Agent CLI."""

    TITLE = "Giyu Agent"
    SUB_TITLE = "Powered by Phoenix AI"
    CSS = ""                        # All CSS lives inside screens
    ENABLE_COMMAND_PALETTE = False  # Keep UI clean

    BINDINGS = [
        Binding("ctrl+k", "open_config", "Config", show=False, priority=True),
        Binding("ctrl+q", "quit_app",   "Quit",   show=False, priority=True),
    ]

    def action_quit_app(self) -> None:
        self.exit()

    def action_open_config(self) -> None:
        from .cli.setup_wizard import SetupWizard
        from .cli.chat_screen import ChatScreen
        
        # If we are on the ChatScreen, use its reload callback
        if isinstance(self.screen, ChatScreen):
            self.push_screen(SetupWizard(), callback=self.screen._on_config_closed)
        else:
            self.push_screen(SetupWizard())

    def on_mount(self) -> None:
        """Initializes the app and handles the splash-to-main transition."""
        self.register_theme(GIYU_THEME)
        self.theme = "giyu"

        # 1. Immediately show splash to provide instant feedback
        self.push_screen(SplashScreen())

        # 2. Start background loading of the main interface
        self._load_main_interface()

    @work(exclusive=True)
    async def _load_main_interface(self) -> None:
        """Loads the main screen in the background to avoid blocking the UI thread."""
        if _has_valid_config():
            from .cli.chat_screen import ChatScreen
            main_screen = ChatScreen()
        else:
            from .cli.setup_wizard import SetupWizard
            main_screen = SetupWizard()
        
        # Give the splash screen at least 1 second of glory
        await asyncio.sleep(1.0)
        
        # Transition to the main screen
        self.push_screen(main_screen)


def main() -> None:
    """Entry point — handles 'giyu <dir>'."""
    # ── Silence noisy startup logs ─────────────────────────────────────────────
    os.environ.setdefault("LOG_LEVEL", "WARNING")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

    # Handle directory argument (e.g. 'giyu .')
    if len(sys.argv) > 1:
        target_arg = sys.argv[1]
        target_dir = Path(target_arg).resolve() # Use resolve() to get absolute path
        if target_dir.is_dir():
            print(f"[*] Switching to directory: {target_dir}")
            os.chdir(target_dir)
        else:
            print(f"[!] Error: {target_arg} is not a valid directory.")
            sys.exit(1)
    else:
        # If no arg, ensure we work in current shell CWD
        print(f"[*] Working in directory: {os.getcwd()}")

    app = GiyuApp()
    app.run()


if __name__ == "__main__":
    main()
