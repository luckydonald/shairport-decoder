# -*- coding: utf-8 -*-
from threading import Thread

__author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)

from luckydonaldUtils.encoding import to_binary
from luckydonaldUtils import py2

from shairportdecoder import Processor
from shairportdecoder.decode import Infos
import shairportdecoder


try:  #py2
	from SimpleHTTPServer import SimpleHTTPRequestHandler
except ImportError:  # py3
	from http.server import SimpleHTTPRequestHandler
#end try
try:  #py2
	from SocketServer import TCPServer
except ImportError:  # py3
	from socketserver import TCPServer
#end try

from os import path # locate script folder
import os.path
from json import dumps as json_dump
folder = path.join(path.dirname(path.realpath(__file__)), (path.basename(__file__).split(".")[0] + "_files"))
logger.info("Dir with static files should be at {path}.".format(path=folder))

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
	def __init__(self, request, client_address, server):
		super().__init__(request, client_address, server)
	@property
	def info(self):
		"""
		Wrapper becase I am lazy to type it every time...
		:rtype: Infos
		"""
		assert isinstance(self.server.processor.info, Infos)
		return self.server.processor.info

	def do_GET(self):
		logger.info("Hit {url}".format(url=self.path))
		if self.path == "/":
			msg = "YO!"
			print(self.path)
			self.do_write_text(msg)

		elif self.path.endswith("/cover.img.json"):
			msg = json_dump(self.info.songcoverart.as_dict(True))
			self.do_write_text(msg)
			return

		elif self.path.endswith("/cover.json"):
			msg = json_dump(self.info.songcoverart.as_dict())
			self.do_write_text(msg)
			return

		elif self.path.endswith("/cover.png"):
			cover = self.info.songcoverart
			if cover.mime == "image/jpeg":
				self.send_response(307)
				self.send_header("Location", "cover.jpg")
				self.end_headers()
				return
			if cover:
				return self.do_write_text(cover.binary, content_type=cover.mime, is_binary=True)
			self.do_write_default_cover_png()

		elif self.path.endswith("/cover.jpg"):
			cover = self.info.songcoverart
			if cover.mime == "image/png":
				self.send_response(307)
				self.send_header("Location", "cover.png")
				self.end_headers()
				return
			if cover:
				return self.do_write_text(cover.binary, content_type=cover.mime, is_binary=True)
			self.do_write_default_cover_jpg()

		elif self.path.endswith("/cover.img"):
			cover = self.info.songcoverart
			if cover:
				return self.do_write_text(cover.binary, content_type=cover.mime, is_binary=True)
			self.do_write_default_cover_jpg()

		elif self.path.endswith("/volume.json"):
			msg = json_dump({"info": "volume", "software": self.info.volume, "airplay": self.info.airplayvolume})
			self.do_write_text(msg)
		elif self.path.endswith("/meta.json"):
			if py2:
				meta_dict = { key: value for key, value in self.info.__dict__.iteritems() if key != "songcoverart"}  # untested for py2
			else:
				meta_dict = { key: value for key, value in self.info.__dict__.items() if key != "songcoverart"}
			msg = json_dump(meta_dict)
			self.do_write_text(msg)
		elif self.path.endswith("/text"):
			assert isinstance(self.info, Infos)
			msg = self.info.to_simple_string()
			self.do_write_text(msg)
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
		path = super(MyHTTPRequestHandler, self).translate_path(path)
		#half = int(len(path)/2)
		#if path.startswith("/") and len(path) % 2 == 0 and path[half:] == path[:half]:
		#	return path[half:]
		return path
	#end def

	def do_write_default_cover_png(self):
		self.send_response(404)
		self.end_headers()

	def do_write_default_cover_jpg(self):
		self.send_response(404)
		self.end_headers()

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

	def run(self):
		thread = Thread(target=self.run_server, daemon=True)
		thread.start()
		self.run_processor()

	def run_processor(self):
		self.add_listener(event_processor)  # function `event_processor` defined bellow.
		self.parse(self.pipe_file)  # this will probably run forever.


	def run_server(self):
		handler = MyHTTPRequestHandler
		httpd = TCPServer(("", self.port), handler)
		print("HTTP> Starting serving at port {port}.".format(port=self.port))
		httpd.processor = self
		httpd.serve_forever()





import sys  # launch arguments

def main(argv):
	if argv is None or not argv:
		argv = sys.argv[1:]
	if len(argv) > 0 and argv[0]:
		pipe_file = argv[0]
	else:
		pipe_file = "/tmp/shairport-sync-metadata"
	server = http_shairport_server(8080, pipe_file)
	server.run()


def event_processor(event_type, info):
	"""
	This you can use to put into `add_listener(func)`.
	It will then print the events.
	:param event_type:
	:param info:
	:return:
	"""
	assert(isinstance(info, Infos))
	if event_type == shairportdecoder.VOLUME:
		print("Changed Volume to {vol}.".format(vol = info.volume))
	elif event_type == shairportdecoder.COVERART:
		print("Got Coverart.")
	elif event_type == shairportdecoder.META:
		print("Got Metadata,\n{meata}".format(meata=info.to_simple_string())) # lol, meat typo.
	#end if "switch event_type"
#end def


if __name__ == "__main__":
	main([])
