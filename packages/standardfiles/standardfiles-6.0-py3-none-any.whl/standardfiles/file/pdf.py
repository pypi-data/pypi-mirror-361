# See LICENSE file for copyright and license details.
"""Operation with pdf."""
import filecmp
import os

from standardfiles import utils
from standardfiles.message import message


def clean(pdf):
	"""Clean metadata from pdf."""

	tmpfile = utils.get_tmpfile_name()
	tmpfile = f"{tmpfile}.pdf"
	command = f"exiftool -all= {pdf} -o {tmpfile}"
	status, _ = utils.run_command(command.split())
	if status:
		message.warning(f"Don't clear metadata from pdf: {pdf}")
		return -1

	if utils.replace_file(tmpfile, pdf, remove=True):
		return -2

	return 0


def is_clean(pdf):
	"""Check if pdf is clean of metadata."""

	tmpfile = utils.get_tmpfile_name()
	tmpfile = f"{tmpfile}.pdf"
	command = f"exiftool -all= {pdf} -o {tmpfile}"
	status, _ = utils.run_command(command.split())
	if status:
		message.warning(f"Don't clear metadata from pdf: {pdf}")
		return -1

	status = filecmp.cmp(tmpfile, pdf)
	os.remove(tmpfile)
	if status:
		return 0

	return -2


__all__ = [
	'clean',
	'is_clean',
]
