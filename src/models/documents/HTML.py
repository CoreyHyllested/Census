from pprint		import pprint as pp
from bs4 import BeautifulSoup as BS4
from bs4 import Comment

from models.Website  import *
from models.Snapshot import *
from models.documents.Document import *



class HTML(Document):
	def __init__(self, website, uri, snapshot=None, name=None):
		super(HTML, self).__init__(website, uri, snapshot, name=name)
		self.__page_urls = None
		self.__site_urls = None
		self.__documents = None


	def parse(self, debug=False):
		self.__documents = []
		soup = BS4(self.content())
		tags = soup.find_all('a')
		urls = []
		site = []
		imgs = []
		docs = []

		urls_origin = urltools.parse(self.url)[4:6]
		for anchor in tags:
			href = anchor.get('href')
			urls.append( href )

			if ((href[-4:] == '.img') or (href[-4:] == '.png') or (href[-4:] == '.jpg') or (href[-5:] == '.jpeg')):
				imgs.append( href )
				continue
			if ((href[-4:] == '.pdf') or (href[-4:] == '.doc') or (href[-5:] == '.docx')):
				docs.append( href )
				continue
			if (href[0] == '#'): continue

			try:
				self.__documents.append( Document(self.website, href, self.snapshot) )
			except Exception as e:
				print e
		self.__page_urls = set(urls)
		self.__site_urls = set(site)
		if (debug): print '%s/%s has %d urls, %d internal' % (self.website.domain, self.filename, len(self.__page_urls), len(self.__site_urls))


	def documents(self, debug=False):
		self.__collect_urls(debug)
		return self.__documents


	def site_urls(self, debug=False):
		self.__collect_urls(debug)
		return self.__site_urls


	def page_urls(self, debug=False):
		self.__collect_urls(debug)
		return self.__page_urls


	def __collect_urls(self, debug=False):
		if (self.__page_urls == None):
			self.load()
			if (self.content() == None):
				raise Exception('No HTML document content found')	
			self.parse(debug)

