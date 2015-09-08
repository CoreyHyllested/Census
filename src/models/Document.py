import sys, os, time
import requests, urllib3, socks, socket
import re, random, time, json
import Queue
from pprint		import pprint as pp
from datetime	import datetime as dt 

from models.Snapshot import *



class DocState(object):
	EMPTY		= 0
	READ_WWW	= 0x200
	READ_CACHE	= 0x201
	READ_FAIL	= 0x404
	READ_QUIT	= 0xFFF




class Document(object):
	errors = {}
	ratelimited = Queue.Queue()
	DIR_RAWHTML = os.getcwd() + '/data/raw/'

	def __init__(self, snapshot, uri=None, force_webcache=False):
		self.uri = uri
		self.snapshot = snapshot
		self.filename = 'document.html'
		self.content = None

		self.use_webcache = force_webcache
	


	def __repr__ (self): return '<Document %r/%r>' % (self.snapshot, self.uri)
	def __str__  (self): return '<Document %r/%r>' % (self.snapshot, self.uri)
	

	def snapshot_exists(self, days=30):
		if os.path.exists(self.location) is False:
			return None

		last_ss = None
		last_ts = days
		for dir_name in os.listdir(self.location):
			if (os.path.isdir(self.location + '/' + dir_name) is False):
				continue

			timedelta = dt.now() - dt.strptime(dir_name, '%Y-%m-%d')
			if (timedelta.days < last_ts):
				last_ts = timedelta.days
				last_ss = self.location + '/' + dir_name + '/' + self.filename
		return last_ss



	def get_document(self, debug=False):
		# check if a recent document already exists?
		if (debug): print '\n%s.get_document(%r)' % (self.doc_source.SOURCE_TYPE, self)
		snapshot_file = self.snapshot_exists(days=21)
		if (snapshot_file): return self.read_cache(debug)

		try:
			self.download(debug)
			self.write_cache(debug)
		except Exception as e:
			print e
			print 're-raising'
			#raise e
		return True



	def __read_cache_path(self):
		# for metadata, files should ALWAYS exist.
		return self.snapshot_exists(days=365)


	def __write_cache_path(self):
		timestamp = dt.now().strftime('%Y-%m-%d')
		directory = self.location + '/' + str(timestamp)
		safe_mkdir(directory)
		return directory + '/' + self.filename



	def read_cache(self, debug=False):
		file_path = self.__read_cache_path()
		if (file_path):
			fp = None
			try:
				if (debug): print '%s.reading cache...' % (self.doc_source.SOURCE_TYPE)
				fp = open(file_path, 'r')
				self.content	= fp.read()
				self.doc_state	= DocState.READ_CACHE
			except Exception as e:
				print e
			finally:
				if (fp): fp.close()



	def download(self, debug=False):
		print '%s.download doc' % (self.doc_source.SOURCE_TYPE)
		self.doc_state	= DocState.READ_FAIL

		try:
			s = requests.Session()
			response = s.get(self.uri)
			response.raise_for_status()

			# check document for any rate-limited message, if so, try using the webcache
			if 'Sorry, we had to limit your access to this website.' in response._content:
				self.ratelimited.put(self.uri)
				print 'rate-limited: %d times, retry with %s' % (len(self.ratelimited.qsize()), self.webcache)
				response = s.get(self.webcache)
				if 'Sorry, we had to limit your access to this website.' in response._content:
					print 'Rate limited again.'
					#raise Exception('WEBCACHE-FAILED')
			if (response._content): 
				self.content	= response._content
				self.doc_state	= DocState.READ_WWW
			else:
				print 'Something fucked up'
				print 'status code(%d|%s) elapsed %s, encoding %s' % (response.status_code, response.reason, response.elapsed, response.encoding)
				pp(response.headers)
		except requests.exceptions.HTTPError as e:
			print 'HTTPError %d: %s' % (response.status_code, self.uri)
			self.doc_source.add_error('HTTPError', self.uri)
			# perhaps take this URL out of rotation.
			if (response.status_code == 500): self.doc_state = DocState.READ_QUIT
			print e
		except requests.exceptions.ConnectionError as e:
			print e
			self.doc_source.add_error('ConnectionError', self.uri)
			print 'Connection Error: trying to sleep for 5min'
			self.doc_source.sleep(5 * 60)
		except Exception as e:
			print 'General Exception'
			self.doc_source.add_error('download_failed', self.uri)
			print type(e), e
			print 'content:', response._content
		finally:
			# hit URL, always sleep
			self.doc_source.sleep()



	def write_cache(self, debug=False):
		if (not self.content): return
		file_path = self.__write_cache_path()
		if (debug): print '%s.caching file %s' % (self.doc_source.SOURCE_TYPE, file_path)
		filesystem.write_file(file_path, self.content)


	def backup(self, file_path=None, debug=False):
		if (not file_path):
			file_path = self.location + '/' + self.filename[:-5] + '-' + dt.now().strftime('%Y-%m-%d-%H') + '.backup'
			filesystem.write_file(file_path, self.content)
