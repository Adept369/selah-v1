# orchestrator/app/orchestration/dispatcher.py

from app.orchestration.registry import AGENT_REGISTRY

async def dispatch_command(update: dict) -> str:
    msg = update.get("message", {})
    text = msg.get("text", "")
    chat = msg.get("chat", {}).get("id")

    if not text.lower().startswith("/agent"):
        return "Use /agent [name] [query]"

    try:
        _, name, query = text.split(maxsplit=2)
    except ValueError:
        return "Usage: /agent [name] [query]"

    agent = AGENT_REGISTRY.get(name)
    if not agent:
        return f"Unknown agent '{name}'"

    result = agent.run(query)
    if hasattr(result, "__await__"):
        result = await result
    return result
