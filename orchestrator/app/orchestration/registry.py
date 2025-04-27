# orchestrator/app/orchestration/registry.py

from app.agents.case_law_scholar.case_law_agent import CaseLawScholarAgent
from app.agents.memo_drafter.memo_agent import MemoDrafterAgent

AGENT_REGISTRY = {
    "case_law_scholar": CaseLawScholarAgent(),
    "memo_drafter": MemoDrafterAgent(),
}
