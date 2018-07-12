import platform, os, sys, urllib3, re, sqlite3, time, json
import multiprocessing
import base64

class Base:
	
	def __init__(self):
		manager = multiprocessing.Manager()
		self.scouter_log = manager.dict()
		self.name = "Scouter"
		self.date = time.strftime("%Y-%m-%d")  # Date Format ISO 8601
		self.start = time.strftime("%I_%M")  # Time
		self.exec_time = str(time.strftime("%I_%M_%p"))  # Time
		self.log_dir = self.get_log_dir(self.name)
		self.timeout = 10

	def write_log(self, log: dict, filename=""):
		log_dir = self.get_log_dir(self.name)
		if not os.path.isdir(log_dir):
			os.makedirs(log_dir)
		if filename:
			file = log_dir + filename + "-" + self.date+"-"+self.exec_time+".json"
		else:
			file = log_dir + self.date + "-" + self.exec_time + ".json"
		print("Logging to: " + file)
		with open(file, 'w') as jsonfile:
			jsonfile.write(json.dumps(log, sort_keys=False, indent=4, separators=(',', ':')))
		jsonfile.close()

	def get_extension(self, file: str):
		return re.findall('(?i)(\.\w{2,4})', file)[-1]

	def log(self, the_dict: dict, first_log:dict):
		if len(self.scouter_log) <= 0:
			self.scouter_log = first_log.copy()
		main_keys = self.scouter_log.keys()
		for key, value in the_dict.items():
			if key in main_keys:
				mkeys = self.scouter_log[key].keys()
				for k,v in value.items():
					if k in mkeys:
						temp = self.scouter_log[key][k].keys()
						for x,y in v.items():
							if x in temp:
								pass
							else:
								self.scouter_log[key][k][x] = y
					else:
						self.scouter_log[key][k] = v
			else:
				self.scouter_log[key] = value

	def get_response(self, url, username="", password=""):
		pool = urllib3.PoolManager()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		if username and password:
			creds = username + ":" + password
			# creds = username + ":" + base64.b64encode(bytes(password, 'utf-8'))
			headers = urllib3.make_headers(basic_auth=creds)
			response = pool.urlopen('HEAD', url, headers=headers, timeout=self.timeout)
		else:
			response = pool.urlopen('HEAD', url, timeout=self.timeout)
		return response

	def get_source(self, url, username="", password=""):
		print("Requesting: " + str(url))
		pool = urllib3.PoolManager()
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		if username and password:
			creds = username + ":" + password
			# creds = username + ":" + base64.b64encode(bytes(password, 'utf-8'))
			headers = urllib3.make_headers(basic_auth=creds)
			response = pool.urlopen('GET', url, headers=headers, timeout=self.timeout)
		else:
			response = pool.urlopen('GET', url, timeout=self.timeout)
			
		# print(response.data)
		return str(response.data)

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

	def get_log_dir(self, application):
		return os.environ['USERPROFILE'] + '\\Documents\\' + str(
			application) + '\\Results\\' if platform.system() == 'Windows' else os.path.expanduser(
			"~/Documents/" + application + "/Results/")

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

