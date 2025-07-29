#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import validate_args_type
from modusa.io import ModusaIO
from IPython.display import display, HTML, Audio
import numpy as np

class AudioPlayer(ModusaIO):
	"""
	
	"""
	
	#--------Meta Information----------
	_name = "Audio Player"
	_description = ""
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-08"
	#----------------------------------
	
	@staticmethod
	def play(
		y: np.ndarray,
		sr: int,
		regions: list[tuple[float, float]] | None = None,
		title: str | None = None
	) -> None:
		"""
		Plays audio clips for given regions in Jupyter Notebooks.

		Parameters
		----------
		y : np.ndarray
			Audio time series.
		sr : int
			Sampling rate.
		regions : list of (float, float), optional
			Regions to extract and play (in seconds).
		title : str, optional
			Title to display above audio players.

		Returns
		-------
		None
		"""
		if not AudioPlayer._in_notebook():
			return
		
		if title:
			display(HTML(f"<h4>{title}</h4>"))
			
		if regions:
			for i, (start_sec, end_sec) in enumerate(regions):
				start_sample = int(start_sec * sr)
				end_sample = int(end_sec * sr)
				clip = y[start_sample:end_sample]
				
				display(HTML(f"<b>Clip {i+1}</b>: {start_sec:.2f}s → {end_sec:.2f}s"))
				display(Audio(data=clip, rate=sr))
		else:
			display(Audio(data=y, rate=sr))
			
	@staticmethod
	def _in_notebook() -> bool:
		try:
			from IPython import get_ipython
			shell = get_ipython()
			return shell and shell.__class__.__name__ == "ZMQInteractiveShell"
		except ImportError:
			return False