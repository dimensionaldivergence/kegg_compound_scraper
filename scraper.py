#!/usr/bin/env python3
"""
Script for scraping molecular formulas from https://www.genome.jp/ based on KEGG

Usage:
`python3 scraper.py`

Output:    KEGG.xlsx file will get updated
"""
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