# See LICENSE file for copyright and license details.
"""Module to standard files's utils."""
import os
from pathlib import Path

import magic

from standardfiles.message import message


def class_files(file_list, standard=False):
	"""Classify the file list.

	The category are.
	- image.
	- pdf.
	- audio.
	- video
	"""

	standard_files = {
		'img': [],
		'pdf': [],
		'audio': [],
		'video': [],
	}

	mime = magic.Magic(mime=True)
	for file in file_list:

		try:
			mime_type = mime.from_file(file)
		except (FileNotFoundError, PermissionError, FileExistsError):
			message.warning(f"Error in file: {file}")
			continue

		if standard:
			# Get standard files
			match mime_type:
				case "image/png":
					standard_files['img'].append(file)
				case "application/pdf":
					standard_files['pdf'].append(file)
				case "audio/x-hx-aac-adts" | "audio/flac":
					standard_files['audio'].append(file)
				case "video/x-matroska":
					standard_files['video'].append(file)
		else:
			# Get type files
			if mime_type.find("image") != -1:
				standard_files['img'].append(file)
				continue
			if mime_type.find("pdf") != -1:
				standard_files['pdf'].append(file)
				continue
			if mime_type.find("audio") != -1:
				standard_files['audio'].append(file)
				continue
			if mime_type.find("video") != -1:
				standard_files['video'].append(file)
				continue

	return standard_files


def get_files(recursive=False, standard=False):
	"""Get in a dict all files in current directory by mime class."""

	# Get all files list
	if recursive:
		message.step("Search standard files (recursive)")
		all_file_list = Path().rglob('*')
	else:
		message.step("Search standard files")
		all_file_list = Path().glob('*')

	file_list = []
	for file in all_file_list:
		if os.path.isfile(file):
			file_list.append(str(file))

	file_list.sort()

	if standard:
		file_list = class_files(file_list, standard=True)
	else:
		file_list = class_files(file_list, standard=False)

	return file_list


def get_standard_img():
	"""Get all standard images (.ff.bz2)."""

	img = []
	for file in Path().glob('*.ff.bz2'):
		if os.path.isfile(file):
			img.append(str(file))
	return img


__all__ = [
	'class_files',
	'get_files',
	'get_standard_img',
]
