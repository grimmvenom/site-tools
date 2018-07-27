# -*- coding: utf-8 -*-

import argparse, sys, os
import getpass, re
import base64


def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', "-url", action='append', dest='url', help='-u <url> \thttp://<url> or https://<URL>')
	parser.add_argument('-f', "-file", action='store', dest='file', help=' -f <filepath.txt> \n.txt file to import a list of urls from. One URL per line. Include http:// or https://')
	parser.add_argument('-base', action='store', dest='base_url', help='-base "http://www.google.com" \nbase url to be prepended to urls without specified base url or don\'t start with http(s)://')
	parser.add_argument('-user', "-username", "-webuser", action='store', dest='web_username', help='--user <username> \nusername for website, you will be prompted for password')
	
	# Option to check url status
	parser.add_argument('-status', action='store_true', dest='status', help='-status \nto verify urls are available')
	# Scrape + Verify Options
	parser.add_argument("-scrape", action='store_true', dest='scrape', help='-scrape \nto scrape and build report of (links, images, form elements')
	parser.add_argument('-verify', action='store_true', dest='verify', help='-verify \nto verify scraped images and links')
	parser.add_argument('--limit', action='append', dest='limit', help='--limit <domain> \nto only check content with specified domain')
	parser.add_argument('--exclude', action='append', dest='exclude', help='--exclude <domain> \nSpecific domains to ignore content for')
	arguments = parser.parse_args()
	arguments.urls = list()
	
	print("\n")
	
	try:
		arguments.urls = list(arguments.url)
	except:
		pass
	
	if arguments.file:
		f = open(arguments.file, 'r')
		file_urls = f.read().splitlines(keepends=False)
		for url in file_urls:
			if len(url) > 2:
				arguments.urls.append(url)
	
	# If List of Urls is not at least 1, exit
	if len(arguments.urls) < 1:
		parser.error("You must specify a url with the (-u) flag or specify a .txt filepath with 1 url per line with the (-f) flag")
		exit()
		
	if arguments.base_url:
		if arguments.base_url.endswith("/"):
			arguments.base_url = arguments.base_url.replace('/', '', 1)[-1]
			if not arguments.base_url.startswith('http://') and not arguments.base_url.startswith('https://'):
				arguments.base_url = "http://" + arguments.base_url
		print("Base URL: " + str(arguments.base_url))
		for index, url in enumerate(arguments.urls):
			if not url.startswith(arguments.base_url):
				if not url.startswith('http://') and not url.startswith('https://'):
					if url.startswith("/"):
						url = arguments.base_url + url
					else:
						url = arguments.base_url + "/" + url
					arguments.urls[index] = url
	
	if arguments.status:  # If Status is defined, don't scrape and verify content on pages
		arguments.scrape = False
		arguments.verify = False
		
	# Ensure Scrape and Verify Flags work together
	if not arguments.scrape or arguments.verify:
		arguments.scrape = True
	elif arguments.verify:
		arguments.scrape = True
	
	if arguments.web_username:
		arguments.web_password = getpass.getpass('Please enter your authentication\'s Password: ')
	
	return arguments


# 	parser.add_argument('-db', "--database", action='store', dest='db',
# 	                    help='Determine Which database to lookup information in')
# 	parser.add_argument('-q', "--query", "--sql", action='store', dest='query',
# 	                    help='SQL Query to check the <project>_sitemap table in automation.db')
# 	# Extra Test Case Functionality for executing test cases mapped in table
# 	parser.add_argument('-hi', "--hubip", "--hubIP", action='store', dest='hubIP',
# 	                    help='IP of Selenium Hub Server. (ex: 10.128.194.170 (which is prod)')
# 	parser.add_argument('-b', "--browser", action='append', dest='browsers',
# 	                    help='Select Browsers to test in selenium. options: firefox, chrome, ie, standard3')
# 	parser.add_argument('-sc', "--svncreds", "--svncredentials", "--svncreds", action='store',
# 	                    dest='svncredentials', help='SVN Credentials (<username>:<password>). Required for executing Component Tests stored in SVN')
# 	# End of Extra Test Case Functionality
#
# 	if (arguments.db):
# 		try:
# 			arguments.db = get_resource(arguments.db)
# 		except FileNotFoundError as e:
# 			print(e)
#
# 	if arguments.query:
# 		if not arguments.db:
# 			parser.error("Must specify databse with -db flag if executing using a query (-q)")
# 		else:
# 			queried_urls = query_sitemap_db(arguments.db, arguments.query)
# 			for q_url in queried_urls:
# 				urls.append(q_url)
# 			# Set LIMIT in query
# 			limit_statement = re.search("LIMIT (\d+)", arguments.query)  # extract limit
# 			if limit_statement:  # if a limit statement is found
# 				limit = int(limit_statement.group(1))  # extract only the number
# 				if not limit <= 10:  # Replace Limit with 10 if it is > 10 in query
# 					print("Limit is > 10... Setting LIMIT to 10 in query")
# 					arguments.query = arguments.query.replace(limit_statement.group(0), "LIMIT 10")
# 			else:
# 				arguments.query = arguments.query.replace(";", " LIMIT 10;")
# 			queried_urls = query_sitemap_db(arguments.db, arguments.query)
# 			for q_url in queried_urls:
# 				urls.append(q_url)
# 	else:
# 		arguments.query = ""
#
# 	if not arguments.hubIP:
# 		arguments.hubIP = "10.128.194.170"
#
# 	if len(urls) <= 0:
# 		parser.error("Must specify urls. use the -u, -f, or -q parameters to specify a list of urls")
# 	else:
# 		arguments.urls = urls  # Overwrite Arguments.urls with urls list
#
# 	return arguments
