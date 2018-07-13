
import json, multiprocessing, math, sys
from multiprocessing import Pipe
from src.base.base import Base


class Verify:

	def __init__(self, log, arguments):
		self.arguments = arguments
		self.log = log.copy()
		self.base = Base()
		self.unique_requests = list()

	def main(self):
		self._unique_requests()
		self._worker()
		return self.log
	
	def _unique_requests(self):
		for url_key in self.log.keys():  # Loop Through URL Keys
			for element_type in self.log[url_key].keys():  # Loop Through element type keys
				if not element_type.startswith(('ignored_', 'forms')):  # Ignore some keys
					for index, value in self.log[url_key][element_type].items():  # Append data to list
						target_url = value['target_url']
						if target_url not in self.unique_requests:
							self.unique_requests.append(target_url)
						# request_list.append([url_key, element_type, index, value])
					
	def _worker(self):
		print("Verifying Links")
		print(str(len(self.unique_requests)) + " Unique URLs Found\n")
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
		response_data = dict()
		# print([element_url, element_type, element_index])
		try:
			if self.arguments.web_username and self.arguments.web_password:
				response, page_source = self.base.get_response(url, str(self.arguments.web_username), str(self.arguments.web_password))
			else:
				response, page_source = self.base.get_response(url)
			
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
		return [url, response_data]
		# self.log[url][element_type][element_index] = element_data
