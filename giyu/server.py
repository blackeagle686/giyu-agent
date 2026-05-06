"""
Giyu Server — backward-compatibility shim.

All logic has moved to giyu.backend.*
This file re-exports the symbols that other modules import from
`giyu.server` so that existing code continues to work unchanged.
"""

import os
from dotenv import load_dotenv
load_dotenv() # Load from current directory

# Re-export the FastAPI app (used by uvicorn: "giyu.server:app")
from giyu.backend.app import app  # noqa: F401

# Re-export shared state used by tools and cognition modules
from giyu.backend.state import (        # noqa: F401
    vscode_ipc_context,
    _pending_file_opens,
)

# ── CLI entry ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("giyu.server:app", host="127.0.0.1", port=8765, reload=False)
