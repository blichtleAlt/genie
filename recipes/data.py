import csv
import ast
import os
import requests
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipes.settings")
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
def seedDatabase():
    csvFilePath = r'recipes_w_search_terms.csv'

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
            if (len(ingredientsList) <= 8):
                key = rows['name']
                recipeId = rows['id']
                data[key] = rows
                count += 1

                for ingredient in ast.literal_eval(rows["ingredients"]):
                    counts[ingredient] += 1

                    if ingredient in ingredients.keys():
                        prev = ingredients[ingredient]
                    
                        ingredients[ingredient] = {
                            "recipes": prev.get("recipes") + [recipeId],
                            "count": prev["count"] + 1
                        }
                    else:
                        ingredients[ingredient] = {
                            "recipes": [recipeId],
                            "count": 1
                        }
                    
    print("recipes before", count)

    final_recipes = set()
    for k, v in ingredients.items():
        final_recipes = (set(final_recipes) | set(v['recipes']))

    for k, v in list(data.items()):
        if v['id'] not in final_recipes:
            del data[k]

    print("recipes after", len(final_recipes))

    print("Finding Images")
    sort = dict(sorted(ingredients.items(), key=lambda x: x[1]['count'], reverse=True)[:2000])

    count = 1
    total = len(sort.keys())
    for k in sort.keys():
        print("getting image: ", count, "/", total)
        count += 1
        sort[k]["img"] = getGoogleImg(k)

    print("Clearing DB")
    Recipe.objects.all().delete()
    Ingredient.objects.all().delete()

    count = 1
    total = len(data.keys())
    for k, v in data.items():
        print("inserting recipe: ", count, "/", total)
        count += 1
        recipeId = v['id']
        recipe = Recipe(id=recipeId, json=v)
        recipe.save()

    count = 1
    total = len(sort.keys())
    for k, v in sort.items():
        print("inserting ingredient: ", count, "/", total)
        count += 1
        ingredient = Ingredient(name=k, json=v)
        ingredient.save()


def main():
    seedDatabase()

if __name__ == "__main__":
    main()