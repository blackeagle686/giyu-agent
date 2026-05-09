import asyncio
import os
import pty
import shlex
import signal
import subprocess
import time
from typing import Callable, Dict, Optional


DEFAULT_WORKDIR = os.getenv("GIYU_WORKDIR", "/tmp/giyu")
MAX_OUTPUT_BYTES = 4 * 1024


def _sanitize_env(env_vars: Optional[dict]) -> dict:
    clean = {}
    blocked_keys = {"PATH", "LD_PRELOAD", "LD_LIBRARY_PATH"}
    for key, value in (env_vars or {}).items():
        if any(blocked in key.upper() for blocked in blocked_keys):
            continue
        clean[str(key)] = str(value)
    return clean


def _apply_ulimits() -> None:
    import resource

    resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    # 512MB virtual memory
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    # 30s CPU time
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))


class PTYExecutor:
    def __init__(self, chunk_size: int = MAX_OUTPUT_BYTES):
        self.chunk_size = chunk_size

    async def execute(
        self,
        command: str,
        working_dir: Optional[str] = None,
        env_vars: Optional[dict] = None,
        timeout_ms: int = 30000,
        on_chunk: Optional[Callable[[dict], None]] = None,
    ) -> Dict:
        os.makedirs(DEFAULT_WORKDIR, exist_ok=True)
        cwd = working_dir or DEFAULT_WORKDIR
        cmd = shlex.split(command)
        master_fd, slave_fd = pty.openpty()
        start_ts = time.time()
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env={**os.environ, **_sanitize_env(env_vars)},
            stdin=subprocess.DEVNULL,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=_apply_ulimits,
            close_fds=True,
            text=False,
        )
        os.close(slave_fd)

        timed_out = False
        output = bytearray()

        async def _pump():
            while True:
                try:
                    chunk = await asyncio.to_thread(os.read, master_fd, self.chunk_size)
                except OSError:
                    break
                if not chunk:
                    break
                output.extend(chunk)
                if on_chunk:
                    on_chunk({"type": "STDOUT_CHUNK", "data": chunk.decode(errors="replace")})

        pump_task = asyncio.create_task(_pump())
        try:
            await asyncio.wait_for(asyncio.to_thread(proc.wait), timeout=timeout_ms / 1000)
        except asyncio.TimeoutError:
            timed_out = True
            proc.kill()
            await asyncio.to_thread(proc.wait)
        finally:
            await pump_task
            try:
                os.close(master_fd)
            except OSError:
                pass

        elapsed_ms = int((time.time() - start_ts) * 1000)
        code = -9 if timed_out else int(proc.returncode or 0)
        return {
            "exit_code": code,
            "pid": proc.pid,
            "execution_ms": elapsed_ms,
            "timed_out": timed_out,
            "output": output.decode(errors="replace"),
        }
