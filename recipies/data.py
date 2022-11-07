import csv
import json
import ast
import os
import requests
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipies.settings")
django.setup()
from query.models import Recipe, Ingredient
from collections import defaultdict
from bs4 import BeautifulSoup


def getGoogleImg(query):
    """
    gets a link to the first google image search result
    :param query: search query string
    :result: url string to first result
    """
    url = "https://www.google.com/search?q=" + str(query) + "+image&source=lnms&tbm=isch"
    headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    html = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html, 'html.parser')
    image = next((x for x in soup.find_all('img') if x['src'].find("encrypted") != -1), 0)

    if not image:
        return 
    return image['src']
 
 
# Function to convert a CSV to JSON
# Takes the file paths as arguments
def makeJson(csvFilePath, jsonFilePath):
    csvFilePath = r'recipes_w_search_terms.csv'
    jsonFilePath = r'result.json'

    ingredientsFilePath = r'ingredients.json'
    # create a dictionary
    data = {}
    ingredients = {}
    counts = defaultdict(int)
    count = 1

    # Open a csv reader called DictReader
    print("Compiling Ingredients")
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
         
        # Convert each row into a dictionary and add it to data
        for rows in csvReader:
            ingredientsList = ast.literal_eval(rows["ingredients"])
            if (len(ingredientsList) <= 5):
                key = rows['name']
                recipeId = rows['id']
                data[key] = rows
                count += 1

                for ingredient in ast.literal_eval(rows["ingredients"]):
                    counts[ingredient] += 1

                    if ingredient in ingredients.keys():
                        prev = ingredients[ingredient]
                    
                        ingredients[ingredient] = {
                            "recipies": prev.get("recipies") + [recipeId],
                            "count": prev["count"] + 1
                        }
                    else:
                        ingredients[ingredient] = {
                            "recipies": [recipeId],
                            "count": 1
                        }
                    
    # Open a json writer, and use the json.dumps()
    # function to dump data
    print("recipies before", count)

    final_recipies = set()
    for k, v in ingredients.items():
        final_recipies = (set(final_recipies) | set(v['recipies']))

    for k, v in list(data.items()):
        if v['id'] not in final_recipies:
            del data[k]

    print("recipies after", len(final_recipies))

    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))

    print("Finding Images")
    sort = dict(sorted(ingredients.items(), key=lambda x: x[1]['count'], reverse=True)[:500])

    total = len(sort.keys())
    count = 1
    for k in sort.keys():
        print(count, "/", total)
        count += 1
        sort[k]["img"] = getGoogleImg(k)

    with open(ingredientsFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(sort, indent=4))

def migrate():
    dirname = os.path.dirname(__file__)
    jsonFilePath = os.path.join(dirname, 'query/data/result.json')
    ingredientsJsonFilePath = os.path.join(dirname, 'query/data/ingredients.json')

    jsonRecipies = None
    ingredients = None

    with open(jsonFilePath, 'r') as jsonf:
        jsonRecipies = json.load(jsonf)

    with open(ingredientsJsonFilePath, 'r') as jsonf:
        ingredients = json.load(jsonf)

    for k, v in jsonRecipies.items():
        recipeId = v['id']
        recipe = Recipe(id=recipeId, json=v)
        recipe.save()

    for k, v in ingredients.items():
        ingredient = Ingredient(name=k, json=v)
        ingredient.save()


def main():
    #makeJson(None, None)
    migrate()

if __name__ == "__main__":
    main()