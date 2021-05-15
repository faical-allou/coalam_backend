import simplejson as json



class dataInterface:

    def getAllRecipes(self ):
        recipes = {"name": "Classic Burger", "creator": "Faical"}
        result = json.dumps(recipes)

        return result


def __init__(self):
        print ("in init")
