import argparse
from .interface.backend.base import app

def main(host, port, debug):
	app.run(host, port, debug)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--host', default='localhost', type=str)
	parser.add_argument('-p', '--port', default=5000, type=int)
	parser.add_argument('--debug', default=False, type=bool)

	args = parser.parse_args()
	main(host=args.host, port=args.port, debug=args.debug)

