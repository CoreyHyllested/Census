import os, time
import requests, urltools
from pprint		import pprint as pp

#from models.Snapshot	import *
from models.Document	import *



class Website(object):
	SECONDS = 60

	def __init__(self, website, site_ctx=None, debug=False):
		self.uri	= urltools.normalize(website)
		self.parsed	= urltools.parse(website.lower())
		self.domain	= '.'.join(self.parsed[3:6]).lstrip('www.')
#		self.access	= '.'.join(self.parsed[0:7])

		self.robots = None
		self.sitemap = None
		self.error	= {}
		self.debug	= debug

		self.__session = None
		self.load_domain_state()


	def __repr__ (self):	return '<Website %r>'% (self.domain)
	def __str__  (self):	return '<Website %r>'% (self.domain)



	def session(self):
		if (not self.__session):
			self.__session = requests.Session()
		return self.__session
	

	def sleep(self, seconds=None):
		if (not seconds):
			seconds = self.SECONDS + random.randint(0, 15)
		time.sleep(seconds)



	def load_domain_state(self):
		self.__create_domain_state()
		self.__load_meta()


	def __create_domain_state(self):
		location = self.location()
		if (not os.path.exists(location)):
			os.makedirs(location)
			os.makedirs(location + '/documents')


	def __load_meta(self):
		self.doc_robots	 = Document(self, '/robots.txt'  )
		self.doc_sitemap = Document(self, '/sitemap.xml' )
		self.doc_robots.load()
		self.doc_sitemap.load()



	def location(self, new_location=None):
		return os.getcwd() + '/data/domain/' + self.domain



	def create_snapshot(self, context=None):
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



	def raise_for_errors(self, response):
		return

		# check document for any rate-limited message, if so, try using the webcache
		if 'Sorry, we had to limit your access to this website.' in response._content:
			self.ratelimited.put(self.url)
			print 'rate-limited: %d times, retry with %s' % (len(self.ratelimited.qsize()), self.webcache)
			response = s.get(self.webcache)
			if 'Sorry, we had to limit your access to this website.' in response._content:
				print 'Rate limited again.'
				#raise Exception('WEBCACHE-FAILED')
		else:
			print 'Something fucked up'
			print 'status code(%d|%s) elapsed %s, encoding %s' % (response.status_code, response.reason, response.elapsed, response.encoding)
			pp(response.headers)
