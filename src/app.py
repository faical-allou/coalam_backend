from flask import Flask, send_file
import simplejson as json
import os, os.path
from werkzeug.serving import WSGIRequestHandler

from models.dataInterface import *

# simple version for working with CWD
print 

app = Flask(__name__)

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
    count = len(os.listdir('./assets/image/recipe-'+recipeId+'/'))
    return json.dumps({'data':count})

@app.route('/get_image/<recipeId>/<id>')
def getRecipeImage(recipeId,id):
    try:
       filename = '../assets/image/recipe-'+recipeId+'/'+id+'.jpg'
       return send_file(filename, mimetype='image/jpg')
    except:
       filename = '../assets/image/error404.gif'
       return send_file(filename, mimetype='image/gif')
    return 


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    if os.environ.get('ON_HEROKU'):
        app.run(host='0.0.0.0', port=port)
    else :
        app.run(host='localhost', port=port)