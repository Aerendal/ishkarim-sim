#!/usr/bin/env python3
"""
demo.py — demo ishkarim-sim

Symulacje agentowe (ABM) + differentiable physics — lokalne środowiska AI bez GPU

Uruchomienie:
    python projects/ishkarim-sim/demo.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[0] / "src"))
import ishkarim_sim as m

docs = m.load_knowledge_index()
mesa_docs = [d for d in docs if "mesa" in d["name"].lower() or "abm" in d["name"].lower()]
rl_docs   = [d for d in docs if "rl" in d["name"].lower() or "differentiable" in d["name"].lower()]
llm_docs  = [d for d in docs if "llm" in d["name"].lower() or "social" in d["name"].lower()]

print(f"Symulacje AI — {len(docs)} katalogów wiedzy")
print(f"  Mesa/ABM:              {len(mesa_docs)}")
print(f"  Differentiable/RL:     {len(rl_docs)}")
print(f"  LLM social sims:       {len(llm_docs)}")
for d in docs[:4]:
    print(f"  • [{d['maturity']:8s}] {d['name'][:60]}")

