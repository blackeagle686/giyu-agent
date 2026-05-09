import asyncio
from typing import Awaitable, Callable


class StreamForwarder:
    """Forward runtime chunks to IPC/event sink."""

    def __init__(self, push_fn: Callable[[dict], Awaitable[None]], chunk_size: int = 4096):
        self.push_fn = push_fn
        self.chunk_size = chunk_size

    async def emit_stdout(self, text: str) -> None:
        for idx in range(0, len(text), self.chunk_size):
            await self.push_fn(
                {"type": "STDOUT_CHUNK", "content": text[idx : idx + self.chunk_size]}
            )

    async def emit_stderr(self, text: str) -> None:
        for idx in range(0, len(text), self.chunk_size):
            await self.push_fn(
                {"type": "STDERR_CHUNK", "content": text[idx : idx + self.chunk_size]}
            )

    async def emit_terminal(self, receipt: dict) -> None:
        await self.push_fn({"type": "EXIT_CODE", "content": receipt})
        await self.push_fn({"type": "EOF"})
