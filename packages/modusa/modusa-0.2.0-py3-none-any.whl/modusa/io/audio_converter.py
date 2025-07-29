#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import validate_args_type
from modusa.io.base import ModusaIO
from typing import Any
import subprocess
from pathlib import Path


class AudioConverter(ModusaIO):
	"""
	Converts audio using FFmpeg.

	Note
	----
	- Use `convert()` to perform the actual format conversion.
	- Requires FFMPEG to be installed on the system.
	"""
	
	#--------Meta Information----------
	_name = "Audio Converter"
	_description = "Convert audio files using ffmpeg"
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-05"
	#----------------------------------
	
	@staticmethod
	@validate_args_type()
	def convert(inp_audio_fp: str | Path, output_audio_fp: str | Path) -> Path:
		"""
		Converts an audio file from one format to another using FFmpeg.

		.. code-block:: python
			
			from modusa.engines import AudioConverter
			converted_audio_fp = AudioConverter.convert(
				inp_audio_fp="path/to/input/audio.webm", 
				output_audio_fp="path/to/output/audio.wav"
			)

		Parameters
		----------
		inp_audio_fp: str | Path
			Filepath of audio to be converted.
		output_audio_fp: str | Path
			Filepath of the converted audio. (e.g. name.mp3)

		Returns
		-------
		Path:
			Filepath of the converted audio.

		Note
		----
		- The conversion takes place based on the extensions of the input and output audio filepath.
		"""
		inp_audio_fp = Path(inp_audio_fp)
		output_audio_fp = Path(output_audio_fp)

		cmd = [
			"ffmpeg",
			"-y",  # Overwrite output
			"-i", str(inp_audio_fp),
			"-vn",  # No video
			str(output_audio_fp)
		]

		try:
			subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError:
			raise RuntimeError(f"FFmpeg failed to convert {inp_audio_fp} to {output_audio_fp}")
			
		return output_audio_fp