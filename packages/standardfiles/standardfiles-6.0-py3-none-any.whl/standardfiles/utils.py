# See LICENSE file for copyright and license details.
"""Module to utils functions."""
import filecmp
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from standardfiles.message import message
from standardfiles.options import config


def check_size(files):
	"""Check file size."""

	if config.options.mode.notmp:
		return

	files_size = 0
	if isinstance(files, str):
		files_size = int(os.path.getsize(files) / 1024)
	else:
		for file in files:
			files_size = files_size + int(os.path.getsize(file) / 1024)

	# Get tmp size
	command = "df"

	status, info = run_command(command.split())
	if status:
		message.error("Don't get current /tmp size")
		sys.exit(-1)
	info = info.stdout.decode('utf-8')

	info = re.findall("^.* /tmp$", info, re.MULTILINE)
	info = info[0].split()
	free_tmp = int(info[3])
	proportion = files_size / free_tmp

	# Check free RAM
	if 0.8 < proportion:
		proportion = str(int(proportion * 100))
		message.warning(
			f"Don't enough free space in /tmp: {proportion}"
		)
		sys.exit(-1)


def create_tmpdir():
	"""Create tmp directory.

	The tmp directory can be the next options.
	- In RAM /tmp/standardfiles_XXXXX (default)
	- In the current directory, in this mode the command create a tmp
		directory.
	"""

	message.step("Create tmp directory")
	new_tmp = None
	if config.options.mode.notmp:
		current_tmp = os.getcwd()
		new_tmp = uuid.uuid4().hex[:8]
		new_tmp = f"{current_tmp}/tmp_{new_tmp}"
		# Remove directory
		command = f"rm -rf {new_tmp}"
		status, _ = run_command(command.split())
		if status:
			message.error("Can't delete the ./tmp directory")
			sys.exit(-1)
	else:
		new_tmp = uuid.uuid4().hex[:8]
		new_tmp = f"/tmp/standardfiles_{new_tmp}"

	# Create tmp
	try:
		os.makedirs(new_tmp)
	except OSError:
		message.error("Can't create tmp directory: {new_tmp}")
		sys.exit(-1)

	config.config.tmp_dir = new_tmp


def get_all():
	"""Return a list of directories and files in current directory."""

	return list(Path().glob('*'))


def get_tmpfile_name():
	"""Get a tmp name from file in tmp directory."""

	new_file = uuid.uuid4().hex
	return f"{config.config.tmp_dir}/{new_file}"


def move_file(file_origin, file_destine):
	"""Move file."""

	try:
		shutil.move(file_origin, file_destine)
	except (FileNotFoundError, PermissionError):
		return -1

	return 0


def remove_tmpdir():
	"""Remove tmp directory."""

	message.step("Remove tmp directory")
	command = f"rm -rf {config.config.tmp_dir}"
	status, _ = run_command(command.split())
	if status:
		message.error("Can't delete the tmp directory: {tmp_dir}")
		sys.exit(-1)


def replace_file(file_origin, file_destine, remove=False):
	"""Replace original file if it is different from tmpfile."""

	# Check if files exist
	if not os.path.exists(file_origin):
		message.warning(f"Don't exist the origin file: {file_origin}")
		return -1
	if not os.path.exists(file_destine):
		message.warning(f"Don't exist the destine file: {file_destine}")
		return -2

	# If the same file
	if filecmp.cmp(file_origin, file_destine):
		if remove:
			os.remove(file_origin)
		return 0

	# Replace file
	command = f"cp {file_origin} {file_destine}"
	status, _ = run_command(command.split())
	if status:
		message.warning(f"Don't replace: {file_destine}")
		return -1

	# Remove origin file
	if remove:
		os.remove(file_origin)

	return 0


def run_command(command, shell=False):
	"""Run a command"""

	try:
		info = subprocess.run(
			command,
			shell=shell,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			check=True
		)
	except subprocess.CalledProcessError as e:
		return -1, e.output.decode('utf-8')

	return 0, info


__all__ = [
	'check_size',
	'create_tmpdir',
	'get_all',
	'get_tmpfile_name',
	'move_file',
	'remove_tmpdir',
	'replace_file',
	'run_command',
]
