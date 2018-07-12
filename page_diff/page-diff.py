#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:
Grimm Venom <grimmvenom@gmail.com>

Summary:
Perform GET Requests and compare page_sources
Compare new requests to old cached requests

"""

import os, time, sys, datetime, requests, re, difflib, urllib3
from lxml.html import fromstring
from bs4 import BeautifulSoup

# Global Variables
date = time.strftime("%m-%d-%y") # Date Format mm-dd-yyyy_Hour_Min
Time = time.strftime("%H_%M") # Time
current_dir = os.path.dirname(os.path.realpath(__file__)) # Get Current Directory of Running Script
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir)) # Get Parent of Current Directory of Script
workspace_dir = current_dir + "/workspace"
cache_dir = current_dir + "/cache" # Define output directory
timeout = 15
status_code_messages = {"200": "", "300": "Redirect", "301": "Site has moved", "302": "Redirect",
						"400": "Bad Request", "401": "Unauthorized", "403": "Forbidden", "404": "Not Found",
						"Connection Issue": "Connection Issue When Testing. Check Manually"}

if not os.path.exists(cache_dir):  # Check if logs directory does not exist
	os.makedirs(cache_dir)  # Create logs directory


def log_output(log_name):
	log_dir = current_dir + "/logs"
	if not os.path.exists(log_dir):  # Check if logs directory does not exist
		os.makedirs(log_dir)  # Create logs directory
	pylog = log_dir + "/" + log_name + ".txt"
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
	return pylog


def read_input_file(input_file):
	# Read File and build list
	f = open(input_file, 'r+')
	for line in f.readlines():
		line = line.replace("\n", "")
		urls = line.split(',')
		# print(urls)
		total_urls.append(urls)


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


def Basic_Request(url, print_output=False):
	request_response = {}
	try:

		response = requests.get(url, stream=True, timeout=timeout)

		if response.history:
			request_response["statusCode"] = str(response.history[0].status_code)
			request_response["redirectedURL"] = str(response.url)

			response = requests.get(request_response["redirectedURL"], stream=True, timeout=timeout)

		else:
			request_response["statusCode"] = str(response.status_code)
			request_response["redirectedURL"] = ""

		try:
			request_response["message"] = status_code_messages[str(request_response["statusCode"])]  # Set Message based on Link Status
		except:
			request_response["message"] = ""
		try:
			tree = fromstring(response.content)
			page_title = striphtml(str(tree.findtext('.//title')))
			page_title = str(page_title)
			page_title = str(page_title.replace("\n", ""))
			request_response["pageTitle"] = str(page_title)
			page_source = str(response.content)
		except:
			request_response["pageTitle"] = ""
			page_source = ""
			pass
	except requests.exceptions.RequestException as e:##(ConnectionRefusedError, ConnectionAbortedError, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
		print("connection Issue: " + str(e))
		print(" ")
		request_response["statusCode"] = "Connection Issue"
		request_response["redirectedURL"] = ""
		request_response["pageTitle"] = ""
		request_response["message"] = "Connection Issue"
		page_source = "N/A"
		pass

	if print_output == True:
		print(request_response)

	return request_response, page_source


def compare(source1, source2):
	add_count = 0
	removed_count = 0
	new = []
	removed = []
	d = difflib.Differ()
	diff = d.compare(source1, source2)
	for line in diff:
		if len(diff) > 0:
			if line.startswith('+'):
				add_count += 1
				line = line.replace("+", "")
				new += line + "\n"
			elif line.startswith('- '):
				removed_count += 1
				line = line.replace("-", "")
				removed += line + "\n"
	print("+ Lines Unique to Latest Version: " + str(add_count))
	print("-----------------------")
	print(''.join(new))
	print(" ")
	print("- Lines Unique to cached version: " + str(removed_count))
	print("-----------------------")
	print(''.join(removed))
	print(" ")


total_urls = []
counter = 0

log_name= "Page-Diff-" + str(date) + "_" + str(Time)
log_output(log_name)

read_input_file("test.csv") # Read input file and get a list of urls to compare

# Loop Through URLs
for urls in total_urls:
	counter += 1
	url1 = urls[0]
	url1_file = cache_dir + "/" + str(counter) + "_a.txt"
	url2 = urls[1]
	url2_file = cache_dir + "/" + str(counter) + "_b.txt"
	print(" ")
	print("Count: " + str(counter))
	# print("Count: " + str(counter) + "\n" + url1 + "\n" + url2 + "\n")

	# http = urllib3.PoolManager()
	# r1 = http.request('get', url1)
	# print(url1 + " Status: " + str(r1.status))
	# r2 = http.request('get', url2)
	# print(url2 + " Status: " + str(r2.status))

	url1_response, url1_page_source = Basic_Request(url1)
	print(url1 + " Status: " + str(url1_response["statusCode"]))

	url2_response, url2_page_source = Basic_Request(url2)
	print(url2 + " Status: " + str(url2_response["statusCode"]))

	soup1= BeautifulSoup(str(url1_page_source), 'html.parser', from_encoding="utf8")
	page_source1 = str(soup1.prettify())
	soup2 = BeautifulSoup(str(url2_page_source), 'html.parser', from_encoding="utf8")
	page_source2 = str(soup2.prettify())
	with open(url1_file, 'w') as file1:
		file1.write(str(page_source1))
	with open(url2_file, 'w') as file2:
		file2.write(str(page_source2))

	compare(page_source1, page_source2)

	print("================================")
