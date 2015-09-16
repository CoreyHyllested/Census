import sys, os, time, json
from pprint		import pprint as pp
from datetime	import datetime as dt 

from models.documents.Document import *


class SnapshotState(object):
	EMPTY		= 0
	SAVED		= 0x10
	CACHE		= 0x20		



class Snapshot(object):
	errors = {}

	def __init__(self, website=None, context=None):
		self.website	= website
		self.documents	= []

		self.state		= SnapshotState.EMPTY
		self.timestamp	= dt.now()

		location = self.location()
		if (not os.path.exists(location)):
			os.makedirs(location)



	def __repr__ (self):	return '<Snapshot %r %r>'% (self.website.domain, self.timestamp.strftime('%Y-%m-%d-%H'))
	def __str__  (self):	return '<Snapshot %r %r>'% (self.website.domain, self.timestamp.strftime('%Y-%m-%d-%H'))
	def location (self):	return self.website.location() + '/snapshots/' + self.timestamp.strftime('%Y-%m-%d')


	def __read_cache_path(self):
		return self.snapshot_exists(days=365)


	def __write_cache_path(self):
		timestamp = dt.now().strftime('%Y-%m-%d')
		directory = self.website.location() + '/' + str(timestamp)
		safe_mkdir(directory)
		return directory + '/' + self.filename



	def prime(self, count=5):
		root = Document(self.website, snapshot=self, resource='/', name='root').get_document(debug=True)
		urls = root.find_urls(all_urls=False)
		self.documents.append(root)

#		for document_id in xrange(count):
#			self.documents.append( Document(self.website, self ))



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

