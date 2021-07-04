import simplejson as json
import pandas as pd
import pathlib
import os
import sqlalchemy
import pg8000
from sqlalchemy.sql.elements import Null
import config
from google.cloud.sql.connector import connector
import time 
from flask import send_file
from models.imageInterface import *

imageInterface = imageInterface()

class recipe:
    def __init__(self, chefId, chefName, recipeId, recipeName, description, ingredients, tools):
        self.chefid = chefId
        self.chefname = chefName
        self.recipeid = recipeId
        self.recipename = recipeName
        self.description = description
        self.ingredients = ingredients
        self.tools = tools
    
class chef:
    def __init__(self, gId, chefId, chefName, chefDescription):
        self.gid = gId
        self.chefid = chefId
        self.chefname = chefName
        self.chefdescription = chefDescription

class dataInterface:
    
    

    def easyconnect(self):         
        if os.environ.get('RUN_LOCALLY'):
            _dbURL = config.localGpostgresURL
        else:
           _dbURL = config.appengineGpostgresURL
        engine = sqlalchemy.create_engine(_dbURL)
        return engine

    def getAllRecipes(self ):
        engine = self.easyconnect()
        with engine.connect() as con:
            res = con.execute("select * from recipes").all()     
        recipes = [r._asdict() for r in res]
        result = json.dumps(recipes)
        print(result)
        return result

    def getRecipebyId(self, inputId):
        engine = self.easyconnect()
        with engine.connect() as con:
            res = con.execute("select * from recipes where recipeid = %s;", inputId).all()    
        print(res) 
        recipes = [r._asdict() for r in res]
        result = json.dumps(recipes)
        return result
    
    def getRecipebyChefId(self, inputId):
        engine = self.easyconnect()
        with engine.connect() as con:
            res = con.execute("select * from recipes where chefid = %s;", inputId).all()    
        print(res) 
        recipes = [r._asdict() for r in res]
        result = json.dumps(recipes)
        return result

    def getChefbyId(self, inputId):
        if inputId == '0':
            result = json.dumps([vars(chef("0",0,'', ''))])           
        else:
            engine = self.easyconnect()
            with engine.connect() as con:
                res = con.execute("select * from chefs where chefid = %s;", inputId).all()    
            print(res) 
            recipes = [r._asdict() for r in res]
            result = json.dumps(recipes)
        return result
    
    def getChefbygId(self, gId):
        engine = self.easyconnect()
        with engine.connect() as con:
            res = con.execute("select * from chefs where gid = %s;", gId).all()    
        print(res) 
        chefoutput = [r._asdict() for r in res]
        if len(chefoutput) == 0:
            result = json.dumps([vars(chef("0",0,'', ''))])  
        else:
            result = json.dumps(chefoutput)
 
        return result

    def insertRecipe(self, recipe):       
        engine = self.easyconnect()
        recipe.recipeid = self.getMaxRecipeId()+1
        if recipe.chefname == "":
            _chef = json.loads(self.getChefbyId(recipe.chefid))
            recipe.chefname = _chef[0]['chefname']
        with engine.connect() as con:
            con.execute("INSERT INTO recipes VALUES ( %(recipeid)s,%(recipename)s,%(chefname)s,%(chefid)s,%(ingredients)s,%(tools)s,%(description)s  );", recipe.__dict__)       
        return recipe.recipeid

    def updateRecipe(self, recipe):       
        engine = self.easyconnect()
        with engine.connect() as con:
            con.execute("DELETE FROM recipes WHERE recipeid = %s;",recipe.recipeid)
            con.execute("INSERT INTO recipes VALUES ( %(recipeid)s,%(recipename)s,%(chefname)s,%(chefid)s,%(ingredients)s,%(tools)s,%(description)s  );", recipe.__dict__)       
        return '1'
    
    def insertChef(self, chef):       
        engine = self.easyconnect()
        chef.chefid = self.getMaxChefId()+1
        with engine.connect() as con:
            con.execute("INSERT INTO chefs VALUES ( %(gid)s,%(chefid)s,%(chefname)s,%(chefdescription)s);", chef.__dict__)       
        return  chef.chefid

    def updateChef(self, chef):       
        engine = self.easyconnect()
        print(chef.__dict__)
        with engine.connect() as con:
            con.execute("DELETE FROM chefs WHERE chefid = %s;",chef.chefid)
            con.execute("INSERT INTO chefs VALUES ( %(gid)s,%(chefid)s,%(chefname)s,%(chefdescription)s);", chef.__dict__)       
        return '1'


    def getMaxRecipeId(self):       
        engine = self.easyconnect()
        with engine.connect() as con:
            res = con.execute("select max(recipeid) from recipes;").scalar()    
        result = int(res)
        return result

    def getMaxChefId(self):       
        engine = self.easyconnect()
        with engine.connect() as con:
            res = con.execute("select max(chefid) from chefs;").scalar()    
        result = int(res)
        return result

    def deleteRecipe(self, recipeid):       
        engine = self.easyconnect()
        with engine.connect() as con:
            con.execute("DELETE FROM recipes WHERE recipeid = %s;", recipeid)
        return '1'

    def deleteChef(self, chefid):       
        engine = self.easyconnect()
        with engine.connect() as con:
            con.execute("DELETE FROM chefs WHERE chefid = %s;",chefid)        
        return 'done'