# -*- coding: utf-8 -*-


import platform, os, sys, re, time, json, csv
from src.base.base import Base


class Parse_TSV:
	def __init__(self, arguments):
		self.arguments = arguments
		self.date = time.strftime("%Y-%m-%d")  # Date Format ISO 8601
		self.start = time.strftime("%I_%M")  # Time
		self.exec_time = str(time.strftime("%I_%M_%p"))  # Time
		self.base = Base()
		self.log_dir = self.base.get_log_dir()
		self.main()
		
	def main(self):
		if not os.path.isdir(self.log_dir):
			os.makedirs(self.log_dir)
		
	def retrieve_headers(self, test_dict: dict, name_var=''):
		for element in test_dict:
			if isinstance(test_dict[element], dict):
				self.retrieve_headers(test_dict[element], name_var + '||' + element)
			else:
				header_dict[name_var + '||' + element] = test_dict[element]
		# output_file = open(report_path, 'w')
		# csv_writer = csv.writer(output_file, delimiter='\t', quotechar='"')
		# # csv_writer = uniccsv.writer(output_file, delimiter=',', quotechar='"')
		
		# records = []
		# header_list = []
		#
		# for record in json_results.items():
		# 	records.append(record)
		# print("Records count: " + str(len(records)))
		#
		# for key, item in json_results.items():
		# 	self.retrieve_headers(item)
		# 	for item_label in header_dict:
		# 		if item_label not in header_list:
		# 			header_list.append(item_label)
		# csv_writer.writerow(header_list)
		
		# cursor_records = collection.find()
		# for cursor in cursor_records:
		# 	row_to_push = []
		# 	header_dict = {}
		# 	self.retrieve_headers(cursor)
		# 	for item_label in header_list:
		# 		if item_label in header_dict:
		# 			row_to_push.append(header_dict[item_label])
		# 		else:
		# 			row_to_push.append('')
		# 	csv_writer.writerow(row_to_push)
	
	def scraper_to_tsv(self, json_results: dict, filename=''):
		global header_dict
		
		total_records = dict()
		
		if filename:
			report_path = self.log_dir + filename + "-" + self.date + "-" + self.exec_time + ".tsv"
		else:
			report_path = self.log_dir + self.date + "-" + self.exec_time + ".tsv"
		
		print(json_results.keys())
		print("\nWriting results to: " + str(report_path))
		
		headers = dict()
		
		# Get Unique Headers
		for url, url_data in json_results.items():
			for type, type_data in url_data.items():
				if type not in headers:
					headers[type] = list()
				for index, data in type_data.items():
					json_results[url][type][index]['scraped_from'] = url
					for key, value in data.items():
						if key not in headers[type]:
							headers[type].append(key)
		# print(headers)
		
		# sort headers
		for type in headers.keys():
			if 'scraped_from' in headers[type]:
				headers[type].insert(0, headers[type].pop(headers[type].index('scraped_from')))
			if 'target_url' in headers[type]:
				headers[type].insert(1, headers[type].pop(headers[type].index('target_url')))
			
			if 'href' in headers[type]:
				headers[type].insert(2, headers[type].pop(headers[type].index('href')))
			elif 'src' in headers[type]:
				headers[type].insert(2, headers[type].pop(headers[type].index('src')))
			
			if 'htmlTag' in headers[type]:
				headers[type].insert(3, headers[type].pop(headers[type].index('htmlTag')))
			
			if 'status' in headers[type]:
				headers[type].insert(4, headers[type].pop(headers[type].index('status')))
				if 'message' in headers[type]:
					headers[type].insert(5, headers[type].pop(headers[type].index('message')))
				if 'pageTitle' in headers[type]:
					headers[type].insert(6, headers[type].pop(headers[type].index('pageTitle')))
				elif 'valid_url' in headers[type]:
					headers[type].insert(7, headers[type].pop(headers[type].index('valid_url')))
			elif 'valid_url' in headers[type]:
				headers[type].insert(5, headers[type].pop(headers[type].index('valid_url')))
				
		# Combine dictionary results by type
		for url, url_data in json_results.items():
			for type, type_data in url_data.items():
				if type not in total_records.keys():
					total_records[type] = list()
				for index, data in type_data.items():
					total_records[type].append(data)
		
		# print(total_records)
		
		output_file = open(report_path, 'w')
		csv_writer = csv.writer(output_file, delimiter='\t', quotechar='"')
		for type, type_data in total_records.items():
			output_file.write("\n" + str(type) + "\n")
			csv_writer.writerow(headers[type])
			output_file.write("\n")
			for item in type_data:
				order = ["\t"] * len(headers[type])
				for key, value in item.items():
					index = headers[type].index(key)
					order[index] = value
				csv_writer.writerow(order)
			output_file.write("\n\n")
		

