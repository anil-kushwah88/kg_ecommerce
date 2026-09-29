# E-Commerce Knowledge Graph + AI Retrieval (Python, NetworkX, Claude)

Natural-language question -> LLM -> graph query -> retrieve from graph -> LLM -> answer (only from retrieved data).

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
# open .env and paste your ANTHROPIC_API_KEY
```

## Run
```bash
python main.py --check                       # graph stats + banana count (expect 5)
python main.py -q "Which products from brand Zenith are supplied by vendor Sunrise Traders?"
python main.py                               # interactive mode
python main.py --demo                        # runs 7 sample questions -> sample_results.md
python main.py --offline --demo              # no API key: rule-based planner (testing only)
```

## Project structure
| File | Purpose |
|---|---|
| `data/*.csv` | Sample dataset (brands, categories, vendors, products, customers, orders, order_items, keywords) |
| `kg.py` | Builds the NetworkX graph, describes schema, executes graph queries |
| `llm.py` | Claude integration: question -> JSON query, retrieved data -> answer |
| `offline.py` | Rule-based fallback (no LLM) for testing |
| `main.py` | CLI / demo runner |
| `sample_results.md` | Sample questions with results |

## Knowledge graph
Nodes: Product, Brand, Category, Vendor, Customer, Order, Keyword.

Relationships:
- `Product -[HAS_BRAND]-> Brand`
- `Product -[IN_CATEGORY]-> Category`
- `Vendor -[SUPPLIES]-> Product`
- `Customer -[PLACED]-> Order`
- `Order -[CONTAINS {quantity}]-> Product`
- `<Product|Brand|Category|Vendor> -[HAS_KEYWORD]-> Keyword`

## Retrieval flow
1. LLM gets the graph schema + known entity names and returns a JSON query:
   `{"return_type": "Product", "filters": [{"type": "Brand", "name": "Zenith"}, {"type": "Vendor", "name": "Sunrise Traders"}]}`
2. `kg.execute()` finds the filter nodes, walks the relationship path between the types (found from the schema graph), and returns nodes of `return_type` connected to ALL filters. `ANY` returns direct neighbours.
3. Retrieved nodes (with their relations) are sent to the LLM to write the final answer.

## Answers only from retrieved data
- LLM never sees the whole graph and never executes code; it only produces a constrained JSON query (validated in `kg.execute`).
- Answer prompt: use ONLY the retrieved JSON, no outside knowledge, temperature 0.
- Empty result -> fixed reply: "I could not find this in the knowledge graph."

## Banana requirement
`data/keywords.csv` has exactly 5 rows with value `banana` (K1-K5). Each becomes a `Keyword` node linked to a Product (x2), Brand, Vendor, Category. The word appears nowhere else in the dataset. Verify: `python main.py --check` -> `banana nodes: 5`. Retrieve: "What is linked to banana in the knowledge graph?" or "Which products have the banana keyword?"

## Optional: model
Default model is `claude-sonnet-5`; override with `ANTHROPIC_MODEL` in `.env`.
