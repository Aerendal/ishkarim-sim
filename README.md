# ishkarim-sim

> Symulacje ABM i fizyczne: Mesa, differentiable physics, LLM w symulacjach społecznych.

## Instalacja

```bash
pip install -e projects/ishkarim-sim
```

Lub lokalnie z tego repozytorium:

```bash
cd projects/ishkarim-sim
pip install -e ".[dev]"
```

## Użycie

```python
import ishkarim_sim as m

# Lista dostępnych modułów
print(m.MODULES)

# Wczytaj indeks wiedzy
docs = m.load_knowledge_index()
```

## Obszar tematyczny

Ten projekt agreguje wiedzę z **23 katalogów** obszaru `sim`:

- `AMBER  - CPU-only scaffold dla ABM`
- `AMBER: kolumnowa architektura dla szybszych symulacji`
- `Ceny dualne jako kompas w symulacjach`
- `Differentiable simulators & hybrids`
- `Hybrid physics-ML notable papers & code`
- `Mikrojądra dyfuzyjne w silnikach symulacyjnych`
- `Mini‑grid i TextWorld: małe, deterministyczne harnessy`
- `New agent‑based simulation updates_04`
- … i 15 więcej (pełna lista w [MODULES.md](MODULES.md))

## Przykładowe źródła

### AMBER  - CPU-only scaffold dla ABM

# WORK — AMBER: CPU-only scaffold dla ABM
**Data:** 2026-02-27  
**Autor:** deep-index (Copilot)  
**Status:** PLAN WDROŻENIOWY — scaffold koncepcyjnie domknięty, wymaga dopięcia `qabm.worker` i testów integracyjnych  
**Źródła:** pliki `_1.md` – `_16.md` w tym katalogu

### AMBER: kolumnowa architektura dla szybszych symulacji

# WORK — AMBER: kolumnowa architektura dla szybszych symulacji
## 0-Metadane
- **Ścieżka:** AMBER: kolumnowa architektura dla szybszych symulacji/
- **Liczba plików:** 21/21 (wszystkie z treścią, brak placeholderów)
- **Tagi:** ABM, Polars, columnar, LazyFrame, agent-simulation, determinism, event-ledger, snapshot, pytest, edge-cases

### Ceny dualne jako kompas w symulacjach

# Ceny dualne jako kompas w symulacjach — WORK
_Data: 2026-02-27_
## 0 — Metadane
- **Projekt**: Ceny dualne (shadow prices) jako sygnał planistyczny dla agentów i RL
- **Domena**: Programowanie liniowe / alokacja zasobów / systemy agentowe / RL z ograniczeniami


## Struktura projektu

```
ishkarim-sim/
├── pyproject.toml        # installable package
├── README.md
├── MODULES.md            # pełny indeks 23 katalogów-źródeł
├── src/
│   └── ishkarim_sim/
│       ├── __init__.py   # publiczne API
│       ├── utils.py      # wspólne narzędzia
│       └── *.py          # kod wyekstrahowany z WORK.md
├── tests/
│   ├── __init__.py
│   └── test_sim.py
└── docs/
    ├── overview.md
    └── sources.md
```

## Testy

```bash
pytest projects/ishkarim-sim/tests/ -v
```

## Źródło danych

Katalogi źródłowe znajdują się w katalogu głównym repozytorium Ishkarim.
Każdy katalog zawiera `WORK.md` (notatki badawcze) i `TAGS.md` (metadane).

---
*Wygenerowano automatycznie przez `scripts/build_projects.py`*
