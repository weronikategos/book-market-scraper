"""Scrapes book data from books.toscrape.com and saves it to an SQLite database.

books.toscrape.com is a site built specifically for practising web scraping.
"""
import argparse
import sqlite3
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_books(html, page_url):
    """Returns the books from one catalogue page and the URL of the next page."""
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        rating_class = card.select_one("p.star-rating")["class"]
        rating_word = next(c for c in rating_class if c != "star-rating")
        price_text = card.select_one("p.price_color").get_text(strip=True)
        books.append({
            "title": link["title"],
            "url": urljoin(page_url, link["href"]),
            "price_gbp": float(price_text.lstrip("Â£")),
            "rating": RATINGS[rating_word],
            "in_stock": "In stock" in card.select_one("p.availability").get_text(),
        })
    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return books, next_url


def parse_category(html):
    """Reads the book's category from its detail page."""
    soup = BeautifulSoup(html, "html.parser")
    crumbs = soup.select("ul.breadcrumb li a")
    return crumbs[-1].get_text(strip=True) if len(crumbs) >= 3 else None


def init_db(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS books (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               url TEXT UNIQUE NOT NULL,
               price_gbp REAL NOT NULL,
               rating INTEGER NOT NULL,
               in_stock INTEGER NOT NULL,
               category TEXT
           )"""
    )


def save_books(conn, books):
    """Saves books; a URL that is already stored is not duplicated."""
    conn.executemany(
        """INSERT OR IGNORE INTO books (title, url, price_gbp, rating, in_stock, category)
           VALUES (:title, :url, :price_gbp, :rating, :in_stock, :category)""",
        books,
    )
    conn.commit()


def scrape(db_path, max_pages, delay, with_categories):
    session = requests.Session()
    session.headers["User-Agent"] = "book-market-scraper (educational project)"
    conn = sqlite3.connect(db_path)
    init_db(conn)

    url, page = START_URL, 0
    while url and page < max_pages:
        page += 1
        response = session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"
        books, url = parse_books(response.text, response.url)
        for book in books:
            book["category"] = None
            if with_categories:
                detail = session.get(book["url"], timeout=15)
                detail.raise_for_status()
                detail.encoding = "utf-8"
                book["category"] = parse_category(detail.text)
                time.sleep(delay)
        save_books(conn, books)
        print(f"Page {page}: saved {len(books)} books")
        time.sleep(delay)

    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    conn.close()
    print(f"Done. The database contains {total} books.")


def main():
    parser = argparse.ArgumentParser(description="Book scraper for books.toscrape.com")
    parser.add_argument("--db", default="books.db", help="SQLite database file")
    parser.add_argument("--pages", type=int, default=50, help="how many catalogue pages to scrape (max 50)")
    parser.add_argument("--delay", type=float, default=0.5, help="pause between requests in seconds")
    parser.add_argument("--no-categories", action="store_true",
                        help="skip categories (faster, 1 request per page)")
    args = parser.parse_args()
    scrape(args.db, args.pages, args.delay, not args.no_categories)


if __name__ == "__main__":
    main()
