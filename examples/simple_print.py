# -*- coding: utf-8 -*-
__author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)

from shairportdecoder import Processor
from shairportdecoder.decode import Infos
import shairportdecoder






def main(argv):
	if argv is None:
		argv = sys.argv[1:]
	if len(argv) > 0 and argv[0]:
		filename = argv[0]
	else:
		filename = "/tmp/shairport-sync-metadata"
	processor = Processor()
	processor.add_listener(event_processor)  # function `event_processor` defined bellow.
	processor.parse(filename)

#end def main

import sys  # launch arguments

if __name__ == "__main__":
	main(None)


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
		cover_file = info.write_cover_file()
		print("Got Coverart, wrote it to {file} .".format(file = cover_file))
	elif event_type == shairportdecoder.META:
		print("Got Metadata,\n{meata}".format(meata=info.to_simple_string())) # lol, meat typo.
	#end if "switch event_type"
#end def
