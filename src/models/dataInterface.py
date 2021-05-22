import simplejson as json
import pandas as pd
import pathlib
from flask import send_file


class dataInterface:

    def getAllRecipes(self ):
        recipes = pd.read_csv('./assets/data/recipes.csv')
        result = recipes.to_json(orient="records")
        return result

    def getRecipebyId(self, inputId):
        recipes = pd.read_csv('./assets/data/recipes.csv')
        recipe = recipes[recipes['id'].astype(str) == inputId]

        result = recipe.to_json(orient="records")
        return result
    


