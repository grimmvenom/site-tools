# -*- coding: utf-8 -*-
"""
Summary:
		Script to scan urls for links, inpage links, verify links, and components
		that we have written test cases for. All output is to an XML file.
Update:
		canary being separated into modules to be used independently so canary can function
		as the eyes of Ivan and still perform it's tasks. All output will be in JSON and html

author:
grimm venom <grimmvenom@gmail.com>

refactored:
Dakota Carter <dakota22789@gmail.com>

"""

from src.base.base import Base
from src.base.get_arguments import get_arguments
import multiprocessing
import json, time


class Canary:
	def __init__(self, arguments):
		# Global Variables
		self.arguments = arguments
		self.urls = arguments.urls
		self.status_log = dict()
		self.scrape_log = dict()
		self.verified_log = dict()
		self.main()

	def main(self):
		logger = Base()
		start_time = time.time()
		
		if self.arguments.exclude:
			print(self.arguments.exclude)
			print("\n")

		if self.arguments.status:
			from src.modules.status import Status
			url_status = Status(self.arguments)  # Set Variables in status.py
			self.status_log = url_status.main()  # Request all unique urls and get a list of statuses
			if self.arguments.tsv_output:
				from src.modules.parse_results import Parse_TSV
				parser = Parse_TSV(self.arguments)
				parser.scraper_to_tsv(self.status_log, 'statusCheck')
			else:
				logger.write_log(self.status_log, 'statusCheck')  # Write Log to json File
			
		if self.arguments.scrape:
			from src.modules.scraper import Scrape
			scraper = Scrape(self.arguments)  # Set Variables in scraper.py
			self.scrape_log = scraper.main()  # Scrape content and return dictionary
			if self.arguments.verify:
				from src.modules.verifier import Verify
				verifier = Verify(self.scrape_log, self.arguments)  # Define Verifier
				self.verified_log = verifier.main()  # Run Verifier Method
		
			if self.arguments.tsv_output:  # Write Scraped / Verified Data to file
				from src.modules.parse_results import Parse_TSV
				parser = Parse_TSV(self.arguments)
				if self.verified_log:
					parser.scraper_to_tsv(self.verified_log, 'verifiedInfo')  # Write Log to tsv File
				else:
					parser.scraper_to_tsv(self.scrape_log, 'scrapedInfo')  # Write Scraped Dictionary to tsv File
			else:
				if self.verified_log:
					logger.write_log(self.verified_log, 'verifiedInfo')  # Write Log to json File
				else:
					logger.write_log(self.scrape_log, 'scrapedInfo')  # Write Scraped Dictionary to json File

		end_time = '{:.2f}'.format((time.time() - start_time))
		print("\nTotal Runtime: " + str(end_time) + " (seconds)\n")
		
	def merge_two_dicts(self, x, y):
		z = x.copy()  # start with x's keys and values
		z.update(y)  # modifies z with y's keys and values & returns None
		return z


if __name__ == '__main__':
	multiprocessing.freeze_support()
	arguments = get_arguments()
	Canary(arguments)
