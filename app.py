import os
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_celery import make_celery
import requests
from flask_sqlalchemy import SQLAlchemy
from db import db


app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'amqp://jdcsohky:6n7Niqm9-hEtQiUWg912u0EWzCt-bLE_@crow.rmq.cloudamqp.com/jdcsohky'
app.config['CELERY_BACKEND'] = 'rpc://'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
celery = make_celery(app)
db = SQLAlchemy(app)

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


@app.before_first_request
def create_tables():
	db.create_all()

@celery.task(name='dht.receive')
def receive_dht():
	r = requests.get("http://192.168.0.34:5000/dht")
	data = r.json()
	temp = data['temperature']
	name = data['humidity']
	print(f"temp: {temp} hum: {name}")
	test_temp = fixdb(temp, name)
	test_temp.add_to_db()
	print(temp)
	print(name)
	return 'ok'

@app.route('/create', methods=['GET'])
def postrandom():
	receive_dht.delay()
	return 'ok'


@app.route('/list', methods=['GET'])
def list():
	list = db.session.query(fixdb.temp, fixdb.name).all()
	for m in list:
		print(m)
	return jsonify(list)

@app.route('/name/<string:name>', methods=['GET'])
def getindex(name):
	if fixdb.query.filter_by(name=name).first():
		return {"index": ['name:', name]}


@app.route('/delete/<string:name>', methods=['POST'])
def delete(name):
	data = request.get_json()
	print(name)
	object = fixdb.query.filter_by(name=name).first()
	print(name)
	fixdb.delete_from_db(object)	
	return jsonify("deleted", name)


@app.route('/dht_receive', methods=['GET', 'POST'])
def input():
	if request.method == 'POST':
		tempan = request.form.get('temperature')
		return jsonify(tempan)


@app.route('/dht', methods=['GET'])
def getdht():
	data = request.get_json()
	temp = data['temperature']
	return jsonify(temp)


	 

if __name__ == '__main__':
	app.run(host= '0.0.0.0', debug=True)