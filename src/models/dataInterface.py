import simplejson as json
import pandas as pd
import pathlib

class dataInterface:

    def getAllRecipes(self ):

        print(pathlib.Path().absolute())

        recipes = pd.read_csv('./assets/data/recipes.csv')
        print(recipes)
        result = json.dumps(recipes.to_json(orient="records"))
        return result

    def getRecipebyId(self, inputId):
        recipes = pd.read_csv('./assets/data/recipes.csv')
        print(recipes)

        print(inputId)

        recipe = recipes[recipes['id'].astype(str) == inputId]
        
        print(recipe)

        print(recipe.to_json(orient="records"))

        result = json.dumps(recipe.to_json(orient="records"))
        return result

def __init__(self):
        print ("in init")
