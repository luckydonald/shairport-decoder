# -*- coding: utf-8 -*-
__author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)


filename = '/Users/luckydonald/Downloads/covershit.xml'
filename = "/tmp/shairport-sync-metadata"
#filename = "/tmp/dumpf.foorb"

import xml.etree.ElementTree as xml
from DictObject import DictObject
from luckydonaldUtils.files import open_file_folder
from luckydonaldUtils.encoding import to_unicode, to_binary, unicode_type
from luckydonaldUtils.xml import etree_to_dict

from base64 import decodebytes, encodebytes
from datetime import datetime

import sys  # launch arguments
import tempfile  # write cover image to temp file



def main(argv):
	if argv is None:
		argv = sys.argv[1:]
	#bla
	temp_line = ""
	furb = Foo()
	with open(filename) as f:
		for line in f:
			if not line.strip().endswith("</item>"):
				temp_line += line.strip()
				continue
			line = temp_line + line
			temp_line = ""
			#print(line)
			furb.process_line(line)

#end def main



class Foo(object):

	def __init__(self):
		super().__init__()
		self.info = Infos()

	# core code reference: (until google code goes finally offline :/ )
	# http://ios5-tutorial.googlecode.com/svn/trunk/OutSourcing/OnlineAudio/%E7%BD%91%E7%BB%9C%E7%94%B5%E5%8F%B0/ReferCode/nto-AirSpeaker/AirTunes/DMAP.m

	def process_line(self, line):
		item = Item(line)
		if item is None:
			return
		#print("{type}, {code}".format(type = item.type, code = item.code))
		if item.type == "ssnc":
			if item.code == "pfls":  # play stream flush.
				pass
			elif item.code == "PICT":  # the payload is a picture, either a JPEG or a PNG. Check the first few bytes to see which.
				self.info.songcoverart = item.data
			elif item.code == "mdst":  # -- a sequence of metadata is about to start
				self.info = Infos()
				pass
			elif item.code == "snua":  # -- for example: iTunes/12.2 (Macintosh; OS X 10.9.5)
				self.info.useragent = item.data_str


			elif item.code == "mden":  # -- a sequence of metadata has ended
				assert(self.info is not None)
				self.info.publish()
			elif item.code == "pbeg":  # -- play stream begin. No arguments
				self.info.playstate = Infos.PLAYING
			elif item.code == "prsm":  # -- play stream resume. No arguments
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
				print(self.info.volume)
				self.info.volume = -1 if airplay_volume == -144 else (volume - (lowest_volume)) / (-1* (lowest_volume - highest_volume))
				self.info.airplayvolume = -1 if airplay_volume == -144 else ((airplay_volume + 30) / 30) * 100
			elif item.code in ["prgr", "daid"]:
				logger.warn("KNOWN unknown shairport-sync (ssnc) code \"{code}\", with data {data}.".format(code=item.code, data=item.data_base64))
			else:
				logger.warn("Unknown shairport-sync (ssnc) code \"{code}\", with data {data}.".format(code=item.code, data=item.data_base64))
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
				self.found_new_info("songgrouping")
			elif item.code == "ascd":  # -- daap.songcodectype
				self.info.songcodectype = item.data_str
			elif item.code == "ascs":  # -- daap.songcodecsubtype
				self.info.songcodecsubtype = item.data_int
			elif item.code == "asct":  # -- daap.songcategory
				self.info.songcategory = item.data_str
			elif item.code == "ascn":  # -- daap.songcontentdescription
				self.info.songcontentdescription = item.data_str
				self.found_new_info("songgrouping")
			elif item.code == "ascr":  # -- daap.songcontentrating
				self.info.songcontentrating = item.data_int
				self.found_new_info("songcontentrating")
			elif item.code == "asri":  # -- daap.songartistid
				self.info.songartistid = item.data_int
			elif item.code == "asai":  # -- daap.songalbumid
				self.info.songalbumid = item.data_int
			elif item.code == "askd":  # -- daap.songlastskipdate
				self.info.songlastskipdate = item.data_date

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
				logger.warn("KNOWN unknown DMAP-core code: {code}, with data {data}.".format(code=item.code, data=item.data_base64))
			else:
				logger.warn("Unknown DMAP-core code: {code}, with data {data}.".format(code=item.code, data=item.data_base64))
				#raise AttributeError("Unknown DMAP (core) code \"{code}\", data is {data}".format(code=item.code, data=item.data_base64))
			#end if-else
		#end if shairport / if core
		pass
	#end def

	def found_new_info(self, attr):
		obj = getattr(self.info, attr)
		if	(isinstance(obj, unicode_type) and len(obj) > 0) or \
			(isinstance(obj, int) and obj != 0):
				logger.info("Got unknown value for {attr}, {value}. Please submit an issue, so we can identify the values.".format(attr=attr, value=obj))
		#end if
	#end def
#end class





