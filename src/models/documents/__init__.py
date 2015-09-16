import sys, os, random, time
import requests, ssl, certifi
from pprint		import pprint as pp
from datetime	import datetime as dt 

from bs4 import BeautifulSoup, Comment
from models.documents.Document	import *
from models.documents.Sitemap	import *



class DocState(object):
	EMPTY		= 0
	READ_WWW	= 0x200
	READ_CACHE	= 0x201
	READ_FAIL	= 0x404
	READ_QUIT	= 0xFFF




