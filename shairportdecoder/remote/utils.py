# -*- coding: utf-8 -*-
__author__ = 'luckydonald'


import threading
import time
from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)


class ResultWaiter(threading.Thread):
	def i_am_a_callback(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs
		self.callback_callback()


	def __init__(self, listener, browser):#callback_callback):
		super(ResultWaiter, self).__init__()
		#self.callback_callback = callback_callback
		self.listener = listener
		self.browser = browser

	def run(self):
		while True:
			if self.listener.info:
				#self.browser.cancel()
				break
			time.sleep(1)


class ServiceListener(object):
	def __init__(self, expected_name, zeroconf):
		super(ServiceListener, self).__init__()
		self.expected_name = expected_name
		self.zeroconf = zeroconf
		self.info = None

	def remove_service(self, zeroconf, type, name):
		logging.debug("Service %s removed" % (name,))

	def add_service(self, zeroconf, type, name):
		info = zeroconf.get_service_info(type, name)
		self.info = info
		print("Service %s added, service info: %s" % (name, info))