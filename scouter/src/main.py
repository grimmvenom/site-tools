"""
Summary:
		Script to scan urls for links, inpage links, verify links, and components
		that we have written test cases for. All output is to an XML file.
Update:
		Scouter being separated into modules to be used independently so scouter can function
		as the eyes of Ivan and still perform it's tasks. All output will be in JSON and html

author:
grimm venom <grimmvenom@gmail.com>

refactored:
Dakota Carter <dakota22789@gmail.com>


"""

from src.base.base import Base
from src.base.get_arguments import get_arguments
import multiprocessing
import json

class Scouter:
	def __init__(self, arguments):
		# Global Variables
		self.arguments = arguments
		self.urls = arguments.urls
		self.status_log = dict()
		self.scouter_log = dict()
		self.main()

	def main(self):
		logger = Base()
		
		if self.arguments.status:
			from src.modules.status import Status
			url_status = Status(self.arguments)  # Set Variables in status.py
			self.status_log = url_status.main()  # Request all unique urls and get a list of statuses
			logger.write_log(self.status_log, 'statusCheck')  # Write Log to File
		elif self.arguments.scrape:
			from src.modules.scraper import Scrape
			scraper = Scrape(self.arguments)  # Set Variables in scraper.py
			self.scouter_log = scraper.main()  # Scrape content and return dictionary
			if self.arguments.verify:
				from src.modules.verifier import Verify
				verifier = Verify(self.scouter_log, self.arguments)  # Define Verifier
				verified_data = verifier.main()  # Run Verifier Method
				logger.write_log(verified_data, 'verifiedInfo')  # Write Log to File
			else:
				logger.write_log(self.scouter_log, 'scrapedInfo')  # Write Scraped Dictionary to File
				# z = self.merge_two_dicts(self.scouter_log, temp)
		
	def merge_two_dicts(self, x, y):
		z = x.copy()  # start with x's keys and values
		z.update(y)  # modifies z with y's keys and values & returns None
		return z


if __name__ == '__main__':
	multiprocessing.freeze_support()
	arguments = get_arguments()
	Scouter(arguments)

