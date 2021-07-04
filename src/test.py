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
from app import doDeleteChef, doDeleteRecipe

from models.dataInterface import *
from models.imageInterface import *
from models.eventInterface import *


import config
from google.cloud import storage


dataInterface = dataInterface()
imageInterface = imageInterface()
eventInterface = eventInterface()
 


testChef = chef('123',"6",'name','cool')
testRecipe = recipe("6",'name','5',"recipe", "description", "ingredients", "tools")

dataInterface.insertChef(testChef)
dataInterface.insertRecipe(testRecipe)

#doDeleteChef("6")
doDeleteRecipe('5')

