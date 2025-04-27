
from app.orchestration.master_agent import MasterAgent

# instantiate once
master = MasterAgent()

async def dispatch_command(payload: dict) -> str:
    """
    New signature: returns the reply text directly.
    """
    return await master.run(payload)