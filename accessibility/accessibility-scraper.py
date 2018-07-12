#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:
Grimm Venom <grimmvenom@gmail.com>

Summary:
Scrape images with alt-text
Scrape elements with aria-label
Scrape elements with aria-labelledby
"""

# Import Libraries
import os, time, sys, datetime, requests, re, argparse
from bs4 import BeautifulSoup

# Global Variables
date = time.strftime("%m-%d-%y") # Date Format mm-dd-yyyy_Hour_Min
Time = time.strftime("%H_%M") # Time
current_dir = os.path.dirname(os.path.realpath(__file__)) # Get Current Directory of Running Script
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir)) # Get Parent of Current Directory of Script


def log_output(log_name):
    log_dir = current_dir + "/logs"  # Define Logging Directory
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


def get_arguments():
    urls = []
    # Define Arguments the Script will accept
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', "--url", action='append', dest='urls', help='http://<url> or https://<URL>')
    parser.add_argument('-f', "--file", action='store', dest='file', help='.txt file to import a list of urls from. One URL per line. Include http:// or https://')
    parser.add_argument('-wc', "--webcreds", "--webcredentials", "--webcreds", action='store', dest='webcredentials',
                        help='Site Credentials (<username>:<password>)')

    arguments = parser.parse_args()

    if (arguments.webcredentials):
        webcredentials = arguments.webcredentials  # Credentials for request authentication <username>:<password>
        web_username = webcredentials.split(":", 1)[0]  # Website Username
        web_password = webcredentials.split(":", 1)[1]  # Website Password
    else:
        webcredentials = ""
        web_username = ""
        web_password = ""

    if (arguments.file):
        with open(arguments.file, 'r') as f:
            file_urls = f.readlines()
            file_urls = [s.replace('\r', '').replace('\n', '') for s in file_urls]  # remove all the 8s
        for file_url in file_urls:  # Convert from list to string and append to url list
            urls.append(file_url)

    if (arguments.urls):
        for url in arguments.urls:  # Convert from list to string and append to url list
            urls.append(url)

    if len(urls) <= 0:
        print("Must specify urls. use the -u or -f parameters to specify a list of urls")
        exit()
    return urls, web_username, web_password


def Basic_Request(url, web_username="", web_password=""):
    if (len(web_username) > 1) and (len(web_password) > 1):
        response = requests.get(url, auth=(web_username, web_password)) # Perform authenticated Get Request of url to gather info
    else:
        response = requests.get(url)  # Perform unauthenticated Get Request of url to gather info

    if response.history:
        status_code = str(response.history[0].status_code)
        redirected_url = response.url
        response = requests.get(redirected_url, timeout=15)
    else:
        status_code = str(response.status_code)
        redirected_url = ""
    page_source = response.text
    print("Requesting page from: " + str(url) + " --> " + str(status_code))
    return page_source, status_code, redirected_url


def Scrape_Alt_Text(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    images = soup.findAll('img')
    count = 0
    print(" ")
    print("Images alt-text:")
    print("-----------------------")
    for image in images:
        count = count + 1

        try:
            img_src = image['src']
        except:
            img_src = "N/A"
            pass

        try:
            alt_text = image['alt']
        except:
            alt_text = "N/A"
            pass

        print(str(count) + ") - Image Source: " + img_src)
        print("alt-text: " + alt_text)
        print(" ")

    print(" ")


def Scrape_Aria_labels(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    aria_labels = soup.findAll(attrs={"aria-label": True})
    count = 0
    print(" ")
    print("Elements with aria-labels:")
    print("-----------------------")
    for label in aria_labels:
        count = count + 1
        print(str(count) + "): ")
        print(label)
        print(" ")

    print(" ")


def Scrape_Aria_labelledby(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    aria_labels = soup.findAll(attrs={"aria-labelledby": True})
    count = 0
    print(" ")
    print("Elements with aria-labelledby:")
    print("-----------------------")
    for label in aria_labels:
        count = count + 1
        print(str(count) + "): ")
        print(label)
        print(" ")

    print(" ")


log_output("AccessibilityCheck-" + date + "_" + str(Time)) # Record STDOUT and generate a log file

urls, web_username, web_password = get_arguments() # Set Variables from script arguments

for url in urls:
    if url.startswith("http://") or url.startswith("https://"):
        print(" ")
        print("Checking: " + url)
        print("=====================================================")
        page_source, status_code, redirected_url = Basic_Request(url, web_username, web_password)
        Scrape_Alt_Text(page_source) # Scrape all Images with Alt Text
        Scrape_Aria_labels(page_source) # Scrape All aria-label elements
        Scrape_Aria_labelledby(page_source) # Scrape all aria-labelledby elements
        print(" ")
    else:
        print(str(url))
        print("All urls must start with http:// or https://")