import sys, os, random, time
import requests, ssl, certifi
from pprint		import pprint as pp
from datetime	import datetime as dt 

from bs4 import BeautifulSoup, Comment
from models.Website  import *
from models.Snapshot import *


class Document(object):
	errors = {}

	def __init__(self, website, uri, snapshot=None, force_webcache=False, name=None):
		print 'Document (%s, %s, %r, %s)' % (website.domain, uri, snapshot, name)
		self.website	= website
		self.snapshot	= snapshot

		self.__create_url(uri, name)
		self.__content	= None
		self.timestamp	= dt.now().strftime('%Y-%m-%d')

		self.use_webcache = force_webcache
	

	def __repr__ (self): return '<Document %r/%s>' % (self.website.domain, self.parsed_uri[7])
	def __str__  (self): return '<Document %r/%s>' % (self.website.domain, self.parsed_uri[7])
	def content	 (self): return self.__content


	def __create_url(self, uri, filename):
		self.parsed_uri	= urltools.parse(str(uri))

		if ((uri[0] == '/') or self.parsed_uri[4] == ''):
			self.parsed_uri = urltools.parse(self.website.uri + str(uri))

		if (self.parsed_uri[4:6] != self.website.parsed[4:6]):
			# allows subdomain to differ!
			raise Exception ('Document (Invalid, domain does not match)')

		self.filename	= filename or Document.normalize_filename(self.parsed_uri.path)
		self.url		= urltools.construct(self.parsed_uri)
		#print 'Document (%s) => %s' % (self.url, self.filename)



	@staticmethod
	def normalize_filename(path):
		if (path == '/'): return 'root'
		return path.lstrip('/').replace('/', '_')


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



	def load(self, debug=False):
		self.__load_doc(debug)

		if (self.__content == None):
			self.get_document(debug)
		return self



	def get_document(self, debug=False):
		try:
			if (debug): print '%s get_document(%s)' % (self.website.domain, self.filename)
			self.__download(debug)
		except Exception as e:
			print 're-raising', type(e), e
			raise e
		return self



	def __read_cache_path(self):
		# for metadata, files should ALWAYS exist.
		return self.snapshot_exists(days=365)




	def __read_cache(self, debug=False):
		file_path = self.__read_cache_path()
		if (file_path):
				if (fp): fp.close()


	def __session(self):
		if (self.snapshot):
			return self.snapshot.session()
		return self.website.session()


	def __download(self, debug=False):
		if (debug): print 'downloading %s' % (self.url)

		try:
			session = self.__session()
			response = session.get(self.url, verify=False)
			response.raise_for_status()
			self.website.raise_for_errors(response)

			# save content
			self.__content = response._content
			self.__save_doc(debug)
		except requests.exceptions.HTTPError:
			print 'HTTPError %d: %s' % (response.status_code, self.url)
#			self.doc_source.add_error('HTTPError', self.url)
		except requests.exceptions.ConnectionError:
			print 'Connection Error: (%s) trying to sleep for 2 min' % self.url
			#self.doc_source.add_error('ConnectionError', self.url)
			self.website.sleep(5)
		except Exception as e:
			print 'General Exception'
			print type(e), e
			#self.doc_source.add_error('download_failed', self.url)
			print 'content:', response._content
		finally:
			# hit URL, always sleep
			self.website.sleep()



	def __save_doc(self, debug=False):
		if (not self.__content): return

		file_path = self.__cache_path()

		fp = None
		try:
			fp = open(file_path, 'w+')
			fp.truncate()
			fp.write(self.__content)
			if (debug): print 'wrote doc %s file_path %s' % (self.filename, file_path)

		except Exception as e:
			print type(e), e
		finally:
			if (fp): fp.close()



	def __load_doc(self, debug=False):
		if (self.__content): return self.__content

		fp = None
		try:
			if (debug): print 'loading document %s/%s' % (self.website.domain, self.filename)
			fp = open(self.__cache_path(), 'r')
			self.__content = fp.read()
		except IOError:
			pass
		except Exception as e:
			print type(e), e
		finally:
			if (fp): fp.close()
		return self.__content



	def backup(self, file_path=None, debug=False):
		if (not file_path):
			file_path = self.website.location() + '/' + self.filename[:-5] + '-' + dt.now().strftime('%Y-%m-%d-%H') + '.backup'
			filesystem.write_file(file_path, self.__content)


	def __cache_path(self):
		if (self.snapshot):
			return self.snapshot.location() + '/'           + self.filename
		return     self.website.location()  + '/documents/' + self.filename


#		snapshot_file = self.snapshot_exists(days=21)
#		if (snapshot_file): return self.read_cache(debug)

