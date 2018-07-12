#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Script to do the following:
Verify a list of URL's
Store a Cache of Web Pages
Check for changes to web pages


function order:
1 - check_dirs
2 - read_urls
    3 - Validate_URLs
    4 - Convert_HTML
        5 - Cache_Page
    6 - Compare Site

"""


import os
import time
import sys
import urllib2
import difflib


# Name of Environment / Text File to import URL's From
url_import = ['wwwqa.ford.com']
# Update Cache (Will Overwrite current Cache if set to true)
update_cache = "false"
special_count = 0 # To continue from specific line number if script fails

# Global Variables
date = time.strftime("%m-%d-%y") # Date Format mm-dd-yyyy_Hour_Min
sys_time = time.strftime("%H_%M")
current_dir = os.path.dirname(os.path.realpath(__file__))
cache_dir = current_dir + "/cache"


# Make Sure Necessary Directories Exist
def check_dirs():
    # Create the cache folder if it doesn't exist already.
    if not os.path.exists(cache_dir):
        print(cache_dir + " Does Not Exist....... Creating Directory")
        print(" ")
        os.makedirs(cache_dir)
    else:
        print(cache_dir + " Exists")
        print(" ")

    # Create environment folder under ./cache if it does not exist (for each environment listed)
    for project in url_import:
        project_dir = cache_dir + "/" + project
        if not os.path.exists(project_dir):
             print(project_dir + " Does Not Exist....... Creating Directory")
             print(" ")
             os.makedirs(project_dir)
        else:
            print(project_dir + "Exists")
            print(" ")



# Read URLs from Project Files
def read_urls(project):
    print("Reading URL's for:" + project)
    file_path = current_dir + "/" + project + ".txt"
    print("Opening " + file_path)
    print(" ")
    if special_count != 0:
        count = special_count
    else:
        count = 0

    file = open(file_path).readlines()[special_count:]
    for url in file:
        url = str(url).rstrip('\n')
        count += 1
        status = validate_url(url)
        print("Status Code: " + status )
        if status == "200":
            convert_html(url, count)
            # new_data = convert_html(url, count)
            # print(data)
            compare_site(url, count)
        print("=============================================")
        print(" ")
        print(" ")


# Ensure that URL is reachable
def validate_url(url):
    print("Checking url: " + url)
    validate = urllib2.urlopen(url)
    status = validate.getcode()
    return str(status)


# Convert URL to HTML
def convert_html(url, count):
    site = urllib2.urlopen(url)
    cache_file = project_dir + "/" + str(count) + ".txt"
    data = site.read()
    site.close()
    out_data = str(data)
    # print("URL: " + url)
    print("Imported URL Line Number: " + str(count))
    print("=============================================")
    # print(data)
    if os.path.exists(cache_file):
        if update_cache == "true":
            cache_page(url, count, str(data))
        elif update_cache != "true":
            print("Caching is set to False.....Cache Will Not Update")
    else:
        print("Cache Does not Exist - is considered new - Creating Cache")
        cache_page(url, count, str(data))

    # Create Temp File to Compare
    cache_page(url, "temp", str(data))

    # return str(out_data) # Return New Data to


# Caches Page
def cache_page(url, count, new_data):
    cache_file = project_dir + "/" + str(count) + ".txt"
    if count != "temp":
        print("Caching Page: " + url)
        file = open(cache_file, "w")
        file.write("URL: " + str(url) + "\n")
        file.write("Project: " + project + "\n")
        file.write("Import Line Number: " + str(count) + "\n")
        file.write("\n")
        file.write(new_data)
        file.write("\n")
        file.close()
    else: # For Temp Files to Compare
        file = open(cache_file, "w")
        file.write("URL: " + str(url) + "\n")
        file.write("Project: " + project + "\n")
        file.write("Temp File: " + str(count) + "\n")
        file.write("\n")
        file.write(new_data)
        file.write("\n")
        file.close()


def compare_site(url, count):
    print("Comparing Site........")
    cache_file = project_dir + "/" + str(count) + ".txt"
    temp_file = project_dir + "/temp.txt"
    last_modified = time.ctime(os.path.getmtime(cache_file))
    add_count = 0
    new = []
    remove_count = 0
    removed = []

    file1 = open(cache_file, 'r')
    file2 = open(temp_file, 'r')
    old_lines = file1.read()
    old_lines = old_lines.splitlines()
    new_lines = file2.read()
    new_lines = new_lines.splitlines()

    d = difflib.Differ()
    diff = d.compare(old_lines, new_lines)
    #diff = list(d.compare(old_lines, new_lines))
    #diff = list(difflib.unified_diff(old_lines,new_lines))

    for line in diff:
    #if len(diff) > 0:
        if line.startswith('+'):
            add_count += 1
            line = line.replace("+", "")
            new += line + "\n"
        elif line.startswith('- '):
            remove_count += 1
            line = line.replace("-", "")
            removed += line + "\n"

    # remove_count = remove_count - 4 # Remove top 4 lines from total count
    print("+ Lines Unique to Latest Version: " + str(add_count))
    print("-----------------------")
    print(''.join(new))
    print(" ")
    print("- Lines Unique to cached version: " + str(remove_count))
    print("-----------------------")
    print(''.join(removed))
    print(" ")
    # print(str(diff))

    # os.remove(temp_file) # Remove Temporary Comparison File


check_dirs()
for project in url_import:
    project_dir = cache_dir + "/" + project
    print("Current Project: " + project)
    read_urls(project)

