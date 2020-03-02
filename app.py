import os
from flask import Flask, request, jsonify, session
from flask_restful import Resource, Api
from flask_celery import make_celery
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import db



app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'amqp://jdcsohky:6n7Niqm9-hEtQiUWg912u0EWzCt-bLE_@crow.rmq.cloudamqp.com/jdcsohky'
app.config['CELERY_BACKEND'] = 'db+postgres://liwrnidwmrvjrl:dd967c421553a2bafb708b4865c8bb5c36461ee00a2f8b2971ae19b96afc29b6@ec2-46-137-177-160.eu-west-1.compute.amazonaws.com:5432/dd0178iv33fmmj'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
celery = make_celery(app)
db = SQLAlchemy(app)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'


class fixdb(db.Model):
	__tablename__ = 'dht_new'

	id = db.Column(db.Integer, primary_key =True)
	temp = db.Column(db.String(80))
	name = db.Column(db.String(80))

	def __init__(self, temp, name):
		self.temp = temp
		self.name = name

	def add_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()

"""@app.before_first_request
def create_tables():
	db.create_all()"""

@celery.task(name='dht.receive')
def receive_dht():
	#r = requests.get("http://192.168.0.34:5000/dht")
	#data = r.json()

	#temp = data['temperature']
	#name = data['humidity']
	temp = 12
	name = 44
	print(f"temp: {temp} hum: {name}")
	new_temp = temp
	new_name = name
	#url = "http://0.0.0.0:5000/temp"
	#session['new_temp'] = new_temp
	#session['new_name'] = new_name
	#r = requests.post(url, temp)	#print(r.text)
	#print(f"new_list: {new_list}")
	return 'ok'

@celery.task(name='dht.list')
def dht_list():
	list = db.session.query(fixdb.temp, fixdb.name).all()
	for m in list:
		print(m)
	return jsonify(list)


@app.route('/create', methods=['GET'])
def postrandom():
	receive_dht.delay()
	temp = session.get('new_temp')
	name = session.get('new_name')
	print(f"temp i create: {temp}")
	print(f"hum i create: {name}")

	test_temp = fixdb(temp, name)
	test_temp.add_to_db()
	return 'ok'
	
@app.route('/list', methods=['GET'])
def list():
	dht_list.delay()
	return'ok'
	
@app.route('/name/<string:name>', methods=['GET'])
def getindex(name):
	if fixdb.query.filter_by(name=name).first():
		print(name)
	return'ok'

@app.route('/delete/<string:name>', methods=['POST'])
def delete(name):
	data = request.get_json()
	print(name)
	object = fixdb.query.filter_by(name=name).first()
	print(name)
	object.delete_from_db()	
	return 'deleted'
		 

if __name__ == '__main__':
	db.create_all()
	app.run(host= '0.0.0.0', debug=True)