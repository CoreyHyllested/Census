import sys, os, random, time
import requests, ssl, certifi
from pprint		import pprint as pp
from datetime	import datetime as dt 
from bs4 import BeautifulSoup as BS4
from bs4 import Comment
from models.Website  import *
from models.Snapshot import *

from models.documents.Document import *


class Sitemap(Document):
	def __init__(self, website, resource=None, force_webcache=False):
		super(Sitemap, self).__init__(website, resource, force_webcache)
		self.sitemap_urls = []


	def parse(self):
		soup = BS4(self.content())
		urls = soup.findAll('url')

		for url in urls:
			uri  = url.find('loc')
			prio = url.find('priority')
			freq = url.find('changefreq')
			last = url.find('lastmod')
			self.sitemap_urls.append(uri.string)
#		pp(self.sitemap_urls)


	def urls(self):
		# BeautifulStoneSoup to parse the document
		if (not self.sitemap_urls):
			self.load()
			if (self.content() == None):
				raise Exception('No Sitemap found')	
			self.parse()
		return self.sitemap_urls

		

