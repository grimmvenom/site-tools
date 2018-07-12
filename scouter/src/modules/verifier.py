
import json, multiprocessing, math, sys
from multiprocessing import Pipe
from src.base.base import Base


class Verify:

	def __init__(self, log, arguments):
		self.arguments = arguments
		self.log = log.copy()
		self.base = Base()

	def main(self):
		self._worker()
		return self.log

	def _worker(self):
		print("Verifying Links")
		request_list = list()
		for url_key in self.log.keys():  # Loop Through URL Keys
			for element_type in self.log[url_key].keys():  # Loop Through element type keys
				if not element_type.startswith(('ignored_', 'forms')):  # Ignore some keys
					for index, value in self.log[url_key][element_type].items():  # Append data to list
						request_list.append([url_key, element_type, index, value])
		#for item in request_list:
		#	print(item)
		with multiprocessing.Pool(processes=10) as pool:  # Start Multiprocessing pool
			results = pool.map(self._verify, request_list)
		# queue = dict(pair for d in results for pair in d.items())  # convert the returned list to dictionary
		# print(results)
		for result in results:
			# print(result)
			element_url = str(result[0])
			element_type = str(result[1])
			element_index = result[2]
			element_data = result[3]
			# print([element_url, element_type, element_index, element_data['target_url'], element_data['status']])
			self.log[element_url][element_type][element_index]['status'] = element_data['status']
			self.log[element_url][element_type][element_index]['message'] = element_data['message']

	def _verify(self, request):
		element_url = request[0]
		element_type = request[1]
		element_index = request[2]
		element_data = request[3]
		# print([element_url, element_type, element_index])
		url = request[3]['target_url']
		try:
			if self.arguments.web_username and self.arguments.web_password:
				response = self.base.get_response(url, str(self.arguments.web_username), str(self.arguments.web_password))
			else:
				response = self.base.get_response(url)
			
			element_data['status'] = response.status
			element_data['message'] = response.reason
			# print(json.dumps(self.log[fkey][skey], indent=4, separators=(",", ":")))
		except TimeoutError as e:
			element_data['status'] = 408
			element_data['message'] = str(e)
			
		except Exception as e:
			element_data['status'] = "ERROR"
			element_data['message'] = "Request Error"
			print("Error: \n" + str(e))
			print("\nFailure @: " + str(element_url) + ", " + str(element_type) + ", " + str(element_index))
			print("\n")
		# print([element_url, element_type, element_index, element_data])
		return [element_url, element_type, element_index, element_data]
		# self.log[url][element_type][element_index] = element_data
