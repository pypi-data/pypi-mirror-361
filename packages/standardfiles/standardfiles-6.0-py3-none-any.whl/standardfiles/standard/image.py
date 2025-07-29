# See LICENSE file for copyright and license details.
"""Convert images."""
import os

from standardfiles.message import message
from standardfiles.options import config
from standardfiles.utils import move_file
from standardfiles.file import image


def convert_to_standard_image(img):
	"""Convert images to ff.bz2.

	The result is save in tmp directory.

	Steps.
	1. Convert to png.
	2. Convert to ff and compress to ff.bz2
	"""

	img_name = os.path.splitext(img)[0]
	tmpfile_ffbz2 = f'{config.config.tmp_dir}/image/{img_name}'
	if image.convert(img, tmpfile_ffbz2):
		return -1

	# Check mode replace
	if not config.options.mode.replace:
		return 0

	# Replace file
	os.remove(img)
	img_new = f'{img_name}.ff.bz2'
	tmpfile_ffbz2 = f'{tmpfile_ffbz2}.ff.bz2'

	if move_file(tmpfile_ffbz2, img_new):
		message.warning(f"Error to copy standard image: {img}")
		return -3

	return 0


__all__ = ['convert_to_standard_image']
