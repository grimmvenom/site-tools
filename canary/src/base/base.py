# -*- coding: utf-8 -*-
"""
Summary:
		This Module Contains base methods for functionality
author:
grimm venom <grimmvenom@gmail.com>

"""

import platform, os, sys, re, sqlite3, time, json, requests
import urllib.parse
import multiprocessing
from bs4 import BeautifulSoup
from http.client import responses
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class Base:
	def __init__(self):
		manager = multiprocessing.Manager()
		self.canary_log = manager.dict()
		self.date = time.strftime("%Y-%m-%d")  # Date Format ISO 8601
		self.start = time.strftime("%I_%M")  # Time
		self.exec_time = str(time.strftime("%I_%M_%p"))  # Time
		self.log_dir = self.get_log_dir()
		self.timeout = 10

	def write_log(self, log: dict, filename=""):
		if not os.path.isdir(self.log_dir):
			os.makedirs(self.log_dir)
		if filename:
			file = self.log_dir + filename + "-" + self.date+"-"+self.exec_time+".json"
		else:
			file = self.log_dir + self.date + "-" + self.exec_time + ".json"
		print("Logging to: " + file)
		with open(file, 'w') as jsonfile:
			jsonfile.write(json.dumps(log, sort_keys=False, indent=4, separators=(',', ':')))
		jsonfile.close()

	def get_extension(self, file: str):
		return re.findall('(?i)(\.\w{2,4})', file)[-1]

	def log(self, the_dict: dict, first_log:dict):
		if len(self.canary_log) <= 0:
			self.canary_log = first_log.copy()
		main_keys = self.canary_log.keys()
		for key, value in the_dict.items():
			if key in main_keys:
				mkeys = self.canary_log[key].keys()
				for k,v in value.items():
					if k in mkeys:
						temp = self.canary_log[key][k].keys()
						for x,y in v.items():
							if x in temp:
								pass
							else:
								self.canary_log[key][k][x] = y
					else:
						self.canary_log[key][k] = v
			else:
				self.canary_log[key] = value

	def get_response(self, url, source=False, username="", password=""):
		# print("Requesting: " + str(url))
		request_response = {}
		try:
			if username and password:
				# Perform Get Request of url with authentication to gather info
				response = requests.get(url, auth=(username, password), stream=True, allow_redirects=True, timeout=self.timeout)
			else:
				response = requests.get(url, stream=True, allow_redirects=True, timeout=self.timeout)
			
			if response.history:
				request_response["status"] = str(response.history[0].status_code)
				request_response["message"] = str(responses[int(request_response["status"])])  # Set Message based on Link Status
				request_response["redirectedURL"] = str(response.url)
			else:
				request_response["status"] = response.status_code
				request_response["message"] = str(responses[int(request_response["status"])])  # Set Message based on Link Status
			
			page_source = str(response.content)
			
			try:
				html = BeautifulSoup(page_source, 'html.parser')
				page_title = html.title.text
				page_title = urllib.parse.unquote(page_title)  # Decode text in url format
				page_title = self.unicodetoascii(page_title)  # Decode unicode to ascii
				request_response["pageTitle"] = str(page_title)
			except:
				request_response["pageTitle"] = ""
		
		except requests.exceptions.Timeout as e:
			request_response['status'] = 408
			request_response['message'] = str(e)
			request_response['pageTitle'] = "N/A"
			page_source = ""
		if source:
			return request_response, page_source
		else:
			return request_response

	def get_protocol(self, url):
		return re.findall('(?i)(https?:)', url)[0]

	def get_site_root(self, url):
		return re.findall('(?i)(.+?://\w+.\w+.\w+)', url)[0]

	def query_sitemap_db(self, db, query):  # Query Components DB for list of components and identifiers
		queried_urls = []
		conn = sqlite3.connect(db)
		cur = conn.cursor()
		print("Querying " + db + " using the following query")
		print(query)
		print(" ")
		cur.execute(query)
		data = cur.fetchall()
		# print(data)

		if data:
			for row in cur.execute(str(query)):
				q_url = str(row[0])
				# print(q_url)
				queried_urls.append(q_url)
		else:
			print("No Results Found. Please find a valid database or update your query")
			exit()
		return queried_urls

	def get_log_dir(self):
		# determine if application is a script file or frozen exe
		if getattr(sys, 'frozen', False):
			current_dir = os.path.dirname(sys.executable)
			log_dir = current_dir + "/Results/"
		elif __file__:
			current_dir = os.path.dirname(__file__)
			parent_dir = os.path.abspath(
				os.path.join(current_dir, os.pardir))  # Get Parent of Current Directory of Script
			parent_parent_dir = os.path.abspath(
				os.path.join(parent_dir, os.pardir))  # Get Parent of Current Directory of Script
			log_dir = parent_parent_dir + "/Results/"
		else:
			current_dir = os.path.dirname(os.path.realpath(__file__))  # Get Current Directory of Running Script
			parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))  # Get Parent of Current Directory of Script
			parent_parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))  # Get Parent of Current Directory of Script
			log_dir = parent_parent_dir + "/Results/"
		if platform.system() == 'Windows':
			log_dir = log_dir.replace("/", "\\")
		return log_dir
		#  Deprecated old directory based on user home directories
		# return os.environ['USERPROFILE'] + '\\Documents\\' + str(
		# 	application) + '\\Results\\' if platform.system() == 'Windows' else os.path.expanduser(
		# 	"~/Documents/" + application + "/Results/")

	def get_resource(self, relative_path):
		""" Get absolute path to resource, works for dev and for PyInstaller """
		try:
			# PyInstaller creates a temp folder and stores path in _MEIPASS
			basePath = sys._MEIPASS
		# check if _meipass is equal to the documents path,
		# if it is equal use os.path.abspath('.')
		except Exception:
			basePath = os.path.abspath(".")

		return os.path.join(basePath, relative_path)

	def mkdir(self, dir):
		if not os.path.exists(dir):  # Check if logs directory does not exist
			os.makedirs(dir)  # Create logs directory
			print("Successfully create: " + dir)
		else:
			print("Directory already exists.")

	def unicodetoascii(self, string):
		# print("Replacing Characters")
		uni2ascii = {
			'\\xc2\\xae': '®',
			'\\u00ae': '®',
			'\\xe2\\x80\\x99': "'",
			'\\xe2\\x80\\x9c': '"',
			'\\xe2\\x80\\x9d': '"',
			'\\xe2\\x80\\x9e': '"',
			'\\xe2\\x80\\x9f': '"',
			'\\xc3\\xa9': 'e',
			'\\xe2\\x80\\x93': '-',
			'\\xe2\\x80\\x92': '-',
			'\\xe2\\x80\\x94': '-',
			'\\xe2\\x80\\x98': "'",
			'\\xe2\\x80\\x9b': "'",
			'\\xe2\\x80\\x90': '-',
			'\\xe2\\x80\\x91': '-',
			'\\xe2\\x80\\xb2': "'",
			'\\xe2\\x80\\xb3': "'",
			'\\xe2\\x80\\xb4': "'",
			'\\xe2\\x80\\xb5': "'",
			'\\xe2\\x80\\xb6': "'",
			'\\xe2\\x80\\xb7': "'",
			'\\xe2\\x81\\xba': "+",
			'\\xe2\\x81\\xbb': "-",
			'\\xe2\\x81\\xbc': "=",
			'\\xe2\\x81\\xbd': "(",
			'\\xe2\\x81\\xbe': ")",
			'\\xe2\\x80\\x8e': '',
		}
		for uni, char in uni2ascii.items():
			string = string.replace(uni, char)
		return string

	def detect_valid_url(self, string):
		regex = re.compile(
			r'^(?:http|ftp)s?://'  # http:// or https://
			r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
			r'localhost|'  # localhost...
			r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
			r'(?::\d+)?'  # optional port
			r'(?:/?|[/?]\S+)$', re.IGNORECASE)
		
		if re.match(regex, string) is not None:
			result = True
		else:
			result = "Malformed"
		return result