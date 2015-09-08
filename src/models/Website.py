import os
import requests, urltools
from pprint		import pprint as pp
from datetime	import datetime as dt 

from models.Snapshot	import *
from models.Document	import *


class Website(object):
	def __init__(self, domain, site_ctx=None, debug=False):
		self.domain = urltools.normalize(domain.lower())
		self.robots = None
		self.sitemap = None

		self.error	= {}
		self.debug	= debug

	def __repr__ (self):	return '<Website %r>'% (self.domain)
	def __str__  (self):	return '<Website %r>'% (self.domain)


	
	def location(self, new_location=None):
		return os.getcwd() + '/data/' + self.domain


	def create_snapshot(self, context=None):
		session = requests.Session()
		self.snapshot = Snapshot(self, context=None)

		try:
#			self.snapshot.prime_snapshot()		Get robots, humans, sitemap.xml
			self.snapshot.prime_documents(5)
		except Exception as e:
			print type(e), e
		finally:
			pass

	def robots(self, ctx):	pass
	def sitemap(self, ctx):	pass

