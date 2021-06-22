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

import config
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="cloudstorage_creds.json"

app = Flask(__name__)
CORS(app)
dataInterface = dataInterface()
imageInterface = imageInterface()

ImageFile.LOAD_TRUNCATED_IMAGES = True


@app.route('/')
def hello():
    return 'Hello there'

def authorize(key):
    if key == config.appkey:
        print('authorized')
    else:
        print('not authorized')
        abort(404) 
        
@app.route('/v1/all')
def getAllrecipes():
    authorize(request.headers['Authorization'])
    listRecipes = dataInterface.getAllRecipes()
    print(listRecipes)
    return listRecipes


@app.route('/v1/recipe/<id>')
def getRecipeId(id):
    authorize(request.headers['Authorization'])
    recipe = dataInterface.getRecipebyId(id)
    return recipe

@app.route('/v1/chef/<id>')
def getChefId(id):
    authorize(request.headers['Authorization'])
    chef = dataInterface.getChefbyId(id)
    print(chef)
    return chef

@app.route('/v1/gchef/<id>')
def getgChefId(id):
    print('in gsearch')
    print(id)
    #authorize(request.headers['Authorization'])
    chef = dataInterface.getChefbygId(id)
    print(chef)
    return chef

@app.route('/v1/get_image/<recipeId>/count')
def getRecipeImageCount(recipeId):
    authorize(request.headers['Authorization'])
    count = imageInterface.getCountImages('image/recipe-'+recipeId)
    return json.dumps({'data':count})


@app.route('/v1/get_image/<recipeId>/<id>')
def getRecipeImage(recipeId,id):
    # authorize(request.headers['Authorization'])
    return imageInterface.getRecipeImage(recipeId,id)


@app.route('/v1/get_image/<id>')
def getChefImage(id):
    # authorize(request.headers['Authorization'])
    return imageInterface.getChefImage(id)


@app.route('/v1/get_schedule/<chefId>/<recipeId>')
def getSchedule(chefId,recipeId):
    #authorize(request.headers['Authorization'])
    query = chefId + '-' + recipeId 
    calendarId = config.calendarIdpct
    key = config.Gkey
    url = 'https://www.googleapis.com/calendar/v3/calendars/'+calendarId+'/events?q='+query+'&key='+key
    x = requests.get(url)
    jsonX = x.json()
    return jsonX

@app.route('/v1/add_event/<chefId>/<recipeId>', methods=['POST'])
def addEvent(chefId,recipeId):
    #authorize(request.headers['Authorization'])
    query =  chefId + '-' + recipeId
    data = dict(request.form)
    event = {"summary": chefId + '-' + recipeId,
             "description": data['eventDescription'] ,
              "start": {
                "dateTime": data['eventStart'],
                "timeZone": "UTC"
              },
              "end": {
                "dateTime": data['eventEnd'],
                "timeZone": "UTC"
              },
              "conferenceDataVersion": 1,
              "conferenceData": {
                  "createRequest": {
                        "conferenceSolutionKey": { 
                                    "type": "hangoutsMeet", 
                                    },
                        "requestId": str(datetime.datetime.now()),
                        },
                  }
              }

    event = service.events().insert(calendarId=config.calendarIdat, body=event,  conferenceDataVersion=1).execute()
    print ('Event created: ' +  str(event))
    return 'event added'

@app.route('/v1/delete_event/<eventId>', )
def deleteEvent(eventId):
    authorize(request.headers['Authorization'])   
    event = service.events().delete(calendarId=config.calendarIdat, eventId=eventId).execute()
    return 'event deleted'

@app.route('/v1/edit_recipe/', methods=['POST'])
def editRecipe():
    authorize(request.headers['Authorization'])
    data = dict(request.form)
    dataDF = recipe(data['chefId'],data['recipeId'],data['recipeName'],data['recipeDescription'],data['ingredients'],data['tools'])
    if data['recipeId']=='0':
        data['recipeId'] = str(dataInterface.getMaxRecipeId() +1)
        dataInterface.insertRecipe(dataDF)
    else:
        dataInterface.updateRecipe(dataDF)
        print('inserting')
    
    print('request.files length is: ' + str(len(request.files)) )
        
    if len(request.files) > 0:
        bytefile = request.files['image1']
        imageInterface.addimage(bytefile,'image/recipe-'+data['recipeId']+'/1.jpg' )
        print('saved as ' + 'image/recipe-'+data['recipeId']+'/1.jpg')

    return json.dumps({'recipeId':data['recipeId'], 'chefId':data['chefId'], 'status':'success'})


@app.route('/v1/edit_account/', methods=['POST'])
def editAccount():
    authorize(request.headers['Authorization'])
    data = dict(request.form)
    dataDF = chef(data['gId'],data['chefId'],data['chefName'],data['chefDescription'])
    if data['chefId']=='0':
        data['chefId'] = dataInterface.getMaxChefId() +1
        dataInterface.insertChef(dataDF)
        print('inserted')
    else:
        dataInterface.updateChef(dataDF)
        print('updated')

    print('request.files length is: ' + str(len(request.files)) )        
    if len(request.files) > 0:
        bytefile = request.files['image1']
        imageInterface.addimage(bytefile,'image/chef-'+data['chefId']+'/1.jpg' )
    return json.dumps({'chefId':data['chefId'], 'status':'success'})

@app.route('/v1/delete_recipe/<id>')
def doDeleteRecipe(id):
    authorize(request.headers['Authorization'])
    dataInterface.deleteRecipe(id)
    try:
        imageInterface.deleteFiles('image/recipe-'+id)
    except Exception as e:
        print('problem when deleting Recipe')
        print( e )
    return 'deleted'
 
@app.route('/v1/delete_chef/<id>')
def doDeleteChef(id):
    authorize(request.headers['Authorization'])
    dataInterface.deleteChef(id)
    try:
        imageInterface.deleteFiles('image/chef-'+id)
    except Exception as e:
        print('problem when deleting Chef')
        print( e )
    return 'deleted'



if __name__ == '__main__':
    # Doing the google authentification
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    if os.environ.get('ON_HEROKU'):
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else :
        app.run(host='0.0.0.0', port=5000, debug=True)