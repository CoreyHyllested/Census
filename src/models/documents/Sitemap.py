from pprint		import pprint as pp
from bs4 import BeautifulSoup as BS4
from bs4 import Comment
from models.Website  import *
from models.Snapshot import *
from models.documents.Document import *


class Sitemap(Document):
	def __init__(self, website, snapshot=None, resource=None, name=None):
		super(Sitemap, self).__init__(website, snapshot, resource, name=name)
		self.sitemap_urls = []


	def parse(self):
		soup = BS4(self.content())
		urls = soup.find_all('url')

		for url in urls:
			uri  = url.find('loc')
			prio = url.find('priority')
			freq = url.find('changefreq')
			last = url.find('lastmod')
			self.sitemap_urls.append( Document.normalize_url_path(uri.string) )
#		pp(self.sitemap_urls)


	def urls(self):
		# BeautifulStoneSoup to parse the document
		if (not self.sitemap_urls):
			self.load()
			if (self.content()):
				self.parse()
		return self.sitemap_urls

		

