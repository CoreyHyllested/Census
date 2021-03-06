import os, random
from pprint		import pprint as pp
from datetime	import datetime as dt 

from models.documents.Document	import *
from models.documents.HTML		import *


class SnapshotState(object):
	EMPTY		= 0
	SAVED		= 0x10
	CACHE		= 0x20		



class Snapshot(object):
	errors = {}

	def __init__(self, website=None, context=None):
		self.website	= website
		self.documents	= []
		self.count		= 5

		self.timestamp	= dt.now()
		self.state		= SnapshotState.EMPTY
		self.__session	= None

		location = self.location()
		if (not os.path.exists(location)):
			os.makedirs(location)
		self.documents.extend( self.website.sitemap )



	def __repr__ (self):	return '<Snapshot %r %r>'% (self.website.domain, self.timestamp.strftime('%Y-%m-%d-%H'))
	def __str__  (self):	return '<Snapshot %r %r>'% (self.website.domain, self.timestamp.strftime('%Y-%m-%d-%H'))



	def collect_snapshot(self, debug=False):
		if (debug): print 'PRE-PRIME', self.website.domain, 'to collect %d of %d' % (self.count, len(self.documents))
		self.prime(5)
		if (debug): print 'POSTPRIME', self.website.domain, 'to collect %d of %d' % (self.count, len(self.documents))
		pp(self.documents)

		for document in self.documents[:self.count]:
			document.load(debug=debug)
		print self.website.domain, 'cookies:'
		pp(self.cookies())


	def location(self):
		return self.website.location() + '/snapshots/' + self.timestamp.strftime('%Y-%m-%d')


	def session(self):
		if (not self.__session):
			self.__session = requests.Session()
		return self.__session


	def cookies(self):
		session = self.session()
		return requests.utils.dict_from_cookiejar(session.cookies)


	def __read_cache_path(self):
		return self.snapshot_exists(days=365)


	def __write_cache_path(self):
		timestamp = dt.now().strftime('%Y-%m-%d')
		directory = self.website.location() + '/' + str(timestamp)
		safe_mkdir(directory)
		return directory + '/' + self.filename



	def prime(self, count=5):
		print 'Snapshot.prime(%s)'% (self.website.domain)
		root = HTML(self.website, '/', snapshot=self, name='root').load(debug=True)
		docs = root.documents(debug=True)
		print self.website.domain, 'has collected %d documents' % (len(self.documents))
	#	pp(docs)

		self.documents.append( root )
		self.documents.extend( docs )
		random.shuffle(self.documents, random.random)

		self.count = count

#		self.visit = self.docsuments[:count]
#			doc = Document(self.website, url, snapshot=self)
			#print 'Snapshot.prime() creating a Document(%s), stored as %s' % (url, doc.filename)
#			self.documents.append(doc)



	def snapshot_exists(self, days=30):
		if os.path.exists(self.website.location()) is False:
			return None
		last_ss = None
		last_ts = days
		for dir_name in os.listdir(self.website.location()):
			if (os.path.isdir(self.website.location() + '/' + dir_name) is False):
				continue

			timedelta = dt.now() - dt.strptime(dir_name, '%Y-%m-%d')
			if (timedelta.days < last_ts):
				last_ts = timedelta.days
				last_ss = self.website.location() + '/' + dir_name + '/' + self.filename
		return last_ss



	def read_cache(self, debug=False):
		file_path = self.__read_cache_path()
		if (file_path):
			fp = None
			try:
				if (debug): print '%s.reading cache...' % (self.doc_source.SOURCE_TYPE)
				fp = open(file_path, 'r')
				self.content	= fp.read()
				self.ss_state	= SnapshotState.READ_CACHE
			except Exception as e:
				print e
			finally:
				if (fp): fp.close()

