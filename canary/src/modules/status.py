# -*- coding: utf-8 -*-
"""
Summary:
		This Module will make multiprocessed requests to determine a list of urls availability
		results are returned in json / dictionary format
author:
grimm venom <grimmvenom@gmail.com>

"""

from src.base.base import Base
import multiprocessing, requests, json
import urllib3
from http.client import responses
from lxml.html import fromstring


class Status:
	def __init__(self, arguments):
		self.arguments = arguments
		self.urls = self.arguments.urls
		self.base = Base()
		self.status_results = dict()
		self.session = requests.session()
		if self.arguments.web_username and self.arguments.web_password:
			print("Setting Auth with username: " + str(self.arguments.web_username))
			self.session.auth = (self.arguments.web_username, self.arguments.web_password)
		multiprocessing.freeze_support()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		
	def main(self):
		print("Checking URL Statuses")
		print("# of Urls Defined: " + str(len(self.urls)))
		self._worker()
		return self.status_results
	
	def _worker(self):
		unique_urls = list()
		malformed_urls = list()
		for url in self.urls:
			valid = self.base.detect_valid_url(url)
			if valid == True:
				if url not in unique_urls:
					unique_urls.append(url)
			else:
				malformed_urls.append(url)
		print("# of Unique Urls to request: " + str(len(unique_urls)))
		print("# of Malformed URLs: " + str(len(malformed_urls)))
		print(str(malformed_urls) + "\n")
		with multiprocessing.Pool(processes=10) as pool:  # Start Multiprocessing pool
			results = pool.map(self._verify, unique_urls)
		self.status_results = results
		print("\n")
	
	def _verify(self, url):
		response_data, session = self.base.session_get_response(self.session, url, False)
		return {url: response_data}