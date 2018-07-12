"""

import xml.etree.cElementTree as ET

root = ET.Element("root")
doc = ET.SubElement(root, "url")

ET.SubElement(doc, "field1", name="blah").text = "some value1"
links = ET.SubElement(doc, "External-links")
link = ET.SubElement(links, "link")
ET.SubElement(link, "SRC").text = "link1"
ET.SubElement(link, "Status").text = "Status"
ET.SubElement(link, "Redirect").text = ""

tree = ET.ElementTree(root)
tree.write("test.xml")

"""
import requests
import xml.etree.cElementTree as ETX

urls = ["http://www.ford.com", "http://www.google.com"]

xml_root = ETX.Element("root") # Start XML Element
for url in urls: # Loop through list of urls
    doc = ETX.SubElement(xml_root, "Page", url=url)
    ETX.SubElement(doc, "field1", name="blah").text = "some value1"
    response = requests.get(url) # Perform Get Request of url to gather info

tree = ETX.tostring(xml_root)  # Form XML
# tree = ETX.fromstring(xml_root)
text_file = open("test.xml", "wb")
text_file.write(tree)
text_file.close()


