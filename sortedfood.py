#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# "THE SCOTCH-WARE LICENSE" (Revision 42):
# <DonMarco42@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a scotch whisky in return
# Marco 'don' Kaulea
# ----------------------------------------------------------------------------
"""sortedfood fetches recipies from sortedfood.com.

Usage:
    sortedfood.py [<pageID>]

"""

import docopt as dopt
import requests
import json
import functools


dump_json = functools.partial(json.dumps,
                              indent=4,
                              ensure_ascii=False,
                              sort_keys=True)


def get_recipe(page_name,
               ingredients=True,
               instructions=True,
               session=None):
    if session is None:
        session = requests.Session()
    payload = {'recipeid':  page_name,
               'getIngredients': 'true' if ingredients else 'false',
               'getInstructions': 'true' if instructions else 'false'}
    response = session.get('https://cms.sortedfood.com/apiRecipe/getRecipe',
                           params=payload)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return ""


def scrape_page():
    print("Scraping site")


def main():
    arguments = dopt.docopt(__doc__)
    if(arguments.get("<pageID>", None) is not None):
        page_id = int(arguments["<pageID>"])
        print(dump_json(get_recipe(page_id)))
        scrape_page()


if __name__ == "__main__":
    main()
