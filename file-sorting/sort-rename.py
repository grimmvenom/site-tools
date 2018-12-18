#!/usr/bin/python3
"""
Summary:
Recursively Check Directory for filenames that contain spaces
Rename files without spaces
Replace references in all files (in / below directory defined) to the old path, with the new path

Author:
grimmvenom <grimmvenom@gmail.com>

"""

import os, sys, platform, time, glob, argparse, shutil, json
from os.path import basename


class SortFiles:
	def __init__(self, arguments):
		self.operating_system = platform.system()
		self.date = time.strftime("%m-%d-%Y")  # Date Format ISO 8601
		self.time = time.strftime("%I_%M")  # Time
		self.exec_time = str(time.strftime("%I_%M_%p"))  # Time
		self.current_dir = os.path.dirname(os.path.realpath(__file__))
		self.output_dir = self.current_dir + "/output"
		# self.out_file = self.output_dir + "/SortingResults-" + str(self.date) + "_" + str(self.exec_time) + ".txt"
		self.arguments = arguments
		self.extensions = self.arguments.extensions
		self.working_dir = arguments.working_dir
		if self.operating_system == 'Windows':
			self.current_dir = self.current_dir.replace("/", "\\")
			self.working_dir = self.working_dir.replace("/", "\\")
			self.output_dir = self.output_dir.replace("/", "\\")
		self.allfiles = list()
		self.files_with_spaces = list()
		self.directories_with_spaces = list()
		self.replacement_dict = dict()
		
	def logger(self, type, message):
		if not os.path.exists(self.output_dir):
			os.mkdir(self.output_dir)
		out_file = self.output_dir + "/Sorted-" + str(type) + "-" + str(self.date) + "_" + str(self.exec_time) + ".txt"
		if not os.path.exists(out_file):
			with open(out_file, "w") as myfile:
				myfile.write(str(message) + "\n")
		else:
			with open(out_file, "a") as myfile:
				myfile.write(str(message) + "\n")
	
	def list_directories(self):
		directories = [os.path.join(dirpath, d)
			for dirpath, dirnames, files in os.walk(self.working_dir)
			for d in dirnames if not d.startswith('.')]
		self.directories = set(directories)
		return self.directories
	
	def list_directories_with_spaces(self):
		print("Listing Directories with Spaces")
		directories = [os.path.join(dirpath, d)
			for dirpath, dirnames, files in os.walk(self.working_dir)
			for d in dirnames if d.__contains__(" ")]
		self.directories_with_spaces = list(set(directories))
		if self.directories_with_spaces:
			counter = 0
			self.replacement_dict['directories'] = dict()
			for directory in self.directories_with_spaces:
				counter += 1
				dirname = basename(directory)
				new_dirname = basename(dirname.replace(" - ", "_").replace(" ", "_").replace("/_", "/").replace("\\_", "\\"))
				new_dirpath = directory.replace(dirname, new_dirname)
				if directory not in self.replacement_dict:
					self.replacement_dict['directories'][str(counter)] = {'old_path': str(directory),
													'old_dirname': str(dirname),
													'new_path': str(new_dirpath),
													'new_dirname': str(new_dirname),
													'parent_dir': str(directory.split('/')[-2])}
		report = json.dumps(self.replacement_dict['directories'], indent=4, sort_keys=False)
		self.logger("Directories", report)
		print(str(len(self.directories_with_spaces)), " Directories Identified with Spaces")
		return self.directories_with_spaces, self.replacement_dict
	
	def rename_directories(self):
		if self.directories_with_spaces:
			print(" --> Renaming " + str(len(self.directories_with_spaces)) + " Directories")
			for index, data in self.replacement_dict['directories'].items():
				# print(data)
				old_dirpath = str(data['old_path'])
				old_dirname = str(data['old_dirname'])
				new_dirpath = str(data['new_path'])
				new_dirname = str(data['new_dirname'])
				try:
					shutil.move(old_dirpath, new_dirpath)
				except Exception as e:
					# parsed = json.loads(str(data))
					# parsed = json.dumps(str(data), indent=4, sort_keys=False)
					print("Error: " + str(e))
					# print(parsed)
					print("\n\n")
					pass
		
	def list_files(self):
		print("Listing Files with extensions " + str(self.extensions))
		self.files = [os.path.join(dirpath, f)
			for dirpath, dirnames, files in os.walk(self.working_dir)
			for f in files if not f.startswith('.') and f.endswith(tuple(self.extensions))]
		return self.files
	
	def list_files_with_spaces(self):
		print("Listing Files with Spaces and extensions: " + str(self.extensions))
		self.files_with_spaces = [os.path.join(dirpath, f)
			for dirpath, dirnames, files in os.walk(self.working_dir)
			for f in files if f.endswith(tuple(self.extensions)) and f.__contains__(" ")]
		if self.files_with_spaces:
			self.replacement_dict['files'] = dict()
			counter = 0
			for file in self.files_with_spaces:
				counter += 1
				filename = basename(file)
				new_filename = filename.replace(" - ", "_").replace(" ", "_")
				new_filepath = file.replace(filename, new_filename)
				# self.renamed_files_with_spaces.append(new_filepath)
				if str(counter) not in self.replacement_dict['files'].keys():
					self.replacement_dict['files'][str(counter)] = {
										'old_path': str(file),
										'old_filename': str(filename),
										'new_path': str(new_filepath),
										'new_filename': str(new_filename),
										'parent_dir': str(file.split('/')[-2])}
		report = json.dumps(self.replacement_dict['files'], indent=4, sort_keys=False)
		self.logger("Files", report)
		print(str(len(self.replacement_dict['files'].keys())), " Files Identified with Spaces")
		return self.files_with_spaces, self.replacement_dict
	
	def rename_files(self):
		if self.directories_with_spaces:
			print(" --> Renaming " + str(len(self.files_with_spaces)) + " Files")
			for index, data in self.replacement_dict['files'].items():
				# print(data)
				old_filepath = str(data['old_path'])
				old_filename = str(data['old_filename'])
				new_filepath = str(data['new_path'])
				new_filename = str(data['new_filename'])
				try:
					shutil.move(old_filepath, new_filepath)
				except Exception as e:
					# parsed = json.loads(str(data))
					# parsed = json.dumps(str(data), indent=4, sort_keys=False)
					print("Error: " + str(e))
					# print(parsed)
					print("\n\n")
					pass
	
	def replace_references(self):
		if self.arguments.replace_references:
			self.allfiles = self.list_files()
			print("Files to Search: ", str(len(self.allfiles)), "\n\n")
			if 'directories' in self.replacement_dict.keys():  # Replace Directory References
				self.replace_directory_references()
			if 'files' in self.replacement_dict.keys():
				self.replace_file_references()
			report = json.dumps(self.replacement_dict, indent=4, sort_keys=False)
			self.logger("report", report)
	
	def replace_directory_references(self):
		print("Replacing Directory References")
		file_counter = 0
		directories_identified = 0
		for file in self.allfiles[0:]:
			file_counter += 1
			contents = open(file, 'r', encoding='ISO-8859-1').readlines()
			# print(file)
			# print(contents)
			try:
				# print("Replacing Directory Refs")
				for index, data in self.replacement_dict['directories'].items():
					old_dirpath = str(data['old_path'])
					old_dirname = str(data['old_dirname'])
					new_dirpath = str(data['new_path'])
					new_dirname = str(data['new_dirname'])
					parent_dir = str(data['parent_dir'])
					# print(old_dirpath)
					pattern_found = False
					for string in contents:
						if old_dirpath in string:
							pattern_found = True
						elif (parent_dir + "/" + old_dirname in string) or (parent_dir + "\\" + old_dirname in string):
							pattern_found = True
							
					if pattern_found:
						if 'patternFoundIn' in data.keys():
							counter = len(data['patternFoundIn'].keys()) + 1
						else:
							self.replacement_dict['directories'][index]['patternFoundIn'] = dict()
							counter = 1
						directories_identified += 1
						self.replacement_dict['directories'][index]['patternFoundIn'][counter] = str(file)
						
						new_contents = list()
						for line in contents:
							line = line.replace(parent_dir + "/" + old_dirname, parent_dir + "/" + new_dirname)
							line = line.replace(parent_dir + "\\" + old_dirname, parent_dir + "\\" + new_dirname)
							line = line.replace(old_dirname, new_dirname)
							line = line.replace(old_dirpath, new_dirpath)
							new_contents.append(line)
						contents = new_contents.copy()
						open(file, 'w').write("".join(contents))
			except Exception as e:
				# print("\n", e, " on: ", file)
				pass
				
			pacman = "\rFiles identified containing old directory names: "
			sys.stdout.write(pacman + str(directories_identified))
			sys.stdout.flush()
		print("\n")
	
	def replace_file_references(self):
		print("Replacing File References")
		file_counter = 0
		files_identified = 0
		for file in self.allfiles[0:]:
			file_counter += 1
			contents = open(file, 'r', encoding='ISO-8859-1').readlines()
			# print(file)
			# print(contents)
			try:
				for index, data in self.replacement_dict['files'].items():
					old_path = str(data['old_path'])
					old_filename = str(data['old_filename'])
					new_path = str(data['new_path'])
					new_filename = str(data['new_filename'])
					parent_dir = str(data['parent_dir'])
					# print(old_dirpath)
					pattern_found = False
					for string in contents:
						if old_path in string:
							pattern_found = True
						elif (parent_dir + "/" + old_filename in string) or (parent_dir + "\\" + old_filename in string):
							pattern_found = True
					
					if pattern_found:
						if 'patternFoundIn' in data.keys():
							counter = len(data['patternFoundIn'].keys()) + 1
						else:
							self.replacement_dict['files'][index]['patternFoundIn'] = dict()
							counter = 1
						files_identified += 1
						self.replacement_dict['files'][index]['patternFoundIn'][counter] = str(file)
						
						new_contents = list()
						for line in contents:
							line = line.replace(parent_dir + "/" + old_filename, parent_dir + "/" + new_filename)
							line = line.replace(parent_dir + "\\" + old_filename, parent_dir + "\\" + new_filename)
							line = line.replace(old_path, new_path)
							new_contents.append(line)
						contents = new_contents.copy()
						open(file, 'w').write("".join(contents))
			except Exception as e:
				# print("\n", e, " on: ", file)
				pass
			pacman = "\rFiles identified containing old file names: "
			sys.stdout.write(pacman + str(files_identified))
			sys.stdout.flush()
		print("\n")


def get_arguments():
	# Define Arguments the Script will accept
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '-dir', '--dir', action='store', dest='working_dir', required=True, help='Path to Directory')
	parser.add_argument('--rename-dirs', action='store_true', dest='rename_dirs', help='Path to Directory')
	parser.add_argument('-ext', '--ext', action='append', dest='extensions', help='File Extension')
	parser.add_argument('--replace-references', action='store_true', dest='replace_references', help='Search all files for old file paths and replace with new names')
	arguments = parser.parse_args()
	if not os.path.exists(arguments.working_dir):
		parser.error("Path Not Found")
		exit()
	if not arguments.rename_dirs and not arguments.extensions:
		parser.error("You must specify an option for cleanup\n")
		exit()
	return arguments


if __name__ == '__main__':
	arguments = get_arguments()
	SortFiles = SortFiles(arguments)
	if arguments.rename_dirs:
		SortFiles.list_directories_with_spaces()
		SortFiles.rename_directories()
	
	if arguments.extensions:
		SortFiles.list_files_with_spaces()
		SortFiles.rename_files()
	
	if arguments.replace_references:
		SortFiles.replace_references()
