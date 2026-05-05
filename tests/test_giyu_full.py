import asyncio
import os
import sys
from dotenv import load_dotenv

# Add Giyu path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env from Giyu folder
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from giyu.agent import get_giyu_agent
from phoenix.services.llm.openai import OpenAILLM

async def test_brains(agent):
    print("\n--- Testing Brains ---")
    
    # 1. Thinker
    print("Testing Thinker...")
    obj = await agent.thinker.analyze("System looks slow, check CPU and RAM", agent.memory, "test_session")
    print(f"Thinker Objective: {obj}")
    
    # 2. Analyzer (Non-LLM)
    print("Testing Analyzer (Non-LLM)...")
    analysis = agent.analyzer.analyze_logs(["ERROR: OutOfMemory", "Warning: High CPU"])
    print(f"Analyzer Result: {analysis}")
    
    # 3. Stability Scorer (Non-LLM)
    print("Testing Stability Scorer (Non-LLM)...")
    score = agent.stability_scorer.compute_score({"cpu_usage": 85, "ram_usage": 95, "disk_usage": 40})
    print(f"Stability Score: {score}")
    
    # 4. Decision Gate (Non-LLM)
    print("Testing Decision Gate (Non-LLM)...")
    decision = agent.decision_gate.evaluate(score)
    print(f"Decision: {decision}")
    
    # 5. Correlation Engine (Hybrid/LLM)
    print("Testing Correlation Engine (Hybrid)...")
    events = [{"type": "error", "msg": "DB Timeout"}, {"type": "metric", "msg": "CPU Spike"}]
    correlation = await agent.correlation_engine.correlate(events)
    print(f"Correlation: {correlation}")

async def test_tools(agent):
    print("\n--- Testing Tools ---")
    tools_to_test = [
        "system_snapshot_reader",
        "agent_heartbeat_monitor",
        "resource_pressure_monitor",
        "stability_score_calculator"
    ]
    
    for tool_name in tools_to_test:
        print(f"Testing Tool: {tool_name}...")
        tool = agent.tools.get_tool(tool_name)
        # Handle different kwargs for different tools
        kwargs = {}
        if tool_name == "stability_score_calculator":
            kwargs = {"cpu": 50, "ram": 50, "disk": 50}
            
        result = await tool.execute(**kwargs)
        print(f"Result: {result.output if result.success else result.error}")

async def test_full_loop(agent):
    print("\n--- Testing Full Agent Loop ---")
    prompt = "Perform a full system stability diagnostic"
    # We use run_stream to see progress
    async for event in agent.run_stream(prompt, session_id="test_loop_session"):
        if event["type"] == "status":
            print(f"STATUS: {event['content']}")
        elif event["type"] == "chunk":
            print(event["content"], end="", flush=True)
    print("\nLoop Complete.")

async def main():
    print("--- Debug Information ---")
    print(f"CWD: {os.getcwd()}")
    print(f"OPENAI_API_KEY: {'[SET]' if os.getenv('OPENAI_API_KEY') else '[NOT SET]'}")
    print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
    print(f"OPENAI_LLM_MODEL: {os.getenv('OPENAI_LLM_MODEL')}")
    
    print("\nInitializing Giyu Agent...")
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in .env")
        return

    agent = await get_giyu_agent()
    
    # Check if LLM is initialized
    try:
        from phoenix.core.container import container
        llm = container.get("llm_openai")
        print(f"LLM Client initialized: {llm.client is not None}")
        if not llm.client:
            print("Force initializing LLM...")
            await llm.init()
            print(f"LLM Client initialized after force: {llm.client is not None}")
    except Exception as e:
        print(f"Error checking LLM: {e}")

    await test_brains(agent)
    await test_tools(agent)
    await test_full_loop(agent)

if __name__ == "__main__":
    asyncio.run(main())
