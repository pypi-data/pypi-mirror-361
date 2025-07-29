#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from modusa.signals.signal_ops import SignalOps
from typing import Self, Any
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class AudioSignal(ModusaSignal):
	"""
	Represents a 1D audio signal within modusa framework.

	Note
	----
	- It is highly recommended to use  :class:`~modusa.io.AudioLoader` to instantiate an object of this class.
	- This class assumes audio is mono (1D numpy array).
	- Either `sr` (sampling rate) or `t` (time axis) must be provided.
	- If both `t` and `sr` are given, `t` takes precedence for timing and `sr` is computed from that.
	- If `t` is provided but `sr` is missing, `sr` is estimated from the `t`.
	- If `t` is provided, the starting time `t0` will be overridden by `t[0]`.

	Parameters
	----------
	y : np.ndarray
		1D numpy array representing the audio signal.
	sr : int | None
		Sampling rate in Hz. Required if `t` is not provided.
	t : np.ndarray | None
		Optional time axis corresponding to `y`. Must be the same length as `y`.
	t0 : float, optional
		Starting time in seconds. Defaults to 0.0. Set to `t[0]` if `t` is provided.
	title : str | None, optional
		Optional title for the signal. Defaults to `"Audio Signal"`.
	"""

	#--------Meta Information----------
	_name = "Audio Signal"
	_description = ""
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-04"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, y: np.ndarray, sr: int | None = None, t: np.ndarray | None = None, t0: float = 0.0, title: str | None = None):
		
		if y.ndim != 1:
			raise excp.InputValueError(f"`y` must have 1 dimension, not {y.ndim}.")
			
		if t is not None:
			if len(t) != len(y):
				raise excp.InputValueError("Length of `t` must match `y`.")
			if sr is None:
				# Estimate sr from t if not provided
				dt = t[1] - t[0]
				sr = round(1.0 / dt)  # Round to avoid floating-point drift
			t0 = float(t[0])  # Override t0 from first timestamp
			
		elif sr is None:
			raise excp.InputValueError("Either `sr` or `t` must be provided.")
			
		self._y = y
		self._sr = sr
		self._t0 = t0
		self.title = title or self._name
			
	#----------------------
	# Properties
	#----------------------
	@immutable_property("Create a new object instead.")
	def y(self) -> np.ndarray:
		"""Audio data."""
		return self._y
	
	@immutable_property("Create a new object instead.")
	def sr(self) -> np.ndarray:
		"""Sampling rate of the audio."""
		return self._sr
	
	@immutable_property("Create a new object instead.")
	def t0(self) -> np.ndarray:
		"""Start timestamp of the audio."""
		return self._t0
	
	@immutable_property("Create a new object instead.")
	def t(self) -> np.ndarray:
		"""Timestamp array of the audio."""
		return self.t0 + np.arange(len(self.y)) / self.sr 
	
	@immutable_property("Mutation not allowed.")
	def Ts(self) -> int:
		"""Sampling Period of the audio."""
		return 1.0 / self.sr

	@immutable_property("Mutation not allowed.")
	def duration(self) -> int:
		"""Duration of the audio."""
		return len(self.y) / self.sr
	
	@immutable_property("Mutation not allowed.")
	def info(self) -> None:
		"""Prints info about the audio."""
		print("-" * 50)
		print(f"{'Title':<20}: {self.title}")
		print(f"{'Kind':<20}: {self._name}")
		print(f"{'Duration':<20}: {self.duration:.2f} sec")
		print(f"{'Sampling Rate':<20}: {self.sr} Hz")
		print(f"{'Sampling Period':<20}: {(self.Ts*1000) :.4f} ms")
		print("-" * 50)
	
	#----------------------
	# Methods
	#----------------------
	def __getitem__(self, key):
		if isinstance(key, (int, slice)):
			# Basic slicing of 1D signals
			sliced_data = self._data[key]
			sliced_axis = self._axes[0][key]  # assumes only 1 axis
			
			return self.replace(data=sliced_data, axes=(sliced_axis, ))
		else:
			raise TypeError(
				f"Indexing with type {type(key)} is not supported. Use int or slice."
			)
			
	@validate_args_type()
	def crop(self, t_min: int | float | None = None, t_max: int | float | None = None) -> "AudioSignal":
		"""
		Crop the audio signal to a time range [t_min, t_max].

		.. code-block:: python

			from modusa.generators import AudioSignalGenerator
			audio_example = AudioSignalGenerator.generate_example()
			cropped_audio = audio_example.crop(1.5, 2)
	
		Parameters
		----------
		t_min : float or None
			Inclusive lower time bound. If None, no lower bound.
		t_max : float or None
			Exclusive upper time bound. If None, no upper bound.
	
		Returns
		-------
		AudioSignal
			Cropped audio signal.
		"""
		y = self.y
		t = self.t
		
		mask = np.ones_like(t, dtype=bool)
		if t_min is not None:
			mask &= (t >= t_min)
		if t_max is not None:
			mask &= (t < t_max)
			
		cropped_y = y[mask]
		new_t0 = t[mask][0] if np.any(mask) else self.t0  # fallback to original t0 if mask is empty
		
		return self.__class__(y=cropped_y, sr=self.sr, t0=new_t0, title=self.title)
	
	
	@validate_args_type()
	def plot(
		self,
		scale_y: tuple[float, float] | None = None,
		ax: plt.Axes | None = None,
		color: str = "b",
		marker: str | None = None,
		linestyle: str | None = None,
		stem: bool | None = False,
		legend_loc: str | None = None,
		title: str | None = None,
		ylabel: str | None = "Amplitude",
		xlabel: str | None = "Time (sec)",
		ylim: tuple[float, float] | None = None,
		xlim: tuple[float, float] | None = None,
		highlight: list[tuple[float, float]] | None = None,
	) -> plt.Figure:
		"""
		Plot the audio waveform using matplotlib.
		
		.. code-block:: python
		
			from modusa.generators import AudioSignalGenerator
			audio_example = AudioSignalGenerator.generate_example()
			audio_example.plot(color="orange", title="Example Audio")
		
		Parameters
		----------
		scale_y : tuple of float, optional
			Range to scale the y-axis data before plotting. Useful for normalization.
		ax : matplotlib.axes.Axes, optional
			Pre-existing axes to plot into. If None, a new figure and axes are created.
		color : str, optional
			Color of the waveform line. Default is `"b"` (blue).
		marker : str or None, optional
			Marker style for each point. Follows matplotlib marker syntax.
		linestyle : str or None, optional
			Line style for the waveform. Follows matplotlib linestyle syntax.
		stem : bool, optional
			If True, use a stem plot instead of a continuous line.
		legend_loc : str or None, optional
			If provided, adds a legend at the specified location (e.g., "upper right").
		title : str or None, optional
			Plot title. Defaults to the signal’s title.
		ylabel : str or None, optional
			Label for the y-axis. Defaults to `"Amplitude"`.
		xlabel : str or None, optional
			Label for the x-axis. Defaults to `"Time (sec)"`.
		ylim : tuple of float or None, optional
			Limits for the y-axis.
		xlim : tuple of float or None, optional
			Limits for the x-axis.
		highlight : list of tuple of float or None, optional
			List of time intervals to highlight on the plot, each as (start, end).
		
		Returns
		-------
		matplotlib.figure.Figure
			The figure object containing the plot.
		"""
		
		from modusa.io import Plotter
		
		title = title or self.title
		
		fig: plt.Figure | None = Plotter.plot_signal(y=self.y, x=self.t, scale_y=scale_y, ax=ax, color=color, marker=marker, linestyle=linestyle, stem=stem, legend_loc=legend_loc, title=title, ylabel=ylabel, xlabel=xlabel, ylim=ylim, xlim=xlim, highlight=highlight)
		
		return fig
	
	def play(self, regions: list[tuple[float, float], ...] | None = None, title: str | None = None):
		"""
		Play the audio signal inside a Jupyter Notebook.
	
		.. code-block:: python
	
			from modusa.generators import AudioSignalGenerator
			audio = AudioSignalGenerator.generate_example()
			audio.play(regions=[(0.0, 1.0), (2.0, 3.0)])
	
		Parameters
		----------
		regions : list of tuple of float, optional
			List of (start_time, end_time) pairs in seconds specifying the regions to play.
			If None, the entire signal is played.
		title : str or None, optional
			Optional title for the player interface. Defaults to the signal’s internal title.
	
		Returns
		-------
		IPython.display.Audio
			An interactive audio player widget for Jupyter environments.

		Note
		----
		- This method uses :class:`~modusa.io.AudioPlayer` to render an interactive audio player.
		- Optionally, specific regions of the signal can be played back, each defined by a (start, end) time pair.
		"""
		
		from modusa.io import AudioPlayer
		audio_player = AudioPlayer.play(y=self.y, sr=self.sr, regions=regions, title=self.title)
		
		return audio_player
	
	def to_spectrogram(
		self,
		n_fft: int = 2048,
		hop_length: int = 512,
		win_length: int | None = None,
		window: str = "hann"
	) -> "Spectrogram":
		"""
		Compute the Short-Time Fourier Transform (STFT) and return a Spectrogram object.
		
		Parameters
		----------
		n_fft : int
			FFT size.
		win_length : int or None
			Window length. Defaults to `n_fft` if None.
		hop_length : int
			Hop length between frames.
		window : str
			Type of window function to use (e.g., 'hann', 'hamming').
		
		Returns
		-------
		Spectrogram
			Spectrogram object containing S (complex STFT), t (time bins), and f (frequency bins).
		"""
		from modusa.signals.spectrogram import Spectrogram
		import librosa
		
		S = librosa.stft(self.y, n_fft=n_fft, win_length=win_length, hop_length=hop_length, window=window)
		f = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)
		t = librosa.frames_to_time(np.arange(S.shape[1]), sr=self.sr, hop_length=hop_length)
		t += self.t0
		spec = Spectrogram(S=S, f=f, t=t)
		if self.title != self._name: # Means title of the audio was reset so we pass that info to spec
			spec.title = self.title
			
		return spec
	
	
	#----------------------------
	# Math ops
	#----------------------------
	
	def __array__(self, dtype=None):
		return np.asarray(self._S, dtype=dtype)
	
	def __add__(self, other):
		other_data = other.y if isinstance(other, self.__class__) else other
		result = np.add(self.y, other_data)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __radd__(self, other):
		result = np.add(other, self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __sub__(self, other):
		other_data = other.y if isinstance(other, self.__class__) else other
		result = np.subtract(self.y, other_data)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __rsub__(self, other):
		result = np.subtract(other, self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __mul__(self, other):
		other_data = other.y if isinstance(other, self.__class__) else other
		result = np.multiply(self.y, other_data)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __rmul__(self, other):
		result = np.multiply(other, self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __truediv__(self, other):
		other_data = other.y if isinstance(other, self.__class__) else other
		result = np.true_divide(self.y, other_data)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __rtruediv__(self, other):
		result = np.true_divide(other, self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __floordiv__(self, other):
		other_data = other._y if isinstance(other, self.__class__) else other
		result = np.floor_divide(self.y, other_data)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __rfloordiv__(self, other):
		result = np.floor_divide(other, self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __pow__(self, other):
		other_data = other.y if isinstance(other, self.__class__) else other
		result = np.power(self.y, other_data)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __rpow__(self, other):
		result = np.power(other, self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def __abs__(self):
		result = np.abs(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)
	
	
	#--------------------------
	# Other signal ops
	#--------------------------
	def sin(self) -> Self:
		"""Compute the element-wise sine of the signal data."""
		result = np.sin(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def cos(self) -> Self:
		"""Compute the element-wise cosine of the signal data."""
		result = np.cos(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def exp(self) -> Self:
		"""Compute the element-wise exponential of the signal data."""
		result = np.exp(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def tanh(self) -> Self:
		"""Compute the element-wise hyperbolic tangent of the signal data."""
		result = np.tanh(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def log(self) -> Self:
		"""Compute the element-wise natural logarithm of the signal data."""
		result = np.log(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def log1p(self) -> Self:
		"""Compute the element-wise natural logarithm of (1 + signal data)."""
		result = np.log1p(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def log10(self) -> Self:
		"""Compute the element-wise base-10 logarithm of the signal data."""
		result = np.log10(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)

	def log2(self) -> Self:
		"""Compute the element-wise base-2 logarithm of the signal data."""
		result = np.log2(self.y)
		return self.__class__(y=result, sr=self.sr, t0=self.t0, title=self.title)
	

	#--------------------------
	# Aggregation signal ops
	#--------------------------
	def mean(self) -> float:
		"""Compute the mean of the signal data."""
		return float(np.mean(self.y))
	
	def std(self) -> float:
		"""Compute the standard deviation of the signal data."""
		return float(np.std(self.y))
	
	def min(self) -> float:
		"""Compute the minimum value in the signal data."""
		return float(np.min(self.y))
	
	def max(self) -> float:
		"""Compute the maximum value in the signal data."""
		return float(np.max(self.y))
	
	def sum(self) -> float:
		"""Compute the sum of the signal data."""
		return float(np.sum(self.y))
	
	#-----------------------------------
	# Repr
	#-----------------------------------
	
	def __str__(self):
		cls = self.__class__.__name__
		data = self.y
		
		arr_str = np.array2string(
			data,
			separator=", ",
			threshold=50,       # limit number of elements shown
			edgeitems=3,          # show first/last 3 rows and columns
			max_line_width=120,   # avoid wrapping
			formatter={'float_kind': lambda x: f"{x:.4g}"}
		)
		
		return f"Signal({arr_str}, shape={data.shape}, kind={cls})"
	
	def __repr__(self):
		cls = self.__class__.__name__
		data = self.y
		
		arr_str = np.array2string(
			data,
			separator=", ",
			threshold=50,       # limit number of elements shown
			edgeitems=3,          # show first/last 3 rows and columns
			max_line_width=120,   # avoid wrapping
			formatter={'float_kind': lambda x: f"{x:.4g}"}
		)
		
		return f"Signal({arr_str}, shape={data.shape}, kind={cls})"