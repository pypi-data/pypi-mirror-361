#!/usr/bin/env python3


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
	tick_mode="cen",
	n_ticks=(5, 5),
	value_range=None
)
