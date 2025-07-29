# See LICENSE file for copyright and license details.
"""Operation with video."""
import filecmp
import re

from standardfiles import utils
from standardfiles.file.audio import check_codec as audio_codec
from standardfiles.message import message


FFMPEG_OPT = "-map_metadata -1 -c copy -y"


def check_codec(text, lossless=False):
	"""Check video codec is standard file.

	lossless: ffv1.
	loss: h264.
	"""

	video_codec = "h264"
	if lossless:
		video_codec = "ffv1"

	# Check codec
	check_video = re.findall("^  Stream.*: Video:", text, re.MULTILINE)
	check_format = re.findall(
		f"^  Stream.*: Video: {video_codec}",
		text,
		re.MULTILINE
	)

	if len(check_format) != len(check_video):
		return -1
	return 0


def check_standard(video):
	"""Check if the video is standard file."""

	command = f"ffprobe {video} 2>&1"
	status, info = utils.run_command(command, shell=True)
	if status:
		message.warning(f"Don't identify the video: {video}")
		return -1
	info = info.stdout.decode('utf-8')

	# Check mkv
	check_mkv = re.findall("^Input.*matroska.*from", info, re.MULTILINE)
	if len(check_mkv) == 0:
		return -2

	# Check audio
	if __check_all_codec(info):
		return -3
	return 0


def clean(video):
	"""Clean all metadata from standard video."""

	# Clear metadata
	tmpfile = utils.get_tmpfile_name()
	tmpfile = f"{tmpfile}.mkv"
	command = f"ffmpeg -i {video} {FFMPEG_OPT} {tmpfile}"
	status, _ = utils.run_command(command.split())
	if status:
		message.warning(f"Don't clear metadata from video: {video}")
		return -2

	if is_clean(tmpfile):
		message.warning(f"The metadata don't remove from video: {video}")
		return -3

	if filecmp.cmp(tmpfile, video):
		return -1

	if utils.replace_file(tmpfile, video, remove=True):
		return -4

	return 0


def convert(video, destine):
	"""Convert video to mkv with h264 and acc."""

	if check_standard(video):
		command = (
			f"ffmpeg -i {video} -c:v libx264 -c:a aac "
			f"-fflags +bitexact -flags:v +bitexact -flags:a +bitexact -y "
			f"{destine}.mkv"
		)
	else:
		command = f"cp {video} {destine}.mkv"

	status, _ = utils.run_command(command.split())
	if status:
		message.warning(f"Don't convert to video: {video}")
		return -1

	return 0


def is_clean(video):
	"""Check metadata from standard video."""

	command = "ffprobe -loglevel error -show_entries stream_tags:format_tags "
	command = f"{command} {video}"
	status, info = utils.run_command(command.split())
	if status:
		message.warning(f"Don't check metadata from audio: {video}")
		return -1
	info = info.stdout.decode('utf-8')

	info = re.sub(".*(STREAM|FORMAT|TAG:DURATION=|TAG:ENCODER=).*\n", "", info)
	if 0 < len(info):
		return -2
	return 0


def __check_all_codec(text):
	"""Check video and audio codec."""

	status_audio_loss = audio_codec(text, mkv=True)
	status_audio_lossless = audio_codec(text, lossless=True, mkv=True)
	if status_audio_loss and status_audio_lossless:
		return -1

	status_video_loss = check_codec(text)
	status_video_lossless = check_codec(text, lossless=True)
	if status_video_loss and status_video_lossless:
		return -2

	if not (status_video_loss or status_audio_loss):
		return 0
	if not (status_video_lossless or status_audio_lossless):
		return 0

	return -3


__all__ = [
	'check_codec',
	'check_standard',
	'clean',
	'convert',
	'is_clean',
]
