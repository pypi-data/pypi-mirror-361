# See LICENSE file for copyright and license details.
"""Package entry point."""
import sys

from importlib.metadata import version

from standardfiles.clear import clear_metadata
from standardfiles.image import image_to_png
from standardfiles.message import message
from standardfiles.name import check_name
from standardfiles.options import config
from standardfiles.options.args import get_args, set_config
from standardfiles.standard.standard import convert_to_standard


def standardfiles_main():
	"""Main function to update system."""

	if set_config(get_args()):
		message.error("Error in number of process")
		return -1

	if config.options.version:
		print("standardfiles-v" + version("standardfiles"))
		return 0
	if config.options.clear:
		clear_metadata()
		return 0
	if config.options.image:
		image_to_png()
		return 0
	if config.options.name:
		return check_name()

	convert_to_standard()

	return 0


def main():
	""""Entry point."""

	retval = standardfiles_main()
	sys.exit(retval)


if __name__ == "__main__":
	main()
