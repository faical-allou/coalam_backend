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
    def __init__(self, gId, chefId, chefName, chefDescription):
        self.gId = gId
        self.chefId = chefId
        self.chefName = chefName
        self.chefDescription = chefDescription



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
    
    def getChefbyId(self, inputId):
        chefs = pd.read_csv('./static/data/chefs.csv',dtype=object)
        if inputId == '0':
            result = json.dumps([vars(chef("0",0,'', ''))])           
        else:
            chefs['chefId'] = chefs['chefId'].astype(int)
            result = chefs[chefs['chefId'].astype(str) == inputId]
            result = result.to_json(orient="records")
        return result
    
    def getChefbygId(self, gId):
        chefs = pd.read_csv('./static/data/chefs.csv',dtype=object)
        if len(chefs[chefs['gId'].astype(str) == str(gId)]) == 0:
            result = json.dumps([vars(chef("0",0,'', ''))])           
        else:
            chefs['gId'] = chefs['gId'].astype(str)
            chefs['chefId'] = chefs['chefId'].astype(int)
            result = chefs[chefs['gId'] == str(gId)]

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
    
    def insertChef(self, chef):       
        chefs = pd.read_csv('./static/data/chefs.csv')
        data = vars(chef)
        print(data)
        data['chefId'] = self.getMaxChefId()+1
        df = chefs.append(data, ignore_index=True)
        df.to_csv('./static/data/chefs.csv', index = False)               
        return '1'

    def updateChef(self, chef):       
        chefs = pd.read_csv('./static/data/chefs.csv')
        chefs['chefId'] =  chefs['chefId'].astype(str)
        data = vars(chef)    
        chefId = data['chefId']
        for column in chefs:
            if data[column] != '':
                chefs.loc[chefs['chefId'] == chefId, column] = data[column]
        chefs.to_csv('./static/data/chefs.csv', index = False)              
        return '1'

    def getMaxRecipeId(self):       
        recipes = pd.read_csv('./static/data/recipes.csv')
        result = max(recipes['recipeId'])
        return result

    def getMaxChefId(self):       
        chefs = pd.read_csv('./static/data/chefs.csv')
        result = max(chefs['chefId'])
        return result

    def deleteRecipe(self, recipeId):       
        recipes = pd.read_csv('./static/data/recipes.csv')
        df = recipes[recipes.recipeId != int(recipeId)]
        
        df.to_csv('./static/data/recipes.csv', index = False)               
        return '1'

    def deleteChef(self, chefId):       
        chefs = pd.read_csv('./static/data/chefs.csv')
        df = chefs[chefs.chefId != int(chefId)]
        
        df.to_csv('./static/data/chefs.csv', index = False)               
        return '1'