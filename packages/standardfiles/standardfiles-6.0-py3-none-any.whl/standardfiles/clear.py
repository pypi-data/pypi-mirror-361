# See LICENSE file for copyright and license details.
"""Module to clean metadata."""
from multiprocessing.dummy import Pool as ThreadPool

import magic

from standardfiles import utils
from standardfiles.file import image, audio, video, pdf
from standardfiles.file.utils import get_files
from standardfiles.message import message
from standardfiles.options import config


def clear_metadata():
	"""Clean the metadata from standard files."""

	message.process("Clear metadata")
	utils.create_tmpdir()
	list_files = get_files(
		config.options.mode.recursive,
		standard=True
	)

	if list_files['img']:
		message.message("Images")
		pool = ThreadPool(config.options.mode.process)
		pool.map(__remove_img, list_files['img'])
		pool.close()
		pool.join()
	if list_files['pdf']:
		message.message("Pdf")
		pool = ThreadPool(config.options.mode.process)
		pool.map(__remove_pdf, list_files['pdf'])
		pool.close()
		pool.join()
	if list_files['audio']:
		message.message("Audio")
		for file in list_files['audio']:
			utils.check_size(file)
			__remove_audio(file)
	if list_files['video']:
		message.message("Video")
		for file in list_files['video']:
			utils.check_size(file)
			__remove_video(file)

	utils.remove_tmpdir()

	return 0


def __remove_audio(file):
	"""Remove all metadata from audio."""

	if not audio.is_clean(file):
		return 0

	if audio.clean(file):
		return -1

	message.file(file)
	return 0


def __remove_img(img):
	"""Remove all metadata from img.

	The condition are.
		- Only accept png.
		- Do nothing with gif.
	"""

	mime = magic.Magic(mime=True)
	mime_type = mime.from_file(img)

	# Check if image is png
	if mime_type != "image/png":
		# If image is a gif, do nothing
		if mime_type != "image/gif":
			message.warning(f"It isn't png: {img}")
		return -1

	if image.clean(img):
		return -2

	message.file(img)
	return 0


def __remove_pdf(file):
	"""Remove all metadata from pdf."""

	if not pdf.is_clean(file):
		return 0

	if pdf.clean(file):
		return -1

	message.file(file)
	return 0


def __remove_video(file):
	"""Remove all metadata from video."""

	if not video.is_clean(file):
		return 0

	if video.clean(file):
		return -1

	message.file(file)
	return 0


__all__ = ['clear_metadata']
