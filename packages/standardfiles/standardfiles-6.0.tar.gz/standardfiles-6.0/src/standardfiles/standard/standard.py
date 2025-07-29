# See LICENSE file for copyright and license details.
"""Sub-module entry point."""
import os
from multiprocessing.dummy import Pool as ThreadPool

from standardfiles import utils
from standardfiles.file.utils import get_files
from standardfiles.message import message
from standardfiles.options import config
from standardfiles.standard.audio import convert_to_standard_audio
from standardfiles.standard.image import convert_to_standard_image
from standardfiles.standard.pdf import convert_to_standard_pdf
from standardfiles.standard.video import convert_to_standard_video


def convert_to_standard():
	"""Convert to standard files.

	Convert all files in current files to standard files.

	The standard files are.
	- image: .ff.bz2
	- pdf
	- audio: aac
	- video: mkv with h264 and aac
	"""

	if config.options.mode.replace:
		message.process("Convert to standard files (replace files)")
	else:
		message.process("Convert to standard files")

	utils.create_tmpdir()
	all_files = get_files(standard=False)

	message.step("Convert and clean files")
	if all_files['img']:
		message.message("Images")
		os.makedirs(f'{config.config.tmp_dir}/image')
		pool = ThreadPool(config.options.mode.process)
		pool.map(convert_to_standard_image, all_files['img'])
		pool.close()
		pool.join()
	if all_files['pdf']:
		message.message("Pdf")
		os.makedirs(f'{config.config.tmp_dir}/pdf')
		pool = ThreadPool(config.options.mode.process)
		pool.map(convert_to_standard_pdf, all_files['pdf'])
		pool.close()
		pool.join()
	if all_files['audio']:
		message.message("audio")
		os.makedirs(f'{config.config.tmp_dir}/audio')
		for file in all_files['audio']:
			utils.check_size(file)
			convert_to_standard_audio(file)
	if all_files['video']:
		message.message("Video")
		os.makedirs(f'{config.config.tmp_dir}/video')
		for file in all_files['video']:
			utils.check_size(file)
			convert_to_standard_video(file)

	# Check mode replace
	if config.options.mode.replace:
		utils.remove_tmpdir()
		return 0

	# Get direcotrie
	current_dir = os.getcwd()
	end_dir = f"{current_dir}/standardfiles"
	current_tmp = config.config.tmp_dir

	# Remove old standard files
	message.process("Remove the current standard files")
	command = f"rm -fr {end_dir}"
	utils.run_command(command.split())

	# Save files
	message.process("Move the standard files")
	command = f"mv {current_tmp} {end_dir}"
	status, _ = utils.run_command(command.split())
	if status:
		message.error(f"Don't move the tmp directory: {current_tmp}")

	# Remove tmp directory
	config.config.tmp_dir = current_tmp
	utils.remove_tmpdir()

	return 0
