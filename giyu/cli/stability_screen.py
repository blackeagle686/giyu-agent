"""
Giyu Agent — Real-time System Stability Monitor.
"""

import asyncio
import psutil
import time
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Header, Footer, ProgressBar, Label, Digits
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.reactive import reactive
from textual import on, work
from rich.text import Text
from rich.panel import Panel
from rich.progress_bar import ProgressBar as RichProgressBar
from rich.console import RenderableType

class StatCard(Container):
    """A card displaying a specific system metric."""
    
    DEFAULT_CSS = """
    StatCard {
        background: $surface;
        border: round $border;
        padding: 1 2;
        margin: 1;
        height: auto;
        min-height: 8;
    }
    StatCard:hover {
        border: round $primary;
        background: $panel;
    }
    .card-title {
        color: $secondary;
        text-style: bold;
        margin-bottom: 1;
    }
    .card-value {
        color: $text;
        font-size: 1.5rem;
        text-style: bold;
    }
    .card-meta {
        color: $text-muted;
        font-size: 0.8rem;
    }
    """

    def __init__(self, title: str, unit: str = "", **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.unit = unit

    def compose(self) -> ComposeResult:
        yield Label(self.title_text, classes="card-title")
        yield Label("0" + self.unit, id="value", classes="card-value")
        yield ProgressBar(total=100, id="progress", show_percentage=False)
        yield Label("", id="meta", classes="card-meta")

    def update(self, value: float, meta: str = "") -> None:
        self.query_one("#value", Label).update(f"{value:.1f}{self.unit}")
        self.query_one("#progress", ProgressBar).progress = value
        if meta:
            self.query_one("#meta", Label).update(meta)

class StabilityScreen(Screen):
    """Interactive system stability dashboard."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back to Chat"),
        ("r", "refresh", "Refresh Stats"),
    ]

    DEFAULT_CSS = """
    StabilityScreen {
        background: $background;
        padding: 1;
    }

    #stability-header {
        height: 3;
        background: $surface;
        border-bottom: thick $border;
        align: center middle;
        margin-bottom: 1;
    }

    #stability-grid {
        grid-size: 2 3;
        height: 1fr;
    }

    .health-section {
        column-span: 2;
        height: 10;
        align: center middle;
        background: $panel;
        border: double $primary;
        margin: 1;
    }

    #health-score {
        color: #00f2ff;
        text-style: bold;
    }
    """

    health_score = reactive(0)

    def compose(self) -> ComposeResult:
        with Horizontal(id="stability-header"):
            yield Static("[bold #00f2ff]🌊 GIYU SYSTEM SENTINEL[/] [dim #7000ff]— REAL-TIME STABILITY LOG[/]")

        with Grid(id="stability-grid"):
            with Vertical(classes="health-section"):
                yield Label("SYSTEM STABILITY INDEX", classes="card-title")
                yield Digits("00.0", id="health-digits")
                yield Label("GUARDING HASHIRA-OS", classes="card-meta")

            yield StatCard("CPU LOAD", unit="%", id="cpu-card")
            yield StatCard("MEMORY USAGE", unit="%", id="mem-card")
            yield StatCard("NETWORK BANDWIDTH", unit=" MB/s", id="net-card")
            yield StatCard("DISK I/O", unit=" ops", id="disk-card")

        yield Footer()

    def on_mount(self) -> None:
        self.update_stats()
        self.set_interval(1.0, self.update_stats)

    @work(exclusive=True)
    async def update_stats(self) -> None:
        """Fetch and update system metrics."""
        # CPU
        cpu_usage = psutil.cpu_percent()
        
        # Memory
        mem = psutil.virtual_memory()
        mem_usage = mem.percent
        mem_meta = f"{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB"

        # Network (Calculated over 1s)
        n1 = psutil.net_io_counters()
        await asyncio.sleep(0.5)
        n2 = psutil.net_io_counters()
        net_speed = ((n2.bytes_sent + n2.bytes_recv) - (n1.bytes_sent + n1.bytes_recv)) / (1024**2)
        net_meta = f"↑ {n2.bytes_sent // (1024**2)}MB  ↓ {n2.bytes_recv // (1024**2)}MB"

        # Disk
        d1 = psutil.disk_io_counters()
        await asyncio.sleep(0.4)
        d2 = psutil.disk_io_counters()
        disk_ops = (d2.read_count + d2.write_count) - (d1.read_count + d1.write_count)
        
        # Health Score (Weighted)
        # Low usage = high stability
        score = 100 - (cpu_usage * 0.4 + mem_usage * 0.4 + min(net_speed * 2, 20))
        score = max(0, min(100, score))

        # Update UI
        self.query_one("#cpu-card", StatCard).update(cpu_usage, f"Cores: {psutil.cpu_count()}")
        self.query_one("#mem-card", StatCard).update(mem_usage, mem_meta)
        self.query_one("#net-card", StatCard).update(min(net_speed * 10, 100), net_meta)
        self.query_one("#disk-card", StatCard).update(min(disk_ops / 10, 100), f"{disk_ops} operations/sec")
        
        self.query_one("#health-digits", Digits).update(f"{score:04.1f}")
        
        # Color transition for health digits
        if score > 80:
            self.query_one("#health-digits", Digits).styles.color = "#10b981" # Green
        elif score > 50:
            self.query_one("#health-digits", Digits).styles.color = "#f59e0b" # Warning
        else:
            self.query_one("#health-digits", Digits).styles.color = "#ef4444" # Error
