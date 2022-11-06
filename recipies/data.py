import csv
import json
import ast

from collections import defaultdict
 
# Function to convert a CSV to JSON
# Takes the file paths as arguments
def makeJson(csvFilePath, jsonFilePath):
    csvFilePath = r'recipes_w_search_terms.csv'
    jsonFilePath = r'result.json'
    # create a dictionary
    data = {}
    counts = defaultdict(int)
     
    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
         
        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:
            ingredientsList = ast.literal_eval(rows["ingredients"])
            if (len(ingredientsList) <= 6):
                key = rows['name']
                data[key] = rows

            counts[len(ingredientsList)] += 1
