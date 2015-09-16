# -*- coding: utf-8 -*-

__author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
from luckydonaldUtils.encoding import to_native as n  # pip install luckydonald-utils
from luckydonaldUtils.dependencies import import_or_install  # pip install luckydonald-utils
from luckydonaldUtils.network.ip import binary_ip_to_str  # pip install luckydonald-utils
logger = logging.getLogger(__name__)
import requests
from shairportdecoder.remote.utils import ServiceListener, ResultWaiter

zeroconf = import_or_install("zeroconf", "zeroconf")
from zeroconf import ServiceBrowser, Zeroconf

airplay_zeroconf_service = "_dacp._tcp.local."  # local?
airplay_prefix = "iTunes_Ctrl_{dacp_id}"
base_url = "{host}:{port}/ctrl-int/1/{command}"


class AirplayRemote(object):
	"""
	GET /ctrl-int/1/pause HTTP/1.1
	Active-Remote: 1986535575
	"""

	def __init__(self,  token, host, port):
		super(AirplayRemote, self).__init__()
		self.token = token
		self.host = host
		self.port = port

	@classmethod
	def from_dacp_id(cls, dacp_id, token):
		zeroconf = Zeroconf()
		try:
			listener = ServiceListener(airplay_prefix.format(dacp_id=dacp_id), zeroconf)
			browser = ServiceBrowser(zeroconf, airplay_zeroconf_service, listener)
			wait_for_it = ResultWaiter(listener, browser)
			wait_for_it.start()
			wait_for_it.join()
			del wait_for_it
		finally:
			zeroconf.close()
		assert(listener.info)  # fails if service was not found.
		host = "http://" +  binary_ip_to_str(listener.info.address)
		port = listener.info.port
		return AirplayRemote(token, host, port)

	def begin_fast_forward(self):
		"""
		begin fast forward
		:return: None
		"""
		return self.do("beginff")

	def begin_rewind(self):
		"""
		begin rewind
		:return: None
		"""
		return self.do("beginrew")

	def previous_item(self):
		"""
		play previous item in playlist
		:return: None
		"""
		return self.do("previtem")

	def next_rewind(self):
		"""
		play next item in playlist
		:return: None
		"""
		return self.do("pause")

	def pause(self):
		"""
		pause playback
		:return: None
		"""
		return self.do("pause")

	def play_pause(self):
		"""
		toggle between play and pause
		:return: None
		"""
		return self.do("playpause")

	def play(self):
		"""
		start playback
		:return: None
		"""
		return self.do("play")

	def stop(self):
		"""
		stop playback
		:return: None
		"""
		return self.do("stop")

	def play_resume(self):
		"""
		play after fast forward or rewind
		:return: None
		"""
		return self.do("playresume")

	def shuffle_songs(self):
		"""
		shuffle playlist
		:return: None
		"""
		return self.do("shuffle_songs")

	def volume_down(self):
		"""
		turn audio volume down
		:return: None
		"""
		return self.do("volumedown")

	def volume_up(self):
		"""
		turn audio volume up
		:return: None
		"""
		return self.do("volumeup")


	def do(self, command):
		"""
		Send a request to the api.

		:param action:
		:param data:
		:param query:
		:return:
		"""
		headers = {"Active-Remote": self.token, "Easter-Egg": "http://flutterb.at/4458"}
		url = base_url.format(command=n(command), host=self.host, port=self.port, headers=headers)
		r = requests.get(url, verify=False)  # Allow unsigned certificates.
		return r


import sys  # launch arguments

def main(argv):
	if argv is None:
		argv = sys.argv
	return "THIS IS AN EXAMPLE, EDIT THE DACP-ID. ELSE IT WILL NOT TERMINATE. WHY AM I WRITING CAPSLOCK?"
	example = AirplayRemote.from_dacp_id(dacp_id="1595DA80A46BF32B", token="todo: example here")
	example.volume_down()



if __name__ == "__main__":
	main([])

