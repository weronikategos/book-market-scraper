"""Analizuje książki zapisane w bazie SQLite i tworzy wykresy w folderze charts/."""
import argparse
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

QUERIES = {
    "Średnia cena wg oceny": """
        SELECT rating, COUNT(*) AS books, ROUND(AVG(price_gbp), 2) AS avg_price
        FROM books GROUP BY rating ORDER BY rating""",
    "Top 10 kategorii wg liczby książek": """
        SELECT category, COUNT(*) AS books, ROUND(AVG(price_gbp), 2) AS avg_price,
               ROUND(AVG(rating), 2) AS avg_rating
        FROM books WHERE category IS NOT NULL
        GROUP BY category ORDER BY books DESC LIMIT 10""",
    "5 najdroższych książek z oceną 5": """
        SELECT title, price_gbp FROM books
        WHERE rating = 5 ORDER BY price_gbp DESC LIMIT 5""",
}


def load(db_path):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM books", conn)


def run_queries(db_path):
    with sqlite3.connect(db_path) as conn:
        return {name: pd.read_sql_query(sql, conn) for name, sql in QUERIES.items()}


def make_charts(df, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["price_gbp"], bins=20, color="#4C72B0", edgecolor="white")
    ax.set(title="Rozkład cen książek", xlabel="Cena (GBP)", ylabel="Liczba książek")
    fig.tight_layout()
    fig.savefig(out_dir / "price_distribution.png", dpi=120)
    plt.close(fig)

    by_rating = df.groupby("rating")["price_gbp"].mean()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(by_rating.index.astype(str), by_rating.values, color="#55A868")
    ax.set(title="Średnia cena wg oceny", xlabel="Ocena (gwiazdki)", ylabel="Średnia cena (GBP)")
    fig.tight_layout()
    fig.savefig(out_dir / "price_by_rating.png", dpi=120)
    plt.close(fig)

    if df["category"].notna().any():
        top = df["category"].value_counts().head(10).sort_values()
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(top.index, top.values, color="#C44E52")
        ax.set(title="10 kategorii z największą liczbą książek", xlabel="Liczba książek")
        fig.tight_layout()
        fig.savefig(out_dir / "top_categories.png", dpi=120)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Analiza danych o książkach")
    parser.add_argument("--db", default="books.db")
    parser.add_argument("--out", default="charts")
    args = parser.parse_args()

    df = load(args.db)
    print(f"Liczba książek: {len(df)}")
    print(f"Średnia cena: {df['price_gbp'].mean():.2f} GBP, mediana: {df['price_gbp'].median():.2f} GBP")
    print(f"Dostępne w magazynie: {df['in_stock'].mean():.0%}")
    print(f"Korelacja ocena–cena: {df['rating'].corr(df['price_gbp']):.3f}\n")
    for name, result in run_queries(args.db).items():
        print(f"== {name}\n{result.to_string(index=False)}\n")
    make_charts(df, args.out)
    print(f"Wykresy zapisane w folderze {args.out}/")


if __name__ == "__main__":
    main()
