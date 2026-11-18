#!/usr/bin/env python3
"""Run a transparent, hypothetical service-dependency scenario from JSON."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def calculate(nodes, overrides=None, municipality="todos", scenario_name="Escenario"):
    overrides = overrides or {}
    if not isinstance(nodes, list):
        raise ValueError("nodes debe ser una lista")
    by_id = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"]:
            raise ValueError("Cada nodo requiere un id de texto")
        if node["id"] in by_id:
            raise ValueError(f"ID duplicado: {node['id']}")
        deps = node.get("dependencies", [])
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
            raise ValueError(f"Dependencias inválidas en {node['id']}")
        cap = node.get("capacity")
        if cap is not None and (not isinstance(cap, (int, float)) or cap < 0):
            raise ValueError(f"Capacidad inválida en {node['id']}")
        if cap is not None and not node.get("unit"):
            raise ValueError(f"Falta unidad de capacidad en {node['id']}")
        by_id[node["id"]] = node
    for key, value in overrides.items():
        if key not in by_id:
            raise ValueError(f"Nodo afectado inexistente: {key}")
        if not isinstance(value, (int, float)) or not 0 <= value <= 100:
            raise ValueError(f"Disponibilidad directa fuera de rango para {key}")
    visiting, done, cache = set(), set(), {}
    def visit(key):
        if key in visiting:
            raise ValueError(f"Dependencia circular detectada en {key}")
        if key in done:
            return
        if key not in by_id:
            raise ValueError(f"Dependencia inexistente: {key}")
        visiting.add(key)
        for dep in by_id[key].get("dependencies", []):
            visit(dep)
        visiting.remove(key); done.add(key)
    for key in by_id:
        visit(key)
    def effective(key):
        if key in cache:
            return cache[key]
        node = by_id[key]
        dep_values = [effective(dep) for dep in node.get("dependencies", [])]
        bottleneck = min(dep_values) if dep_values else 100.0
        value = float(overrides.get(key, 100)) * bottleneck / 100.0
        cache[key] = value
        return value
    selected = [n for n in nodes if municipality == "todos" or n.get("municipality") == municipality]
    results = []
    for n in selected:
        pct = round(effective(n["id"]), 2)
        cap = n.get("capacity")
        eff_cap = round(float(cap) * pct / 100, 4) if cap is not None else None
        results.append({
            "id": n["id"], "name": n.get("name", n["id"]),
            "municipality": n.get("municipality"), "sector": n.get("sector"),
            "criticality": n.get("criticality"), "source": n.get("source"),
            "direct_availability": float(overrides.get(n["id"], 100)),
            "effective_availability_pct": pct, "capacity": cap,
            "unit": n.get("unit"), "effective_capacity": eff_cap,
            "capacity_loss": round(float(cap)-eff_cap, 4) if cap is not None else None,
            "dependencies": n.get("dependencies", []), "affected": pct < 99.999
        })
    affected = [x for x in results if x["affected"]]
    critical = [x for x in affected if x.get("criticality") == "critica"]
    return {
        "application": "PREPPER MAP PRO", "version": "2.1.0",
        "scenario_name": scenario_name, "scope": municipality,
        "assumptions": {
            "unaffected_nodes_start_at_100_pct": True,
            "dependency_rule": "Each dependency is required; effective availability is direct availability multiplied by the minimum effective availability of all providers.",
            "capacity_rule": "Declared reference capacity is multiplied by effective availability.",
            "data_status": "Hypothetical user-supplied model; not a forecast, alert, dispatch order, or official operational picture."
        },
        "summary": {
            "nodes_in_scope": len(results), "affected_nodes": len(affected),
            "critical_nodes_affected": len(critical),
            "average_effective_availability_pct": round(sum(x["effective_availability_pct"] for x in results)/len(results),2) if results else None
        },
        "overrides": overrides, "results": results
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,help="JSON con objeto {nodes:[...]}")
    p.add_argument("--override",action="append",default=[],help="ID=porcentaje, repetible")
    p.add_argument("--municipality",default="todos")
    p.add_argument("--name",default="Escenario")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding="utf-8"))
    overrides={}
    for item in a.override:
        if "=" not in item: raise ValueError(f"Override inválido: {item}")
        k,v=item.split("=",1); overrides[k]=float(v)
    result=calculate(data.get("nodes"),overrides,a.municipality,a.name)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
