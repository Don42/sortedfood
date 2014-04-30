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
    if response.status_code == 200:
        return response.text
    else:
        return ""


def parse_recipe_page(page_name, page):
    store = {}
    soup = bs4.BeautifulSoup(page)
    store["title"] = soup.find(id="titleLink").text
    store["name"] = page_name
    store["bodyText"] = soup.find(id="pageBodyText").text
    store["ingredients"] = [li.text for li in soup.find(
                            id="expansionMoreBody").ul.find_all("li")]
    instructions = soup.find(id="expansionMoreBody").p.text.split("\n\n")
    if len(instructions) == 2:
        store["instructions"] = instructions[0]
        store["portions"] = instructions[1]
    elif len(instructions) == 1:
        store["instuctions"] = instructions[0]
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