class Infos(object):
	PLAYING = "playing"
	STOPPED = "stopped"

	def __init__(self):
		self.itemid = None  				# int
		self.itemkind = None  				# int, so far only '2' has been seen, audio.
		self.itemname = None  				# unicode, the actual song title, e.g. "Chapter 9"  -- Yes, I am using an audiobook to test. lol.
		self.persistentid = None  			# int

		self.volume = None					# int, from 0-100. This is the real Volume. Shairport does logarithmically scaling of the airplay value.
		self.playstate = None				# Enum: Infos.PLAYING, Infos.STOPPED
		self.useragent = None  				# unicode, e.g. iTunes/12.2 (Macintosh; OS X 10.9.5)
		self.airplayvolume = None			# int, from 0-100. This is linear what the client sends.

		self.songsize = None				# int
		self.songyear = None  				# int
		self.songtime = None  				# int, in ms
		self.songalbum = None				# unicode, e.g. "Fallout: Equestria"
		self.songgenre = None				# unicode
		self.songartist = None				# unicode, e.g. "Kkat"
		self.songformat = None  			# unicode, e.g. "mp3"
		self.songbitrate = None				# int, e.g. 128
		self.songalbumid = None	 			# int, persistend id probably.
		self.songcomment = None				# unicode, e.g. "Narrated by Scorch_Mechanic.\nDownloaded with pon3dl. https://github.com/luckdonald/pon3downloader"
		self.songstoptime = None  			# int
		self.songdatakind = None  			# int, 1 = RADIO_STREAM, 0/2 = DAAP_STREAM ???
		self.songartistid = None  			# int, probably. I guess a persistent artist id? like self.persistentid ? -- http://git.io/vZJeg
		self.songdisabled = None  			# bool
		self.songcoverart = None			# bytes
		self.songcomposer = None			# unicode
		self.songeqpreset = None			# unicode
		self.songgrouping = None  			# unicode, ??
		self.songcategory = None			# unicode, ??
		self.songdisccount = None			# int
		self.songstarttime = None			# int, in ms
		self.songcodectype = None  			# unicode, "mpeg" and "mp4a"
		self.songdateadded = None			# datetime
		self.songdiscnumber = None			# int
		self.songsamplerate = None			# int
		self.songtrackcount = None  		# int
		self.songuserrating = None  		# int
		self.songdateplayed = None			# datetime
		self.songtracknumber = None  		# int
		self.songtracknumber = None  		# int
		self.songcompilation = None			# bool
		self.songdescription = None			# unicode
		self.songcodecsubtype = None  		# int, known values are 3 = MPEG, 4 = MP4A; seems to be same as `self.songcodectype`, but as enum.
		self.songdatemodified = None 		# datetime, seems to be in future?
		self.songlastskipdate = None  		# datetime, seems to be in future?
		self.songcontentrating = None		# int, content rating means maybe something like PG18 (us) or FSK18 (de)??
		self.songrelativevolume = None 		# int
		self.songsbeatsperminute = None 	# int, 0 when not known, e.g. 180
		self.songcontentdescription = None 	# unicode, ??

		self.itunesepisodenumstr = None  	# unicode
		self.itunesnormvolume = None		# int
		self.itunesseriesname = None  		# unicode
		self.itunesmediakind = None  		# int, could have values 1/4/6/7/8/23 ??  -- http://git.io/vZfpR
		self.itunesispodcast = None			# bool
		self.ituneshasvideo = None			# bool

	def write_cover_file(self):
		temp_file = tempfile.NamedTemporaryFile(prefix="image_", suffix=".png", delete=False)
		with temp_file as file:
			file.write()
		open_file_folder(temp_file.name)

	def publish(self):
		print(self.to_simple_string())

	def to_simple_string(self):
		"""
		String like
		"[title] - [artist]\n[album]"
		will be returned.
		:return:
		"""
		return (self.itemname if self.itemname else "Unknown Track") + ((" - " + self.songartist) if self.songartist else "") + (("\n" + self.songalbum) if self.songalbum else "")


class Item(object):
	def __init__(self, e):
		if isinstance(e, str):
			try:
				e = xml.fromstring(e)
			except xml.ParseError:
				logger.warn("Skipping malformed line: {line}".format(line=e), exc_info=True)
				return
		if isinstance(e, xml.Element):
			e = etree_to_dict(e)
		if isinstance(e, dict):
			e = DictObject.objectify(e)
		assert isinstance(e, DictObject)
		self.type = ascii_integers_to_string(e.item.type)
		self.code = ascii_integers_to_string(e.item.code)
		self.length = int(e.item.length)
		if "data" in e.item:
			assert self.length > 0  # length is zero if data is undefined.
			self.data = encoded_to_str(e.item.data["#text"], e.item.data["@encoding"], as_bytes=True)
			if e.item.data["@encoding"] == "base64":
				self._data_base64 = to_unicode(e.item.data["#text"])
			else:
				self._data_base64 = None
		else:
			assert self.length == 0  # length is zero if data is undefined.
			self.data = to_binary("")
			self._data_base64 = None

	@property
	def data_str(self):
		return to_unicode(self.data)

	@property
	def data_int(self):
		return int("0x" + ''.join([hex(x)[2:] for x in self.data]), base=16)

	@property
	def data_date(self):
		return datetime.fromtimestamp(self.data_int)

	@property
	def data_bool(self):
		if self.data_int == 1:
			return True
		elif self.data_int == 0:
			return False
		else:
			raise TypeError("Data boolean is neither 0 or 1, but is {val}.".format(val=self.data))

	@property
	def data_base64(self):
		if self._data_base64:
			return self._data_base64
		else:
			return encodebytes(to_binary(self.data))
#end def


def ascii_integers_to_string(string, base=16, digits_per_char=2):
	return "".join([chr(int(string[i:i+digits_per_char], base=base)) for i in range(0, len(string), digits_per_char)])


def data_string_decode(e, as_bytes=True):
	return encoded_to_str(e.item.data["#text"], e.item.data["@encoding"], as_bytes=as_bytes)

def encoded_to_str(data, encoding, as_bytes=True):
	if encoding == "base64":
		bytes = decodebytes(data.encode('ascii'))
		if as_bytes:
			return bytes
		else:
			return to_unicode(bytes)
	else:
		raise AttributeError("unknown encoding format: {f}".format(f=encoding))




if __name__ == "__main__":
	main(None)
