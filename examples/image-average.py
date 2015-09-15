# -*- coding: utf-8 -*-
__author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)


from PIL import Image
import sys
from luckydonaldUtils.images.color import most_frequent_color


def average_colour(image):

	colour_tuple = [None, None, None]
	for channel in range(3):

		# Get data for one channel at a time
		pixels = image.getdata(band=channel)

		values = []
		for pixel in pixels:
			values.append(pixel)

		colour_tuple[channel] = sum(values) / len(values)

	return tuple(colour_tuple)

def save(name, integer, image=None, color=None):
	"""
	DEBUG FUNCTION
	 WITH CAPSLOCK DESCRIPTION
	:param name:
	:param integer:
	:param image:
	:param color:
	:return:
	"""
	if image:
		image.save(name.replace(".png", "export-{}.png".format(integer)))
	if color:
		sample = Image.new("RGB", (200, 200,), color)
		sample.save(name.replace(".png", "export-{}.png".format(integer)))

picture = "Bildschirmfoto 2015-09-15 um 17.37.49"
path = "/Users/luckydonald/Desktop/{}.png".format(picture)

def main():
	image = Image.open(path)
	max_colors = 10
	#if "mode" in sys.argv:
	results = most_frequent_color(image, colors=max_colors)

	#result2 = average_colour(image)
	for i in range(0, max_colors):
		save(path, i+1, color=results[i][1])


if __name__ == "__main__":
	main()

