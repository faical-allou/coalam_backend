from flask import Flask
from models.dataInterface import *

app = Flask(__name__)

dataInterface = dataInterface()


@app.route('/')
def hello():
    return 'Hello World! from the container'

@app.route('/all')
def all():
    listRecipes = dataInterface.getAllRecipes()
    return listRecipes

@app.route('/<id>')
def recipeId(id):
    recipe = dataInterface.getRecipebyId(id)
    return recipe


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)