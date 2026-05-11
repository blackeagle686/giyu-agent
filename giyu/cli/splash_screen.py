"""
Giyu Agent — Cinematic Splash Screen.
"""

import asyncio
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Center, Middle
from textual.reactive import reactive
from rich.text import Text

class SplashScreen(Screen):
    """A stunning splash screen that appears on launch."""

    DEFAULT_CSS = """
    SplashScreen {
        background: #020408;
        align: center middle;
    }

    #splash-logo {
        color: #00f2ff;
        text-style: bold;
        text-align: center;
        width: auto;
        content-align: center middle;
    }

    #splash-subtitle {
        color: #94a3b8;
        text-align: center;
        width: auto;
        margin-top: 1;
        text-style: italic;
    }
    """

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Static("", id="splash-logo")
                yield Static("powered by phoenix-ai engine", id="splash-subtitle")

    def on_mount(self) -> None:
        self._animate_aura()

    def _animate_aura(self) -> None:
        logo = (
            " ██████╗ ██╗██╗   ██╗██╗   ██╗\n"
            "██╔════╝ ██║╚██╗ ██╔╝██║   ██║\n"
            "██║  ███╗██║ ╚████╔╝ ██║   ██║\n"
            "██║   ██║██║  ╚██╔╝  ██║   ██║\n"
            "╚██████╔╝██║   ██║   ╚██████╔╝\n"
            " ╚═════╝ ╚═╝   ╚═╝    ╚═════╝ \n"
            "   S T A B I L I T Y   S E N T I N E L"
        )
        self.query_one("#splash-logo", Static).update(Text(logo, style="bold #00f2ff"))
        self.query_one("#splash-subtitle", Static).update("powerd by phoenix-ai")

    def _dismiss(self) -> None:
        self.app.pop_screen()
