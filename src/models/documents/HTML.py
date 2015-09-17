from pprint		import pprint as pp
from bs4 import BeautifulSoup as BS4
from bs4 import Comment

from models.Website  import *
from models.Snapshot import *
from models.documents.Document import *



class HTML(Document):
	def __init__(self, website, snapshot=None, resource=None, name=None):
		super(HTML, self).__init__(website, snapshot, resource, name=name)
		self.__page_urls = None
		self.__site_urls = None


	def parse(self, debug=False):
		soup = BS4(self.content())
		tags = soup.find_all('a')
		urls = []
		site = []

		for anchor in tags:
			href = anchor.get('href')
			if (href[0] == '#'): continue
			urls.append( href )

			if (href[0] == '/'): 
				site.append( href )
		self.__page_urls = set(urls)
		self.__site_urls = set(site)
		if (debug): print '%s/%s has %d urls, %d internal' % (self.website.domain, self.filename, len(self.__page_urls), len(self.__site_urls))


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


