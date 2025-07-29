# See LICENSE file for copyright and license details.
"""Module to get configuration."""
from dataclasses import dataclass


@dataclass()
class OptionsMode:
	"""Mode to run command."""
	notmp: bool = False
	process: int = None
	recursive: bool = False
	replace: bool = False


@dataclass()
class Options:
	"""Run options."""

	image: bool = False
	name: bool = False
	clear: bool = False
	version: bool = False

	mode: OptionsMode = None


@dataclass()
class Configuration:
	"""Run configuration."""

	tmp_dir: str = None
