# -*- coding: utf-8 -*-
# __author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)

from hashlib import sha256
import xml.etree.ElementTree as xml
from DictObject import DictObject
from luckydonaldUtils.files import open_file_folder, guess_extension
from luckydonaldUtils.encoding import to_unicode, to_binary
from luckydonaldUtils.xml import etree_to_dict
from luckydonaldUtils import py2, py3

if py2:
	from base64 import decodestring as decodebytes
	from base64 import encodestring as encodebytes
else:
	from base64 import decodebytes, encodebytes
from datetime import datetime

import tempfile  # write cover image to temp file
import magic


class Infos(object):
	PLAYING = "playing"
	PAUSE = "paused"
	STOPPED = "stopped"

	def __init__(self):
		self.itemid = None  				# int
		self.itemkind = None  				# int, so far only '2' has been seen, audio.
		self.itemname = None  				# unicode, the actual song title, e.g. "Chapter 9"  -- Yes, I am using an audiobook to test. lol.
		self.persistentid = None  			# int

		self.sortname = None				# unicode, equal to the song's name (?)
		self.sortalbum = None  				# unicode, equal to the song's name (?)

		self.volume = None					# float/double, from 0-1. This is the real Volume. Shairport does logarithmically scaling of the airplay value. (Python2 has a `double` type, too, not sure which you get there.)
		self.playstate = None				# Enum: Infos.PLAYING, Infos.STOPPED
		self.useragent = None  				# unicode, e.g. iTunes/12.2 (Macintosh; OS X 10.9.5)
		self.songcoverart = CoverArt()		# CoverArt, (with bytes, base64, mime and stuff)
		self.airplayvolume = None			# float, from 0-1. This is linear what the client sends. (Python2 has a `double` type, too, not sure which you get there.)

		self.dacp_id = None 				# str, the DACP-ID.				Needed for controlling the streaming client. See http://git.io/vZPp1
		self.active_remote = None		  	# str, the Active-Remote token.	Needed for controlling the streaming client. See http://git.io/vZPp1

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
			file.write(self.songcoverart.binary)  # this is not base64!
		return temp_file

	def to_simple_string(self):
		"""
		String like
		"[title] - [artist]\n[album]"
		will be returned.
		:return:
		"""
		return (self.itemname if self.itemname else "Unknown Track") + ((" - " + self.songartist) if self.songartist else "") + (("\n" + self.songalbum) if self.songalbum else "")

class CoverArt(object):
	def __init__(self, base64=None, binary=None, mime=None, extension=None, checksum=None):
		self._binary = binary  # the actual file bytes
		self._base64 = base64  # base64 encoding
		self._mime	 = mime    # e.g. "image/png"
		self._extension = extension # e.g. ".png"
		self._checksum = checksum  # sha256 of binary

	@property
	def base64(self):
		if self._base64:
			return self._base64
		if self._binary:
			self._base64 = encodebytes(to_binary(self._binary))
			return self._base64
		else:
			return None

	@property
	def binary(self):
		if self._binary:
			return self._binary

	@property
	def mime(self):
		if self._mime:
			return self._mime
		if self.binary:
			#self._mime = magic.from_buffer(memoryview(self.binary), mime=True).decode("utf-8")
			self._mime = magic.from_buffer(self.binary, mime=True).decode("utf-8")
			return self._mime
		else:
			return None

	@property
	def extension(self):
		self._extension = guess_extension(self.mime)
		return self._extension

	@property
	def checksum(self):
		if self._checksum:
			return self._checksum
		if self.binary:
			self._checksum = sha256(self.binary).hexdigest()
			return self._checksum
		else:  # self.binary is None
			return None

	def as_dict(self, base64=False):
		data_dict = {
			"mime": self.mime,
			"extension": self.extension,
			"checksum": self.checksum,
			}
		if base64:
			data_dict["base64"] = self.base64
		return data_dict


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
		assert hasattr(e.item, "type")
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
		if self.data:
			if py3:
				return int("0x" + ''.join([hex(x)[2:] for x in self.data]), base=16)
			else:
				return int("0x" + ''.join([hex(ord(x))[2:] for x in self.data]), base=16)

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

