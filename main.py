"""CLI: python main.py [-q "question"] [--demo] [--offline] [--check]"""
import argparse, json
import kg
from offline import offline_plan, offline_answer

SAMPLE_QUESTIONS = [
    "Which products from brand Zenith are supplied by vendor Sunrise Traders?",
    "Which customers bought products from brand Lumo?",
    "List all products in the Electronics category with their vendors.",
    "Which vendors supply products in the Grocery category?",
    "Which orders contain products supplied by Metro Wholesale?",
    "What is linked to banana in the knowledge graph?",
    "Which products have the banana keyword?",
]


def ask(question, g, offline=False):
    if offline:
        plan = offline_plan(question, g)
    else:
        import llm
        plan = llm.plan_query(question, kg.describe_schema(g))       # LLM -> graph query
    retrieved = kg.execute(g, plan)                                   # graph retrieval
    if offline:
        ans = offline_answer(question, retrieved)
    else:
        ans = llm.answer(question, retrieved)                         # LLM answers from retrieved data only
    return plan, retrieved, ans


def show(question, plan, retrieved, ans):
    print(f"\nQ: {question}\nGraph query: {json.dumps(plan)}\nRetrieved: {retrieved['count']} node(s) {retrieved['notes']}\nAnswer: {ans}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-q", "--question")
    p.add_argument("--demo", action="store_true", help="run sample questions and write sample_results.md")
    p.add_argument("--offline", action="store_true", help="no LLM (rule-based planner) - testing only")
    p.add_argument("--check", action="store_true", help="print graph stats + banana count")
    a = p.parse_args()
    g = kg.build_graph()
    if a.check:
        print(f"Nodes: {g.number_of_nodes()}  Edges: {g.number_of_edges()}  banana nodes: {kg.banana_count(g)}")
        return
    if a.demo:
        md = [f"# Sample Results ({'offline rule-based planner' if a.offline else 'LLM: Claude'})\n"]
        for i, q in enumerate(SAMPLE_QUESTIONS, 1):
            plan, ret, ans = ask(q, g, a.offline)
            show(q, plan, ret, ans)
            names = ", ".join(f'{r["type"]}:{r["name"]}' for r in ret["results"]) or "-"
            md.append(f"## {i}. {q}\n**Graph query:** `{json.dumps(plan)}`\n\n**Retrieved:** {names}\n\n**Answer:** {ans}\n")
        open("sample_results.md", "w", encoding="utf-8").write("\n".join(md))
        print("\nSaved sample_results.md")
    elif a.question:
        show(a.question, *ask(a.question, g, a.offline))
    else:
        print("Ask a question (blank to quit)")
        while (q := input("\n> ").strip()):
            show(q, *ask(q, g, a.offline))


if __name__ == "__main__":
    main()
