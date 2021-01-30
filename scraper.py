#!/usr/bin/env python3
import traceback
from lib_scraper import KEGGScraper

def main():
    parser = KEGGScraper()
    parser.scrape_keggs()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.print_exc())