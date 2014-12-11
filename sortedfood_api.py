#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# "THE SCOTCH-WARE LICENSE" (Revision 42):
# <DonMarco42@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a scotch whisky in return
# Marco 'don' Kaulea
# ----------------------------------------------------------------------------

import requests
import json


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
        return {}


def get_categories(session=None):
    if session is None:
        session = requests.Session()
    response = session.get(
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


def get_recipies_from_category(category,
                               usertype=1,
                               page=0,
                               count=0,
                               session=None):
    if session is None:
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


def get_recipe_ids_from_category(category,
                                 usertype=1,
                                 page=0,
                                 count=0,
                                 session=None):
    content = get_recipies_from_category(category,
                                         usertype,
                                         page,
                                         count,
                                         session)
    recipes_list = content.get('recipe', list())
    ids = set()
    for recipe in recipes_list:
        ids.add(recipe['recipe_id'])
    return ids
