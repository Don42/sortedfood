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
    sortedfood.py [<pageName>]

"""

import docopt as dopt
import bs4
import requests
import pathlib as pl
import json


def retrieve_recipe_page(page_name):
    response = requests.get(
        "http://sortedfood.com/support/client/ajax/pageload.php?" +
        "page={0}".format(page_name))
    response.encoding = "utf-8"
    if response.status_code == 200:
        return response.text
    else:
        return ""


def retrieve_index_page(pagination_number):
    response = requests.get(
        "http://sortedfood.com/support/client/ajax/pageload.php?" +
        "page=recipes&screen={0}".format(pagination_number))
    response.encoding = "utf-8"
    if response.status_code == 200:
        return response.text
    else:
        return ""


def parse_ingredients(expansion_body):
    headings = [p.get_text() for p in expansion_body.find_all("p")[:-1]]
    lists = expansion_body.find_all("ul")
    clean_item = lambda x: x.get_text().strip()
    lists = [[clean_item(li) for li in ul.find_all("li")] for ul in lists]
    if len(headings) == len(lists):
        return dict(zip(headings, lists))
    elif len(lists) > 0:
        return {"main": lists[0]}
    else:
        raise Warning("ParseError in Ingredients")


def parse_instructions(expansion_body):
    try:
        return expansion_body.find_all("p")[-1].get_text().split("\n")[:-1]
    except IndexError:
        raise Warning("ParseError in instructions")


def parse_portions(expansion_body):
    try:
        return expansion_body.find_all("p")[-1].get_text().split("\n")[-1]
    except IndexError:
        raise Warning("ParseError in portions")


def parse_recipe_page(page_name, page):
    store = {}
    soup = bs4.BeautifulSoup(page, from_encoding='utf-8')
    store["title"] = soup.find(id="titleLink").get_text()
    store["name"] = page_name
    store["bodyText"] = soup.find(id="pageBodyText").get_text()
    expansion_body = soup.find(id="expansionMoreBody")
    store["ingredients"] = parse_ingredients(expansion_body)
    store["instructions"] = parse_instructions(expansion_body)
    store["portions"] = parse_portions(expansion_body)
    return store


def extract_recipe_links(recipe_page):
    soup = bs4.BeautifulSoup(recipe_page)
    links = soup.find_all("a")
    link_filter = lambda x: x.get("class", "") == ["active"]
    return [a["href"].replace("/", "") for a in links if link_filter(a)]


def store_recipe(recipe, override=False):
    recipes_dir = pl.Path("./recipes")
    if not recipes_dir.exists() or not recipes_dir.is_dir():
        try:
            recipes_dir.mkdir()
        except pl.FileExistsError:
            print("Could not create directory")
            return
    recipe_file = recipes_dir / recipe["name"]
    if override or not recipe_file.exists():
        with recipe_file.open(mode='w', encoding='utf-8') as f:
            json.dump(recipe, f)


def download_and_store_recipe(recipe_name):
    response = retrieve_recipe_page(recipe_name)
    recipe = parse_recipe_page(recipe_name, response)
    store_recipe(recipe)


def iterate_recipe_links():
    screen = 1
    while(True):
        index_page = retrieve_index_page(screen)
        soup = bs4.BeautifulSoup(index_page)
        links = soup.find_all("a")
        link_filter = lambda x: x.get("class", "") == ["active"]
        clean_link = lambda x: x["href"].split("/")[-2]
        links = [clean_link(a) for a in links if link_filter(a)]
        if len(links) == 0:
            raise StopIteration()
        for link in links:
            yield link
        screen += 1


def scrape_page():
    print("Scraping site")
    for link in iterate_recipe_links():
        print("Loading recipe: {0}".format(link))
        try:
            download_and_store_recipe(link)
        except AttributeError as e:
            print("{0}: {1}".format(e, link))
            continue
        except Warning as e:
            print("{0}: {1}".format(e, link))
            continue


def main(args):
    if(arguments.get("<pageName>", None) is not None):
        pageName = arguments["<pageName>"]
        download_and_store_recipe(pageName)
    else:
        scrape_page()


if __name__ == "__main__":
    arguments = dopt.docopt(__doc__)
    main(arguments)
