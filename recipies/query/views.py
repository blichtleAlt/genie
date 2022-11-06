from django.shortcuts import render
import os
import json
import ast
from urllib.parse import unquote
from .forms import SearchForm
from bs4 import BeautifulSoup
import requests

def get_google_img(query):
    """
    gets a link to the first google image search result
    :param query: search query string
    :result: url string to first result
    """
    url = "https://www.google.com/search?q=" + str(query) + "+food&source=lnms&tbm=isch"
    headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

    html = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html, 'html.parser')
    image = soup.find_all('img')[1]

    image = next((x for x in soup.find_all('img') if x['src'].find("encrypted") != -1), 0)

    if not image:
        return 
    return image['src']


def createDatebase(): 
    dirname = os.path.dirname(__file__)
    jsonFilePath = os.path.join(dirname, 'db/result.json')

    jsonRecipies = None

    recipiesDB = {}
    ingredientsDB = {}

    with open(jsonFilePath, 'r') as jsonf:
        jsonRecipies = json.load(jsonf)

    for _, details in jsonRecipies.items():
        recipeId = details['id']
        recipiesDB[recipeId] = details

        for ingredient in ast.literal_eval(details["ingredients"]):
            ingredientsDB.setdefault(unquote(unquote(ingredient)),[]).append(recipeId)

    return recipiesDB, ingredientsDB

def home(request):
    print(request)

    if request.method == 'POST':

        form = SearchForm(request.POST)

        if(form.is_valid()):
            print(form.cleaned_data)
            
            recipiesDB, ingredientsDB = createDatebase()

            ingredients = form.cleaned_data['ingredients'].split()

            result = []
            union = []
            
            for ingredient in ingredients:
                recipies = ingredientsDB[ingredient]
                union = recipies if len(union) == 0 else list(set(recipies) & set(union))


            for recipe in union:
                    result.append(recipiesDB[recipe])

            context = {
                "recipies": result[:10]
            }
            print(context)

            for recipe in context['recipies']:
                recipe['img'] = get_google_img(recipe['name'])

            
            return render(request, "results.html", context)


        return render(request, "home.html")
    else:
        return render(request, "home.html")

    
