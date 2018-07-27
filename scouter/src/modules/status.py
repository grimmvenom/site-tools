# -*- coding: utf-8 -*-

from src.base.base import Base
import multiprocessing


class Status:
	def __init__(self, arguments):
		self.arguments = arguments
		self.urls = self.arguments.urls
		self.base = Base()
		self.status_results = dict()
		multiprocessing.freeze_support()
		
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
		response_data = dict()
		# print([element_url, element_type, element_index])
		try:
			if self.arguments.web_username and self.arguments.web_password:
				response = self.base.get_response(url, False, str(self.arguments.web_username), str(self.arguments.web_password))
			else:
				response = self.base.get_response(url)
			
			response_data["status"] = int(response["status"])
			try:
				response_data["redirectedURL"] = response["redirectedURL"]
			except:
				pass
			response_data["pageTitle"] = response["pageTitle"]
			response_data["message"] = response["message"]
		
		# print(json.dumps(self.log[fkey][skey], indent=4, separators=(",", ":")))
		except Exception as e:
			response_data['status'] = "ERROR"
			response_data['message'] = "Request Error"
			response_data['pageTitle'] = "N/A"
			print("Error: \n" + str(e))
			print("\nFailure @: " + str(url))
			print("\n")
		# print([element_url, element_type, element_index, element_data])
		return {url: response_data}