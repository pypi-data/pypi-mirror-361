# See LICENSE file for copyright and license details.
"""Operation with audio."""
import re

from standardfiles import utils
from standardfiles.message import message


FFMPEG_OPT = (
	"-vn -c:a aac -q 10 "
	"-fflags +bitexact -flags:v +bitexact -flags:a +bitexact -y "
)


def check_codec(info, lossless=False, mkv=False):
	"""Check audio codec is standard file.

	lossless: flac.
	loss: aac.
	"""

	audio_codec = "aac"
	if lossless:
		audio_codec = "flac"

	audio_container = audio_codec
	if mkv:
		audio_container = "matroska"

	# Check container
	check_container = re.findall(
		f"^Input.*{audio_container}.*from",
		info,
		re.MULTILINE
	)
	if len(check_container) == 0:
		return -1

	# Check codec
	check_audio = re.findall("^  Stream.*: Audio:", info, re.MULTILINE)
	check_format = re.findall(
		f"^  Stream.*: Audio: {audio_codec}",
		info,
		re.MULTILINE
	)

	if len(check_format) != len(check_audio):
		return -2
	return 0


def clean(audio):
	"""Remove all metadata from standard audio."""

	# Clear metadata
	command = f"metaflac --remove {audio}"
	status, _ = utils.run_command(command.split())
	if status:
		message.warning(f"Don't clear metadata from audio: {audio}")
		return -1

	if is_clean(audio):
		message.warning(f"Don't clear metadata from audio: {audio}")
		return -2

	return 0


def convert(audio, destine):
	"""Convert image to ff.bz2."""

	check_status, ext = get_extension(audio)
	if check_status:
		command = f"ffmpeg -i {audio} {FFMPEG_OPT} {destine}{ext}"
	else:
		command = f"cp {audio} {destine}{ext}"
	status, _ = utils.run_command(command.split())
	if status:
		message.warning(f"Don't convert to audio: {audio}")
		return -1

	return 0


def get_extension(audio):
	"""Check if the audio is standard file."""

	ext = ".aac"
	command = f"ffprobe {audio} 2>&1"
	status, info = utils.run_command(command, shell=True)
	if status:
		message.warning(f"Don't identify the audio: {audio}")
		return -1, ext
	info = info.stdout.decode('utf-8')

	# Check video
	check_audio = re.findall("^  Stream.*: Video:", info, re.MULTILINE)
	if len(check_audio) != 0:
		return -2, ext

	status_loss = check_codec(info)
	status_lossless = check_codec(info, lossless=True)

	if not status_lossless:
		ext = ".flac"

	if status_loss and status_lossless:
		return -3, ext

	return 0, ext


def is_clean(audio):
	"""Check metadata from standard audio."""

	command = "ffprobe -loglevel error -show_entries stream_tags:format_tags "
	command = f"{command} {audio}"

	status, info = utils.run_command(command.split())
	if status:
		message.warning(f"Don't check metadata from audio: {audio}")
		return -1
	info = info.stdout.decode('utf-8')

	info = re.sub(".*(STREAM|FORMAT).*\n", "", info)
	if 0 < len(info):
		return -2
	return 0


__all__ = [
	'check_codec',
	'clean',
	'convert',
	'get_extension',
	'is_clean',
]
