import sys, os, threading
import socks, socket, requests
import re, random, time
import cmd, argparse
import Queue
from multiprocessing import Process
from bs4 import BeautifulSoup, Comment
from pprint		import pprint as pp
from datetime	import datetime as dt 
from models		import *

from models.Snapshot			import *

VERSION = 0.08
UA_VER	= 0.1
THREADS	= 1

threads	= []



requests.packages.urllib3.disable_warnings()


def configure_network(args):
	requests.packages.urllib3.disable_warnings()
	host_response = requests.get('http://icanhazIP.com')

	def create_connection(address, timeout=None, source_address=None):
		sock = socks.socksocket()
		sock.connect(address)
		return sock

	socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
	socket.socket = socks.socksocket
	socket.create_connection = create_connection

	post_response = requests.get('http://icanhazIP.com')
	print 'PrivacyCensus - Host IP: %s\t configure IP: %s ' % (host_response._content.rstrip(), post_response._content.rstrip())
	if (host_response._content == post_response._content): print 'PrivacyCensus - Using host IP address.  Some sites may fail' #Not running tor:9050

	# setup user-agent information
	ua = None #urllib2.build_opener()
	#ua = urllib2.build_opener()
	#ua_string = 'PCBot/v%d' % UA_VER
	#ua_string = 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
	#ua.addheaders = [('User-agent', ua_string)]
	return ua


def configure_db():
	def safe_mkdir_local(path):
		directory = os.getcwd() + path
		if (os.path.exists(directory) == False):
			os.makedirs(directory)

	safe_mkdir_local('/data/')



def load_sources(config_params):
	q = Queue.Queue()
#	q.put( Website('https://soulcrafting.co').create_snapshot()		)
	q.put( Website('https://www.yahoo.com').create_snapshot()		)
	q.put( Website('https://amazon.com').create_snapshot()			)
#	q.put( Website('https://nytimes.com').create_snapshot()			)
#	q.put( Website('https://www.google.com').create_snapshot()		)

	print 'PrivacyCensus - queue size %d' % (q.qsize())
	return q






if __name__ == '__main__':
	print 'PrivacyCensus v' + str(VERSION)
	parser = argparse.ArgumentParser(description='Scrape, normalize, and process html, javascript, and cookies')
	parser.add_argument('-T', '--tor',			action='store_true',	help='use Tor')
	parser.add_argument('-V', '--verbose',		action='store_true',	help='increase verbosity')
	parser.add_argument('-O', '--overwrite',	action='store_true',	help='Overwrite output file')
	parser.add_argument('-S', '--source',								help='Single source')
	args = parser.parse_args()

	#configure_network(args)
	configure_db()

	q = load_sources(args)
	for thread_id in xrange(THREADS):
		print 'PrivacyCensus - starting thread %d' % (thread_id)
		t = ScraperThread(q, id=thread_id, debug=True)
		t.start()
		threads.append(t)

	for thread in threads:
		thread.join()

	sys.exit()
