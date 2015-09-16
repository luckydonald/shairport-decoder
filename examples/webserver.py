# -*- coding: utf-8 -*-
__author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)

from luckydonaldUtils.encoding import to_binary
from luckydonaldUtils import py3
from luckydonaldUtils import dependencies
from luckydonaldUtils.images.color import most_frequent_color

dependencies.import_or_install("PIL", "Pillow")
from PIL import Image

dependencies.import_or_install("webbrowser")
import webbrowser

from threading import Thread

from shairportdecoder.remote import AirplayRemote
from shairportdecoder.metadata import Infos
from shairportdecoder import decoder
from shairportdecoder.decoder import Processor
from time import sleep

if py3:
	from socketserver import TCPServer
	from http.server import SimpleHTTPRequestHandler
else:
	from SimpleHTTPServer import SimpleHTTPRequestHandler
	from SocketServer import TCPServer
from socket import error

from datetime import datetime  # check if isinstance date for encoding json
from os import path # locate script folder
import os.path
from io import BytesIO # coverart to PIL.open

from json import dumps as json_dump
folder = path.join(path.dirname(path.realpath(__file__)), (path.basename(__file__).split(".")[0] + "_files"))
logger.info("Dir with static files should be at {path}.".format(path=folder))

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):

	def log_message(self, format, *args):
		logger.info("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format%args))

	def log_request(self, code='-', size='-'):
		logger.debug('%s - - "%s" %s %s', self.client_address[0], self.requestline, str(code), str(size))

	def log_error(self, format, *args):
		logger.error("%s - - %s" % (self.client_address[0], format%args))

	def __init__(self, request, client_address, server):
		if py3:
			super(MyHTTPRequestHandler, self).__init__(request, client_address, server)
		else:
			SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

	@property
	def info(self):
		"""
		Wrapper becase I am lazy to type it every time...
		:rtype: Infos
		"""
		assert isinstance(self.server.processor.info, Infos)
		return self.server.processor.info

	def do_GET(self):
		parts = self.path.split("?", 1) #py3: self.path.split("?", maxsplit=1)
		self.path = parts[0]
		if len(parts)>1:
			self.query = parts[1]
		else:
			self.query = None
		logger.debug("Hit {url}".format(url=self.path))
		if self.path == "/":
			msg = """<html><head>    <title>OMG PONIES!</title>    </head><body>
			<h1>YO!</h1>
			<a href="info.html">Ajax Interface</a><br />
			<a href="info_noscript.html">No-Script Interface</a><br />
			</body></html>"""
			self.do_write_text(msg)
			return
		elif self.path.endswith("/cover.img.json"):
			msg = json_dump(self.info.songcoverart.as_dict(base64=True))
			self.do_write_text(msg)
			return
		elif self.path.endswith("/cover.color.json"):
			def rgb_to_array(r, g, b):
				return {"r": r, "g": g, "b": b}
			def color_result_to_array(img):
				return rgb_to_array(color[1][0],color[1][1],color[1][2])
			if not self.info.songcoverart.binary:
				meta_dict = {"colors": [rgb_to_array(0,0,0),rgb_to_array(255,255,255), rgb_to_array(255,255,255)]}
			else:
				img = Image.open(BytesIO(self.info.songcoverart.binary))
				colors = most_frequent_color(img, colors=3)
				meta_dict = {"colors": list([color_result_to_array(color) for color in colors])}
			msg = json_dump(meta_dict)
			self.do_write_text(msg)
			return
		elif self.path.endswith("/cover.json"):
			msg = json_dump(self.info.songcoverart.as_dict())
			self.do_write_text(msg)
			return

		elif self.path.endswith("/cover.png"):
			cover = self.info.songcoverart
			if cover:
				if cover.mime == "image/jpeg":
					self.send_response(307)
					self.send_header("Location", "cover.jpg")
					self.end_headers()
					return
				return self.do_write_text(cover.binary, content_type=cover.mime, is_binary=True)
			return self.do_write_default_cover_png()

		elif self.path.endswith("/cover.jpg") or self.path.endswith("/cover.jpe") or self.path.endswith("/cover.jpeg"):
			cover = self.info.songcoverart
			if not cover or cover.mime == "image/png":
				self.send_response(307)
				self.send_header("Location", "cover.png")
				self.end_headers()
				return
			return self.do_write_text(cover.binary, content_type=cover.mime, is_binary=True)

		elif self.path.endswith("/cover.img"):
			cover = self.info.songcoverart
			if cover:
				return self.do_write_text(cover.binary, content_type=cover.mime, is_binary=True)
			self.do_write_default_cover_png()
			return
		elif self.path.endswith("/volume.json"):
			msg = json_dump({"info": "volume", "software": self.info.volume, "airplay": self.info.airplayvolume})
			self.do_write_text(msg)
		elif self.path.endswith("/meta.json"):
			skiplist = ["songcoverart"]
			meta_dict = {}
			for key, value in self.info.__dict__.items():  # this eats memory on python 2
				if key in skiplist:
					continue
				if isinstance(value, datetime):
					meta_dict[key] = str(value.isoformat())
				else:
					meta_dict[key] = value
			msg = json_dump(meta_dict)
			self.do_write_text(msg)
			return
		elif self.path.endswith("/text"):
			assert isinstance(self.info, Infos)
			msg = self.info.to_simple_string()
			self.do_write_text(msg)
			return
		elif self.path.endswith("/debug_breakpoint"):
			self.do_write_text("This is a debug line with an breakpoint added in PyCharm.")
			return
		else:
			self.path = folder + self.path  #  e.g. localhost/123/foo.bar -> /path/to/script/webserver_files/123/foo.bar
			logger.debug("Requested file {file}".format(file = self.path))
			f = self.send_head()  # this handles 404'ing for us
			if f:
				try:
					self.copyfile(f, self.wfile)
				finally:
					f.close()
				#end try
			#end if
		#end if-else 'switch'
	#end def

	def translate_path(self, path):
		if os.path.exists(path):
			return path
		if py3:
			super(MyHTTPRequestHandler, self).translate_path(path)
		else:
			SimpleHTTPRequestHandler.translate_path(self, path)
		#half = int(len(path)/2)
		#if path.startswith("/") and len(path) % 2 == 0 and path[half:] == path[:half]:
		#	return path[half:]
		return path
	#end def

	def do_write_default_cover_png(self):
		try:
			cover = open(os.path.join(os.path.join(folder,"img"),"no_cover.png"))
			msg = cover.read()
			cover.close()
			self.do_write_text(msg)
			self.send_response(200)
			self.end_headers()
			return
		except Exception as e:
			self.send_response(404)
			self.do_write_text("Default Cover Exception: \"" + e.message + "\"")
			self.end_headers()
		return

	def do_write_text(self, msg, content_type="text/plain", is_binary=False):
		# Now do servery stuff.
		if not is_binary:
			msg = to_binary(msg)
		if msg is None:
			self.send_response(404)
			self.end_headers()
			return
		self.send_response(200)
		self.send_header("Content-type", content_type)
		self.send_header("Content-Length", str(len(msg)))
		self.end_headers()
		self.wfile.write(msg)
		return
	#end def


class http_shairport_server(Processor):
	def __init__(self, port, pipe_file):
		super(http_shairport_server, self).__init__()
		self.port = port
		self.pipe_file = pipe_file
		self.remote = None

	def run(self):
		thread = Thread(target=self.run_server)
		thread.daemon = True
		thread.start()
		self.run_processor()

	def run_processor(self):
		self.add_listener(self.event_processor)  # function `event_processor` defined bellow.
		self.parse(self.pipe_file)  # this will probably run forever.


	def run_server(self):
		handler = MyHTTPRequestHandler
		#httpd = TCPServer(("", self.port), handler)
		started = False
		while not started:
			try:
				httpd = TCPServer(("", self.port), handler)
				started = True
			except error as e:
				if e.errno in [48, 98]:
					logger.warn("Starting Server failed. Address already in use. Retrying.")
					sleep(1)
				else:
					raise

		webbrowser.open("http://localhost:{port}/info.html".format(port=self.port))
		logger.info("Started serving web interface at port {port}.".format(port=self.port))
		httpd.processor = self
		httpd.serve_forever()

	def event_processor(self, event_type, info):
		"""
		This you can use to put into `add_listener(func)`.
		It will then print the events.
		:param event_type:
		:param info:
		:return:
		"""
		assert(isinstance(info, Infos))
		if event_type == decoder.VOLUME:
			print("Changed Volume to {vol}.".format(vol = info.volume))
		elif event_type == decoder.COVERART:
			print("Got Coverart.")
		elif event_type == decoder.META:
			print("Got Metadata,\n{meata}".format(meata=info.to_simple_string())) # lol, meat typo.
		elif event_type == decoder.META_START:
			print("Started Meta block")
		elif event_type == decoder.CLIENT_REMOTE_AVAILABLE:
			print("Got Airplay Remote informations.")
			self.remote = AirplayRemote.from_dacp_id(self.info.dacp_id, self.info.active_remote)
		#end if "switch event_type"
	#end def




import sys  # launch arguments
def main(argv):
	if argv is None or not argv:
		argv = sys.argv[1:]
	if len(argv) > 0 and argv[0]:
		pipe_file = argv[0]
	else:
		pipe_file = "/tmp/shairport-sync-metadata"
	logging.add_colored_handler(level=logging.INFO)
	server = http_shairport_server(8080, pipe_file)
	server.run()





if __name__ == "__main__":
	main([])
