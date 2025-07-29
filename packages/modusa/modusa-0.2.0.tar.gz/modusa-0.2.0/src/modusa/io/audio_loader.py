#!/usr/bin/env python3

from modusa.io import ModusaIO
from modusa.signals import AudioSignal
from modusa.decorators import validate_args_type
from pathlib import Path
import tempfile
import numpy as np

class AudioLoader(ModusaIO):
	"""
	Loads audio from various sources like filepath, YouTube, etc.
	
	Note
	----
	- All `from_` methods return :class:`~modusa.signals.AudioSignal` instance.
	
	"""
	
	#--------Meta Information----------
	_name = "Audio Loader"
	_description = "Loads audio from various sources."
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-05"
	#----------------------------------
	
	def __init__(self):
		super().__init__()

	@staticmethod
	@validate_args_type()
	def from_youtube(url: str, sr: int | None = None) -> "AudioSignal":
		"""
		Loads audio from youtube url using :class:`~modusa.io.YoutubeDownloader`,
		:class:`~modusa.io.AudioConverter` and `librosa`.

		.. code-block:: python
			
			from modusa.io import AudioSignalLoader
		
			# From youtube
			audio_signal = AudioSignalLoader.from_youtube(
				url="https://www.youtube.com/watch?v=lIpw9-Y_N0g", 
				sr=None
			)

		PARAMETERS
		----------
		url: str
			Link to the YouTube video.
		sr: int
			Sampling rate to load the audio in.
		
		Returns
		-------
		
		AudioSignal:
			`Audio signal` instance with loaded audio content from YouTube.
		"""

		from modusa.io import YoutubeDownloader, AudioConverter
		import librosa
		
		# Download the audio in temp directory using tempfile module
		with tempfile.TemporaryDirectory() as tmpdir:
			audio_fp: Path = YoutubeDownloader.download(url=url, content_type="audio", output_dir=Path(tmpdir))
			
			# Convert the audio to ".wav" form for loading
			wav_audio_fp: Path = AudioConverter.convert(inp_audio_fp=audio_fp, output_audio_fp=audio_fp.with_suffix(".wav"))
			
			# Load the audio in memory and return that
			audio_data, audio_sr = librosa.load(wav_audio_fp, sr=sr)
		
		audio = AudioSignal(y=audio_data, sr=sr, title=audio_fp.stem)

		return audio
	
	@staticmethod
	@validate_args_type()
	def from_fp(fp: str | Path, sr: int | None = None) -> AudioSignal:
		"""
		Loads audio from a filepath using `librosa`.

		.. code-block:: python
			
			from modusa.io import AudioSignalLoader
			
			# From file
			audio_signal = AudioSignalLoader.from_fp(
				fp="path/to/audio.wav", 
				sr=None
			)

		Parameters
		----------
		fp: str | Path
			Local filepath of the audio.
		sr: int | None
			Sampling rate to load the audio in.
		
		Returns
		-------
		AudioSignal
			`Audio signal` instance with loaded audio content from filepath.
		
		"""
		import librosa
		
		fp = Path(fp)
		y, sr = librosa.load(fp, sr=sr)
		
		audio_signal = AudioSignal(y=y, sr=sr, title=fp.name)
		
		return audio_signal
	
	
	@staticmethod
	def from_array(y: np.ndarray, t: np.ndarray | None = None) -> AudioSignal:
		"""
		Loads audio from numpy arrays.

		.. code-block:: python
			
			from modusa.io import AudioSignalLoader
			import numpy as np
			
			# From numpy array
			audio_signal = AudioSignalLoader.from_array(
				x=np.random.random((100, )),
				t = None # Automatically creates time index (integer)
			)

		Parameters
		----------
		y: np.ndarray
			Data of the audio signal.
		t: np.ndarray | None
			Corresponding time stamps of the audio signal.
		
		Returns
		-------
		AudioSignal
			`Audio signal` instance with loaded audio content from arrays.
		"""
		
		return  AudioSignal(y=y, t=t)
	
	@staticmethod
	def from_array_with_sr(y: np.ndarray, sr: int) -> AudioSignal:
		"""
		Loads audio with a given sampling rate.
	
		.. code-block:: python
			
			from modusa.io import AudioSignalLoader
			import numpy as np
			
			# From numpy array
			audio_signal = AudioSignalLoader.from_array_with_sr(
				x=np.random.random((100, )),
				sr = 100 # Automatically generates time index
			)

		Parameters
		----------
		y: np.ndarray
			Data of the audio signal.
		sr: int
			Sampling rate of the audio signal.
		
		Returns
		-------
		AudioSignal
			`Audio signal` instance with loaded audio content from sampling rate.
		"""
		
		return AudioSignal(y=y, sr=sr)
	
	@staticmethod
	def from_list(y: list, t: list) -> AudioSignal:
		"""
		Loads `AudioSignal` instance from python list.
		
		.. code-block:: python
			
			from modusa.io import AudioSignalLoader
			
			# From list
			audio_signal = AudioSignalLoader.from_list(
				y=[1, 2, 3, 2, 3],
				t = [0.1, 0.2, 0.3, 0.4, 0.5]
			)

		Parameters
		----------
		y: list
			Data of the audio signal.
		t: np.ndarray | None
			Corresponding time stamps of the audio signal.
		
		Returns
		-------
		AudioSignal
			`Audio signal` instance with loaded audio content from python list.
		"""
		y = np.array(y)
		t = np.array(t)
		
		return AudioSignal(y=y, t=t)
		
		