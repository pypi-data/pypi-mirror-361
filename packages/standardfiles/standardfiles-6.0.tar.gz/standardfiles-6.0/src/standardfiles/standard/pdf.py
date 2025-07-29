# See LICENSE file for copyright and license details.
"""Convert pdf."""
import os
import shutil

from standardfiles.file import pdf
from standardfiles.message import message
from standardfiles.options import config
from standardfiles.utils import move_file


def convert_to_standard_pdf(pdf_file):
	"""Convert pdf."""

	message.file(pdf_file)

	pdf_name = os.path.splitext(pdf_file)[0]
	tmpfile = f'{config.config.tmp_dir}/pdf/{pdf_name}.pdf'

	try:
		shutil.copy(pdf_file, tmpfile)
	except (FileNotFoundError, PermissionError):
		return -1

	if pdf.is_clean(tmpfile):
		if pdf.clean(tmpfile):
			return -2

	# Check mode replace
	if not config.options.mode.replace:
		return 0

	# Replace file
	os.remove(pdf_file)
	pdf_name = f'{pdf_name}.pdf'

	if move_file(tmpfile, pdf_name):
		message.warning(f"Error to copy standard pdf: {pdf_file}")
		return -3

	return 0


__all__ = ['convert_to_standard_pdf']
