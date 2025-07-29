# See LICENSE file for copyright and license details.
"""Module to check the names."""
import os

from standardfiles.message import message
from standardfiles.utils import get_all


def check_name():
	"""Erase all spaces from files/directories names."""

	message.process("Check names")
	files = get_all()
	files_error = []
	for file in files:
		old = str(file)
		new = old.replace(" ", "_")
		if old == new:
			continue

		# Replace
		try:
			os.rename(old, new)
			message.rename(old, new)
		except (FileNotFoundError, PermissionError, FileExistsError):
			files_error.append(old)

	# Exist some error in replace
	if not files_error:
		return 0

	message.error("Files/directories not replaced")
	for file in files_error:
		message.file(file)
	return -1


__all__ = ['check_name']
