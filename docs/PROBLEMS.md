# PROBLEMS — ishkarim-sim

> Symulacje agentowe (ABM) + differentiable physics — lokalne środowiska AI bez GPU

## ✅ Co ten projekt rozwiązuje

- ✅ Mesa/Sugarscape jako deterministyczne środowisko testowe dla agentów AI
- ✅ Differentiable physics — gradienty przez symulator (RL, optymalizacja)
- ✅ LLM-sterowane symulacje społeczne (agenci z pamięcią i celami)
- ✅ Lokalne środowisko testowe zamiast kosztownego real-world deployment
- ✅ Reproducible seeds — te same wyniki przy tym samym seedzie RNG

---

## ❌ Czego ten projekt NIE rozwiązuje

- ❌ Fotorealistyczna renderacja — to symulacje logiczne, nie graficzne
- ❌ Skalowanie do milionów agentów — Mesa ma limity ~10k agentów na CPU
- ❌ Real-time symulacje z ludzką interakcją w pętli
- ❌ Physics-accurate fluid/rigid body dynamics — uproszczone modele

---

## ⚠️ Znane problemy i ograniczenia

- ⚠️ **Mesa 3.4.1** — API zmienia się między wersjami (breaking changes w serii 3.x)
- ⚠️ **Differentiable simulators** wymagają JAX/PyTorch — nietrywialny setup na czystym CPU
- ⚠️ **LLM w pętli** spowalnia symulację ~100x względem deterministycznych reguł
- ⚠️ **Brak standardowego formatu** eksportu wyników między frameworkami

---

## 🎯 Przypadki użycia

- 🎯 Prototypowanie strategii NPC przed implementacją w silniku gry
- 🎯 Modelowanie ekonomiczne (rynek, zasoby) dla AI decision-making
- 🎯 Testowanie hipotez badawczych o zachowaniach zbiorowych bez GPU
- 🎯 RL environment sandbox bez kosztów API (lokalny gym-like)

---

## 📊 Matryca decyzyjna

| Pytanie | Odpowiedź |
|---------|-----------|
| Czy potrzebujesz GPU? | **NIE** — zaprojektowany dla CPU-only |
| Czy działa offline? | **TAK** — zero zewnętrznych zależności sieciowych |
| Czy jest produkcyjny? | **WZORCE** — referencja do implementacji, nie plug-and-play |
| Czy obsługuje skalowanie? | **LOKALNIE** — single-node, do ~kilku tysięcy dokumentów |
| Licencja? | **MIT** — możesz używać w projektach komercyjnych |

---

## 🔗 Powiązane projekty

Inne moduły Ishkarim które uzupełniają ten projekt:

| Projekt | Relacja |
|---------|---------|
| `ishkarim-rag` | Wyszukiwanie semantyczne nad bazą wiedzy |
| `ishkarim-sqlite` | Trwała pamięć i event-sourcing |
| `ishkarim-agent` | Architektura agentów AI |
| `ishkarim-security` | Bezpieczeństwo systemów AI |
| `ishkarim-bench` | Benchmarki wydajnościowe |

---

*Ostatnia aktualizacja: 2026-03-11 | Generator: `scripts/enrich_projects.py`*
