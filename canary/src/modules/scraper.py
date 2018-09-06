# -*- coding: utf-8 -*-
"""
Summary:
		This Module Scrapes images, links, forms and the specified attributes for each element type
		results are returned in json / dictionary format
author:
grimm venom <grimmvenom@gmail.com>

"""

from bs4 import BeautifulSoup
from src.base.base import Base
from enum import Enum
import re, urllib3, multiprocessing, requests


class ScrapeRequirements(Enum):
	IMAGES = ["img"], ["src", "name", "class", "id", "value", 'title', 'alt', 'role', 'data-srcset']
	LINKS = ["a"], ["href",  "name", "class", "id", "type", "alt", "title", 'role']
	FORMS = ["input", 'textarea', 'select', 'button'], ["name", "class", "id", "type", "value", 'role']


class Scrape:
	def __init__(self, arguments):
		self.arguments = arguments
		self.urls = self.arguments.urls
		self.base = Base()
		self.scrape_results = dict()
		self.sorted_results = dict()
		self.scraped_total = 0
		self.session = requests.session()
		if self.arguments.web_username and self.arguments.web_password:
			print("Setting Auth with username: " + str(self.arguments.web_username))
			self.session.auth = (self.arguments.web_username, self.arguments.web_password)
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		manager = multiprocessing.Manager()

	def main(self):
		self._worker(self.urls)
		self._sort_dict()
		print("total scraped results: " + str(self.scraped_total) + "\n")
		return self.sorted_results

	def _worker(self, urls):
		element_results = dict()
		with multiprocessing.Pool(processes=10) as pool:  # Start Multiprocessing pool
			results = pool.map(self._scrape, urls)
			# queue = dict(pair for d in results for pair in d.items())  # convert the returned list to dictionary
		for result in results:
			for item in result:
				self.scraped_total += 1
				element_url = str(item['url'])
				element_type = str(item['elementType'])
				element_index = str(item['index'])
				element_data = item['data']
				element_data['htmlTag'] = str(item['htmlTag'])
			
				if element_url not in element_results:  # IF url as key not exist, create it
					element_results[element_url] = {}
				if element_type not in element_results[element_url]:  # If Element Type not exist, create it
					element_results[element_url][element_type] = {element_index: element_data}
				if element_index not in element_results[element_url][element_type]:  # If Element Results not exist, create it
					element_results[element_url][element_type][element_index] = element_data
			self.scrape_results = element_results  # Set Class Log to element_results dictionary
	
	def _scrape(self, url):
		results = list()
		manual = ('java', '#', 'data:')
		print("Scraping data from: " + str(url))
		response, page_source, self.session = self.base.session_get_response(self.session, url, True)
		soup = BeautifulSoup(page_source, 'html.parser')
		# print("URL: " + str(url))
		
		for index, type in enumerate(ScrapeRequirements):
			element_type = str(type).split(".", 1)[1].lower()
			# print("Checking " + str(element_type) + " on: " + str(url))
			element_tags = ScrapeRequirements[element_type.upper()].value[0]
			attributes = ScrapeRequirements[element_type.upper()].value[1]
			
			elements = list()
			for tag in element_tags:
					temp = soup.find_all(tag)
					for t in temp:
						elements.append({'tag': str(tag), 'value': t})
			
			# print(str(element_tags) + " tags found: " + str(len(elements)))
			# print(elements)
			for x, y in enumerate(elements):
				tag = elements[x]['tag']
				element = elements[x]['value']
				element_log = dict()
				for attribute in attributes:
					try:
						# print("scraping " + str(attribute))
						temp = element[attribute]
						if isinstance(temp, list):
							temp = temp[0]
						if attribute in ['href', 'src']:
							if temp.startswith("https://") or temp.startswith("http://"):
								element_log['target_url'] = temp
							elif temp.startswith("//"):
								element_log['target_url'] = self.base.get_protocol(url) + temp
							elif temp.startswith("/"):
								element_log['target_url'] = str(self.base.get_site_root(url)) + temp
							elif temp.startswith(manual):
								pass
							else:
								pass
							if element_log['target_url']:
								valid_url = self.base.detect_valid_url(element_log['target_url'])
								element_log['valid_url'] = valid_url
						element_log[str(attribute)] = str(temp)
					except:
						pass
				element_log['scraped_from'] = str(url)
				result = {'url': str(url),
						'elementType': str(element_type),
						'index': str(x),
						'htmlTag': str(tag),
						'data': element_log}
				if elements[x]['value'].content:
					content = str(element.content).replace("\\t", "").replace("\\r", "").replace("\\n", ",").strip()  # Remove encoded characters
					new_content = str(re.sub("\s{3,}", ",", content))  # Replace 3+ spaces with a comma
					try:
						string = self.base.unicode_to_ascii(new_content)
						result['data']['content'] = string
					except Exception as e:
						result['data']['content'] = new_content
						# print("Content Exception: " + str(e))
						pass
				if elements[x]['value'].text:
					text = str(element.text).replace("\\t", "").replace("\\r", "").replace("\\n", "").strip()  # Remove encoded characters
					new_text = str(re.sub("\s{3,}", ",", text))
					try:
						string = self.base.unicode_to_ascii(new_text)
						result['data']['text'] = string
					except Exception as e:
						result['data']['text'] = str(new_text)
						# print("Text Exception: " + str(e))
						pass
				
				# Domain URL Filters
				if self.arguments.limit:
					if 'target_url' in result['data']:
						target_domain = self.base.get_site_root(result['data']['target_url'])
						protocol = self.base.get_protocol(target_domain)
						# target_domain = target_domain.replace(protocol, '')
						if target_domain in self.arguments.limit:
							results.append(result)
					else:
						results.append(result)
				elif self.arguments.exclude:
					if 'target_url' in result['data']:
						target_domain = self.base.get_site_root(result['data']['target_url'])
						protocol = self.base.get_protocol(target_domain)
						# target_domain = target_domain.replace(protocol, '')
						if not target_domain in self.arguments.exclude:
							results.append(result)
							# print("Excluding link: " + str(result['data']['target_url']))
					else:
						results.append(result)
				else:
					results.append(result)
		return results
	
	def _sort_dict(self):
		# logger = self.base
		print("Sorting Scraped Results")
		verifiable = ['images', 'links']
		for url_key in self.scrape_results.keys():  # Sort Through URLs dictionary and organize it
			for et_key, et_value in self.scrape_results[url_key].items():  # Sort Through Element Types (images, links, forms, etc)
				ignored_count = 0
				x = 0
				if et_key not in verifiable:  # If not a link or image, skip and add to dictionary
					if url_key not in self.sorted_results:
						self.sorted_results[url_key] = {}
					self.sorted_results[url_key][et_key] = et_value
				else:
					for index, value in self.scrape_results[url_key][et_key].items():  # If Element Type is an image or link
						# print("\nKey: " + str(index) + ":\nValue: " + str(value))
						# If not a verifiable link, add to dictionary under ignored_<key>
						# if ('target_url' not in value) or ('href' in value.keys() and (value['href'].startswith(('java', '#', 'data')))) or \
						# 		('src' in value.keys() and value['src'].startswith(('data:'))):
						if 'target_url' not in value:
							ignored_count += 1
							# Add Item to Ignored Key in New Dictionary
							if url_key not in self.sorted_results:
								self.sorted_results[url_key] = {}
							if "ignored_" + str(et_key) not in self.sorted_results[url_key]:
								self.sorted_results[url_key]['ignored_' + str(et_key)] = {}
							if ignored_count not in self.sorted_results[url_key]['ignored_' + str(et_key)]:
								value['original_scraped_index'] = int(index)
								self.sorted_results[url_key]['ignored_' + str(et_key)][ignored_count] = value
						else:
							x += 1
							# Add Item to Ignored Key in New Dictionary
							if url_key not in self.sorted_results:
								self.sorted_results[url_key] = {}
							if str(et_key) not in self.sorted_results[url_key]:
								self.sorted_results[url_key][str(et_key)] = {}
							if x not in self.sorted_results[url_key][str(et_key)]:
								value['original_scraped_index'] = int(index)
								self.sorted_results[url_key][str(et_key)][x] = value
		# logger.write_log(self.sorted_results, 'verifiedInfo')
