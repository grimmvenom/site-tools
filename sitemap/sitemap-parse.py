#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:
Grimm Venom <grimmvenom@gmail.com>

Summary:
Python tool to parse sitemap.xml files and add to DB and write organized xml output
Example:  python3 ./sitemap-parse.py -f Enterprise-Prod-sitemap.xml -db Enterprise.db -table Enterprise_Prod

"""

import os, time, sys, json, ast, datetime
import requests, argparse, sqlite3
import xml.etree.ElementTree as ET
from operator import itemgetter


def log_output(output_name):
	log_dir = current_dir + "/logs"
	if not os.path.exists(log_dir):  # Check if logs directory does not exist
		os.makedirs(log_dir)  # Create logs directory
	pylog = log_dir + "/" + output_name
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


def get_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', "-file", action='append', dest='files', required=True, help='Enter Input .xml file to parse and sort')
	parser.add_argument('-db', "-database", action='store', dest='database', required=True, help='Enter Database File to write information to. Typically <vendor>.db')
	parser.add_argument('-t', "-table", "-p", "-project", action='store', dest='table', required=True, help='Enter table name (<project>_<Environment>). Typically <applicationName>_<env>')
	arguments = parser.parse_args() # Parse through arguments added when the script is called
	
	if not arguments.database.endswith(".db"):
		arguments.database = arguments.database + ".db"
		
	if not os.path.exists(arguments.database):
		if os.path.exists(parent_dir + "/database/" + arguments.database.capitalize()):
			arguments.database = parent_dir + "/database/" + arguments.database
		else:
			arguments.database =  current_dir + "/database/" + arguments.database.capitalize()
			if not os.path.exists(os.path.dirname(os.path.realpath(arguments.database))):
				print("Creating Database Directory")
				os.makedirs(os.path.dirname(os.path.realpath(arguments.database)))
			
	if not arguments.table.endswith("_sitemap"):
		arguments.table = arguments.table + "_sitemap"
	arguments.table = arguments.table.replace('.', '_')
	return arguments


def clarify_domain(file, print_output=False):
	it = ET.iterparse(file)
	for _, el in it:
		if '}' in el.tag:
			el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
	root = it.root

	# Get Domain from Sitemap.xml
	info = root.findall('.//url')[0]
	url = info.find('.//loc').text

	if not url.endswith("/"):
		url = url + "/"
	# Determine Protocol being used for URL
	if url.startswith("http://"):
		protocol = 'http'
	elif url.startswith("https://"):
		protocol = 'https'
	else:
		protocol = 'http'

	site = url.replace(protocol + "://", "") # Remove Protocol to determine domain name
	if "/" in site:
		domain = site.split("/", 1)[0] # Get Site Domain before the "/" in url
		# if site[-1] == '/': site = site[:-1]  # Remove Last character if it is a '/'
		page_path = site.split("/", 1)[-1]# Get the Pages in url after the first "/"
		if (len(page_path) <= 1) or (page_path == domain):
			page_path = "/"
			page = "/"
		else:
			page = page_path.split("/", 1)
			try:
				page.remove("")
			except:
				pass
			page = page[-1]
			page = page.replace("/", "")

	else:
		domain = site
		page_path = "/"
		page = "/"

	if not page_path.startswith("/"):
		page_path = "/" + page_path

	protocol = protocol + "://"
	site_root = protocol + domain

	if print_output == True:
		print(" ")
		print("URL: " + url)
		print("Protocol: " + protocol.strip("://"))
		print("Domain: " + domain)
		print("Page Path: " + page_path)
		print("Page: " + str(page))
		print("Site Root: " + site_root)
		print(" ")
	return domain, site_root, page_path, page


def parse_sitemap(file):
	print("Reading Sitemap from: " + file)
	it = ET.iterparse(file)
	for _, el in it:
		if '}' in el.tag:
			el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
	root = it.root

	# Loop through all entries in sitemap.xml file
	for info in root.findall('.//url'): # Test limited [0:6]
		xml_url = info.find('.//loc').text
		try:
			last_mod = info.find('.//lastmod').text
		except:
			last_mod = str(date)
			pass
		try:
			if "T" in last_mod: # If loastmod == date+time
				last_mod = last_mod.split("T", 1)[0] # Strip the Time out
		except:
			pass

		#print("url: " + xml_url)
		#print("Last Modified: " + last_mod)
		#print(" ")
		entries.append([xml_url, last_mod])

	print(" ")

	sorted_entries = sorted(entries, key=itemgetter(0)) # Sort List alphabetically

	return sorted_entries


def manage_sitemap_db():
	print(" ")
	print("Checking for db: " + arguments.database)
	print("Checking Table: " + arguments.table)
	con = sqlite3.connect(arguments.database)
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS " + arguments.table + "(url TEXT, last_modified TEXT, appended TEXT)")
		for index, entry in enumerate(entries):
			url = str(entry[0])
			last_mod = str(entry[1])
			appended = str(date)
			cur.execute("SELECT url,last_modified FROM " + arguments.table + " WHERE url = ?", (url,))
			data = cur.fetchone()

			if data is None:
				print(str(index) + ") - entry: " + str(entry) + " -- Not Found in DB")
				print(entries[index])
				print(str(data))
				# print('There is no url found for:  %s' % url)
				try:
					cur.execute("insert into " + arguments.table + "  values(?,?,?)", (url, last_mod, appended,))
				except:
					print("Issue Writing Entry to DB")
					pass
				print(" ")

			elif str(data[1]) != str(last_mod):
				print(str(index) + ") - entry: " + str(entry) + " -- Last Modified Dates don't match")
				print(entries[index])
				print(str(data))
				print("data[1]: " + str(data[1] + " last_mod: " + str(last_mod)))
				#print("Updating Last Modified Date")
				try:
					cur.execute("update " + arguments.table + " set last_modified=? , appended=?", (last_mod, appended))
				except:
					print("Issue Updating Entry in DB")
					pass
			else:
				print(str(index) + ") - entry: " + str(entry) + " -- Exists in DB")
				print(" ")
		print(" ")
		#con.executemany('insert into ' + table_name + '(url, last_modified) values (?, ?)', entries)
	con.commit()
	con.close()


# Global Variables
date = time.strftime("%m-%d-%y") # Date Format mm-dd-yyyy_Hour_Min
Time = time.strftime("%H_%M")
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
output_dir = current_dir + "/output/"

arguments = get_arguments()
log_output("Sitemap-parser-" + str(date) + "_" + str(Time))


print("Database: " + str(arguments.database))
print("Table: " + str(arguments.table))
print("Files: " + str(arguments.files))
print(" ")

if len(arguments.files) > 0:
	for file in arguments.files:
		print("Checking " + file)
		file = output_dir + file
		entries = []
		domain, site_root, page_path, page = clarify_domain(file)  # extract domain from sitemap
		entries = parse_sitemap(file)  # Sitemap extract urls and last modified
		manage_sitemap_db()  # Sitemap create DB


