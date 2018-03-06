from flask import Flask
#from flask_pymongo import PyMongo

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from bson.json_util import dumps
from pymongo import MongoClient
from bson import ObjectId
import json

app = Flask(__name__)
client = MongoClient("mongodb://tomi:tomi_insurer@ds143388.mlab.com:43388/mongo_insurer") #host uri
db = client.mongo_insurer    #Select the database
db.authenticate(name='tomi',password='tomi_insurer')

riskTypes = db.riskTypes

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/')
def hello_world():
  return 'Hello Python'

@app.route('/getSetRiskType', methods=['GET','POST'])
@crossdomain(origin='*')
def getSetRiskType():
	if request.method== 'GET':
		 return getRiskTypes()
	
	if request.method== 'POST':
		return postRiskType(request.get_json(force=True,silent=True))

def getRiskTypes():
	return dumps(riskTypes.find()) 

def postRiskType(data):
	riskTypes.insert(data)
	return dumps(riskTypes.find())

@app.route('/getschema', methods=['POST'])
@crossdomain(origin='*')
def getschema():
	data = request.get_json(force=True, silent=True)
	return dumps(riskTypes.find_one({"_id":ObjectId(data['id'])}))
		
		
@app.route('/addfield', methods=['POST'])
@crossdomain(origin='*')
def addfield():
	return updateRiskTypePropsById(request.get_json(force=True, silent=True))
	
def updateRiskTypePropsById(data):
	riskType = riskTypes.find_one({"_id":ObjectId(data['id'])})
	riskType['properties'] = data['properties']
	riskTypes.save(riskType)
	return dumps(riskType)

	
@app.route('/insertdataforfield', methods=['POST'])
@crossdomain(origin='*')
def insertdataforfield():
	return updateRiskTypeFields(request.get_json(force=True, silent=True))
	
def updateRiskTypeFields(data):
	id = data['_id']['$oid']
	riskType=riskTypes.find_one({"_id":ObjectId(id)})
	riskType['properties'] = data['properties']
	riskTypes.save(riskType)
	return dumps(riskType)

@app.route('/deleteRiskType', methods=['POST'])
@crossdomain(origin='*')
def deleteRiskType():
	return removeRiskType(request.get_json(force=True, silent=True))
	
def removeRiskType(data):
	id = data['_id']['$oid']
	riskType=riskTypes.find_one({"_id":ObjectId(id)})
	riskTypes.remove(riskType)
	return dumps(riskTypes.find())
	
  
if __name__ == '__main__':
  app.run()
