

class fixdb(db.Model):
	__tablename__ = 'dht_new'

	id = db.Column(db.Integer, primary_key =True)
	tempa = db.Column(db.String(80))

	def __init__(self, temp):
		self.temp = temp

	fixdb = ('mike')
	db.session.add(self)
	db.session.commit()
