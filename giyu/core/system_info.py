import os
import sys
import subprocess
import platform
import json
import asyncio
from typing import Dict, Any

class SystemProbe:
    """
    Handles platform-specific system information gathering and caching.
    Supports Windows and Linux with optimized commands.
    """
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.cache: Dict[str, Any] = {}

    async def probe_all(self) -> Dict[str, Any]:
        """Runs all platform-specific probes and caches the result."""
        results = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "os": self.os_type,
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count(),
        }

        if self.os_type == "windows":
            results.update(await self._probe_windows())
        elif self.os_type == "linux":
            results.update(await self._probe_linux())
        else:
            # Fallback for Darwin (macOS) or others
            results["details"] = "Basic platform info gathered. Advanced probing only available for Win/Linux."

        self.cache = results
        return results

    async def _run_command(self, cmd: str) -> str:
        """Helper to run shell commands asynchronously."""
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            return stdout.decode().strip()
        except Exception as e:
            return f"Error executing {cmd}: {e}"

    async def _probe_windows(self) -> Dict[str, Any]:
        """Windows-specific high-speed probes."""
        # Using PowerShell for structured data where possible
        ps_cmd = "Get-ComputerInfo | Select-Object OsName, OsVersion, CsProcessors, TotalPhysicalMemory | ConvertTo-Json"
        raw_json = await self._run_command(f'powershell -Command "{ps_cmd}"')
        
        try:
            data = json.loads(raw_json)
            return {
                "os_name": data.get("OsName"),
                "os_version": data.get("OsVersion"),
                "memory_total": f"{int(data.get('TotalPhysicalMemory', 0)) // (1024**3)} GB",
                "cpu_info": data.get("CsProcessors", [{}])[0].get("Name") if isinstance(data.get("CsProcessors"), list) else "Unknown"
            }
        except:
            # Fallback to faster, raw commands
            return {
                "os_name": await self._run_command("wmic os get Caption /value"),
                "cpu_info": await self._run_command("wmic cpu get name /value")
            }

    async def _probe_linux(self) -> Dict[str, Any]:
        """Linux-specific high-speed probes."""
        return {
            "os_release": await self._run_command("cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2"),
            "kernel": await self._run_command("uname -r"),
            "cpu_info": await self._run_command("lscpu | grep 'Model name' | cut -d':' -f2"),
            "memory_info": await self._run_command("free -h | grep Mem | awk '{print $2}'"),
            "disk_info": await self._run_command("df -h / | tail -1 | awk '{print $2}'")
        }

    def get_summary(self) -> str:
        """Returns a string summary of the cached system info."""
        if not self.cache:
            return "System info not yet probed."
        
        summary = [f"System Profile: {self.cache.get('platform')}"]
        for k, v in self.cache.items():
            if k not in ["platform", "details"]:
                summary.append(f"- {k.replace('_', ' ').title()}: {v}")
        return "\n".join(summary)
