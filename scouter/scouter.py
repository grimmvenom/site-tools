from src.main import Scouter
from src.base.get_arguments import get_arguments
import multiprocessing


if __name__ == '__main__':
	multiprocessing.freeze_support()
	arguments = get_arguments()
	Scouter(arguments)
