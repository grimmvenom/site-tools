#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:
Grimm Venom (grimmvenom@gmail.com)

Summary:
Python URL status Tool to get status of http and https requests
and generate an HTML report
"""

import os, time, sys, requests, platform, argparse, re, random
from multiprocessing import Pool, Process, Queue
import multiprocessing as mp
import sqlite3
import unicodedata
from collections import OrderedDict
from lxml.html import fromstring


# Global Variables
date = time.strftime("%m-%d") # Date Format mm-dd-yyyy_Hour_Min
Time = time.strftime("%H_%M") # Time
report_time = time.strftime("%I_%M_%p")
sys_time = time.strftime("%I_%M_%p")
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir)) # Get Parent of Current Directory of Script
log_dir = current_dir + "/logs"
output_dir = current_dir + "/output"
output = output_dir + "/URL-Status-" + date + "_" + report_time + ".html"
if sys.platform.lower == "windows" or sys.platform.lower == "win32":
	current_dir = current_dir.replace("/", '\\')
	parent_dir = parent_dir.replace("/", '\\')
	log_dir = log_dir.replace("/", '\\')
	output_dir = output_dir.replace("/", "\\")
	output = output.replace("/", "\\")

if not os.path.exists(output_dir): # Check if output directory does not exist
	os.makedirs(output_dir) # Create output directory

timeout=30
# HTML Color Codes
platinum = "#E5E4E2"
green = "#81F781"
yellow = "#D0FA58"
orange = "#FE9A2E"
red = "#FE2E2E"
status_code_colors = {"200": green, "300": yellow, "301": yellow, "302": yellow, "400": orange, "401": yellow, "403": yellow, "404": red, "Connection Issue": red}
status_code_messages = {"200": "", "300": "Redirect", "301": "Site has moved", "302": "Redirect",
						"400": "Bad Request", "401": "Unauthorized", "403": "Forbidden", "404": "Not Found",
						"Connection Issue": "Connection Issue When Testing. Check Manually"}


def log_output():
	if not os.path.exists(log_dir):  # Check if logs directory does not exist
		os.makedirs(log_dir)  # Create logs directory
	pylog = log_dir + "/" + "url-status-check-" + date + "_" + Time + ".txt"
	if sys.platform.lower == "windows" or sys.platform.lower == "win32":
		pylog = pylog.replace("/", '\\')
	# Define Standard Output
	# sys.stdout = open(pylog, 'w')
	class Tee(object):
		def __init__(self, *files):
			self.files = files

		def write(self, obj):
			for f in self.files:
				f.write(obj)
				f.flush()  # If you want the output to be visible immediately

		def flush(self):
			for f in self.files:
				f.flush()

	pyout = open(pylog, 'w')
	# original = sys.stdout
	sys.stdout = Tee(sys.stdout, pyout)


def query_db(db, query): # Query Components DB for list of components and identifiers
	queried_urls = []
	conn = sqlite3.connect(db)
	cur = conn.cursor()
	print("Querying " + db + " using the following query")
	print(query)
	print(" ")
	cur.execute(query)
	data = cur.fetchall()
	#print(data)

	if data:
		for row in cur.execute(str(query)):
			q_url = str(row[0])
			#print(q_url)
			queried_urls.append(q_url)
	else:
		print("No Results Found. Please find a valid database or update your query")
		exit()

	return queried_urls


def build_url(arguments, url):
	if arguments.base_url:
		if not url.startswith(arguments.base_url) and not url.startswith("/"):
			url = str(arguments.base_url) + "/" + str(url)
		elif not url.startswith(arguments.base_url) and url.startswith("/"):
			url = str(arguments.base_url) + str(url)
		else:
			url = url
	else:
		if not url.startswith('http://') and not url.startswith('https://'):
			url = "http://" + str(url)
		else:
			url = url
	if url.endswith(" "):
		url = url.replace(" ", '', -1)
	return url


def get_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', "--url", action='append', dest='urls', help=' -u <http:// or https://url>')
	parser.add_argument('-f', "--file", action='append', dest='files', help='-f <filepath>.txt file to import a list of urls from. One URL per line. Include http:// or https://')
	parser.add_argument('-db', "--database", action='store', dest='db', help='Determine Which database to lookup information in')
	parser.add_argument('-q', "--query", "--sql", action='store', dest='query', help='SQL Query to check the <project>_sitemap table in automation.db')
	parser.add_argument('-wc', "--auth","--webcreds", "--webcredentials", "--webcreds", action='store', dest='webcredentials', help='Site Credentials (<username>:<password>)')
	parser.add_argument('-base', "--base", action='store', dest='base_url', help='base url of all urls')

	arguments = parser.parse_args()

	urls = []

	if arguments.webcredentials:
		arguments.web_username = arguments.webcredentials.split(":", 1)[0]  # Website Username
		arguments.web_password = arguments.webcredentials.split(":", 1)[1]  # Website Password
	else:
		arguments.web_username = ""
		arguments.web_password = ""

	if not (arguments.files or arguments.urls or arguments.query):
		parser.error('No action requested, add -u <url> or -q <sql query> or -f <file>')
		exit()

	if arguments.base_url:
		if arguments.base_url.endswith("/"):
			arguments.base_url = arguments.base_url.replace('/', '', 1)[-1]
			if not arguments.base_url.startswith('http://') and not arguments.base_url.startswith('https://'):
				arguments.base_url = "http://" + arguments.base_url
		print("Base URL: " + str(arguments.base_url))

	if arguments.files:
		print("files: " + str(arguments.files))
		for file in arguments.files:
			with open(file, 'r') as f:
				file_urls = f.readlines()
				file_urls = [s.replace('\r', '').replace('\n', '') for s in file_urls]  # remove all the 8s
			for file_url in file_urls:  # Convert from list to string and append to url list
				url = build_url(arguments, file_url)
				urls.append(url)

	if arguments.urls:
		# print("urls: " + str(arguments.urls))
		for url in arguments.urls: # Convert from list to string and append to url list
			url = build_url(arguments, url)
			urls.append(url)

	if arguments.query:
		if not arguments.db:
			print("Must specify databse with -db flag if executing using a query (-q)")
			exit()
		else:
			if os.path.exists(current_dir + "/" + arguments.db):
				db = current_dir + "/" + arguments.db
				print(str(arguments.db) + " Found in current Directory")
				queried_urls = query_db(arguments.db, arguments.query)
				for q_url in queried_urls:
					url = build_url(arguments, q_url)
					urls.append(url)
			elif os.path.exists(parent_dir + "/database/" + arguments.db):
				print("Database found in " + str(parent_dir) + "/database/" + str(arguments.db))
				db = parent_dir + "/database/" + arguments.db

			else:
				print(str(arguments.db) + " could not be found")
				db = ""
				exit()
			queried_urls = query_db(db, arguments.query)
			for q_url in queried_urls:
				url = build_url(arguments, q_url)
				urls.append(url)

	arguments.urls = urls

	return arguments


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


def html_header():
	print("Starting HTML Report \n")
	html_file.write("<!DOCTYPE html><html><title>URL-Status Report</title><body>")
	html_file.write("<h1>URL Status Report - " + date + " - " + str(sys_time) + "</h1>")
	html_file.write("<br>")
	table = '<table>\n<tr bgcolor="#848482">\n' + \
			'<td><h2 style="color:white" align=center>#</h2></td>\n' + \
			'<td><h2 style="color:white" align=center>URL</h2></td>\n' + \
			'<td><h2 style="color:white" align=center>Page Title</h2></td>\n' + \
			'<td><h2 style="color:white" align=center>Status Code</h2></td>\n' + \
			'<td><h2 style="color:white" align=center>Redirected URL</h2></td>\n' + \
			'<td><h2 style="color:white" align=center>Message</h2></td></tr>\n'
	html_file.write(table)


def request_url(urlinfo):
	response_queue = {}
	count = str(urlinfo[0])
	url = str(urlinfo[1]).replace("\n", "")
	try:
		response = requests.get(url, stream=True, timeout=timeout)
		#response = requests.get(link_url, stream=True,timeout=timeout)
		if response.history:
			status_code = str(response.history[0].status_code)
			redirected_url = response.url
			response = requests.get(redirected_url, stream=True, timeout=timeout)
			# response = requests.get(redirected_url, stream=True, timeout=timeout)
		else:
			status_code = str(response.status_code)
			redirected_url = ""

	except requests.exceptions.RequestException as e:  ##(ConnectionRefusedError, ConnectionAbortedError, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
		print("connection Issue: " + str(e))
		response = "Connection Issue"
		status_code = "Connection Issue"
		redirected_url = ""
		pass

	if response != "Connection Issue":
		try:
			message = str(status_code_messages[str(status_code)])  # Set Message based on Link Status
			color = str(status_code_colors[str(status_code)])  # Set HTML Color
			tree = fromstring(response.content)
			page_title = striphtml(str(tree.findtext('.//title')))
			page_title = str(page_title)
			page_title = page_title.replace("\n", "")
		except:
			message = "Not Common Status Code. Lookup Online"
			color = red
			page_title = "N/A"
			pass

		# print("Page Title: " + page_title)
		link_src = str(url)
		# print(str(count) + ") - " + url + " : " + str(status_code) + " (" + message + ") -> " + redirected_url + "\n")
		response_queue[str(count)] = {"url": str(url),
									  "statusCode": str(status_code),
		                              "redirectedURL": str(redirected_url),
		                              "pageTitle": unicodedata.normalize('NFKD', str(page_title)).encode('ascii','ignore').decode('utf-8'),
		                              "color": str(color),
		                              "message": str(message)}
	else:
		response_queue[str(count)] = {"url": str(url),
		                              "statusCode": "N/A",
		                              "redirectedURL": "",
		                              "pageTitle": "N/A",
		                              "color": str(red),
		                              "message": "Connection Issue"}

	print(str(count) + ") - " + str(response_queue[str(count)]['url']) + " : " + str(response_queue[str(count)]['statusCode']) +
	      " (" + str(response_queue[str(count)]['message']) + ") -> " + str(response_queue[str(count)]['redirectedURL']) + "\n")
	return response_queue


def write_output(queue):
		for key, value in queue.items():
			# print("Count: " + str(key) + " Value: " + str(value))
			count = key
			url = str(value['url'])
			page_title  = str(value['pageTitle'])
			status_code = str(value['statusCode'])
			color = str(value['color'])
			redirected_url = str(value['redirectedURL'])
			message = str(value['message'])

			print(value)

			# Write to HTML Report
			try:
				row = '<tr><td bgcolor="' + platinum + '">' + str(count) + '</td>\n' + \
					  '<td bgcolor="' + platinum + '"><a href="' + url + '">' + url + '</a></td>\n' + \
					  '<td bgcolor="' + platinum + '">' + page_title + '</td>\n'

				if len(redirected_url) <= 0:
					row = row + '<td bgcolor="' + color + '">' + str(status_code) + '</td>\n' + \
						  '<td bgcolor="' + color + '"></td>'
				else:
					row = row + '<td bgcolor="' + color + '"><a href="' + redirected_url + '">' + str(
						status_code) + '</a></td>\n' + \
						  '<td bgcolor="' + color + '"><a href="' + url + '">' + str(redirected_url) + '</td>\n'

				row = row + '<td bgcolor="' + color + '">' + message + "</td>\n</tr>\n"
				# print(row)
				# row = row.encode('utf-8', 'ignore')
				html_file.write(row)  # Write row to table
			except UnicodeDecodeError as e:
				print("Unicode Error!!!!!")
				print(str(e))
				pass


def html_footer():
	html_file.write("</table></body></html>")
	html_file.close()


if __name__ == '__main__':
	mp.freeze_support()

	log_output() # Start Logging STDOUT

	arguments = get_arguments() # Get CMDLINE arguments

	html_file = open(output, 'w')
	html_header()

	ignored_links = []
	count = 0
	start = time.time()
	print("url Count: " + str(len(arguments.urls)))
	print(str(arguments.urls))
	print("=============================== \n")

	urls = []
	response_queue = {}
	for index, url in enumerate(arguments.urls):
		urls.append([str(index), str(url)])
	with Pool(processes=10) as pool:
		response_queue = pool.map(request_url, iter(urls))
		# print(response_queue)
	queue = dict(pair for d in response_queue for pair in d.items()) # convert the returned list to dictionary
	queue = OrderedDict(sorted(queue.items(), key=lambda t: int(t[0]))) # sort dictionary keys by integer

	write_output(queue)
	html_footer()
	runtime = str('{:.2f}'.format(time.time() - start))
	print("Total Execution Time: " + runtime)