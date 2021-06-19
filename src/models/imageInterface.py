import simplejson as json
import pandas as pd
import pathlib
import os
from flask import send_file
from google.cloud import storage
import random
import config

class imageInterface:

    def upload_blob(self,bucket_name, source_file_name, destination_blob_name):
        print("uploading")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))

    def download_blob(self,bucket_name, source_blob_name, destination_file_name):
        print("downloading")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print("Blob {} downloaded to {}.".format(source_blob_name, destination_file_name))

    def delete_manyblobs(self,bucket_name, prefixpath):
        print('deleting many')
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefixpath)
        i_ = 0
        for blob in blobs:
            i_ = i_+1
            blob.delete()
        print(str(i_) + ' file(s)/folder(s) deleted')

    def count_blobs(self,bucket_name, prefixpath):
        print('deleting many')
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefixpath)
        i = 0
        for blob in blobs:
            i = i+1
        return i

    def getRecipeImage(self,recipeId,id):
        print('image requested')
        try:
            location = 'image/recipe-'+recipeId+'/'+id+'.jpg'
            tempfilename = 'recipe-'+recipeId+'-'+id+'.jpg'
            self.download_blob(config.Gcloudbucket,location,"./static/temp/"+tempfilename)
            return send_file("../static/temp/"+tempfilename, mimetype='image/jpg')
        except:
            filename = '../static/image/error404.gif'
            return send_file(filename, mimetype='image/gif') 

    def getChefImage(self, id):
        try:
            location = 'image/chef-'+id+'/1.jpg'
            tempfilename = 'chef-'+id+'.jpg'
            self.download_blob(config.Gcloudbucket,location,"./static/temp/"+tempfilename)
            return send_file("../static/temp/"+tempfilename, mimetype='image/jpg')

        except:
            filename = '../static/image/empty-profile.png'
            return send_file(filename, mimetype='image/gif')  
    
    def addimage(self, file, destination):
        tempfilename = "./static/temp/"+str(random.randint(0,1000))
        file.save(tempfilename)
        self.upload_blob(config.Gcloudbucket,tempfilename,destination)
    
    def deleteFiles(self, folderpath):       
        self.delete_manyblobs(config.Gcloudbucket, folderpath)

    def getCountImages(self, path):
        return self.count_blobs(config.Gcloudbucket, path)