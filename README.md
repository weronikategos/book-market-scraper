# Book Market Scraper

Scraper, który pobiera dane o 1000 książkach ze sklepu [books.toscrape.com](https://books.toscrape.com) (strona stworzona do nauki scrapingu), zapisuje je w bazie **SQLite**, a potem analizuje je w **SQL i pandas** i rysuje wykresy.

## Problem
Księgarnia internetowa chce wiedzieć, jak wyglądają ceny u konkurencji: ile kosztują książki w poszczególnych kategoriach i czy lepiej oceniane tytuły są droższe.

## Co robi projekt
1. `scraper.py` przechodzi po 50 stronach katalogu, odczytuje tytuł, cenę, ocenę, dostępność i kategorię, i zapisuje je w `books.db`. Nie dubluje rekordów przy ponownym uruchomieniu.
2. `analysis.py` liczy statystyki zapytaniami SQL i w pandas, a wykresy zapisuje w `charts/`.

## Technologie
Python, requests, BeautifulSoup, SQLite, pandas, matplotlib, pytest

## Jak uruchomić
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scraper.py            # pełne pobranie (ok. 1000 zapytań, kilkanaście minut)
python scraper.py --pages 5 --no-categories   # szybki test
python analysis.py
python -m pytest             # testy
```

## Wyniki
Dane z pełnego pobrania: 1000 książek z 50 stron katalogu.

- **Średnia cena:** 35,07 GBP, **mediana:** 35,98 GBP. Ceny rozkładają się dość równomiernie w przedziale ok. 10–60 GBP.
- **Ocena a cena:** korelacja wynosi **0,028**, czyli praktycznie zero. Lepiej oceniane książki nie są droższe: średnia cena dla każdej liczby gwiazdek mieści się w przedziale 34,56–36,09 GBP.
- **Kategorie:** najwięcej książek ma kategoria **Default** (152), a z kategorii tematycznych **Nonfiction** (110) i **Sequential Art** (75). Najdroższa średnio z top 10 jest **Fantasy** (39,59 GBP).
- Wszystkie książki są dostępne w magazynie.

![Rozkład cen](charts/price_distribution.png)

![Średnia cena wg oceny](charts/price_by_rating.png)

![Top 10 kategorii](charts/top_categories.png)

## Co bym dodał(a) dalej
- harmonogram (np. codzienne pobieranie) i śledzenie zmian cen w czasie
- dashboard w Power BI lub Streamlit
