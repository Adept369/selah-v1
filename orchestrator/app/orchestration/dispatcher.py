
async def dispatch_command(payload: dict) -> str:
    msg = payload.get("message", {}).get("text", "")
    chat = payload.get("message", {}).get("chat", {}).get("id")

    # if they didn't invoke /agent, show usage
    if not msg.startswith("/agent"):
        return "Use /agent [name] [query]"

    parts = msg.split(maxsplit=2)
    if len(parts) < 3:
        return "Usage: /agent [name] [query]"

    _, name, query = parts
   
    agent = AGENT_REGISTRY.get(name)
    if not agent:
        return f"Unknown agent '{name}'."

    # run the agent (assumed to be sync here; if it's async, await it)
    try:
        result = agent.run(query)
    except Exception:
        logger = __import__("logging").getLogger(__name__)
        logger.exception("agent.run failed")
        return "Agent encountered an error."

    # agent.run() now returns a plain string
    return agent.run(query)
