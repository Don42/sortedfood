#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# "THE SCOTCH-WARE LICENSE" (Revision 42):
# <don@0xbeef.org> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a scotch whisky in return
# Marco 'don' Kaulea
# ----------------------------------------------------------------------------
"""Bindings for the Web-API of sortedfood.com

If speed is an issue a session can be reused by passing it to all used
functions.

"""

import requests
import json


def get_recipe(recipe_id,
               ingredients=True,
               instructions=True,
               session=None):
    """Get recipe from id

    Args:
        recipe_id (string): Numeric recipe id
        ingredients (bool): Request list of ingredients with the recipe.
            Defaults to True
        instructions (bool): Request list of instructions with the recipe.
            Defaults to True
        session (Requests.Session): HTTP session to be used for the request.
            Defaults to None. When no session is provied a new one will be
            created and used.

    Returns:
        string: Response parsed as json

    Raises:
        Exception: It the status code is not 200

    """
    if session is None:
        session = requests.Session()
    payload = {'recipeid':  recipe_id,
               'getIngredients': 'true' if ingredients else 'false',
               'getInstructions': 'true' if instructions else 'false'}
    response = session.get('https://cms.sortedfood.com/apiRecipe/getRecipe',
                           params=payload)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        return json.loads(response.text)
    else:
        raise requests.HTTPError(response)


def get_categories(session=None):
    """Get all categories

    Args:
        session (Requests.Session): HTTP session to be used for the request.
            Defaults to None. When no session is provied a new one will be
            created and used.

    Returns:
        dict: containing categories addressed by category id

    Raises:
        requests.HTTPError: If the status code is not 200

    """
    if session is None:
        session = requests.Session()
    response = session.get(
        'https://cms.sortedfood.com/apiRecipe/getCategoryMenu')
    if response.status_code != 200:
        raise requests.HTTPError(response)
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


def get_recipies_from_category(category_id,
                               usertype=1,
                               page=0,
                               count=0,
                               session=None):
    """Get recipe excerpt from category

    Args:
        category_id (string): Numeric category id
        usertype (int): 1 for sortedfood, 2 for everyone else. Defaults to 1.
        page (int): Which page to retrieve. Defaults to 0.
        count(int): How many items per page. Defaults to 0, meaning all.
        session (Requests.Session): HTTP session to be used for the request.
            Defaults to None. When no session is provied a new one will be
            created and used.

    Returns:
        string: Response parsed as json

    Raises:
        requests.HTTPError: If the status code is not 200

    """
    if session is None:
        session = requests.Session()
    payload = {'categoryId': category_id,
               'usertype': usertype,
               'page': page,
               'offset': count}
    response = session.get(
        'https://cms.sortedfood.com/apiRecipe/getFeaturedByUsertype',
        params=payload)
    if response.status_code != 200:
        raise response.HTTPError(response)
    response.encoding = 'utf-8'
    return json.loads(response.text)


def get_recipe_ids_from_category(category_id,
                                 usertype=1,
                                 page=0,
                                 count=0,
                                 session=None):
    """Get recipe ids from a category

    Args:
        category_id (string): Numeric category id
        usertype (int): 1 for sortedfood, 2 for everyone else. Defaults to 1.
        page (int): Which page to retrieve. Defaults to 0.
        count(int): How many items per page. Defaults to 0, meaning all.
        session (Requests.Session): HTTP session to be used for the request.
            Defaults to None. When no session is provied a new one will be
            created and used.

    Returns:
        set: Containing unique recipe ids.

    Raises:
        requests.HTTPError: If the status code is not 200

    """
    content = get_recipies_from_category(category_id,
                                         usertype,
                                         page,
                                         count,
                                         session)
    recipes_list = content.get('recipe', list())
    ids = set()
    for recipe in recipes_list:
        ids.add(recipe['recipe_id'])
    return ids
