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
os.system("python -m pip install pipreqs") # install pipreq

print(" ")

print("Generating requirements.txt:")
os.system("pipreqs --force " + current_dir) # creates requirements.txt

print(" ")

print("Installing python requirements: ")
os.system("python -m pip install -r requirements.txt")