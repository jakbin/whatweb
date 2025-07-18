import re
import socket
import urllib
import argparse
import dns.resolver
from requests import get, head
from bs4 import BeautifulSoup
from colorama import Fore, init
from requests.exceptions import MissingSchema

package_name = "whatweb"
__version__ = "0.0.7"

init(autoreset=True)

def get_status(status_code: int):
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

def get_bootstrap_verion(soup):

	css_link_tags = soup.find_all('link', {'rel': 'stylesheet'})
	js_script_tags = soup.find_all('script')

	bootstrap_pattern = re.compile(r'bootstrap/\d\.\d\.\d')
	bootstrap_version = None
	for tag in css_link_tags + js_script_tags:
		if 'href' in tag.attrs:
			match = bootstrap_pattern.search(tag['href'])
			if match:
				bootstrap_version = match.group()
				break
	if bootstrap_version:
		return True, bootstrap_version.replace("bootstrap/", "")
	else:
		return False, None

def get_jquery_verion(soup):

	css_link_tags = soup.find_all('link', {'rel': 'stylesheet'})
	js_script_tags = soup.find_all('script')

	jquery_pattern = re.compile(r'jquery/\d\.\d\.\d')
	jquery_version = None
	for tag in css_link_tags + js_script_tags:
		if 'src' in tag.attrs:
			match = jquery_pattern.search(tag['src'])
			if match:
				jquery_version = match.group()
				break
	if jquery_version:
		return True, jquery_version.replace("jquery/", "")
	else:
		return False, None

def get_shodan_internetdb_info(ip: str):
    try:
        response = get(f"https://internetdb.shodan.io/{ip}").json()
        
        # Extract relevant information
        ports = response.get("ports", [])
        cpes = response.get("cpes", [])
        hostnames = response.get("hostnames", [])
        tags = response.get("tags", [])
        vulns = response.get("vulns", [])
        
        # Format the results
        shodan_info = ""
        if ports:
            shodan_info += f"Ports[{', '.join(map(str, ports))}] "
        if cpes:
            shodan_info += f"CPEs[{', '.join(cpes)}] "
        if hostnames:
            shodan_info += f"Hostnames[{', '.join(hostnames)}] "
        if tags:
            shodan_info += f"Tags[{', '.join(tags)}] "
        if vulns:
            shodan_info += f"Vulnerabilities[{', '.join(vulns)}] "
        
        return shodan_info
    except Exception as e:
        return f"ShodanError[{str(e)}] "

def whatweb(target: str):
	try:
		r = get(target)
	except MissingSchema:
		r = get(f"http://{target}")

	status_code = get_status(r.status_code)

	soup = BeautifulSoup(r.text, 'html.parser')
	title = soup.title.get_text()

	# get all meta generator
	generator_tags = soup.find_all('meta', attrs={'name': 'generator'})
	generators = ""
	for generator in generator_tags:
		generators += f"{generator['content']}, "
	if generators != "": 
		final_generators = f"MetaGenerator[{generators}] "
	else:
		final_generators = ""

	# get wordpress version
	for generator in generator_tags:
		content = generator['content']
		if 'WordPress' in content:
			version = content.replace('WordPress ', '')
			WordPress = f'WordPres[{Fore.LIGHTBLUE_EX}{version}{Fore.RESET}] '
			break
		else:
			WordPress = ''
	else:
		WordPress = ''

	try:
		Ip = f'IP[{socket.gethostbyname(target)}]'
	except socket.gaierror:
		res = head(target, allow_redirects=True)
		try:
			Ip = f'IP[{r.headers["Host"]}]'
		except KeyError:
			parsed_url = urllib.parse.urlparse(target)
			hostname = parsed_url.hostname
			try:
				answers = dns.resolver.query(hostname, 'A')
				for rdata in answers:
					Ip = f'IP[{rdata.address}]'
			except dns.resolver.NXDOMAIN:
				Ip = ''

	try:
		xPoweredBy = f'X-Powered-By[{r.headers["x-powered-by"]}]'
	except KeyError:
		xPoweredBy = ""

	try:
		httpServer = f'HTTPServer[{Fore.LIGHTRED_EX}{r.headers["Server"]}{Fore.RESET}] '
	except KeyError:
		httpServer = ""

	is_bootstrap, bootstrap_version = get_bootstrap_verion(soup)
	if is_bootstrap:
		Bootstrap = f'Bootstrap[{Fore.LIGHTBLUE_EX}{bootstrap_version}{Fore.RESET}] '
	else:
		Bootstrap = ''

	is_jquery, jquery_version = get_jquery_verion(soup)
	if is_jquery:
		Jquery = f'Jquery[{Fore.LIGHTBLUE_EX}{jquery_version}{Fore.RESET}] '
	else:
		Jquery = ''
		
	try:
		ip_address = socket.gethostbyname(target)
		Ip = f'IP[{Fore.LIGHTRED_EX}{ip_address}{Fore.RESET}] '
		shodan_info = get_shodan_internetdb_info(ip_address)

		# Add colors to Shodan info
		if "Ports" in shodan_info:
			shodan_info = shodan_info.replace("Ports", f"{Fore.LIGHTBLUE_EX}Ports{Fore.RESET}")
		if "CPEs" in shodan_info:
			shodan_info = shodan_info.replace("CPEs", f"{Fore.LIGHTGREEN_EX}CPEs{Fore.RESET}")
		if "Hostnames" in shodan_info:
			shodan_info = shodan_info.replace("Hostnames", f"{Fore.LIGHTMAGENTA_EX}Hostnames{Fore.RESET}")
		if "Tags" in shodan_info:
			shodan_info = shodan_info.replace("Tags", f"{Fore.LIGHTCYAN_EX}Tags{Fore.RESET}")
		if "Vulnerabilities" in shodan_info:
			shodan_info = shodan_info.replace("Vulnerabilities", f"{Fore.LIGHTYELLOW_EX}Vulnerabilities{Fore.RESET}")

		# Add prefix and wrap long lines
		if shodan_info:
			shodan_info = f"From Shodan Internal DB: {shodan_info}"
	except socket.gaierror:
		Ip = ''
		shodan_info = ''

	return f"{Fore.LIGHTBLUE_EX}{r.url}{Fore.RESET} [{status_code}] {httpServer}{Ip} {Bootstrap}{Jquery}{final_generators}Title[{Fore.LIGHTYELLOW_EX}{title}{Fore.RESET}] {WordPress}{xPoweredBy} \n{shodan_info}"

example_uses = '''example:
   whatweb example.com'''

def main(argv = None):
	parser = argparse.ArgumentParser(prog=package_name, description=f"WhatWeb - Next generation web scanner version {__version__}", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument("target", help="Enter URL, hostname, IP address")

	args = parser.parse_args(argv)

	if args.target:
		print(whatweb(args.target))
	else:
		parser.print_help()

if __name__ == '__main__':
	raise SystemExit(main())
