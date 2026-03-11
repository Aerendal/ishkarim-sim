# Contributing to this project

## Jak zgłosić problem

Otwórz issue z:
- Opisem problemu
- Wersją Pythona (`python --version`)
- Minimalnym przykładem reprodukcji

## Jak uruchomić testy

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Jak dodać nowy katalog-źródło

1. Dodaj katalog do repozytorium Ishkarim z plikami `WORK.md` i `TAGS.md`
2. Ustaw `topic_area: sim` w `TAGS.md`
3. Uruchom `python scripts/build_projects.py` aby odbudować projekt

## Konwencje

- Kod Python 3.10+
- Formatowanie: Black (`black src/ tests/`)
- Typowanie: mypy (opcjonalne)
- Testy: pytest

## Kontakt

Projekty Ishkarim są materiałami referencyjnymi. Wkład mile widziany przez PR.
