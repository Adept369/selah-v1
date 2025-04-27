
from app.orchestration.master_agent import MasterAgent

from app.orchestration.registry import AGENT_REGISTRY


async def dispatch_command(payload: dict) -> dict:
     msg = payload.get("message", {}).get("text", "")
     chat = payload.get("message", {}).get("chat", {}).get("id")
     if not msg.startswith("/agent"):
         return {"method":"sendMessage","chat_id":chat,"text":"Use /agent [name] [query]"}
     _, name, query = msg.split(maxsplit=2)
     agent = AGENT_REGISTRY.get(name)
     if not agent:
         return {"method":"sendMessage","chat_id":chat,"text":f"Unknown agent '{name}'"}
     result = agent.run(query)
     return {"method":"sendMessage","chat_id":chat,"text":result}
# instantiate once
master = MasterAgent()

async def dispatch_command(payload: dict) -> str:
    """
    New signature: returns the reply text directly.
    """
    return await master.run(payload)