# See LICENSE file for copyright and license details.
"""Module to get args from command."""
import argparse
import multiprocessing
from dataclasses import fields

from standardfiles.options import config
from standardfiles.options.options import Options, OptionsMode


LIST_ARGS = {
	"options": {
		"--recursive": {
			"short": "-r",
			"help": "Run the action recursively",
			"action": "store_true",
		},
		"--replace": {
			"short": "-R",
			"help": "No create a standardfiles directory. Replace the files.",
			"action": "store_true",
		},
		"--notmp": {
			"short": "-T",
			"help": "Don't use /tmp, run in current directory",
			"action": "store_true",
		},
		"--process": {
			"short": "-p",
			"help": "Number of process if it used",
			"type": int,
			"nargs": 1,
			"metavar": ("cores"),
		},
	},
	"actions": {
		"--clear": {
			"short": "-c",
			"help": "Remove all metadata",
		},
		"--image": {
			"short": "-i",
			"help": "Convert images from ff.bz2 to png",
		},
		"--name": {
			"short": "-n",
			"help": "Remove all space in the file and directory name",
		},
		"--version": {
			"short": "-v",
			"help": "Print the version",
		},
	},
}


class CustomArgumentParser(argparse.ArgumentParser):
	"""Replace help."""

	def format_help(self):
		help_text = super().format_help()
		return help_text.replace("options:", "actions:")


def get_args():
	"""Get arguments."""

	message_usage = (
		"\n"
		" %(prog)s [options] [actions]\n"
	)
	message_description = (
		"Convert to standard format all images, videos and audios"
	)

	parser = CustomArgumentParser(
		usage=message_usage,
		description=message_description
	)

	for opt, args in LIST_ARGS['actions'].items():
		arg = [args.pop("short", None), opt]
		parser.add_argument(*arg, **args, action="store_true")

	current_options = parser.add_argument_group("optional arguments")
	for opt, args in LIST_ARGS['options'].items():
		arg = [args.pop("short", None), opt]
		current_options.add_argument(*arg, **args)

	return vars(parser.parse_args())


def set_config(args):
	"""Get the current option."""

	# Set actions
	options_elements = {field.name for field in fields(Options)}
	args_options = {
		k: v for k, v in args.items() if k in options_elements
	}
	config.options = Options(
		**{
			key: args_options.get(key, False)
			for key in Options.__annotations__
		}
	)

	# Set options
	options_elements = {field.name for field in fields(OptionsMode)}
	args_options = {
		k: v for k, v in args.items() if k in options_elements
	}
	config.options.mode = OptionsMode(
		**{
			key: args_options.get(key, False)
			for key in OptionsMode.__annotations__
		}
	)

	# Set number of process
	if not config.options.mode.process:
		config.options.mode.process = multiprocessing.cpu_count()
		return 0

	if __set_process(args["process"]):
		return -1
	return 0


def __set_process(args):
	"""Check number of process"""

	process = args[0]
	local_cpu = multiprocessing.cpu_count()

	if (process <= 0) or (local_cpu < process):
		return -1

	config.options.mode.process = process

	return 0


__all__ = ['get_args', 'set_config']
