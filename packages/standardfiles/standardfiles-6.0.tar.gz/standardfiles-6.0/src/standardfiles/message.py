# See LICENSE file for copyright and license details.
"""Module to print messages."""


class Message:
	"""Print multiple messages by type."""

	color = {
		"null": "\x1b[1;0m",
		"bold": "\x1b[01m",
		"Red": "\x1b[1;31m",
		"red": "\x1b[0;31m",
		"green": "\x1b[0;32m",
		"Green": "\x1b[1;32m",
		"yellow": "\x1b[33m",
		"Cyan": "\x1b[1;36m"
	}

	def rename(self, old, new):
		"""Rename a file or directory."""

		print(
			f"{self.color['green']}{old}"
			f"{self.color['red']} -> "
			f"{self.color['null']}{new}"
		)

	def file(self, file):
		"""Print a file."""

		print(f"{self.color['null']}{file}")

	def format(self, img, ext):
		"""Print a format from image."""

		print(
			f"{self.color['green']}[{ext}] "
			f"{self.color['null']}{img}"
		)

	def process(self, s):
		"""Start process."""

		print(f"{self.color['Cyan']}[P] {s}{self.color['null']}")

	def step(self, s):
		"""Print process step."""

		print(f"{self.color['Green']}[*] {s}{self.color['null']}")

	def message(self, s):
		"""Normal message."""

		print(f"{self.color['green']}[.] {s}{self.color['null']}")

	def warning(self, s):
		"""Warning message."""

		print(f"{self.color['red']}[W] {s}{self.color['null']}")

	def error(self, s):
		"""Error message."""

		print(f"{self.color['Red']}[E] {s}{self.color['null']}")


message = Message()
