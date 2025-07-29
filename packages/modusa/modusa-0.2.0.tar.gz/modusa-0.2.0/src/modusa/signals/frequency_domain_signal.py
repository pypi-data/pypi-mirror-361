#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from typing import Self, Any
import numpy as np
import matplotlib.pyplot as plt

class FrequencyDomainSignal(ModusaSignal):
	"""
	Represents a 1D signal in the frequency domain.
	
	Note
	----
	- The class is not intended to be instantiated directly 
	This class stores the Complex spectrum of a signal
	along with its corresponding frequency axis. It optionally tracks the time
	origin (`t0`) of the spectral slice, which is useful when working with
	time-localized spectral data (e.g., from a spectrogram or short-time Fourier transform).

	Parameters
	----------
	spectrum : np.ndarray
		The frequency-domain representation of the signal (real or complex-valued).
	f : np.ndarray
		The frequency axis corresponding to the spectrum values. Must match the shape of `spectrum`.
	t0 : float, optional
		The time (in seconds) corresponding to the origin of this spectral slice. Defaults to 0.0.
	title : str, optional
		An optional title for display or plotting purposes.
	"""
	#--------Meta Information----------
	_name = ""
	_description = ""
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-09"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, spectrum: np.ndarray, f: np.ndarray, t0: float | int = 0.0, title: str | None = None):
		super().__init__() # Instantiating `ModusaSignal` class
		
		if spectrum.shape != f.shape:
			raise excp.InputValueError(f"`spectrum` and `f` shape must match, got {spectrum.shape} and {f.shape}")
		
		
		self._spectrum = spectrum
		self._f = f
		self._t0 = float(t0)
	
		self.title = title or self._name # This title will be used as plot title by default
		
	
	#----------------------
	# Properties
	#----------------------
	
	@immutable_property("Create a new object instead.")
	def spectrum(self) -> np.ndarray:
		"""Complex valued spectrum data."""
		return self._spectrum
	
	@immutable_property("Create a new object instead.")
	def f(self) -> np.ndarray:
		"""frequency array of the spectrum."""
		return self._f
	
	@immutable_property("Create a new object instead.")
	def t0(self) -> np.ndarray:
		"""Time origin (in seconds) of this spectral slice, e.g., from a spectrogram frame."""
		return self._t0
	
	def __len__(self):
		return len(self._y)
	
	
	#----------------------
	# Tools
	#----------------------
	
	def __getitem__(self, key: slice) -> Self:
		sliced_spectrum = self._spectrum[key]
		sliced_f = self._f[key]
		return self.__class__(spectrum=sliced_spectrum, f=sliced_f, t0=self.t0, title=self.title)
	
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
		xlabel: str | None = "Freq (Hz)",
		ylim: tuple[float, float] | None = None,
		xlim: tuple[float, float] | None = None,
		highlight: list[tuple[float, float]] | None = None,
	) -> plt.Figure:
		"""
		Plot the frequency-domain signal as a line or stem plot.
		
		.. code-block:: python

			spectrum.plot(stem=True, color="r", title="FFT Frame", xlim=(0, 5000))
		
		Parameters
		----------
		scale_y : tuple[float, float], optional
			Range to scale the spectrum values before plotting (min, max).
		ax : matplotlib.axes.Axes, optional
			Axis to plot on. If None, a new figure and axis are created.
		color : str, default="b"
			Color of the line or stem.
		marker : str, optional
			Marker style for points (ignored if stem=True).
		linestyle : str, optional
			Line style for the plot (ignored if stem=True).
		stem : bool, default=False
			Whether to use a stem plot instead of a line plot.
		legend_loc : str, optional
			Legend location (e.g., 'upper right'). If None, no legend is shown.
		title : str, optional
			Title of the plot. Defaults to signal title.
		ylabel : str, default="Amplitude"
			Label for the y-axis.
		xlabel : str, default="Freq (Hz)"
			Label for the x-axis.
		ylim : tuple[float, float], optional
			Limits for the y-axis.
		xlim : tuple[float, float], optional
			Limits for the x-axis.
		highlight : list[tuple[float, float]], optional
			Regions to highlight on the frequency axis as shaded spans.
		
		Returns
		-------
		matplotlib.figure.Figure
			The figure containing the plotted signal.
		
		Note
		----
		- If `ax` is provided, the plot is drawn on it; otherwise, a new figure is created.
		- `highlight` can be used to emphasize frequency bands (e.g., formants, harmonics).
		- Use `scale_y` to clip or normalize extreme values before plotting.
		"""
		
		
		from modusa.io import Plotter
		
		title = title or self.title
		
		fig: plt.Figure | None = Plotter.plot_signal(y=self.spectrum, x=self.f, scale_y=scale_y, ax=ax, color=color, marker=marker, linestyle=linestyle, stem=stem, legend_loc=legend_loc, title=title, ylabel=ylabel, xlabel=xlabel, ylim=ylim, xlim=xlim, highlight=highlight)
		
		return fig
	
	#----------------------------
	# Math ops
	#----------------------------
	
	def __array__(self, dtype=None):
		return np.asarray(self.spectrum, dtype=dtype)
	
	def __add__(self, other):
		other_data = other.spectrum if isinstance(other, self.__class__) else other
		result = np.add(self.spectrum, other_data)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __radd__(self, other):
		result = np.add(other, self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __sub__(self, other):
		other_data = other.spectrum if isinstance(other, self.__class__) else other
		result = np.subtract(self.spectrum, other_data)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __rsub__(self, other):
		result = np.subtract(other, self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __mul__(self, other):
		other_data = other.spectrum if isinstance(other, self.__class__) else other
		result = np.multiply(self.spectrum, other_data)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __rmul__(self, other):
		result = np.multiply(other, self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __truediv__(self, other):
		other_data = other.spectrum if isinstance(other, self.__class__) else other
		result = np.true_divide(self.spectrum, other_data)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __rtruediv__(self, other):
		result = np.true_divide(other, self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __floordiv__(self, other):
		other_data = other.spectrum if isinstance(other, self.__class__) else other
		result = np.floor_divide(self.spectrum, other_data)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __rfloordiv__(self, other):
		result = np.floor_divide(other, self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __pow__(self, other):
		other_data = other.spectrum if isinstance(other, self.__class__) else other
		result = np.power(self.spectrum, other_data)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __rpow__(self, other):
		result = np.power(other, self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def __abs__(self):
		result = np.abs(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	
	#--------------------------
	# Other signal ops
	#--------------------------
	def sin(self) -> Self:
		"""Compute the element-wise sine of the signal data."""
		result = np.sin(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def cos(self) -> Self:
		"""Compute the element-wise cosine of the signal data."""
		result = np.cos(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def exp(self) -> Self:
		"""Compute the element-wise exponential of the signal data."""
		result = np.exp(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def tanh(self) -> Self:
		"""Compute the element-wise hyperbolic tangent of the signal data."""
		result = np.tanh(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def log(self) -> Self:
		"""Compute the element-wise natural logarithm of the signal data."""
		result = np.log(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def log1p(self) -> Self:
		"""Compute the element-wise natural logarithm of (1 + signal data)."""
		result = np.log1p(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def log10(self) -> Self:
		"""Compute the element-wise base-10 logarithm of the signal data."""
		result = np.log10(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	def log2(self) -> Self:
		"""Compute the element-wise base-2 logarithm of the signal data."""
		result = np.log2(self.spectrum)
		return self.__class__(spectrum=result, f=self.f, t0=self.t0, title=self.title)
	
	
	#--------------------------
	# Aggregation signal ops
	#--------------------------
	def mean(self) -> float:
		"""Compute the mean of the signal data."""
		return float(np.mean(self.spectrum))
	
	def std(self) -> float:
		"""Compute the standard deviation of the signal data."""
		return float(np.std(self.spectrum))
	
	def min(self) -> float:
		"""Compute the minimum value in the signal data."""
		return float(np.min(self.spectrum))
	
	def max(self) -> float:
		"""Compute the maximum value in the signal data."""
		return float(np.max(self.spectrum))
	
	def sum(self) -> float:
		"""Compute the sum of the signal data."""
		return float(np.sum(self.spectrum))
	
	#-----------------------------------
	# Repr
	#-----------------------------------
	
	def __str__(self):
		cls = self.__class__.__name__
		data = self.spectrum
		
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
		data = self.spectrum
		
		arr_str = np.array2string(
			data,
			separator=", ",
			threshold=50,       # limit number of elements shown
			edgeitems=3,          # show first/last 3 rows and columns
			max_line_width=120,   # avoid wrapping
			formatter={'float_kind': lambda x: f"{x:.4g}"}
		)
		
		return f"Signal({arr_str}, shape={data.shape}, kind={cls})"
	