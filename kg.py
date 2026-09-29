"""Knowledge Graph (NetworkX) build + safe query executor."""
import csv, os, re
import networkx as nx

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _rows(fname):
    with open(os.path.join(DATA, fname), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build_graph():
    g = nx.MultiDiGraph()
    for r in _rows("brands.csv"):
        g.add_node(r["brand_id"], type="Brand", name=r["name"], country=r["country"])
    for r in _rows("categories.csv"):
        g.add_node(r["category_id"], type="Category", name=r["name"])
    for r in _rows("vendors.csv"):
        g.add_node(r["vendor_id"], type="Vendor", name=r["name"], city=r["city"])
    for r in _rows("customers.csv"):
        g.add_node(r["customer_id"], type="Customer", name=r["name"], city=r["city"])
    for r in _rows("products.csv"):
        g.add_node(r["product_id"], type="Product", name=r["name"], price=int(r["price"]))
        g.add_edge(r["product_id"], r["brand_id"], rel="HAS_BRAND")
        g.add_edge(r["product_id"], r["category_id"], rel="IN_CATEGORY")
        g.add_edge(r["vendor_id"], r["product_id"], rel="SUPPLIES")
    for r in _rows("orders.csv"):
        g.add_node(r["order_id"], type="Order", name=r["order_id"], date=r["date"], status=r["status"])
        g.add_edge(r["customer_id"], r["order_id"], rel="PLACED")
    for r in _rows("order_items.csv"):
        g.add_edge(r["order_id"], r["product_id"], rel="CONTAINS", quantity=int(r["quantity"]))
    # 'banana' keyword nodes (exactly 5 rows in keywords.csv)
    for r in _rows("keywords.csv"):
        g.add_node(r["keyword_id"], type="Keyword", name=r["value"])
        g.add_edge(r["linked_id"], r["keyword_id"], rel="HAS_KEYWORD")
    return g


def banana_count(g):
    return sum(1 for _, d in g.nodes(data=True) if str(d.get("name", "")).lower() == "banana")


def schema_graph(g):
    s = nx.Graph()
    for u, v in g.edges():
        s.add_edge(g.nodes[u]["type"], g.nodes[v]["type"])
    return s


def describe_schema(g):
    """Text description of the graph given to the LLM (schema + known entity names)."""
    attrs, names, rels = {}, {}, set()
    for n, d in g.nodes(data=True):
        attrs.setdefault(d["type"], sorted(k for k in d if k != "type"))
        names.setdefault(d["type"], []).append(d["name"])
    for u, v, d in g.edges(data=True):
        rels.add(f'{g.nodes[u]["type"]} -[{d["rel"]}]-> {g.nodes[v]["type"]}')
    out = ["NODE TYPES AND PROPERTIES:"]
    out += [f"- {t}: {', '.join(a)}" for t, a in attrs.items()]
    out += ["RELATIONSHIPS:"] + [f"- {r}" for r in sorted(rels)]
    out += ["KNOWN ENTITY NAMES:"]
    for t, ns in names.items():
        uniq = sorted(set(ns))
        out.append(f"- {t}: {', '.join(uniq)}")
    return "\n".join(out)


def find_nodes(g, ntype, name):
    name = str(name or "").strip().lower()
    exact = [n for n, d in g.nodes(data=True) if d["type"] == ntype and d["name"].lower() == name]
    if exact:
        return exact
    return [n for n, d in g.nodes(data=True) if d["type"] == ntype and name and name in d["name"].lower()]


def _neighbors(g, n):
    return set(g.successors(n)) | set(g.predecessors(n))


def _walk(g, start_nodes, type_path):
    cur = set(start_nodes)
    for t in type_path[1:]:
        cur = {m for n in cur for m in _neighbors(g, n) if g.nodes[m]["type"] == t}
    return cur


def _view(g, n):
    d = dict(g.nodes[n])
    d["id"] = n
    rels = []
    for _, v, e in g.out_edges(n, data=True):
        extra = f' (quantity={e["quantity"]})' if "quantity" in e else ""
        rels.append(f'{e["rel"]} -> {g.nodes[v]["type"]}: {g.nodes[v]["name"]}{extra}')
    for u, _, e in g.in_edges(n, data=True):
        rels.append(f'{e["rel"]} <- {g.nodes[u]["type"]}: {g.nodes[u]["name"]}')
    d["relations"] = sorted(rels)
    return d


def _key(n):
    return (len(n), n)


def execute(g, plan, limit=50):
    """plan = {"return_type": <NodeType|"ANY">, "filters": [{"type":..., "name":...}]}
    Semantics: return nodes of return_type connected (via the schema path) to EVERY filter node.
    "ANY" returns direct neighbours of the filter nodes. No free-form code is executed."""
    s = schema_graph(g)
    rt = plan.get("return_type")
    filters = plan.get("filters") or []

    def out(res, notes):
        return {"plan": plan, "count": len(res), "results": [_view(g, n) for n in sorted(res, key=_key)[:limit]], "notes": notes}

    if rt != "ANY" and rt not in s:
        return out([], [f"Unknown return_type '{rt}'."])
    if rt == "ANY" and not filters:
        return out([], ["'ANY' needs at least one filter."])
    sets = []
    for f in filters:
        ft, nm = f.get("type"), f.get("name")
        if ft not in s:
            return out([], [f"Unknown filter type '{ft}'."])
        matches = find_nodes(g, ft, nm)
        if not matches:
            return out([], [f"No {ft} named '{nm}' exists in the graph."])
        if rt == "ANY":
            reach = set().union(*[_neighbors(g, m) for m in matches])
        else:
            try:
                path = nx.shortest_path(s, ft, rt)
            except nx.NetworkXNoPath:
                return out([], [f"No relationship path between {ft} and {rt}."])
            reach = _walk(g, matches, path)
        sets.append(reach)
    if rt == "ANY":
        res = set.intersection(*sets)
    else:
        res = {n for n, d in g.nodes(data=True) if d["type"] == rt}
        for r in sets:
            res &= r
    return out(res, [] if res else ["Query ran but matched nothing."])
