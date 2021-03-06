import threading, time
import random
import Queue
from models		import *
from pprint		import pprint as pp
from datetime	import datetime as dt 


class ScraperThread(threading.Thread):
	def __init__(self, q, id, debug=False):
		threading.Thread.__init__(self)
		self.q	= q
		self.id	= id
		self.debug	= debug
		self.errors	= {}
		self.doc_total	= q.qsize()
		self.doc_count	= 0
		self.doc_error	= 0
		self.doc_dload	= 0

	def run(self):
		while not self.q.empty():

			ts = dt.now()
			ss = self.q.get()
			ss.collect_snapshot(debug=True)
			ts_diff	 = dt.now() - ts

#			if (document.doc_state == 0x200):	self.doc_dload = self.doc_dload + 1
#			if (document.doc_state & 0x400):
#				self.doc_error = self.doc_error + 1
#				self.errors[document.doc_state] = document.uri
#			print 'Thread(%d): %d %d|%d|%d\t%s\t%s' % (self.id, self.doc_total, self.doc_count, self.doc_error, self.doc_dload, ts_diff, document.uri)
		if (self.doc_error):
			print 'Errors:'
			pp(self.errors)

	
