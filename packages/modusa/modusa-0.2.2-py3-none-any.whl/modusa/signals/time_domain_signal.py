#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from typing import Self, Any
import numpy as np
import matplotlib.pyplot as plt

class TimeDomainSignal(ModusaSignal):
	"""
	Initialize a uniformly sampled 1D time-domain signal.
	
	This class is specifically designed to hold 1D signals that result
	from slicing a 2D representation like a spectrogram. For example,
	if you have a spectrogram `S` and you perform `S[10, :]`, the result
	is a 1D signal over time, this class provides a clean and consistent
	way to handle such slices.
	
	Parameters
	----------
	y : np.ndarray
		The 1D signal values sampled uniformly over time.
	sr : float
		The sampling rate in Hz (samples per second).
	t0 : float, optional
		The starting time of the signal in seconds (default is 0.0).
	title : str, optional
		An optional title used for labeling or plotting purposes.
	"""
	
	
	#--------Meta Information----------
	_name = "Time Domain Signal"
	_description = ""
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-09"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, y: np.ndarray, sr: float, t0: float = 0.0, title: str | None = None):
		super().__init__() # Instantiating `ModusaSignal` class
	
		self._y = y
		self._sr = sr
		self._t0 = t0
		self.title = title or self._name # This title will be used as plot title by default
	
	
	#----------------------
	# Properties
	#----------------------
	
	@immutable_property("Create a new object instead.")
	def y(self) -> np.ndarray:
		return self._y
	
	@immutable_property("Create a new object instead.")
	def sr(self) -> np.ndarray:
		return self._sr
	
	@immutable_property("Create a new object instead.")
	def t0(self) -> np.ndarray:
		""""""
		return self._t0
	
	@immutable_property("Create a new object instead.")
	def t(self) -> np.ndarray:
		return self.t0 + np.arange(len(self._y)) / self.sr
	
	def __len__(self):
		return len(self._y)
	
	#----------------------
	# Tools
	#----------------------
	
	def __getitem__(self, key: slice) -> Self:
		sliced_y = self._y[key]
		t0_new = self.t[key.start] if key.start is not None else self.t0
		return TimeDomainSignal(y=sliced_y, sr=self.sr, t0=t0_new, title=self.title)
		
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
		Plot the time-domain signal.
		
		.. code-block:: python

			signal.plot(color='g', marker='o', stem=True)
		
		Parameters
		----------
		scale_y : tuple[float, float], optional
			Min-max values to scale the y-axis data.
		ax : matplotlib.axes.Axes, optional
			Axes to plot on; if None, creates a new figure.
		color : str, default='b'
			Line or stem color.
		marker : str, optional
			Marker style for each data point.
		linestyle : str, optional
			Line style to use if not using stem plot.
		stem : bool, default=False
			Whether to draw a stem plot instead of a line plot.
		legend_loc : str, optional
			If given, adds a legend at the specified location.
		
		Returns
		-------
		matplotlib.axes.Axes
			The axes object containing the plot.
		
		Note
		----
		This is useful for visualizing 1D signals obtained from time slices of spectrograms.
		"""
		
		from modusa.io import Plotter
		
		title = title or self.title
		
		fig: plt.Figure | None = Plotter.plot_signal(y=self.y, x=self.t, scale_y=scale_y, ax=ax, color=color, marker=marker, linestyle=linestyle, stem=stem, legend_loc=legend_loc, title=title, ylabel=ylabel, xlabel=xlabel, ylim=ylim, xlim=xlim, highlight=highlight)
		
		return fig
	
	#----------------------------
	# Math ops
	#----------------------------
	
	def __array__(self, dtype=None):
		return np.asarray(self.y, dtype=dtype)
	
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
		other_data = other.y if isinstance(other, self.__class__) else other
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