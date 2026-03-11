#!/usr/bin/env python3
"""
bench_sim.py — benchmarki wydajnościowe dla ishkarim_sim.

Mierzy:
  1. Czas importu modułu
  2. Czas load_knowledge_index()
  3. Przepustowość extract_python_blocks()
  4. Testy specyficzne dla obszaru sim

Uruchomienie:
    python projects/ishkarim-sim/benchmarks/bench_sim.py
    python projects/ishkarim-sim/benchmarks/bench_sim.py --quick
"""
from __future__ import annotations
import time
import sys
import argparse
from pathlib import Path

# Add src/ to path for editable installs fallback
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


def fmt_ms(t: float) -> str:
    if t < 0.001:
        return f"{t*1e6:.1f} µs"
    if t < 1.0:
        return f"{t*1000:.2f} ms"
    return f"{t:.3f} s"


def bench_import(n: int = 5) -> float:
    """Mierzy czas importu modułu (mediana z n prób)."""
    import importlib
    times = []
    for _ in range(n):
        # Force reimport
        mod_name = "ishkarim_sim"
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        t0 = time.perf_counter()
        importlib.import_module(mod_name)
        times.append(time.perf_counter() - t0)
    times.sort()
    return times[len(times) // 2]


def bench_load_index(root: str, n: int = 3) -> tuple[float, int]:
    """Mierzy czas load_knowledge_index() i liczbę rekordów."""
    import ishkarim_sim
    times = []
    count = 0
    for _ in range(n):
        t0 = time.perf_counter()
        docs = ishkarim_sim.load_knowledge_index(root=root)
        times.append(time.perf_counter() - t0)
        count = len(docs)
    times.sort()
    return times[len(times) // 2], count


def bench_extract_blocks(root: str, n_files: int = 20) -> tuple[float, int]:
    """Mierzy przepustowość extract_python_blocks() na n_files plikach WORK.md."""
    from ishkarim_sim.utils import read_work_md, extract_python_blocks
    import ishkarim_sim
    docs = ishkarim_sim.load_knowledge_index(root=root)
    sample = docs[:n_files]

    t0 = time.perf_counter()
    total_blocks = 0
    total_bytes = 0
    for doc in sample:
        work = read_work_md(Path(root) / doc["name"])
        blocks = extract_python_blocks(work)
        total_blocks += len(blocks)
        total_bytes += len(work)
    elapsed = time.perf_counter() - t0

    return elapsed, total_blocks


def bench_tags_parse(root: str, n_files: int = 50) -> tuple[float, int]:
    """Mierzy czas parsowania TAGS.md dla n_files plików."""
    from ishkarim_sim.utils import extract_tags
    import ishkarim_sim
    docs = ishkarim_sim.load_knowledge_index(root=root)
    sample = docs[:n_files]

    t0 = time.perf_counter()
    parsed = 0
    for doc in sample:
        tags = extract_tags(Path(root) / doc["name"])
        if tags:
            parsed += 1
    elapsed = time.perf_counter() - t0
    return elapsed, parsed


def run_area_benchmarks(root: str, quick: bool) -> list[tuple[str, str, str]]:
    """Generic area benchmarks."""
    import importlib
    mod = importlib.import_module("ishkarim_sim")
    docs = mod.load_knowledge_index(root=root)
    n = min(len(docs), 20 if not quick else 5)

    from ishkarim_sim.utils import extract_tags, read_work_md
    t0 = time.perf_counter()
    for doc in docs[:n]:
        extract_tags(Path(root) / doc["name"])
        read_work_md(Path(root) / doc["name"])
    t = time.perf_counter() - t0
    per = t / n * 1000 if n > 0 else 0
    return [("full doc pipeline", fmt_ms(t), f"{n} docs, {per:.1f} ms/doc")]


def main():
    parser = argparse.ArgumentParser(description="Benchmarki dla ishkarim-sim")
    parser.add_argument("--quick", action="store_true", help="Szybki tryb (mniej iteracji)")
    parser.add_argument("--root", default=None, help="Ścieżka do repozytorium Ishkarim")
    args = parser.parse_args()

    # Find repo root
    if args.root:
        root = args.root
    else:
        r = Path(__file__).resolve()
        for _ in range(8):
            if (r / "CHANGELOG.md").exists():
                root = str(r)
                break
            r = r.parent
        else:
            root = str(Path(__file__).parents[4])

    n_iter = 3 if args.quick else 5
    n_files = 10 if args.quick else 20

    print(f"\n============================================================")
    print(f"  Benchmark: ishkarim-sim")
    print(f"  Root: {root}")
    print(f"  Mode: {'quick' if args.quick else 'full'}")
    print(f"============================================================\n")

    results = []

    # 1. Import
    t = bench_import(n_iter)
    results.append(("Import modułu", fmt_ms(t), ""))
    print(f"  Import:           {fmt_ms(t)}")

    # 2. Load index
    t, count = bench_load_index(root, n_iter)
    results.append(("load_knowledge_index()", fmt_ms(t), f"{count} rekordów"))
    print(f"  load_index:       {fmt_ms(t)}  ({count} rekordów)")

    # 3. Extract blocks
    t, blocks = bench_extract_blocks(root, n_files)
    per_file = t / n_files * 1000
    results.append(("extract_python_blocks()", fmt_ms(t), f"{blocks} bloków / {n_files} plików"))
    print(f"  extract_blocks:   {fmt_ms(t)}  ({blocks} bloków, {per_file:.2f} ms/plik)")

    # 4. Tags parse
    t, parsed = bench_tags_parse(root, 50 if not args.quick else 20)
    n_tags = 50 if not args.quick else 20
    per_tag = t / n_tags * 1000
    results.append(("extract_tags()", fmt_ms(t), f"{parsed}/{n_tags} sparsowanych"))
    print(f"  parse_tags:       {fmt_ms(t)}  ({parsed}/{n_tags}, {per_tag:.2f} ms/plik)")

    # Area-specific
    area_results = run_area_benchmarks(root, args.quick)
    for name, timing, note in area_results:
        results.append((name, timing, note))
        print(f"  {name:<22} {timing:<12} {note}")

    # Summary
    print(f"\n────────────────────────────────────────────────────────────")
    print(f"  Wyniki (JSON):")
    import json
    summary = {
        "area": "sim",
        "benchmarks": [
            {"name": r[0], "time": r[1], "note": r[2]} for r in results
        ]
    }
    print("  " + json.dumps(summary, ensure_ascii=False, indent=2).replace("\n", "\n  "))


if __name__ == "__main__":
    main()
