import requests
import ast

from bs4 import BeautifulSoup
from django.shortcuts import render

from .forms import SearchForm
from .models import Recipe, Ingredient

def getGoogleImg(query):
    """
    gets a link to the first google image search result
    :param query: search query string
    :result: url string to first result
    """
    url = "https://www.google.com/search?q=" + str(query) + "+image&source=lnms&tbm=isch"
    headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    html = requests.get(url, headers=headers)
    
    if html.status_code != 200:
        print(html.text)

    soup = BeautifulSoup(html.text, 'html.parser')
    image = next((x for x in soup.find_all('img') if x['src'].find("encrypted") != -1), 0)

    if not image:
        return 
    return image['src']

def getIngredient(name: str):
    try:
        return((Ingredient.objects.filter(name__trigram_similar=name).first().json['recipes']))
    except Exception as e:
        return

def getRecipe(id: str):
    try:
        js = Recipe.objects.get(id=id).json
        try:
            js['ingredients_raw_str'] = ast.literal_eval(js['ingredients_raw_str'])
        except Exception as e:
            js['ingredients_raw_str'] = ["Unavailable"]
        try:
            js['steps'] = ast.literal_eval(js['steps'])
        except Exception as e:
            js['steps'] = ["Unavailable"]
        return js
    except Exception as e:
        return 
    
def home(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if (form.is_valid()):
            ingredients = form.cleaned_data['ingredients'].split()
            result = []
            intersection = []
            union = []
            
            for ingredient in ingredients:
                recipies = getIngredient(ingredient)
                if recipies is None:
                    continue

                intersection = recipies if len(intersection) == 0 else list(set(recipies) & set(intersection))
                union = recipies if len(union) == 0 else list(set(union) | set(recipies))

            fetch = intersection if len(intersection) > 0 else union
            count = 0

            for f in fetch:
                if count > 10:
                    break
                p = getRecipe(str(f))
                if p is not None:
                    count +=1 
                    result.append(p)
                    
            return render(request, "results.html", { "recipes": result })

    return render(request, "home.html")

def recipe(request, id):
    r = getRecipe(str(id))
    r['img'] = getGoogleImg(r['name'])

    return render(request, "recipe.html", context= {"recipe": r})

