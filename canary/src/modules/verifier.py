# -*- coding: utf-8 -*-

"""
Summary:
		This Module will make multiprocessed requests to determine the scraped results availability
		results are returned in json / dictionary format
author:
grimm venom <grimmvenom@gmail.com>

"""

import json, multiprocessing, math, sys
from multiprocessing import Pipe
from src.base.base import Base
import re, urllib3, requests


class Verify:
	def __init__(self, log, arguments):
		self.arguments = arguments
		self.log = log.copy()
		self.base = Base()
		self.unique_requests = list()
		self.session = requests.session()
		if self.arguments.web_username and self.arguments.web_password:
			print("Setting Auth with username: " + str(self.arguments.web_username))
			self.session.auth = (self.arguments.web_username, self.arguments.web_password)
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

	def main(self):
		self._unique_requests()
		self._worker()
		return self.log
	
	def _unique_requests(self):
		counter = 0
		for url_key in self.log.keys():  # Loop Through URL Keys
			for element_type in self.log[url_key].keys():  # Loop Through element type keys
				if not element_type.startswith(('ignored_', 'forms')):  # Ignore some keys
					for index, value in self.log[url_key][element_type].items():  # Append data to list
						target_url = value['target_url']
						if value['valid_url'] == True:
							counter += 1
							if target_url not in self.unique_requests:
								self.unique_requests.append(target_url)
							# request_list.append([url_key, element_type, index, value])
		print("Total Target Urls: " + str(counter))
	
	def _worker(self):
		print("Unique Target Urls: " + str(len(self.unique_requests)))
		print("Verifying Unique Targets\n")
		with multiprocessing.Pool(processes=10) as pool:  # Start Multiprocessing pool
			results = pool.map(self._verify, self.unique_requests)
		# queue = dict(pair for d in results for pair in d.items())  # convert the returned list to dictionary
		for result in results:
			# print(result)
			target_url = result[0]
			response_data = result[1]
			for url_key in self.log.keys():  # Loop Through URL Keys
				for element_type in self.log[url_key].keys():  # Loop Through element type keys
					if not element_type.startswith(('ignored_', 'forms')):  # Ignore some keys
						for index, value in self.log[url_key][element_type].items():  # Append data to list
							dict_target_url = value['target_url']
							if target_url == dict_target_url:
								# print([element_url, element_type, element_index, element_data['target_url'], element_data['status']])
								self.log[url_key][element_type][index]['status'] = response_data['status']
								try:
									self.log[url_key][element_type][index]['redirectedURL'] = response_data['redirectedURL']
								except Exception as e:
									pass
								self.log[url_key][element_type][index]['message'] = response_data['message']
								self.log[url_key][element_type][index]['pageTitle'] = response_data['pageTitle']
	
	def _verify(self, url):
		response_data, self.session = self.base.session_get_response(self.session, url, False)
		return [url, response_data]
		
