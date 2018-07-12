#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This Script will install necessary pyhon libraries for scripts within the current directory

Requirements:
python must be installed
Pip must be installed

# https://github.com/bndr/pipreqs
"""

import pip, os, sys

current_dir = os.path.dirname(os.path.realpath(__file__))

print("Running Setup.py")

print(" ")

print("Installing pipreq:")
os.system("python3 -m pip install pipreqs") # install pipreq
os.system("python2.7 -m pip install pipreqs") # install pipreq
print(" ")

print("Generating requirements.txt:")
os.system("python3 -m pipreqs --force " + current_dir) # creates requirements.txt
#os.system("python2.7 -m pipreqs --force " + current_dir)
print(" ")

print("Installing python requirements: ")
os.system("python3 -m pip install -r requirements.txt")
os.system("python2.7 -m pip install -r requirements.txt")