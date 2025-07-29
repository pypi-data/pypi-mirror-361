# See LICENSE file for copyright and license details.
"""Module to convert images."""
from multiprocessing.dummy import Pool as ThreadPool

from standardfiles.options import config
from standardfiles.message import message
from standardfiles.file.utils import get_standard_img
from standardfiles.file.image import ffbz2_to_png


def image_to_png():
	"""Convert from .ff.bz2 to .png."""

	message.process("Convert images from ff.bz2 to png")

	list_img = get_standard_img()
	if list_img:
		pool = ThreadPool(config.options.mode.process)
		pool.map(ffbz2_to_png, list_img)
		pool.close()
		pool.join()

	return 0


__all__ = ['image_to_png']
