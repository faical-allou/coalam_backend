import simplejson as json
import pandas as pd
import pathlib
import os
from flask import send_file


class recipe:
    def __init__(self, chefId, recipeId, recipeName, description, ingredients, tools):
        self.chefId = chefId
        self.recipeId = recipeId
        self.recipeName = recipeName
        self.description = description
        self.ingredients = ingredients
        self.tools = tools
    
class chef:
    def __init__(self, chefId, chefName):
        self.chefId = chefId
        self.chefName = chefName



class dataInterface:

    def getAllRecipes(self ):
        recipes = pd.read_csv('./static/data/recipes.csv')
        result = recipes.to_json(orient="records")
        return result

    def getRecipebyId(self, inputId):
        recipes = pd.read_csv('./static/data/recipes.csv')
        result = recipes[recipes['recipeId'].astype(str) == inputId]

        result = result.to_json(orient="records")
        return result
    
    def insertRecipe(self, recipe):
        
        recipes = pd.read_csv('./static/data/recipes.csv')

        data = vars(recipe)

        _chef = json.loads(self.getChefbyId(data['chefId']))
        print(_chef)
        data['chefName'] = _chef[0]['chefName']

        data['recipeId'] = self.getMaxRecipeId()+1
        df = recipes.append(data, ignore_index=True)
        df.to_csv('./static/data/recipes.csv', index = False)
               
        return '1'

    def updateRecipe(self, recipe):
        
        recipes = pd.read_csv('./static/data/recipes.csv')
        recipes['recipeId'] =  recipes['recipeId'].astype(str)
        data = vars(recipe)

        _chef = json.loads(self.getChefbyId(data['chefId']))

        data['chefName'] = _chef[0]['chefName']
        recipeId = data['recipeId']
        for column in recipes:
            if data[column] != '':
                recipes.loc[recipes['recipeId'] == recipeId, column] = data[column]

        recipes.to_csv('./static/data/recipes.csv', index = False)
               
        return '1'
    
    def getChefbyId(self, inputId):
        
        chefs = pd.read_csv('./static/data/chefs.csv')
        result = chefs[chefs['chefId'].astype(str) == inputId]

        result = result.to_json(orient="records")

        return result

    def getMaxRecipeId(self):
        
        recipes = pd.read_csv('./static/data/recipes.csv')
        result = len(recipes)

        return result
