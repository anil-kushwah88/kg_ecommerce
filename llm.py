"""LLM integration (Anthropic Claude): question -> JSON graph query, and retrieved data -> answer."""
import json, os, re
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

PLAN_SYSTEM = """You convert e-commerce questions into a JSON graph query. Output ONLY a JSON object, no prose.
Format: {"return_type": "<NodeType or ANY>", "filters": [{"type": "<NodeType>", "name": "<entity name>"}]}
Rules:
- return_type = the node type the user wants back (Product, Brand, Category, Vendor, Order, Customer, Keyword).
- Use "ANY" when the user asks what is linked/connected to some entity (returns its direct neighbours).
- Every entity named in the question becomes a filter; use exact names from KNOWN ENTITY NAMES.
- Results must be connected to ALL filters (AND).
- Use only node types from the schema below.

{schema}"""

ANSWER_SYSTEM = """You answer questions about an e-commerce knowledge graph.
STRICT RULES:
- Use ONLY the RETRIEVED DATA given below. Never use outside knowledge or guess.
- If the data is empty or does not contain the answer, reply exactly: "I could not find this in the knowledge graph."
- Mention entity names/values exactly as they appear. Keep the answer short and clear.
- Simple counting/summing of retrieved values is allowed."""


def _client():
    from anthropic import Anthropic
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY missing. Add it to .env or use --offline.")
    return Anthropic()


def _text(resp):
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def plan_query(question, schema_text):
    resp = _client().messages.create(
        model=MODEL, max_tokens=500,
        system=PLAN_SYSTEM.replace("{schema}", schema_text),
        messages=[{"role": "user", "content": question}],
    )
    raw = _text(resp)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError(f"LLM did not return JSON: {raw}")
    return json.loads(m.group(0))


def answer(question, retrieved):
    resp = _client().messages.create(
        model=MODEL, max_tokens=800, system=ANSWER_SYSTEM,
        messages=[{"role": "user", "content": f"QUESTION: {question}\n\nRETRIEVED DATA (JSON):\n{json.dumps(retrieved, indent=2)}"}],
    )
    return _text(resp)
