import json

from django.shortcuts import render
from django.core import serializers

from .forms import SearchForm
from .models import Recipe, Ingredient

def home(request):
    print(request)
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if (form.is_valid()):
            ingredients = form.cleaned_data['ingredients'].split()
            print("ingredients", ingredients)

            result = []
            intersection = []
            union = []

            for ingredient in ingredients:
                recipies = None

                try:
                    recipies = Ingredient.objects.get(name=ingredient).json['recipies']
                except Exception as e:
                    print(e)

                if recipies is None:
                    continue
                intersection = recipies if len(intersection) == 0 else list(set(recipies) & set(intersection))
                union = recipies if len(union) == 0 else list(set(union) | set(recipies))

            count = 0
            fetch = intersection if len(intersection) > 0 else union
            for recipe in fetch:
                rec = None

                if count > 10:
                    break

                try:
                    rec = Recipe.objects.get(id=recipe)
                except Exception as e:
                    print(e)

                if rec is not None:
                    count += 1
                    result.append(rec)

            fil = []
            for res in result:
                ser = serializers.serialize('json', [res, ])
                js = json.loads(ser)
                fil.append(js[0]['fields']['json'])

            context = { "recipies": fil }
            print("context: ", context)
            
            return render(request, "results.html", context)

        return render(request, "home.html")
    else:
        return render(request, "home.html")

    
