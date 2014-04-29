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
    sortedfood.py

"""

import docopt as dopt
import bs4
import requests


def main(args):
    mainResponse = requests.get("http://sortedfood.com")
    headers = {"Referer": "http://sortedfood.com/",
               "X-Requested-With": "XMLHttpRequest"}
    response = requests.get(
        "http://sortedfood.com/support/" +
        "client/ajax/pageload.php?page=katsucurry",
        headers=headers,
        cookies=mainResponse.cookies)
    print(response)
    soup = bs4.BeautifulSoup(response.text)
    print(soup.find(id="titleLink").text)
    print(soup.find(id="expansionMoreBody"))


if __name__ == "__main__":
    arguments = dopt.docopt(__doc__)
    main(arguments)
