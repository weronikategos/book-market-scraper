import sqlite3
from pathlib import Path

import pandas as pd

from analysis import make_charts, run_queries
from scraper import init_db, parse_books, parse_category, save_books

FIXTURES = Path(__file__).parent / "fixtures"
PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"


def read(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_books_reads_all_fields():
    books, next_url = parse_books(read("catalogue_page.html"), PAGE_URL)
    assert len(books) == 2
    assert books[0] == {
        "title": "A Light in the Attic",
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "price_gbp": 51.77,
        "rating": 3,
        "in_stock": True,
    }
    assert books[1]["rating"] == 1
    assert next_url == "https://books.toscrape.com/catalogue/page-2.html"


def test_parse_category():
    assert parse_category(read("book_page.html")) == "Poetry"


def test_save_books_skips_duplicates_and_analysis_runs(tmp_path):
    books, _ = parse_books(read("catalogue_page.html"), PAGE_URL)
    for book in books:
        book["category"] = "Poetry"
    db = tmp_path / "books.db"
    conn = sqlite3.connect(db)
    init_db(conn)
    save_books(conn, books)
    save_books(conn, books)
    assert conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 2
    conn.close()

    results = run_queries(db)
    assert results["Top 10 categories by number of books"].iloc[0]["books"] == 2

    with sqlite3.connect(db) as c:
        df = pd.read_sql_query("SELECT * FROM books", c)
    make_charts(df, tmp_path / "charts")
    assert (tmp_path / "charts" / "price_distribution.png").exists()
    assert (tmp_path / "charts" / "top_categories.png").exists()


def test_well_rated_categories_query(tmp_path):
    db = tmp_path / "books.db"
    conn = sqlite3.connect(db)
    init_db(conn)
    books = [{"title": f"B{i}", "url": f"u{i}", "price_gbp": 10.0 + i, "rating": 5 if i < 6 else 2,
              "in_stock": True, "category": "Poetry"} for i in range(8)]
    save_books(conn, books)
    conn.close()
    result = run_queries(db)["Most expensive categories among well-rated books (4-5 stars)"]
    assert result.iloc[0]["category"] == "Poetry"
    assert result.iloc[0]["books"] == 6
