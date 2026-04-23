from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    filepath = PROMPTS_DIR / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""


# Pre-load all prompts
ROUTER_PROMPT = load_prompt("router.md")
SYNTHESIS_PROMPT = load_prompt("synthesis.md")
ACTION_PROMPT = load_prompt("action.md")

AGENT_PROMPTS = {
    "sales": load_prompt("agents/sales.md"),
    "inventory": load_prompt("agents/inventory.md"),
    "support": load_prompt("agents/support.md"),
    "marketing": load_prompt("agents/marketing.md"),
    "memory": load_prompt("agents/memory.md"),
}
