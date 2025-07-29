# See LICENSE file for copyright and license details.
"""Convert audio."""
import os

from standardfiles.file import audio
from standardfiles.message import message
from standardfiles.options import config
from standardfiles.utils import move_file


def convert_to_standard_audio(audio_file):
	"""Convert audios to aac."""

	message.file(audio_file)

	audio_name = os.path.splitext(audio_file)[0]
	tmpfile = f'{config.config.tmp_dir}/audio/{audio_name}'

	_, ext = audio.get_extension(audio_file)

	if audio.convert(audio_file, tmpfile):
		return -1

	# Clean metadata
	tmpfile = f'{tmpfile}{ext}'

	if ext == '.flac':
		if audio.clean(tmpfile):
			return -2

	# Check mode replace
	if not config.options.mode.replace:
		return 0

	# Replace file
	os.remove(audio_file)
	audio_new = f'{audio_name}{ext}'

	if move_file(tmpfile, audio_new):
		message.warning(f"Error to copy standard audio: {audio_file}")
		return -3

	return 0


__all__ = ['convert_to_standard_audio']
