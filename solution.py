import json
import os
import sys
import logging
from collections import Counter

import requests

DATA_URL = "https://dmachek.github.io/meteorites-homework/meteorite_landings.json"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
DATA_PATH = os.path.join(CACHE_DIR, "meteorites.json")
ETAG_PATH = os.path.join(CACHE_DIR, "meteorites.etag")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def sync_data():
    os.makedirs(CACHE_DIR, exist_ok=True)

    headers = {}
    if os.path.exists(DATA_PATH) and os.path.exists(ETAG_PATH):
        with open(ETAG_PATH, "r") as f:
            etag = f.read().strip()
        if etag:
            headers["If-None-Match"] = etag

    try:
        resp = requests.get(DATA_URL, headers=headers, timeout=15, stream=True)
        if resp.status_code == 304:
            logging.info("Using cached dataset.")
            return

        resp.raise_for_status()

        with open(DATA_PATH, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        etag = resp.headers.get("ETag")
        if etag:
            with open(ETAG_PATH, "w") as f:
                f.write(etag)

        logging.info("Downloaded latest dataset.")

    except (requests.ConnectionError, requests.Timeout):
        if os.path.exists(DATA_PATH):
            logging.warning("Could not reach server, using cached dataset.")
        else:
            sys.exit("Download failed and no cache is available.")

    except requests.HTTPError as exc:
        sys.exit(f"HTTP error while downloading data: {exc.response.status_code}")


def safe_mass(item):
    try:
        return float(item.get("mass") or 0)
    except (ValueError, TypeError):
        return 0.0


def main():
    sync_data()

    if not os.path.exists(DATA_PATH):
        sys.exit("Data file not found.")

    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            meteorites = json.load(f)
    except json.JSONDecodeError as exc:
        sys.exit(f"Could not parse JSON: {exc}")

    if not isinstance(meteorites, list):
        sys.exit("Unexpected data format.")

    logging.info(f"1. Total entries: {len(meteorites)}")

    heaviest = max(meteorites, key=safe_mass, default={})
    heaviest_mass = safe_mass(heaviest)
    logging.info(f"2. Heaviest: {heaviest.get('name', 'N/A')} ({heaviest_mass:,.0f} g)")

    years = [item["year"][:4] for item in meteorites if item.get("year")]
    if years:
        year, count = Counter(years).most_common(1)[0]
        logging.info(f"3. Peak year: {year} ({count} landings)")
    else:
        logging.info("3. Peak year: N/A")


if __name__ == "__main__":
    main()