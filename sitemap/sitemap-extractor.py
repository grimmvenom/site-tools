#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:
Grimm Venom <grimmvenom@gmail.com>

Summary:
Python SiteMapping Tool to download a sites sitemap.xml
to do authenticated requests use -c <username>:<password>
to define sites do -s <url>

"""

import os, time, sys, json, ast
import requests, argparse, sqlite3
import xml.etree.ElementTree as ET
from StringIO import StringIO


# Global Variables
date = time.strftime("%m-%d-%y") # Date Format mm-dd-yyyy_Hour_Min
Time = time.strftime("%H_%M")
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
output_dir = current_dir + "/output/"

if not os.path.exists(output_dir):
	os.makedirs(output_dir)

# Define Arguments the Script will accept
parser = argparse.ArgumentParser()
parser.add_argument('-c', "--creds", "--credentials", action='store', dest='credentials', help='Site Credentials (<username>:<password>)')
parser.add_argument('-s', "--site", action='append', dest='site', required=True, help='http://<url> or https://<URL>')
arguments = parser.parse_args()
credentials = arguments.credentials # Credentials for request authentication <username>:<password>
if credentials:
	if len(credentials) > 0:
		print(" ")
		username = credentials.split(":", 1)[0]  # Username
		password = credentials.split(":", 1)[1]  # Password
		print("Username: " + username)
		print("Password: " + password)
else:
	credentials = ""
	username = ""
	password = ""

sites = arguments.site # List of URLs to get sitemap.xml from
files = arguments.file # List of Files to import as sitemap.xml

def clarify_domain(url, print_output=False):
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
	return domain, site_root, page_path, page, protocol


def download_sitemap(site_root):
	local_filename = output_dir + domain + "-sitemap.xml"
	request_url = protocol + domain + "/sitemap.xml"
	# NOTE the stream=True parameter
	r = requests.get(request_url, stream=True)
	if r.status_code != 404:
		print("Downloading Sitemap.xml")
		with open(local_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:  # filter out keep-alive new chunks
					f.write(chunk)
					# f.flush() commented by recommendation from J.F.Sebastian
	else:
		print("Sitemap.xml could NOT be found")
	return local_filename


# Execute Functions based on argument parameters
if len(sites) > 0:
	for url in sites:
		domain, site_root, page_path, page, protocol = clarify_domain(url)
		entries = " "
		download_sitemap(site_root)


