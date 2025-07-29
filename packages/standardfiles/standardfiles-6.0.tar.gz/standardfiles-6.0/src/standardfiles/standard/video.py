# See LICENSE file for copyright and license details.
"""Convert videos."""
import os

from standardfiles.file import video
from standardfiles.message import message
from standardfiles.options import config
from standardfiles.utils import move_file


def convert_to_standard_video(video_file):
	"""Convert video to mkv with h264 and acc."""

	message.file(video_file)

	video_name = os.path.splitext(video_file)[0]
	tmpfile = f'{config.config.tmp_dir}/video/{video_name}'

	if video.convert(video_file, tmpfile):
		return -1

	# Clean metadata
	tmpfile = f'{tmpfile}.mkv'
	if video.clean(tmpfile):
		return -2

	# Check mode replace
	if not config.options.mode.replace:
		return 0

	# Replace file
	os.remove(video_file)
	video_new = f'{video_name}.mkv'
	tmpfile = f'{tmpfile}'

	if move_file(tmpfile, video_new):
		message.warning(f"Error to copy standard video: {video_file}")
		return -3

	return 0


__all__ = ['convert_to_standard_video']
