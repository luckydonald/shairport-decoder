# -*- coding: utf-8 -*-
__author__ = 'luckydonald'

from luckydonaldUtils.logger import logging  # pip install luckydonald-utils
logger = logging.getLogger(__name__)


from PIL import Image
import sys


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


def most_frequent_colour(image, colors=10):

	image2 = image.convert("P", palette=Image.ADAPTIVE, colors=colors)
	image3 = image2.convert(image.mode)
	save(path, "0", image=image3,)

	w, h = image3.size
	pixels = image3.getcolors(w * h)

	most_frequent_pixels = [pixels[0]]

	for count, colour in pixels:
		length = len(most_frequent_pixels)
		for i in range(0, length):
			if colour == most_frequent_pixels[i][1]:
				break
			if count > most_frequent_pixels[i][0]:
				most_frequent_pixels.insert(i, (count, colour))
				break
			elif count < most_frequent_pixels[length-1]:
				most_frequent_pixels.append((count, colour))
				break
		#if count > most_frequent_pixel[0]:
		#	most_frequent_pixel2 = most_frequent_pixel
		#	most_frequent_pixel = (count, colour)

	return most_frequent_pixels[:colors]


def average_colour_in_k_clusters(image, k):
	pass


def compare(title, image, colour_tuple):
	image.show(title=title)
	image = Image.new("RGB", (200, 200,), colour_tuple)
	return image

def save(name, integer, image=None, color=None):
	if image:
		image.save(name.replace(".png", "export-{}.png".format(integer)))
	if color:
		sample = Image.new("RGB", (200, 200,), color)
		sample.save(name.replace(".png", "export-{}.png".format(integer)))


picture = "cover Kopie"
path = "/Users/luckydonald/Desktop/{}.png".format(picture)

def main():
	image = Image.open(path)

	#if "mode" in sys.argv:
	results = most_frequent_colour(image)

	#result2 = average_colour(image)
	i = 0
	save(path, i+1, color=results[i][1]); i+=1
	save(path, i+1, color=results[i][1]); i+=1
	save(path, i+1, color=results[i][1]); i+=1
	save(path, i+1, color=results[i][1]); i+=1
	save(path, i+1, color=results[i][1]); i+=1



if __name__ == "__main__":
	main()

