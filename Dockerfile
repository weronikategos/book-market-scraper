FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper.py analysis.py ./
RUN mkdir -p data

# By default: a quick 5-page scrape. Pass a different command after the image name, e.g.
# docker run --rm -v "${PWD}/data:/app/data" book-market-scraper python scraper.py --db data/books.db
CMD ["python", "scraper.py", "--pages", "5", "--no-categories", "--db", "data/books.db"]
