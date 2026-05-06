from fastapi import APIRouter
from .state import get_agent
from giyu.cognition.helpers.backbone import _load_backbone

router = APIRouter(prefix="/stability", tags=["stability"])

@router.get("/status")
async def get_stability_status():
    """Returns the current system stability status and escalation state."""
    data = _load_backbone()
    reports = data.get("stability_reports", [])
    current_report = reports[-1] if reports else {
        "score": 100.0,
        "state": "stable",
        "metrics_evaluated": ["cpu", "ram", "disk"],
        "timestamp": 0
    }
    
    return {
        "current_report": current_report,
        "escalation_state": data.get("escalation_state", {}),
        "anomalies": data.get("anomalies", []),
        "agent_heartbeats": await _get_agent_heartbeats()
    }

@router.get("/history")
async def get_stability_history(limit: int = 50):
    """Returns the history of stability reports."""
    data = _load_backbone()
    return data.get("stability_reports", [])[-limit:]

@router.get("/backbone")
async def get_full_backbone():
    """Returns the entire backbone context."""
    return _load_backbone()

async def _get_agent_heartbeats():
    """Helper to get heartbeats of all agents."""
    from giyu.tools.stability_tools import AgentHeartbeatMonitor
    monitor = AgentHeartbeatMonitor()
    result = await monitor.execute()
    import ast
    try:
        return ast.literal_eval(result.output)
    except:
        return {}
