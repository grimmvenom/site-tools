#!/usr/bin/python3
"""
Summary:
Recursively Check files for old patterns and replace with new patterns

Author:
grimmvenom <grimmvenom@gmail.com>

"""

import os, sys, platform, time, glob, argparse, shutil, json, multiprocessing, ast
from os.path import basename
from multiprocessing.managers import BaseManager
multiprocessing.freeze_support()


class pyGrep:
	def __init__(self, arguments):
		self.operating_system = platform.system()
		self.date = time.strftime("%m-%d-%Y")  # Date Format ISO 8601
		self.time = time.strftime("%I_%M")  # Time
		self.exec_time = str(time.strftime("%I_%M_%p"))  # Time
		self.current_dir = os.path.dirname(os.path.realpath(__file__))
		self.output_dir = self.current_dir + os.sep + "output"
		if not os.path.exists(self.output_dir):
			os.mkdir(self.output_dir)
		self.out_file = self.output_dir + os.sep + "pyGrep-" + str(self.date) + "_" + str(self.exec_time) + ".txt"
		self.arguments = arguments
		self.working_dir = arguments.working_dir
		self.extensions = ['.txt', '.tsv', '.csv']
		self.files = list()
		self.patterns = dict()
		self.patterns_identified = 0
		
	def main(self):
		print("Running Check")
		self.files = self.list_files()
		self.determine_patterns()
		print("\n")
		self._worker()
		print("Patterns Identified: " + str(self.patterns_identified))
		parsed = json.dumps(self.patterns, indent=4, sort_keys=False)
		open(self.out_file, 'w').write(parsed)
		
	def _worker(self):
		files = self.files.copy()
		files = set(files)
		with multiprocessing.Pool(processes=10) as pool:  # Start Multiprocessing pool
			results = pool.map(self._replace_patterns, files)
		# clean_results = set(results)
		for item in set(results):
			if item:  # If item not None
				new_patterns = dict(ast.literal_eval(str(item)))
				for index, data in new_patterns.items():
					if 'OldPatternFoundIn' in new_patterns[index].keys():
						for file, line_num in data['OldPatternFoundIn'].items():
							if 'OldPatternFoundIn' in self.patterns[index].keys():
								identified_index = len(self.patterns[index]['OldPatternFoundIn'].keys()) + 1
								self.patterns_identified += 1
								self.patterns[index]['OldPatternFoundIn'][str(identified_index)] = {'filename': file, 'Lines': str(line_num)}
							else:
								self.patterns[index]['OldPatternFoundIn'] = dict()
								for sub_index, sub_data in data['OldPatternFoundIn'].items():
									self.patterns[index]['OldPatternFoundIn'][str(1)] = {'filename': file, 'Lines': str(line_num)}

	def determine_patterns(self):
		if self.arguments.pattern_path:
			self.read_patterns_csv()
		elif self.arguments.old_pattern and self.arguments.new_pattern:
			self.patterns["1"] = {'old_pattern': str(self.arguments.old_pattern),
								'new_pattern': str(self.arguments.new_pattern)}
		else:
			print("No Patterns Specified")
			exit()
		# parsed = json.loads(str(self.patterns))
		# print(json.dumps(self.patterns, indent=4, sort_keys=True))
		# print("\n")
		return self.patterns
	
	def read_patterns_csv(self):
		print("reading pattern requirements from: " + str(self.arguments.pattern_path))
		contents = open(str(self.arguments.pattern_path), 'r', encoding='ISO-8859-1').readlines()
		counter = 0
		for line in contents[1:]:
			counter += 1
			old_pattern = line.split(',')[0]
			new_pattern = line.split(',')[1]
			if old_pattern.endswith('\n'):
				old_pattern = old_pattern.replace('\n', '')
			if new_pattern.endswith('\n'):
				new_pattern = new_pattern.replace('\n', '')
			self.patterns[str(counter)] = {'old_pattern': str(old_pattern),
											'new_pattern': str(new_pattern)}
		return self.patterns
	
	def list_files(self):
		files = [os.path.join(dirpath, f)
			for dirpath, dirnames, files in os.walk(self.working_dir)
			for f in files if not f.startswith('.') and f.endswith(tuple(self.extensions))]
		# self.files = set(files)
		self.files = files
		print("Listing Files with extensions " + str(self.extensions) + " : " + str(len(self.files)))
		return self.files
	
	def _replace_patterns(self, file):
		patterns = self.patterns
		contents = open(file, 'r', encoding='ISO-8859-1').readlines()
		found = False
		try:
			for index, data in patterns.items():
				found_on = list()
				old_pattern = str(data['old_pattern'])
				new_pattern = str(data['new_pattern'])
				pattern_found = False
				for line_num, string in enumerate(contents):
					if old_pattern in string:
						pattern_found = True
						found_on.append(line_num)
				
				if pattern_found:
					patterns[index]['OldPatternFoundIn'] = dict()
					patterns[index]['OldPatternFoundIn'][str(file)] = str(found_on)
					new_contents = list()
					for line in contents:
						line = line.replace(old_pattern, new_pattern)
						new_contents.append(line)
					open(file, 'w').write("\n".join(new_contents.copy()))
					found = True
		except Exception as e:
			print("\n", e, " on: ", file)
			pass
		if found:
			value = str(patterns)
			return value
		else:
			return None
		
	
def get_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '-dir', '--dir', action='store', dest='working_dir', required=True, help='Path to Parent Directory')
	parser.add_argument('-op', '--old', '--old-pattern', action='store', dest='old_pattern', help='old pattern to overwrite')
	parser.add_argument('-np', '--new', '--new-pattern', action='store', dest='new_pattern', help='new pattern to use in old patterns place')
	parser.add_argument('-f', '-file', '--file', action='store', dest='pattern_path', help='Path to Parent Directory')
	arguments = parser.parse_args()
	if not os.path.exists(arguments.working_dir):
		parser.error("Path Not Found")
		exit()
	
	if (not arguments.old_pattern and not arguments.new_pattern) and (not arguments.pattern_path):
		parser.error("You Must Specify and old pattern and new pattern; or file path with patterns (.csv)")
		exit()
	return arguments


if __name__ == '__main__':
	arguments = get_arguments()
	Grep = pyGrep(arguments)
	Grep.main()
