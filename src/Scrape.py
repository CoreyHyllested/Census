import unittest
import requests, urltools
from pprint		import pprint as pp
from selenium	import webdriver
from selenium.common.exceptions		import *
from selenium.webdriver.common.keys	import Keys
from selenium.webdriver.common.by	import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait	import WebDriverWait


class ParametrizedTestCase(unittest.TestCase):
	""" TestCase classes are parametrized should inherit this class. """

	def __init__(self, methodName='runTest', param=None):
		super(ParametrizedTestCase, self).__init__(methodName)
		self.address = urltools.parse(str(param))
		#URL(parts.scheme, username, password, subdomain, domain, tld, port, parts.path, parts.query, parts.fragment, url)


	@staticmethod
	def parametrize(testcase_klass, param=None):
		""" Create a suite containing all tests taken from the subclass, passing them the parameter 'address'. """

		testloader = unittest.TestLoader()
		testnames = testloader.getTestCaseNames(testcase_klass)
		suite = unittest.TestSuite()
		for name in testnames:
			suite.addTest(testcase_klass(name, param=param))
		return suite




class WebTest(ParametrizedTestCase):

	def setUp(self):
#		self.android = webdriver.Android()		#Mobile
#		self.ie      = webdriver.Ie()
#		self.opera   = webdriver.service.Service('/usr/lib/chromium-browser/chromedriver')	#needed to install on Ubuntu
		self.forward	= None
		self.websites	= []
		self.visited	= []
		self.links_remote = []
		self.files_remote = []
		self.files_local  = []


#	def test_chrome(self):
#		self.chrome  = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')	#needed to install on Ubuntu
#		self.chrome.get(self.address)

#		pp(self.chrome.get_cookies())
#		self.chrome.quit()



	def test_firefox(self):
		print 'Firefox(%s)' % self.address.url
		self.firefox = webdriver.Firefox()

		self.websites.append(self.address.url)
		self.random_walk(self.firefox, 5)
		pp(self.firefox.get_cookies())
		self.firefox.quit()



#	def test_phantom(self):
#		print 'PhantomJS(%s)' % self.address.url
#		self.phantom = webdriver.PhantomJS()
#		self.websites.append(self.address.url)
#		self.random_walk(self.phantom, 5)
#		self.phantom.quit()



	def random_walk(self, webdriver, depth):
		if depth == 0: return

		site = self.websites.pop()
		self.visited.append(site)

		webdriver.get(site)
		WebDriverWait(webdriver, 5)	# wait up to 10 seconds

		if (len(self.visited) == 1) and not urltools.compare(webdriver.current_url, self.address.url):
			self.forward = urltools.parse(webdriver.current_url)
		
		scripts_src	 	= webdriver.find_elements_by_xpath('//script[@src]')
		scripts_code	= webdriver.find_elements_by_xpath('//script[not(@src)]')
		links			= webdriver.find_elements_by_xpath('//link[@href]')
		hrefs			= webdriver.find_elements_by_xpath('//*[@href]')
		forms			= webdriver.find_elements_by_xpath('//form')
		imgs			= webdriver.find_elements_by_xpath('//img')

		self.__parse_scripts(scripts_src)
		self.__parse_links(hrefs, links)
		self.__parse_forms(forms)
		
		for element in imgs:
			try:
				html = element.get_attribute('outerHTML')
			except StaleElementReferenceException:
				continue
			print '<img>', html, element.is_displayed() 

#		for element in links:
#			html = element.get_attribute('outerHTML')
#			print '<link: css? js? other?>', html

		pp(webdriver.get_cookies())
		print '<script> on-page(%d) linked(%d)' % ( len(scripts_code), len(scripts_src) )
		print '<link>  (%d)'  % (len(links))
		print '<image> (%d)'  % (len(imgs) )
		print 'href= (%d)'  %   (len(hrefs))



	def tearDown(self):
		pass
#		self.android.quit()
#		self.ie.quit()
#		self.opera.quit()


	def __parse_scripts(self, scripts_src):
		for element in scripts_src:
			html = element.get_attribute('outerHTML')
			link = element.get_attribute('src')
			if (link and link[0:2] == '//'):
				link = self.address.scheme + ':' + link
				self.files_remote.append(link)
			elif (link and link[0] == '/'):
				link = self.address.url + link
				self.files_local.append(link)
			print '<script>', link



	def __parse_links(self, hrefs, links):
		href_set = set(hrefs) - set(links)
		for element in href_set:
			added = False

			try:
				html = element.get_attribute('outerHTML')
				link = element.get_attribute('href')
			except StaleElementReferenceException:
				continue

			if (link and link[0:2] == '//'):
				link = self.address.scheme + ':' + link
				self.links_remote.append(link)
			elif (link and link[0] == '/'):
				link = self.address.url + link
				self.websites.append(link)
				added = True
			elif (link and link[0] == '#'):
				link = 'ignored'
				pass
			elif (link and link[:4] == 'http'):
				page_link = urltools.parse(link)
				if ((page_link.domain == self.address.domain) or (self.forward and (page_link.domain == self.forward.domain))):
					self.websites.append(link)
					added = True
			print '[href=%s] added(%r) displayed(%r) ' % (link, added, element.is_displayed())

 

	def __parse_forms(self, forms):
		for element in forms:
			try:
				html = element.get_attribute('outerHTML')
			except StaleElementReferenceException:
				continue
			print '<form> ', html, element.is_displayed() 




if __name__ == '__main__':
	suite = unittest.TestSuite()
#	suite.addTest(ParametrizedTestCase.parametrize(WebTest, param='https://www.google.com'))
	suite.addTest(ParametrizedTestCase.parametrize(WebTest, param='http://www.espn.com'))
#	suite.addTest(ParametrizedTestCase.parametrize(WebTest, param='https://soulcrafting.co'))
	unittest.TextTestRunner(verbosity=2).run(suite)
#	unittest.main()
#	def suite():
#		suite = unittest.TestSuite()
#		suite.addTest(test_FF('Firefox'))
#		return suite

