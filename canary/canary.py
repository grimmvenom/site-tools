from src.main import Canary
from src.base.get_arguments import get_arguments
import multiprocessing


if __name__ == '__main__':
	multiprocessing.freeze_support()
	arguments = get_arguments()
	Canary(arguments)
