#!/usr/bin/env python3
"""
Define scraping functions here
"""
from lxml import etree
import requests
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from var_scraper import BASE_URL, EXCEL_FILENAME                                # pylint: disable=wrong-import-position


class KEGGScraper:
    """
    KEGGScraper class containing all necessary methods to perform molecular
    formula scraping from https://www.genome.jp
    """
    def __init__(self):
        self.keggs = self.parse_kegg_xlsx()


    @staticmethod
    def parse_kegg_xlsx():
        """
        Read in KEGG.xlsx which has the following format:
        | 1,3-bisphosphoglycerate_neg | 11-cis-eicosenoic acid_neg | ...
        | C00236                      | C04742                     | ...

        We are to input the molecular formula into the 3rd row.

        Note:
            - Some values (1st row) might appear multiple times
            - Some values (2nd row) might only be "-" character, skip those columns
            - There might be already some values in the 3rd row
        """
        raw_excel_df = pd.read_excel(io=EXCEL_FILENAME, index_col=None)
        raw_excel_df = raw_excel_df.transpose()
        raw_excel_df = raw_excel_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Set names for the columns
        length = len(raw_excel_df.columns)
        if length == 1:
            parsed_excel_df = raw_excel_df.set_axis(['KEGG'], axis=1, inplace=False)
            parsed_excel_df = parsed_excel_df.assign(formula=[None] * len(parsed_excel_df))
        elif length == 2:
            parsed_excel_df = raw_excel_df.set_axis(['KEGG', 'formula'], axis=1, inplace=False)
        else:
            raise Exception("Excel file was possibly empty!")

        return parsed_excel_df


    def scrape_keggs(self):
        """
        Based on the KEGG.xlsx which might already have some molecular formulas
        scraped, scrape the rest.
        """
        for index, row in self.keggs.iterrows():
            if row['KEGG'] != '-' and not pd.isna(row['KEGG']) and row['formula'] is None:
                # Get page with current KEGG
                try:
                    r = requests.get(BASE_URL.format(KEGG=row['KEGG']), verify=False)                   # pylint: disable=invalid-name
                except Exception:
                    print("SSLError, skipping.")
                    continue
                inner_dom = etree.HTML(r.text)                                                      # pylint: disable=c-extension-no-member

                # Parse molecular formula
                try:
                    molecular_formula = inner_dom.xpath("//*[contains(text(),'Formula')]/parent::th/following-sibling::td/div")[0].text     # pylint: disable=line-too-long
                    self.keggs.at[index, 'formula'] = molecular_formula
                    print(f"Found '{molecular_formula}' formula for '{row['KEGG']}' KEGG.")
                except Exception:       # pylint: disable=broad-except
                    print(f"Did not find formula for '{row['KEGG']}' KEGG at URL: '{BASE_URL.format(KEGG=row['KEGG'])}'.")                  # pylint: disable=line-too-long

        # Write updated DataFrame to file
        self.keggs.transpose().to_excel(EXCEL_FILENAME, index=False, na_rep='')
