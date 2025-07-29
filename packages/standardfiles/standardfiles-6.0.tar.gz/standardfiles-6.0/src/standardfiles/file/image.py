# See LICENSE file for copyright and license details.
"""Operation with image."""
import filecmp
import os

from standardfiles import utils
from standardfiles.message import message


def clean(img):
	"""Clean metadata for only png image."""

	# Check extension
	ext = os.path.splitext(img)[1]
	if ext != '.png':
		return -2

	# Clean metadata
	tmpfile = utils.get_tmpfile_name()
	command = f"png2ff < {img} | ff2png > {tmpfile}"
	status, _ = utils.run_command(command, shell=True)
	if status:
		message.warning(f"Don't clear metadata from png: {img}")
		return -3

	if filecmp.cmp(tmpfile, img):
		return -1

	if utils.replace_file(tmpfile, img, remove=True):
		return -4

	return 0


def convert(img, destine):
	"""Convert image to ff.bz2."""

	# Get image type
	type_img = get_type(img)
	if type_img is None:
		return -1

	# Get command to convert
	tmpfile = utils.get_tmpfile_name()
	tmpfile = f'{tmpfile}.png'
	destine_ffbz2 = f'{destine}.ff.bz2'

	match type_img:
		case "WEBP":
			command = f"dwebp {img} -o {tmpfile}"
		case "PNG":
			command = f"cp {img} {tmpfile}"
		case "GIF":
			return -1
		case _:
			command = f"magick {img} {tmpfile}"
	message.format(img, type_img)

	status, _ = utils.run_command(command.split())
	if status:
		message.warning(f"Don't convert to png: {img}")
		os.remove(tmpfile)
		return -2

	# Convert to ff.bz2
	command = f"png2ff < {tmpfile} | bzip2 > {destine_ffbz2}"
	status, _ = utils.run_command(command, shell=True)
	if status:
		message.warning(f"Don't convert to ff.bz2: {img}")
		os.remove(tmpfile)
		os.remove(destine_ffbz2)
		return -3

	os.remove(tmpfile)

	# Check if files standard file exist
	if not os.path.exists(destine_ffbz2):
		message.warning(f"Don't exist the standard file: {destine_ffbz2}")
		return -4


def ffbz2_to_png(img):
	"""Convert from .ff.bz2 to .png."""

	name = os.path.splitext(img)[0]
	name = os.path.splitext(name)[0]
	name = f"{name}.png"
	command = f"bunzip2 < {img} | ff2png > {name}"
	message.rename(img, name)
	status, _ = utils.run_command(command, shell=True)
	if status:
		message.error(f"No convert to png: {img}")
		return -1
	return 0


def get_type(img):
	"""Get image type."""

	command = f"identify {img}"
	status, info = utils.run_command(command.split())
	if status:
		message.warning(f"Don't identify the image: {img}")
		return None
	info = info.stdout.decode('utf-8')

	type_img = info.split()[1]

	return type_img


__all__ = [
	'clean',
	'convert',
	'ffbz2_to_png',
	'get_type',
]
