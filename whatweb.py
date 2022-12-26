import socket
import urllib3
import argparse
from requests import get
from bs4 import BeautifulSoup
from colorama import Fore, init
from requests.exceptions import MissingSchema

package_name = "whatweb"
__version__ = "0.0.2"

init(autoreset=True)

def get_status(status_code:int):
	match status_code:
		case 200:
			statusCode = "200 OK"
		case 301:
			statusCode = "301 Moved Permanently"
		case 400:
			statusCode = "400 Bad Request"
		case 401:
			statusCode = "401 Unauthorized"
		case 403:
			statusCode = "403 Forbidden"
		case 404:
			statusCode = "404 Not Found"
		case 405:
			statusCode = "405 Method Not Allowed"
		case 406:
			statusCode = "406 Not Acceptable"
		case 500:
			statusCode = "500 Internal Server Error"
		case 502:
			statusCode = "502 Bad Gateway"
		case _:
			statusCode = status_code

	return statusCode

def whatweb(target:str):
	try:
		r = get(target)
	except MissingSchema:
		r = get(f"http://{target}")

	status_code = get_status(r.status_code)

	soup = BeautifulSoup(r.text, 'html.parser')
	title = soup.title.get_text()

	generator_tags = soup.findAll('meta', attrs={'name': 'generator'})
	generators = ""
	for generator in generator_tags:
		generators += f"{generator['content']}, "

	Ip = socket.gethostbyname(target)

	try:
		xPoweredBy = r.headers["x-powered-by"]
	except KeyError:
		xPoweredBy = ""

	try:
		httpServer = r.headers["Server"]
	except KeyError:
		httpServer = ""

	return f"{Fore.LIGHTBLUE_EX}{r.url}{Fore.RESET} [{status_code}] HTTPServer[{Fore.LIGHTRED_EX}{httpServer}{Fore.RESET}] IP[{Ip}] MetaGenerator[{generators}] Title[{Fore.LIGHTYELLOW_EX}{title}{Fore.RESET}] X-Powered-By[{xPoweredBy}]"

example_uses = '''example:
   whatweb -t example.com'''

def main(argv = None):
	parser = argparse.ArgumentParser(prog=package_name, description="Next generation web scanner", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument("-t","--target", help="Enter URLs, hostnames, IP addresses")

	parser.add_argument("-v","--version",
							action="store_true",
							dest="version",
							help="check version of t-bot")

	args = parser.parse_args(argv)

	if args.target:
		print(whatweb(args.target))
	elif args.version:
		return __version__
	else:
		parser.print_help()

if __name__ == '__main__':
	raise SystemExit(main())
