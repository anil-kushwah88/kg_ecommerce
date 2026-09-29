"""Rule-based fallback planner/answerer so the project runs without an API key (for testing only)."""
import re

TYPE_WORDS = {
    "Product": ["product", "item"], "Brand": ["brand"], "Category": ["categor"],
    "Vendor": ["vendor", "supplier", "supplies", "supplied", "supply"],
    "Customer": ["customer", "bought", "buyer", "purchased"], "Order": ["order"],
}


def offline_plan(q, g):
    ql, filters, seen = q.lower(), [], set()
    for _, d in g.nodes(data=True):
        if d["type"] == "Order":
            continue
        nm = d["name"].lower()
        if re.search(r"\b" + re.escape(nm) + r"\b", ql) and (d["type"], nm) not in seen:
            seen.add((d["type"], nm))
            filters.append({"type": d["type"], "name": d["name"]})
    ftypes = {f["type"] for f in filters}
    best, pos = "ANY", 10**9
    for t, words in TYPE_WORDS.items():
        if t in ftypes:
            continue
        for w in words:
            i = ql.find(w)
            if i != -1 and i < pos:
                best, pos = t, i
    return {"return_type": best, "filters": filters}


def offline_answer(q, retrieved):
    if not retrieved["results"]:
        return "I could not find this in the knowledge graph."
    lines = [f'Found {retrieved["count"]} result(s):']
    for r in retrieved["results"]:
        lines.append(f'- {r["type"]}: {r["name"]}')
    return "\n".join(lines)
