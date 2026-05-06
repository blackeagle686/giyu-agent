from phoenix import Agent, init_phoenix, startup_phoenix
from .tools.project_generator import project_generator_tool
from .tools.file_tools import file_read_lines_tool, file_update_multi_tool

async def get_giyu_agent(on_startup_progress=None):
    """
    Initializes the Phoenix framework, starts up services, and returns the Giyu agent.
    """
    import os
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    print(f"DEBUG: OPENAI_API_KEY set: {'yes' if os.getenv('OPENAI_API_KEY') else 'no'}")
    print(f"DEBUG: OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
    
    init_phoenix()
    await startup_phoenix()
    from .cognition import GiyuThinker, GiyuPlanner, GiyuReflector, GiyuLoop, GiyuGenerator
    from .cognition.brains.stability_scorer import StabilityScorer
    from .cognition.brains.decision_gate import DecisionGate
    from .cognition.brains.analyzer import GiyuAnalyzer
    from .cognition.brains.correlation_engine import CorrelationEngine
    from phoenix.framework.agent.core.profile import AgentProfile
    import os
    
    # Load Profile
    profile_path = os.path.join(os.path.dirname(__file__), "profile.json")
    profile = AgentProfile.from_json(profile_path)
    
    # Create the agent with the task-file driven loop and upgraded cognition modules
    agent = Agent(
        loop_cls=GiyuLoop,
        component_factories={
            "thinker": lambda **ctx: GiyuThinker(ctx["llm"], profile=profile),
            "planner": lambda **ctx: GiyuPlanner(ctx["llm"], ctx["tools"]),
            "reflector": lambda **ctx: GiyuReflector(ctx["llm"], profile=profile),
            "generator": lambda **ctx: GiyuGenerator(ctx["llm"]),
            "analyzer": lambda **ctx: GiyuAnalyzer(),
            "loop": lambda **ctx: GiyuLoop(
                thinker=ctx["thinker"],
                planner=ctx["planner"],
                actor=ctx["actor"],
                reflector=ctx["reflector"],
                analyzer=ctx["analyzer"] or GiyuAnalyzer(),
                stability_scorer=StabilityScorer(),
                decision_gate=DecisionGate(),
                correlation_engine=CorrelationEngine(ctx["llm"]),
                generator=ctx.get("generator") or GiyuGenerator(ctx["llm"])
            )
        }
    )
    
    from .tools.stability_tools import (
        SystemSnapshotReader, LogStreamAnalyzer, AgentHeartbeatMonitor,
        AnomalyDetector, StabilityScoreCalculator, ProcessStateTracker,
        RollbackRecommendationEngine, CoreEscalationTrigger,
        ResourcePressureMonitor, EventCorrelationTracker
    )
    from phoenix.framework.agent.tools import FileReadTool, FileEditTool
    
    # Register core tools
    agent.register_tool(FileReadTool())
    agent.register_tool(FileEditTool())
    
    # Register specialized stability tools
    agent.register_tool(SystemSnapshotReader())
    agent.register_tool(LogStreamAnalyzer())
    agent.register_tool(AgentHeartbeatMonitor())
    agent.register_tool(AnomalyDetector())
    agent.register_tool(StabilityScoreCalculator())
    agent.register_tool(ProcessStateTracker())
    agent.register_tool(RollbackRecommendationEngine())
    agent.register_tool(CoreEscalationTrigger())
    agent.register_tool(ResourcePressureMonitor())
    agent.register_tool(EventCorrelationTracker())
    
    # Attach brains to agent for direct access (testing/external logic)
    agent.stability_scorer = agent.loop.stability_scorer
    agent.decision_gate = agent.loop.decision_gate
    agent.correlation_engine = agent.loop.correlation_engine
    
    return agent
