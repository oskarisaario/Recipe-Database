from flask import Flask
from flask_pymongo import pymongo
import pymongo
import os
import config


app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key

connection = "mongodb+srv://"+config.mongo_pw+"@cluster0.critmat.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection)
db = client.db

from application import routes