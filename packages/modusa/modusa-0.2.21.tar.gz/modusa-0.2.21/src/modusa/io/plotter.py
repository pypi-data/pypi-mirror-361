#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import validate_args_type
from modusa.io import ModusaIO
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
import warnings

warnings.filterwarnings("ignore", message="Glyph .* missing from font.*") # To supress any font related warnings, TODO: Add support to Devnagri font


class Plotter(ModusaIO):
	"""
	Plots different kind of signals using `matplotlib`.
	
	Note
	----
	- The class has `plot_` methods to plot different types of signals (1D, 2D).

	"""
	
	#--------Meta Information----------
	_name = ""
	_description = ""
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-06"
	#----------------------------------

	@staticmethod
	def plot_signal(
		y: np.ndarray,
		x: np.ndarray | None,
		scale_y: tuple[float, float] | None = None,
		ax: plt.Axes | None = None,
		color: str = "k",
		marker: str | None = None,
		linestyle: str | None = None,
		stem: bool = False,
		labels: tuple[str, str, str] | None = None,
		legend_loc: str | None = None,
		title: str | None = None,
		ylabel: str | None = None,
		xlabel: str | None = None,
		ylim: tuple[float, float] | None = None,
		xlim: tuple[float, float] | None = None,
		highlight: list[tuple[float, float], ...] | None = None,
	) -> plt.Figure | None:
		"""
		Plots 1D signal using `matplotlib` with various settings passed through the
		arguments.

		.. code-block:: python
			
			from modusa.io import Plotter
			import numpy as np
			
			# Generate a sample sine wave
			x = np.linspace(0, 2 * np.pi, 100)
			y = np.sin(x)
			
			# Plot the signal
			fig = Plotter.plot_signal(
				y=y,
				x=x,
				scale_y=None,
				ax=None,
				color="blue",
				marker=None,
				linestyle="-",
				stem=False,
				labels=("Time", "Amplitude", "Sine Wave"),
				legend_loc="upper right",
				zoom=None,
				highlight=[(2, 4)]
			)

		
		Parameters
		----------
		y: np.ndarray
			The signal values to plot on the y-axis.
		x: np.ndarray | None
			The x-axis values. If None, indices of `y` are used.
		scale_y: tuple[float, float] | None
			Linear scaling for `y` values, (a, b) => ay+b
		ax: plt.Axes | None
			matplotlib Axes object to draw on. If None, a new figure and axis are created. Return type depends on parameter value.
		color: str
			Color of the plotted line or markers. (e.g. "k")
		marker: str | None
			marker style for the plot (e.g., 'o', 'x'). If None, no marker is used.
		linestyle: str | None
			Line style for the plot (e.g., '-', '--'). If None, no line is drawn.
		stem: bool
			If True, plots a stem plot.
		labels: tuple[str, str, str] | None
			Tuple containing (title, xlabel, ylabel). If None, no labels are set.
		legend_loc: str | None
			Location string for legend placement (e.g., 'upper right'). If None, no legend is shown.
		zoom: tuple | None
			Tuple specifying x-axis limits for zoom as (start, end). If None, full x-range is shown.
		highlight: list[tuple[float, float], ...] | None
			List of (start, end) tuples to highlight regions on the plot. e.g. [(1, 2.5), (6, 10)]
		
		Returns
		-------
		plt.Figure | None
			Figure if `ax` is None else None.
		
		
		"""
		
		# Validate the important args and get the signal that needs to be plotted
		if y.ndim != 1:
			raise excp.InputValueError(f"`y` must be of dimension 1 not {y.ndim}.")
		if y.shape[0] < 1:
			raise excp.InputValueError(f"`y` must not be empty.")
			
		if x is None:
			x = np.arange(y.shape[0])
		elif x.ndim != 1:
			raise excp.InputValueError(f"`x` must be of dimension 1 not {x.ndim}.")
		elif x.shape[0] < 1:
			raise excp.InputValueError(f"`x` must not be empty.")
			
		if x.shape[0] != y.shape[0]:
			raise excp.InputValueError(f"`y` and `x` must be of same shape")
			
		# Scale the signal if needed
		if scale_y is not None:
			if len(scale_y) != 2:
				raise excp.InputValueError(f"`scale_y` must be tuple of two values (1, 2) => 1y+2")
			a, b = scale_y
			y = a * y + b
			
		# Create a figure
		if ax is None:
			fig, ax = plt.subplots(figsize=(15, 2))
			created_fig = True
		else:
			fig = ax.get_figure()
			created_fig = False 
			
		# Plot the signal with right configurations
		plot_label = labels[0] if labels is not None and len(labels) > 0 else None
		if stem:
			ax.stem(x, y, linefmt=color, markerfmt='o', label=title)
		elif marker is not None:
			ax.plot(x, y, c=color, linestyle=linestyle, lw=1.5, marker=marker, label=title)
		else:
			ax.plot(x, y, c=color, linestyle=linestyle, lw=1.5, label=title)
			
		# Add legend
		if legend_loc is not None:
			ax.legend(loc=legend_loc)
			
		# Set the labels
		if title is not None:
			ax.set_title(title)
		if ylabel is not None:
			ax.set_ylabel(ylabel)
		if xlabel is not None:
			ax.set_xlabel(xlabel)
				
		# Applying axes limits into a region
		if ylim is not None:
			ax.set_ylim(ylim)
		if xlim is not None:
			ax.set_xlim(xlim)
			
		# Highlight a list of regions
		if highlight is not None:
			for highlight_region in highlight:
				if len(highlight_region) != 2:
					raise excp.InputValueError(f"`highlight should be a list of tuple of 2 values (left, right) => (1, 10.5)")
				l, r = highlight_region
				ax.add_patch(Rectangle((l, np.min(y)), r - l, np.max(y) - np.min(y), color='red', alpha=0.2, zorder=10))
				
		# Show/Return the figure as per needed
		if created_fig:
			fig.tight_layout()
			if Plotter._in_notebook():
				plt.close(fig)
				return fig
			else:
				plt.show()
				return fig
	
	@staticmethod
	@validate_args_type()
	def plot_matrix(
		M: np.ndarray,
		r: np.ndarray | None = None,
		c: np.ndarray | None = None,
		log_compression_factor: int | float | None = None,
		ax: plt.Axes | None = None,
		cmap: str = "gray_r",
		title: str | None = None,
		Mlabel: str | None = None,
		rlabel: str | None = None,
		clabel: str | None = None,
		rlim: tuple[float, float] | None = None,
		clim: tuple[float, float] | None = None,
		highlight: list[tuple[float, float, float, float]] | None = None,
		origin: str = "lower",  # or "lower"
		show_colorbar: bool = True,
		cax: plt.Axes | None = None,
		show_grid: bool = True,
		tick_mode: str = "center",  # "center" or "edge"
		n_ticks: tuple[int, int] | None = None,
	) -> plt.Figure:
		"""
		Plot a 2D matrix with optional zooming, highlighting, and grid.

		.. code-block:: python
		
			from modusa.io import Plotter
			import numpy as np
			import matplotlib.pyplot as plt
			
			# Create a 50x50 random matrix
			M = np.random.rand(50, 50)
			
			# Coordinate axes
			r = np.linspace(0, 1, M.shape[0])
			c = np.linspace(0, 1, M.shape[1])
			
			# Plot the matrix
			fig = Plotter.plot_matrix(
				M=M,
				r=r,
				c=c,
				log_compression_factor=None,
				ax=None,
				labels=None,
				zoom=None,
				highlight=None,
				cmap="viridis",
				origin="lower",
				show_colorbar=True,
				cax=None,
				show_grid=False,
				tick_mode="center",
				n_ticks=(5, 5),
			)

		
		Parameters
		----------
		M: np.ndarray
			2D matrix to plot.
		r: np.ndarray
			Row coordinate axes.
		c: np.ndarray
			Column coordinate axes.
		log_compression_factor: int | float | None
			Apply log compression to enhance contrast (if provided).
		ax: plt.Axes | None
			Matplotlib axis to draw on (creates new if None).
		labels: tuple[str, str, str, str] | None
			Labels for the plot (title, Mlabel, xlabel, ylabel).
		zoom: tuple[float, float, float, float] | None
			Zoom to (r1, r2, c1, c2) in matrix coordinates.
		highlight: list[tuple[float, float, float, float]] | None
			List of rectangles (r1, r2, c1, c2) to highlight.
		cmap: str
			Colormap to use.
		origin: str
			Image origin, e.g., "upper" or "lower".
		show_colorbar: bool
			Whether to display colorbar.
		cax: plt.Axes | None
			Axis to draw colorbar on (ignored if show_colorbar is False).
		show_grid: bool
			Whether to show grid lines.
		tick_mode: str
			Tick alignment mode: "center" or "edge".
		n_ticks: tuple[int, int]
			Number of ticks on row and column axes.
	
		Returns
		-------
		plt.Figure
			Matplotlib figure containing the plot.
		
		"""
		
		# Validate the important args and get the signal that needs to be plotted
		if M.ndim != 2:
			raise excp.InputValueError(f"`M` must have 2 dimension not {M.ndim}")
		if r is None:
			r = M.shape[0]
		if c is None:
			c = M.shape[1]
			
		if r.ndim != 1 and c.ndim != 1:
			raise excp.InputValueError(f"`r` and `c` must have 2 dimension not r:{r.ndim}, c:{c.ndim}")
			
		if r.shape[0] != M.shape[0]:
			raise excp.InputValueError(f"`r` must have shape as `M row` not {r.shape}")
		if c.shape[0] != M.shape[1]:
			raise excp.InputValueError(f"`c` must have shape as `M column` not {c.shape}")
			
		# Scale the signal if needed
		if log_compression_factor is not None:
			M = np.log1p(float(log_compression_factor) * M)
			
		# Create a figure
		if ax is None:
			fig, ax = plt.subplots(figsize=(15, 4))
			created_fig = True
		else:
			fig = ax.get_figure()
			created_fig = False
			
		# Plot the signal with right configurations
		# Compute extent
		extent = Plotter._compute_centered_extent(r, c, origin)
		
		# Plot image
		im = ax.imshow(
			M,
			aspect="auto",
			cmap=cmap,
			origin=origin,
			extent=extent
		)
		
		# Set the ticks and labels
		if n_ticks is None:
			n_ticks = (10, 10)
		
		if tick_mode == "center":
			ax.yaxis.set_major_locator(MaxNLocator(nbins=n_ticks[0]))
			ax.xaxis.set_major_locator(MaxNLocator(nbins=n_ticks[1]))  # limits ticks
			
		elif tick_mode == "edge":
			dr = np.diff(r).mean() if len(r) > 1 else 1
			dc = np.diff(c).mean() if len(c) > 1 else 1
		
			# Edge tick positions (centered)
			xticks_all = np.append(c, c[-1] + dc) - dc / 2
			yticks_all = np.append(r, r[-1] + dr) - dr / 2
		
			# Determine number of ticks
			nr, nc = n_ticks
		
			# Choose evenly spaced tick indices
			xtick_idx = np.linspace(0, len(xticks_all) - 1, nc, dtype=int)
			ytick_idx = np.linspace(0, len(yticks_all) - 1, nr, dtype=int)
		
			ax.set_xticks(xticks_all[xtick_idx])
			ax.set_yticks(yticks_all[ytick_idx])
		
		# Set the labels
		if title is not None:
			ax.set_title(title)
		if rlabel is not None:
			ax.set_ylabel(rlabel)
		if clabel is not None:
			ax.set_xlabel(clabel)
			
		# Applying axes limits into a region
		if rlim is not None:
			ax.set_ylim(rlim)
		if clim is not None:
			ax.set_xlim(clim)
				
		# Applying axes limits into a region
		if rlim is not None:
			ax.set_ylim(rlim)
		if clim is not None:
			ax.set_xlim(clim)
			
		# Highlight a list of regions
		if highlight is not None:
			for r1, r2, c1, c2 in highlight:
				row_min, row_max = min(r1, r2), max(r1, r2)
				col_min, col_max = min(c1, c2), max(c1, c2)
				width = col_max - col_min
				height = row_max - row_min
				ax.add_patch(Rectangle((col_min, row_min), width, height, color='red', alpha=0.2, zorder=10))
				
		# Show colorbar
		if show_colorbar is not None:
			cbar = fig.colorbar(im, ax=ax, cax=cax)
			if Mlabel is not None:
				cbar.set_label(Mlabel)
				
		# Show grid
		if show_grid:
			ax.grid(True, color="gray", linestyle="--", linewidth=0.5) # TODO
			
		# Show/Return the figure as per needed
		if created_fig:
			fig.tight_layout()
			if Plotter._in_notebook():
				plt.close(fig)
				return fig
			else:
				plt.show()
				return fig
	
	@staticmethod
	def _compute_centered_extent(r: np.ndarray, c: np.ndarray, origin: str) -> list[float]:
		"""
		
		"""
		dc = np.diff(c).mean() if len(c) > 1 else 1
		dr = np.diff(r).mean() if len(r) > 1 else 1
		left   = c[0] - dc / 2
		right  = c[-1] + dc / 2
		bottom = r[0] - dr / 2
		top    = r[-1] + dr / 2
		return [left, right, top, bottom] if origin == "upper" else [left, right, bottom, top]
	
	@staticmethod
	def _in_notebook() -> bool:
		try:
			from IPython import get_ipython
			shell = get_ipython()
			return shell and shell.__class__.__name__ == "ZMQInteractiveShell"
		except ImportError:
			return False
	