# -*- coding: utf-8 -*-
from luckydonaldUtils.encoding import unicode_type
from luckydonaldUtils.logger import logging
from shairportdecoder.metadata import Infos, Item, CoverArt

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)


class Processor(object):

	def __init__(self):
		super(Processor, self).__init__()
		self._listeners = []
		self.info = Infos()
		self.do_quit = False

	# core code reference: (until google code goes finally offline :/ )
	# http://ios5-tutorial.googlecode.com/svn/trunk/OutSourcing/OnlineAudio/%E7%BD%91%E7%BB%9C%E7%94%B5%E5%8F%B0/ReferCode/nto-AirSpeaker/AirTunes/DMAP.m

	def parse(self, filename="/tmp/shairport-sync-metadata"):
		logger.info("Parsing named pipe: {filename}".format(filename=filename))
		temp_line = ""
		while not (self.do_quit):
			with open(filename) as f:
				for line in f:
					if not line.strip().endswith("</item>"):
						temp_line += line.strip()
						continue
					line = temp_line + line
					temp_line = ""
					#print(line)
					self.process_line(line)
					if self.do_quit:
						break

	def process_line(self, line):
		item = Item(line)
		if item is None:
			return
		#print("{type}, {code}".format(type = item.type, code = item.code))
		if not hasattr(item, "type"):
			logger.warn("Got typeless (malformed) data: >>{data}<<".format(data=line))
			return
		if item.type == "ssnc":
			if item.code == "PICT":  # the payload is a picture, either a JPEG or a PNG. Check the first few bytes to see which.
				self.info.songcoverart = CoverArt(binary=item.data, base64=item.data_base64)  # this is not base64, but raw.
				self._trigger_update_event(COVERART)
			elif item.code == "mdst":  # -- a sequence of metadata is about to start
				self._trigger_update_event(META_START)
				#
			elif item.code == "snua":  # -- for example: iTunes/12.2 (Macintosh; OS X 10.9.5)
				self.info.useragent = item.data_str
			elif item.code == "mden":  # -- a sequence of metadata has ended
				assert(self.info is not None)
				self._trigger_update_event(META)
			elif item.code == "pbeg":  # -- play stream begin. Means someone connected? ("prsm" will be send on playing)  No arguments
				#self.info = Infos()  # reset infos
				print("PBEG!")  # see https://github.com/mikebrady/shairport-sync-metadata-reader/issues/5
			elif item.code == "pfls":  # -- pause stream. No arguments(?)
				self.info.playstate = Infos.PAUSE
			elif item.code == "prsm":  # -- play stream start/resume. No arguments
				self.info.playstate = Infos.PLAYING
			elif item.code == "pend":  # -- play stream end. No arguments
				self.info.playstate = Infos.STOPPED
			elif item.code == "pvol":  # -- play volume. The volume is sent as a string
				# "airplay_volume,volume,lowest_volume,highest_volume",
				# where "volume", "lowest_volume" and "highest_volume" are given in dB.
				# The "airplay_volume" is what's sent by the source (e.g. iTunes) to the player,
				# and is from 0.00 down to -30.00, with -144.00 meaning "mute".
				# This is linear on the volume control slider of iTunes or iOS AirPlay.
				airplay_volume, volume, lowest_volume, highest_volume = tuple([float(i) for i in item.data_str.split(',')])
				self.info.volume = -1 if airplay_volume == -144 else ((volume - (lowest_volume)) / (-1* (lowest_volume - highest_volume)))
				self.info.airplayvolume = -1 if airplay_volume == -144 else ((airplay_volume + 30) / 30)
				self._trigger_update_event(VOLUME)
			elif item.code == "daid":  # -- DACP-ID
				self.info.dacp_id = item.data_str
				self._check_remote()
			elif item.code == "acre":  # -- Active-Remote
				self.info.active_remote = item.data_str
				self._check_remote()
			elif item.code in ["prgr"]:
				logger.warn("Found (already familiar) unknown shairport-sync core (ssnc) code \"{code}\", with base64 data {data}. Any Idea what that means?".format(code=item.code, data=item.data_base64))
			else:
				logger.warn("Unknown shairport-sync core (ssnc) code \"{code}\", with base64 data {data}.".format(code=item.code, data=item.data_base64))
				#raise AttributeError("Unknown shairport-sync (ssnc) code \"{code}\", got data {data}.".format(code=item.code, data=item.data_base64))
		elif item.type == "core":  # -- dmap.itemkind
			if item.code == "mikd":  # -- the kind of item.  So far, only '2' has been seen, an audio
				assert item.data_int == 2  # So far, only '2' has been seen.
				self.info.itemkind = item.data_int
			elif item.code == "minm":  # -- dmap.itemname
				self.info.itemname = item.data_str
			elif item.code == "mper":  # -- dmap.persistentid
				self.info.persistentid = item.data_int
			elif item.code == "miid":  # -- dmap.itemid
				self.info.itemid = item.data_int


			elif item.code == "asal":  # -- daap.songalbum
				self.info.songalbum = item.data_str
			elif item.code == "asar":  # -- daap.songartist
				self.info.songartist = item.data_str
			elif item.code == "ascm":  # -- daap.songcomment
				self.info.songcomment = item.data_str
			elif item.code == "asco":  # -- daap.songcompilation
				self.info.songcompilation = item.data_bool
			elif item.code == "asbr":  # -- daap.songbitrate
				self.info.songbitrate = item.data_int
			elif item.code == "ascp":  # -- daap.songcomposer
				self.info.songcomposer = item.data_str
			elif item.code == "asda":  # -- daap.songdateadded
				self.info.songdateadded = item.data_date
			elif item.code == "aspl":  # -- daap.songdateplayed # https://github.com/jkiddo/jolivia/blob/46e53969d4b4bfb4a538511591b9ad2a8f3fca80/jolivia.protocol/src/main/java/org/dyndns/jkiddo/dmp/IDmapProtocolDefinition.java#L154
				self.info.songdateplayed = item.data_date  # I get dates 25 years in the future, year 2040
			elif item.code == "asdm":  # -- daap.songdatemodified
				self.info.songdatemodified = item.data_date
			elif item.code == "asdc":  # -- daap.songdisccount #SongDiscCount, not the being-cheap Discount. lol.
				self.info.songdisccount = item.data_int
			elif item.code == "asdn":  # -- daap.songdiscnumber
				self.info.songdiscnumber = item.data_int
			elif item.code == "aseq":  # -- daap.songeqpreset
				self.info.songeqpreset = item.data_str
			elif item.code == "asgn":  # -- daap.songgenre
				self.info.songgenre = item.data_str
			elif item.code == "asdt":  # -- daap.songdescription
				self.info.songdescription = item.data_str
			elif item.code == "asrv":  # -- daap.songrelativevolume
				self.info.songrelativevolume = item.data_int
			elif item.code == "assr":  # -- daap.songsamplerate
				self.info.songsamplerate = item.data_int
			elif item.code == "assz":  # -- daap.daap.songsize
				self.info.songsize = item.data_int
			elif item.code == "asst":  # -- daap.songstarttime, in ms
				self.info.songstarttime = item.data_int  # in ms
			elif item.code == "assp":  # -- daap.songstoptime
				self.info.songstoptime = item.data_int
			elif item.code == "astm":  # -- daap.songtime, in ms
				self.info.songtime = item.data_int # in ms
			elif item.code == "astc":  # -- daap.songtrackcount
				self.info.songtrackcount = item.data_int
			elif item.code == "astn":  # -- daap.songtracknumber
				self.info.songtracknumber = item.data_int
			elif item.code == "asur":  # -- daap.songuserrating
				self.info.songuserrating = item.data_int
			elif item.code == "asyr":  # -- daap.songyear
				self.info.songyear = item.data_int
			elif item.code == "asfm":  # -- daap.songformat
				self.info.songformat = item.data_str
			elif item.code == "asdb":  # -- daap.songdisabled
				self.info.songdisabled = item.data_bool
			elif item.code == "asdk":  # -- daap.songdatakind
				self.info.songdatakind = item.data_int
			elif item.code == "asbt":  # -- daap.songsbeatsperminute
				self.info.songsbeatsperminute = item.data_int
			elif item.code == "agrp":  # -- daap.songgrouping
				self.info.songgrouping = item.data_str
				self._found_new_info("songgrouping")
			elif item.code == "ascd":  # -- daap.songcodectype
				self.info.songcodectype = item.data_str
			elif item.code == "ascs":  # -- daap.songcodecsubtype
				self.info.songcodecsubtype = item.data_int
			elif item.code == "asct":  # -- daap.songcategory
				self.info.songcategory = item.data_str
			elif item.code == "ascn":  # -- daap.songcontentdescription
				self.info.songcontentdescription = item.data_str
				self._found_new_info("songgrouping")
			elif item.code == "ascr":  # -- daap.songcontentrating
				self.info.songcontentrating = item.data_int
				self._found_new_info("songcontentrating")
			elif item.code == "asri":  # -- daap.songartistid
				self.info.songartistid = item.data_int
			elif item.code == "asai":  # -- daap.songalbumid
				self.info.songalbumid = item.data_int
			elif item.code == "askd":  # -- daap.songlastskipdate
				self.info.songlastskipdate = item.data_date
			elif item.code == "assn":  # -- daap.sortname
				self.info.sortname = item.data_str
			elif item.code == "assu":  # -- daap.sortalbum
				self.info.sortalbum = item.data_str


			elif item.code == "aeNV":  # -- com.apple.itunes.norm-volume
				self.info.itunesnormvolume = item.data_int
			elif item.code == "aePC":  # -- com.apple.itunes.is-podcast
				self.info.itunesispodcast = item.data_bool
			elif item.code == "aeHV":  # -- com.apple.itunes.has-video
				self.info.ituneshasvideo = item.data_bool
			elif item.code == "aeMK":  # -- com.apple.itunes.mediakind
				self.info.itunesmediakind = item.data_int
			elif item.code == "aeSN":  # -- com.apple.itunes.series-name
				self.info.itunesseriesname = item.data_str
			elif item.code == "aeEN":  # -- com.apple.itunes.episode-num-str
				self.info.itunesepisodenumstr = item.data_str


			elif item.code in ["meia", "meip"]:
				logger.warn("Found (already familiar) unknown DMAP-core code: {code}, with base64 data {data}. Any Idea what that means?".format(code=item.code, data=item.data_base64))
			else:
				logger.warn("Unknown DMAP-core code: {code}, with data {data}.".format(code=item.code, data=item.data_base64))
				#raise AttributeError("Unknown DMAP (core) code \"{code}\", data is {data}".format(code=item.code, data=item.data_base64))
			#end if-else
		#end if shairport / if core
		pass
	#end def

	def _found_new_info(self, attr):
		obj = getattr(self.info, attr)
		if	(isinstance(obj, unicode_type) and len(obj) > 0) or \
			(isinstance(obj, int) and obj != 0):
				logger.info("Got unknown value for {attr}, {value}. Please submit an issue, so we can identify the values.".format(attr=attr, value=obj))
		#end if
	#end def

	def _trigger_update_event(self, event_type):
		"""
		Will print value, if no Listener is given.
		Else the listeners will be called.
		"""
		if not self._listeners or len(self._listeners) == 0:
			logger.debug("No listeners attached.")
		else:  # we have _listeners
			for listener in self._listeners:
				listener(event_type, self.info)
		#end if not _listeners


	def add_listener(self, function):
		"""
		Adds a listener called when data is receiver.
		:param function: Will be called when an update got received.
		You function have to have 2 arguments:
		```function(event_type, info)```
		event_type: META, VOLUME or COVERART
		info: The collected Metadata. Type is decode.Infos
		"""
		if not self._listeners or len(self._listeners) == 0:
			self._listeners = []  # make sure it is really exists. Is unneeded, because is definitely init'ed, but who cares?
		self._listeners.append(function)

	def remove_listener(self, function):
		"""
		Removes a listener again.
		:param function: The function added with `add_listener(func)` before.
		"""
		self._listeners.remove(function)

	def _check_remote(self):
		if self.info.dacp_id is not None and self.info.active_remote is not None:
			logger.debug("DACP Remote client available.")
			self._trigger_update_event(CLIENT_REMOTE_AVAILABLE)
#end class

# because py2 doesn't have Enums... :(
VOLUME = "volume"
META = "meta end"
META_START = "meta start"
COVERART = "coverart"
CLIENT_REMOTE_AVAILABLE = "client remote available"