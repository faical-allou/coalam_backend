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


# Doing the google authentification
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('../token.json'):
    creds = Credentials.from_authorized_user_file('../token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=5000)
    # Save the credentials for the next run
    with open('../token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

class eventInterface:
    def AaddEvent(self, chefId,recipeId):
        print("start function")
        query = '_' + chefId + '_' + recipeId + '_'
        data = dict(request.form)
        event = {"summary": query,
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
        print ('Event created by function: ' +  str(event))
        return 'event added'

    def deleteEvent(self,eventId):
        event = service.events().delete(calendarId=config.calendarIdat, eventId=eventId).execute()
        return 'event deleted'
    
    def getSchedule(self, chefId,recipeId):
        query = '_' + chefId + '_' + recipeId + '_' 
        calendarId = config.calendarIdpct
        key = config.Gkey
        url = 'https://www.googleapis.com/calendar/v3/calendars/'+calendarId+'/events?q='+query+'&key='+key
        print(url)
        x = requests.get(url)
        jsonX = x.json()
        return jsonX