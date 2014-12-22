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
    sortedfood recipe [<pageID>]
    sortedfood categories
    sortedfood scrape

"""

import docopt as dopt
import requests
import json
import functools
import multiprocessing as mp
import os
import sortedfood_api as sf


dump_json = functools.partial(json.dumps,
                              indent=4,
                              ensure_ascii=False,
                              sort_keys=True)


def scrape_page(threads=6):
    """Scrapes all recipes from sortedfood

    Args:
        threads (int): Number of threads to use to get recipe_ids
    """
    print("Scraping site")
    session = requests.Session()
    categories = sf.get_categories(session=session)
    recipe_ids = set()
    cat_ids = sorted(categories.keys())

    i = 1
    with mp.Pool(processes=threads) as pool:
        for ids in pool.imap_unordered(sf.get_recipe_ids_from_category,
                                       cat_ids):
            print("Processing category {}/{}.".format(i, len(cat_ids)))
            i += 1
            recipe_ids.update(ids)

    print("\nRecipe IDs retrieved, starting download")
    i = 1
    for id in recipe_ids:
        print("Processing {}/{}: {}".format(i, len(recipe_ids), id))
        i += 1
        process_recipe_id(id)


def process_recipe_id(id, session=None):
    """Retrieve the recipe if it is not already stored

    Args:
        id (string): Numeric recipe id
        session (Request.Session): HTTP session to be used for the request.
            Defaults to None. When no session is provied a new one will be
            created and used.

    """
    filename = "dump/{}.json".format(id)
    if os.path.isfile(filename):
        print("File already exists\n")
        return

    recipe = sf.get_recipe(id, session=session)
    if not recipe.get('successful', False):
        print("Retieval failure\n")
        return

    recipe = recipe['recipe']
    print("Recipe: {}\n".format(recipe['title']))
    with open(filename, 'w') as out_file:
        out_file.write(dump_json(recipe))


def main():
    arguments = dopt.docopt(__doc__)
    if(arguments.get("<pageID>", None) is not None):
        page_id = int(arguments["<pageID>"])
        print(dump_json(sf.get_recipe(page_id)))
    elif(arguments.get('categories', False)):
        print(dump_json(sf.get_categories()))
    elif(arguments.get('scrape', False)):
        scrape_page()


if __name__ == "__main__":
    main()
