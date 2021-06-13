from flask import Flask, send_file, request, redirect, url_for, abort
import simplejson as json
import os, os.path
from werkzeug.serving import WSGIRequestHandler
import datetime
import os.path
import shutil
import requests

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from models.dataInterface import *
import config


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/image/'

dataInterface = dataInterface()


@app.route('/')
def hello():
    return 'Hello World! from the container'

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

@app.route('/v1/get_image/<recipeId>/count')
def getRecipeImageCount(recipeId):
    authorize(request.headers['Authorization'])
    count = len(os.listdir('./static/image/recipe-'+recipeId+'/'))
    return json.dumps({'data':count})


@app.route('/v1/get_image/<recipeId>/<id>')
def getRecipeImage(recipeId,id):
   # authorize(request.headers['Authorization'])
    try:
       filename = '../static/image/recipe-'+recipeId+'/'+id+'.jpg'
       return send_file(filename, mimetype='image/jpg')
    except:
       filename = '../static/image/error404.gif'
       return send_file(filename, mimetype='image/gif')
    return 

@app.route('/v1/get_image/<id>')
def getChefImage(id):
    # authorize(request.headers['Authorization'])
    try:
       filename = '../static/image/chef-'+id+'/1.jpg'
       return send_file(filename, mimetype='image/jpg')
    except:
       filename = '../static/image/empty-profile.png'
       return send_file(filename, mimetype='image/gif')
    return 


@app.route('/v1/get_schedule/<chefId>/<recipeId>')
def getSchedule(chefId,recipeId):
    #authorize(request.headers['Authorization'])
    query = chefId + '-' + recipeId 
    calendarId = config.calendarIdpct
    key = config.key
    url = 'https://www.googleapis.com/calendar/v3/calendars/'+calendarId+'/events?q='+query+'&key='+key
    x = requests.get(url)
    jsonX = x.json()
    print(jsonX)
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
    
    if len(request.files) > 0:
        file = request.files['image1']
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],'recipe-'+data['recipeId'])):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],'recipe-'+data['recipeId'],'1.jpg'))
        else:
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'],'recipe-'+data['recipeId']))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],'recipe-'+data['recipeId'],'1.jpg'))
    return json.dumps({'recipeId':data['recipeId'], 'chefId':data['chefId'], 'status':'success'})


@app.route('/v1/edit_account/', methods=['POST'])
def editAccount():
    authorize(request.headers['Authorization'])
    data = dict(request.form)
    dataDF = chef(data['chefId'],data['chefName'],data['chefDescription'])
    if data['chefId']=='0':
        data['chefId'] = str(dataInterface.getMaxChefId() +1)
        dataInterface.insertChef(dataDF)
        print('inserted')
    else:
        dataInterface.updateChef(dataDF)
        print('updated')

    if len(request.files) > 0:
            file = request.files['image1']
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],'chef-'+data['chefId'])):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],'chef-'+data['chefId'],'1.jpg'))
            else:
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'],'chef-'+data['chefId']))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],'chef-'+data['chefId'],'1.jpg'))

    return json.dumps({'chefId':data['chefId'], 'status':'success'})

@app.route('/v1/delete_recipe/<id>')
def doDeleteRecipe(id):
    authorize(request.headers['Authorization'])
    dataInterface.deleteRecipe(id)
    try:
        shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'],'recipe-'+id))
    except:
        print('problem when deleting Recipe')
    return 'deleted'
 
@app.route('/v1/delete_chef/<id>')
def doDeleteChef(id):
    authorize(request.headers['Authorization'])
    dataInterface.deleteChef(id)
    try:
        shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'],'chef-'+id))
    except:
        print('problem when deleting Chef')
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