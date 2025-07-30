#!/usr/bin/env python2

from __future__ import print_function
# from safeprint import print as sprint

import requests
import time
import traceback
import sys
import os
import re
import argparse
from bs4 import BeautifulSoup as bs
import clipboard
# import progressbar
from make_colors import make_colors
from pydebugger.debug import debug
from licface import CustomRichHelpFormatter

if sys.platform == 'win32':
	try:
		from idm import IDMan
		idman = IDMan()
		download = idman.download
	except:
		try:
			from downloader import download
		except:
			from .downloader import download		
else:
	try:
		from downloader import download
	except:
		from .downloader import download
		
if sys.version_info.major == 3:
	from urllib.parse import urlparse
	raw_input = input
else:
	from urlparse import urlparse
try:
	from pause import pause
except:
	def pause(*args, **kwargs):
		raw_input("Enter to coninute")

from configset import configset
#if sys.version_info.major == 3:
	#from rich.console import Console
	#from fake_headers import Headers
	#try:
		#from downloader import download
	#except:
		#from .downloader import download
#else:
#try:
	#from . downloader2 import download, download_linux
#except:
	#from downloader2 import download, download_linux

#import pheader
import warnings
warnings.filterwarnings('ignore')
from progress_session import ProgressSession

class Mp4upload(object):

	# SESSION = requests.Session()
	SESSION = ProgressSession()
	CONFIG = configset()
	PREFIX = '{variables.task} >> {variables.subtask}'
	VARIABLES = {'task':' -- ', 'subtask':' -- '}
	# BAR = progressbar.ProgressBar(max_value=100, prefix= PREFIX, variables=VARIABLES)
	URL = "https://www.mp4upload.com/"

	def __init__(self, url = None):
		if url: self.URL = url

	@classmethod
	def logger(self, message, status="info"):
		logfile = os.path.join(os.path.dirname(__file__), self.CONFIG.configfile)
		if not os.path.isfile(logfile):
			lf = open(logfile, 'wb')
			lf.close()
		real_size = bitmath.getsize(logfile).kB.value
		max_size = self.CONFIG.get_config("LOG", 'max_size')
		debug(max_size = max_size)
		if max_size:
			debug(is_max_size = True)
			try:
				max_size = bitmath.parse_string_unsafe(max_size).kB.value
			except:
				max_size = 0
			if real_size > max_size:
				try:
					os.remove(logfile)
				except:
					print("ERROR: [remove logfile]:", traceback.format_exc())
				try:
					lf = open(logfile, 'wb')
					lf.close()
				except:
					print("ERROR: [renew logfile]:", traceback.format_exc())

		str_format = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S.%f") + " - [{}] {}".format(status, message) + "\n"
		# with open(logfile, 'ab') as ff:
		# 	ff.write(str_format)

	@classmethod
	def parser_headers(self, headers_str):
		h = list(filter(None, re.split("\n|\t|\r|  ", headers_str)))
		debug(h = h)
		keys = list(filter(lambda k: k[-1] == ":", h))
		debug(keys = keys)
		values = list(filter(lambda k: k[-1] != ":", h))
		debug(values = values)
		data = {i[:-1]:values[keys.index(i)] for i in keys}
		debug(data = data)
		return data
	
	@classmethod
	def format_cookie(self, cookies):
		cookie = ""
		debug(cookies = cookies)
		if isinstance(cookies, dict):
			
			for i in cookies:
				cookie += i + "=" + cookies.get(i) + "; "
			debug(cookie = cookie)
		if cookie:
			debug(cookie = cookie[:-2])
			return cookie[:-2]
		else:
			return {}

	@classmethod
	def set_header(self, header_str = None):
		if not header_str:
			header_str ="""accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
			accept-encoding: gzip, deflate
			accept-language: en-US,en;q=0.9,id;q=0.8,ru;q=0.7
			sec-fetch-dest: document
			sec-fetch-mode: navigate
			sec-fetch-site: same-origin
			sec-fetch-user: ?1
			upgrade-insecure-requests: 1
			user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"""

		# debug(header_str = header_str)
		header_str = list(filter(None, re.split("\n|\r|\t\t", header_str)))
		# for i in header_str:
		# 	key, value = re.split(": |:\t", i)
		# print([re.split(": |:\t", i) for i in header_str])
		# pause()
		# debug(header_str = header_str)
		headers = {key.strip():value.strip() for key,value in [re.split(": |:\t", i) for i in header_str]}
		# debug(headers = headers)
		return headers

	@classmethod
	def getname(self, url = None, id = None, bsobject = None, timeout = 10, retries = 10):
		if not url and not bsobject and not id:
			return ''
		elif id and not url and not bsobject:
			url = self.URL + str(id)
		error = False
		content = ''
		name = ''
		n = 1
		if url:
			while 1:
				try:
					a = requests.get(url, timeout = timeout)
					break
				except:
					if not n == retries:
						time.sleep(self.CONFIG.get_config('sleep', 'time', '1'))
					else:
						error = True
						break
			if error:
				return ''
			content = a.content
		if content:
			bsobject = bs(content, 'lxml')
		if bsobject:
			name = bsobject.find('div', {'style':'width: 90%'})
			debug(name = name)
			if name:
				name = name.find('h2')
				debug(name = name)
				if name:
					name = re.sub("Download File", '', name.text, re.I)
					debug(name = name)
					if name:
						name = name.strip()
						debug(name = name)
		return name

	@classmethod
	def get_version(self):
		if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), '__version__.py')):
			import __version__
			version = __version__.version
			return version
		else:
			return "UNKNOWN"

	@classmethod
	def generate(self, url = None, id = None, timeout = 10, max_try = 10, downloadit = False, download_path = os.getcwd(), saveas = None):
		debug(url = url)
		if not url and not id:
			print(make_colors("No URL or ID provider !", 'lw', 'r'))
			return '', ''
		debug(url = url)
		debug(id = id)
		if url:
			id = urlparse(url).path.split("/")[-1]
		elif id and not url:
			url = self.URL + str(id)
		debug(id = id)
		debug(url = url)

		if not "www." in url:
			url_parse = urlparse(url)
			url = url_parse.scheme + "://www." + url_parse.netloc + url_parse.path
		debug(url = url)
		# pause()
		error = False

		headers_str = """upgrade-insecure-requests:	1
		user-agent:	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36
		accept:	text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
		sec-fetch-site:	none
		sec-fetch-mode:	navigate
		sec-fetch-user:	?1
		sec-fetch-dest:	document
		accept-encoding:	gzip, deflate
		accept-language:	en-US,en;q=0.9,id;q=0.8,ru;q=0.7
		cookie:	cookieconsent_status=dismiss"""
		self.SESSION.headers.update(self.set_header(headers_str))
		# self.BAR.start()

		if url:
			n = 1
			# self.BAR.max_value = max_try
			while 1:
				try:
					a = self.SESSION.get(url, headers = self.set_header(headers_str), timeout = timeout)
					# self.BAR.update(10, task = make_colors("requests 1", 'lw', 'r'), subtask = make_colors('finish', 'y'))		
					break
				except:
					print(traceback.format_exc())
					tp, vl, tr = sys.exc_info()
					error_type = vl.__class__.__name__
					# print(make_colors("ERROR Requests 1:", 'lw', 'r') + " " + make_colors(error_type, 'b', 'y'))
					task = make_colors("Start", 'y')
					subtask = make_colors("Get", 'lg')
					# self.BAR.update(n, task = make_colors("requests 1", 'lw', 'r'), subtask = make_colors('get', 'y'))
					n+=1
					if n == max_try:
						# print(make_colors("Error get [0]:", 'lw', 'r') + " " + make_colors(url, 'ly') + " [" + make_colors("MAX ATTEMPT !", 'lw', 'bl') + "]")
						error = True
						break
		
		if error:
			return False
		
		content = a.content
		if any('debug' in i.lower() for i in  os.environ):
			with open('result1.html', 'wb') as f:
				f.write(content)
		
		headers_result0 = a.headers
		debug(headers_result0 = headers_result0)
		b = bs(content, 'lxml')
		form = b.find('form', {'id':'form'}) or b.find('form', {'class':'mt-4'})
		debug(form = form)
		if not form:
			AssertionError(make_colors("Error get form !", 'lw', 'r'))
		data = {}
		inputs = form.find_all('input')
		debug(inputs = inputs)
		for i in inputs:
			data.update({
				i.get('name') : i.get('value')
			})
		debug(data = data)
		cookies = self.SESSION.cookies.get_dict()
		debug(cookies = cookies)
		headers_cookies = ''
		if not cookies.get('lang'):
			headers_cookies = "lang=english; "
		if not cookies.get("cookieconsent_status"):
			headers_cookies += "cookieconsent_status=dismiss; "
		if cookies:
			for co in cookies:
				headers_cookies += co + "=" + cookies.get(co) + "; "
		if headers_cookies[-2:] == "; ":
			headers_cookies = headers_cookies[:-2]
		debug(headers_cookies = headers_cookies)
		
		header_str = """cache-control:	max-age=0
		upgrade-insecure-requests:	1
		origin:	https://www.mp4upload.com
		content-type:	application/x-www-form-urlencoded
		user-agent:	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36
		accept:	text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
		sec-fetch-site:	same-origin
		sec-fetch-mode:	navigate
		sec-fetch-user:	?1
		sec-fetch-dest:	document
		referer:	{}
		accept-encoding:	gzip, deflate
		accept-language:	en-US,en;q=0.9,id;q=0.8,ru;q=0.7
		cookie:	{}""".format("https://www.mp4upload.com" + urlparse(url).path, headers_cookies)
		headers = self.set_header(header_str)
		debug(headers = headers)
		self.SESSION.headers.update(headers)
		# pause()
		n = 1
		error = False
		while 1:
			try:
				a1 = self.SESSION.post(url, data = data, headers = headers, timeout = timeout)
				# self.BAR.update(10, task = make_colors("requests 1", 'lw', 'r'), subtask = make_colors('finish', 'y') + " ")		
				break
			except:
				# print("ERROR:", traceback.format_exc())
				tp, vl, tr = sys.exc_info()
				error_type = vl.__class__.__name__
				# print(make_colors("ERROR Requests 2:", 'lw', 'r') + " " + make_colors(error_type, 'b', 'y'))
				# self.BAR.update(n, task = make_colors("requests 2", 'lw', 'r'), subtask = make_colors('get', 'y'))
				n+=1
				if n == max_try:
					# print(make_colors("Error get [1]:", 'lw', 'r') + " " + make_colors(url, 'ly') + " [" + make_colors("MAX ATTEMPT !", 'lw', 'bl') + "]")
					error = True
					break
		if error:
			return False
		
		scode = a1.status_code
		debug(scode = scode)
		content1 = a1.content
		# with open("result.html1", "wb") as f:
		# 	f.write(content1)
		# sprint(content1)
		headers_result1 = a1.headers
		debug(headers_result1 = headers_result1)
		b1 = bs(content1, 'lxml')
		form2 = b1.find('form', {'name':'F1'})
		debug(form2 = form2)
		# pause()
		if not form2:
			# AssertionError(make_colors("Error get form !", 'lw', 'r'))
			print(make_colors("Error get form !", 'lw', 'r'))
			return ''
			# return self.home(url)
		data1 = {}
		inputs1 = form2.find_all('input')
		for i in inputs1:
			data1.update({
				i.get('name') : i.get('value')
			})
		debug(data1 = data1)
		cookies = self.SESSION.cookies.get_dict()
		headers_cookies1 = ""
		if not cookies.get('lang'):
			headers_cookies1 = "lang=english; "
		if not cookies.get("cookieconsent_status"):
			headers_cookies1 += "cookieconsent_status=dismiss; "
		if cookies:
			for co in cookies:
				headers_cookies1 += co + "=" + cookies.get(co) + "; "
		headers_cookies1 = headers_cookies1[:-2]
		debug(cookies = cookies)
		debug(headers_cookies1 = headers_cookies1)
		headers.update({'cookie':headers_cookies1})
		debug(headers = headers)
		# pause()

		error = False
		n = 1
		verify = True
		
		while 1:
			try:
				debug(verify = verify)
				a2 = requests.post(url, data = data1, stream = True, verify = verify, headers = headers)
				# self.BAR.update(10, task = make_colors("requests 3", 'lw', 'r'), subtask = make_colors('finish', 'y') + " ")		
				break
			except:
				tp, vl, tr = sys.exc_info()
				error_type = vl.__class__.__name__
				debug(error_type = error_type)
				# print(make_colors("ERROR Requests 3:", 'lw', 'r') + " " + make_colors(error_type, 'b', 'y'))
				if str(error_type) == 'SSLError':
					verify = False
					# self.BAR.update(n, task = make_colors("ERROR requests 3", 'lw', 'r'), subtask = make_colors(error_type, 'lw', 'r'))
				# else:
					# self.BAR.update(n, task = make_colors("requests 3", 'lw', 'r'), subtask = make_colors('get', 'y'))		
				if os.getenv('DEBUG'):
					print("ERROR:", traceback.format_exc())
				n+=1
				if n == max_try:
					# print(make_colors("Error get [2]:", 'lw', 'r') + " " + make_colors(url, 'ly') + " [" + make_colors("MAX ATTEMPT !", 'lw', 'bl') + "]")
					error = True
					break
		if error:
			return False
		
		scode1 = a2.status_code
		debug(scode1 = scode1)
		url_result = a2.url
		debug(url_result = url_result)
		headers2 = a2.headers
		# content2 = a2.content
		# debug(content2 = content2)
		debug(headers2 = headers2)
		debug(url_result = url_result)
		if url_result:
			if downloadit:
				header_str = f"""User-Agent: Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko
					Accept: */*
					Accept-Encoding: identity
					Accept-Language: en-US
					Accept-Charset: *
					Referer: {os.path.dirname(url_result)}"""
				debug(header_str = header_str)
				sess_cookies = self.SESSION.cookies.get_dict()
				debug(sess_cookies = sess_cookies)
				cookies = ''
				for i in sess_cookies:
					cookies += f'{i}={sess_cookies.get(i)}; '
				cookies += 'cookieconsent_status=dismiss'
				debug(cookies = cookies)
				header = ''
				#headers = dict(self.SESSION.headers)
				headers = self.set_header(header_str)
				debug(headers = headers)
				#headers.update({'cookie': cookies})
				#headers.update({'content-type': 'video/mp4',})
				#debug(session_headers = headers)
				for b in headers:
					header += f'{b}="{headers.get(b)}"&'
				debug(header = header)
				if not sys.platform == 'win32':
					download(url_result, download_path, saveas, cookie = cookies, postData = header)
				else:
					#download(url_result, download_path, saveas, cookies = headers2)
					download(url_result, download_path, saveas, url_result, a2.cookies.get_dict(), headers2)
		
		return url_result

	@classmethod
	def usage(self):
		parser = argparse.ArgumentParser(formatter_class = CustomRichHelpFormatter)
		parser.add_argument('URL', action = 'store', help = make_colors('url', 'lw', 'r') + ' or ' + make_colors('file_code', 'lw', 'bl') + ' example:' + make_colors("https://mp4upload.com/", 'r') + make_colors("gm2emy2qhjrn", 'bl') + " " + make_colors("type 'c' for get url/id from clipboard", 'ly'), nargs='?')
		parser.add_argument('-d', '--download', help = 'Download it', action = 'store_true')
		parser.add_argument('-p', '--download-path', action = 'store', help = 'Save download to dir, default: {}'.format(make_colors(os.getcwd(), 'y')), default = os.getcwd())
		parser.add_argument('-c', '--clipboard', action = 'store_true', help = 'Copy generated url to clipboard')
		parser.add_argument('-t', '--timeout', action = 'store', help = 'timeout connection, default: 10 seconds', default = 10, type = int)
		parser.add_argument('-r', '--retries', action = 'store', help = 'max connection retries, default: 10 seconds', default = 10, type = int)
		parser.add_argument('-s', '--saveas', action = 'store', help = 'save file as name')
		parser.add_argument('-v', '--version', action = 'store_true')
		if len(sys.argv) == 1:
			parser.print_help()
		else:
			download_url = ''
			
			args = parser.parse_args()
			if args.version:
				print(f"VERSION: {self.get_version()}")
				return 
			if not args.URL:
				print("No URL !")
				return 
			saveas = args.saveas
			URL = None
			if args.URL == 'c': args.URL = clipboard.paste()
			if args.clipboard: clipboard.copy(download_url)
			
			download_path = args.download_path
			if not download_path: download_path = self.CONFIG.get_config('download', 'path', os.getcwd())
			if not args.download_path == self.CONFIG.get_config('download', 'path', os.getcwd()) and args.download_path == os.getcwd(): download_path = self.CONFIG.get_config('download', 'path', os.getcwd())
			
			URL = args.URL
			
			if URL[:4] == 'http':
				download_url = self.generate(URL, None, args.timeout, args.retries, args.download, download_path, args.saveas)
				if not saveas: saveas = self.getname(URL)	
			else:
				download_url = self.generate(None, URL, args.timeout, args.retries, args.download, download_path, args.saveas)
				URL = "https://mp4upload.com/" + URL
				URL = re.sub("//", "/", URL)
				if not saveas: saveas = self.getname(None, args.URL)
			
			print(make_colors("URL      :", 'b', 'lc') + " " + make_colors(URL, 'lc'))
			print(make_colors("NAME     :", 'b', 'lg') + " " + make_colors(saveas, 'lg'))
			print(make_colors("GENERATED:", 'lw', 'r') + " " + make_colors(download_url, 'c'))
			if args.clipboard:
				clipboard.copy(download_url)
			
			
def usage():
	return Mp4upload.usage()

if __name__ == '__main__':
	Mp4upload.usage()
	# Mp4upload.format_cookie({"lang":"english", "aff":"148106"})
	# Mp4upload.home("https://www.mp4upload.com/fp318mgcm5m7")
	# Mp4upload.generate("https://mp4upload.com/gm2emy2qhjrn")
	# Mp4upload.getname("https://mp4upload.com/gm2emy2qhjrn")
	# Mp4upload.generate("https://www.mp4upload.com/fp318mgcm5m + " "7")
