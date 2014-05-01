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
    sortedfood.py <pageName>

"""

import docopt as dopt
import bs4
import requests
import pprint


def retrieve_recipe_page(page_name):
    response = requests.get(
        "http://sortedfood.com/support/client/ajax/pageload.php?" +
        "page={0}".format(page_name))
    response.encoding = "utf-8"
    if response.status_code == 200:
        return response.text
    else:
        return ""


def parse_ingredients(expansion_body):
    headings = [p.get_text() for p in expansion_body.find_all("p")[:-1]]
    lists = expansion_body.find_all("ul")
    lists = [[li.get_text() for li in ul.find_all("li")] for ul in lists]
    if len(headings) == len(lists):
        return dict(zip(headings, lists))
    else:
        return {"main": lists[0]}


def parse_instructions(expansion_body):
    try:
        return expansion_body.find_all("p")[-1].get_text().split("\n\n")[0]
    except IndexError:
        return ""


def parse_portions(expansion_body):
    try:
        return expansion_body.find_all("p")[-1].get_text().split("\n\n")[1]
    except IndexError:
        return ""


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
    link_filter = lambda x: x["class"] == ["active"]
    return [a["href"].replace("/", "") for a in links if link_filter(a)]


def main(args):
    if("<pageName>" in arguments):
        pageName = arguments["<pageName>"]
        response = retrieve_recipe_page(pageName)
        recipe = parse_recipe_page(pageName, response)
        further_links = extract_recipe_links(response)
        pprint.pprint(recipe)
        pprint.pprint(further_links)


if __name__ == "__main__":
    arguments = dopt.docopt(__doc__)
    main(arguments)
