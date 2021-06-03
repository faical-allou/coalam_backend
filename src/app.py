from flask import Flask, send_file, request
import simplejson as json
import os, os.path
from werkzeug.serving import WSGIRequestHandler
import datetime
import os.path
import requests

from models.dataInterface import *
import config

# simple version for working with CWD
print 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/image/'

dataInterface = dataInterface()


@app.route('/')
def hello():
    return 'Hello World! from the container'

@app.route('/all')
def getAllrecipes():
    listRecipes = dataInterface.getAllRecipes()
    return listRecipes

@app.route('/<id>')
def getRecipeId(id):
    recipe = dataInterface.getRecipebyId(id)
    return recipe

@app.route('/get_image/<recipeId>/count')
def getRecipeImageCount(recipeId):
    count = len(os.listdir('./static/image/recipe-'+recipeId+'/'))
    return json.dumps({'data':count})

@app.route('/get_image/<recipeId>/<id>')
def getRecipeImage(recipeId,id):
    try:
       filename = '../static/image/recipe-'+recipeId+'/'+id+'.jpg'
       return send_file(filename, mimetype='image/jpg')
    except:
       filename = '../static/image/error404.gif'
       return send_file(filename, mimetype='image/gif')
    return 

@app.route('/get_schedule/<recipeId>/<chefId>')
def getSchedule(recipeId,chefId):
    query = recipeId + '-' + chefId
    calendar = config.calendar
    key = config.key
    url = 'https://www.googleapis.com/calendar/v3/calendars/'+calendar+'/events?q='+query+'&key='+key
    x = requests.get(url)
    jsonX = x.json()
    return jsonX

@app.route('/edit_recipe/', methods=['POST'])
def addRecipe():
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

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    if os.environ.get('ON_HEROKU'):
        app.run(host='0.0.0.0', port=port)
    else :
        app.run(host='localhost', port=port, debug=True)