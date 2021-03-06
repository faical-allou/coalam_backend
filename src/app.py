from flask import Flask, send_file, request, redirect, url_for, abort
from flask_cors import CORS

import simplejson as json
import os, os.path
from werkzeug.serving import WSGIRequestHandler
import datetime
import os.path
import shutil
import requests
import sys
import PIL.Image as Image
from PIL import ImageFile
import io

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from models.dataInterface import *
from models.imageInterface import *
from models.eventInterface import *

import config
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="gcp.json"

app = Flask(__name__)
CORS(app)

dataInterface = dataInterface()
imageInterface = imageInterface()
eventInterface = eventInterface()

ImageFile.LOAD_TRUNCATED_IMAGES = True



@app.route('/')
def hello():
    check = dataInterface.getMaxRecipeId()
    return 'Hello there'
        
@app.route('/v1/all')
def getAllrecipes():
    listRecipes = dataInterface.getAllRecipes()
    return listRecipes

@app.route('/v1/recipe/<id>')
def getRecipeId(id):
    recipe = dataInterface.getRecipebyId(id)
    return recipe

@app.route('/v1/chef/<id>')
def getChefId(id):
    chef = dataInterface.getChefbyId(id)
    return chef

@app.route('/v1/gchef/<id>')
def getgChefId(id):
    chef = dataInterface.getChefbygId(id)
    return chef

@app.route('/v1/get_image/<recipeId>/count')
def getRecipeImageCount(recipeId):
    count = imageInterface.getCountImages('image/recipe-'+recipeId)
    return json.dumps({'data':count})


@app.route('/v1/get_image/<recipeId>/<id>')
def getRecipeImage(recipeId,id):
    return imageInterface.getRecipeImage(recipeId,id)


@app.route('/v1/get_image/<id>')
def getChefImage(id):
    return imageInterface.getChefImage(id)


@app.route('/v1/get_schedule/<chefId>/<recipeId>')
def getSchedule(chefId,recipeId):
    json_out = eventInterface.getSchedule(chefId,recipeId)
    return json_out

@app.route('/v1/add_event/<chefId>/<recipeId>', methods=['POST'])
def doAaddEvent(chefId,recipeId):
    eventInterface.AaddEvent(chefId, recipeId)
    return 'event added'

@app.route('/v1/delete_event/<eventId>', )
def doDeleteEvent(eventId):
    eventInterface.deleteEvent(eventId)
    return 'event deleted'

@app.route('/v1/edit_recipe/', methods=['POST'])
def editRecipe():
    data = dict(request.form)
    dataDF = recipe(data['chefid'],data['chefname'],data['recipeid'],data['recipename'],data['recipedescription'],data['ingredients'],data['tools'])
    if data['recipeid']=='0':
        data['recipeid'] = dataInterface.insertRecipe(dataDF)
    else:
        dataInterface.updateRecipe(dataDF)
    
    if len(request.files) > 0:
        bytefile = request.files['image1']
        imageInterface.addimage(bytefile,'image/recipe-'+str(data['recipeid'])+'/1.jpg' )
    return json.dumps({'recipeid':data['recipeid'], 'chefid':data['chefid'], 'status':'success'})


@app.route('/v1/edit_account/', methods=['POST'])
def editAccount():
    data = dict(request.form)
    dataDF = chef(data['gid'],data['chefid'],data['chefname'],data['chefdescription'])
    
    if data['chefid']=='0':
        data['chefid'] = dataInterface.insertChef(dataDF)
    else:
        dataInterface.updateChef(dataDF)

    if len(request.files) > 0:
        bytefile = request.files['image1']
        imageInterface.addimage(bytefile,'image/chef-'+str(data['chefid'])+'/1.jpg' )
    print(data)
    return json.dumps({'chefid':data['chefid'], 'status':'success'})

@app.route('/v1/delete_recipe/<id>')
def doDeleteRecipe(id):
    input_recipe = json.loads(dataInterface.getRecipebyId(id))
    list2 = eventInterface.getSchedule(str(input_recipe[0]["chefid"]),str(id))
    for e in list2['items']:
        try:
            eventInterface.deleteEvent(e['id'])
        except Exception as e:
            print('problem when deleting Events')
    try:
        imageInterface.deleteFiles('image/recipe-'+id)
    except Exception as e:
        print('problem when deleting Recipe')
        print( e )
    dataInterface.deleteRecipe(id) 
    return 'deleted'
 
@app.route('/v1/delete_chef/<id>')
def doDeleteChef(id):
    dataInterface.deleteChef(id)
    list = json.loads(dataInterface.getRecipebyChefId(id))
    for rec in list:    
        recipeid = rec['recipeid']         
        dataInterface.deleteRecipe(recipeid)  
        imageInterface.deleteFiles('image/recipe-'+str(recipeid))
        list2 = eventInterface.getSchedule(str(id),str(recipeid))
        for e in list2['items']:
            try:
                eventInterface.deleteEvent(e['id'])
            except Exception as e:
                print('problem when deleting Events')
    try:
        imageInterface.deleteFiles('image/chef-'+str(id))
    except Exception as e:
        print('problem when deleting Chef')
        print( e )
    return 'deleted'



if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    if os.environ.get('PORT') != 8080:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=True)
    else :
        app.run(host='0.0.0.0', port=8080, debug=True)



    
