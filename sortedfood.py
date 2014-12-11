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
import os


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


def get_categories():
    response = requests.get(
        'https://cms.sortedfood.com/apiRecipe/getCategoryMenu')
    if response.status_code != 200:
        raise requests.HTTPError()
    response.encoding = 'utf-8'
    data = json.loads(response.text)
    categories = {}
    for category in data['category']:
        for cat in category['child']['category']:
            cat.pop('recipes', None)
            cat.pop('is_empty', None)
            cat.pop('child', None)
            cat['type'] = category['name']
            categories[cat['id']] = cat
    return categories


def get_recipies_from_category(category, usertype=1, page=0, count=0):
    session = requests.Session()
    payload = {'categoryId': category,
               'usertype': usertype,
               'page': page,
               'offset': count}
    response = session.get(
        'https://cms.sortedfood.com/apiRecipe/getFeaturedByUsertype',
        params=payload)
    if response.status_code == 200:
        return json.loads(response.text)


def scrape_page():
    print("Scraping site")
    categories = get_categories()
    recipe_ids = set()
    cat_ids = sorted(categories.keys())
    i = 1
    for id in cat_ids:
        print("Processing category {}/{}: {}".format(i, len(cat_ids), id))
        i += 1
        recipies = get_recipies_from_category(id)
        recipe_ids.update(extract_recipe_ids(recipies))

    print("Recipe IDs retrieved, starting download")
    i = 1
    for id in recipe_ids:
        print("Processing {}/{}: {}".format(i, len(recipe_ids), id))
        filename = "dump/{}.json".format(id)
        i += 1
        if os.path.isfile(filename):
            print("File already exists\n")
            continue

        recipe = get_recipe(id)
        if not recipe.get('successful', False):
            print("Retieval failure\n")
            continue
        recipe = recipe['recipe']
        print("Recipe: {}\n".format(recipe['title']))
        with open(filename, 'w') as out_file:
            out_file.write(dump_json(recipe))


def extract_recipe_ids(page):
    recipes_list = page.get('recipe', list())
    ids = set()
    for recipe in recipes_list:
        ids.add(recipe['recipe_id'])
    return ids


def main():
    arguments = dopt.docopt(__doc__)
    if(arguments.get("<pageID>", None) is not None):
        page_id = int(arguments["<pageID>"])
        print(dump_json(get_recipe(page_id)))
    elif(arguments.get('categories', False)):
        print(dump_json(get_categories()))
    elif(arguments.get('scrape', False)):
        scrape_page()


if __name__ == "__main__":
    main()
