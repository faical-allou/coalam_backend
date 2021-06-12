from flask import Flask, send_file, request, redirect, url_for, abort
import simplejson as json
import os, os.path
from werkzeug.serving import WSGIRequestHandler
import datetime
import os.path
import shutil
import requests

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
        

@app.route('/all')
def getAllrecipes():
    authorize(request.headers['Authorization'])
    listRecipes = dataInterface.getAllRecipes()
    return listRecipes


@app.route('/recipe/<id>')
def getRecipeId(id):
    authorize(request.headers['Authorization'])
    recipe = dataInterface.getRecipebyId(id)
    return recipe

@app.route('/chef/<id>')
def getChefId(id):
    authorize(request.headers['Authorization'])
    chef = dataInterface.getChefbyId(id)
    print(chef)
    return chef

@app.route('/get_image/<recipeId>/count')
def getRecipeImageCount(recipeId):
    authorize(request.headers['Authorization'])
    count = len(os.listdir('./static/image/recipe-'+recipeId+'/'))
    return json.dumps({'data':count})


@app.route('/get_image/<recipeId>/<id>')
def getRecipeImage(recipeId,id):
   # authorize(request.headers['Authorization'])
    try:
       filename = '../static/image/recipe-'+recipeId+'/'+id+'.jpg'
       return send_file(filename, mimetype='image/jpg')
    except:
       filename = '../static/image/error404.gif'
       return send_file(filename, mimetype='image/gif')
    return 

@app.route('/get_image/<id>')
def getChefImage(id):
    # authorize(request.headers['Authorization'])
    try:
       filename = '../static/image/chef-'+id+'/1.jpg'
       return send_file(filename, mimetype='image/jpg')
    except:
       filename = '../static/image/empty-profile.png'
       return send_file(filename, mimetype='image/gif')
    return 


@app.route('/get_schedule/<recipeId>/<chefId>')
def getSchedule(recipeId,chefId):
    authorize(request.headers['Authorization'])
    query = recipeId + '-' + chefId
    calendar = config.calendar
    key = config.key
    url = 'https://www.googleapis.com/calendar/v3/calendars/'+calendar+'/events?q='+query+'&key='+key
    x = requests.get(url)
    jsonX = x.json()
    return jsonX


@app.route('/edit_recipe/', methods=['POST'])
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


@app.route('/edit_account/', methods=['POST'])
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

@app.route('/delete_recipe/<id>')
def doDeleteRecipe(id):
    authorize(request.headers['Authorization'])
    dataInterface.deleteRecipe(id)
    try:
        shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'],'recipe-'+id))
    except:
        print('problem when deleting Recipe')
    return 'deleted'
 
@app.route('/delete_chef/<id>')
def doDeleteChef(id):
    authorize(request.headers['Authorization'])
    dataInterface.deleteChef(id)
    try:
        shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'],'chef-'+id))
    except:
        print('problem when deleting Chef')
    return 'deleted'





if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    if os.environ.get('ON_HEROKU'):
        app.run(host='0.0.0.0', port=port)
    else :
        app.run(host='0.0.0.0', port=port, debug=True)