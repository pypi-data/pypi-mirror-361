#!/usr/bin/env python3

from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.signal_ops import SignalOps
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self
import numpy as np
import matplotlib.pyplot as plt

class ModusaSignal(ABC):
	"""
	Base class for any signal in the modusa framework.
	
	Note
	----
	- Intended to be subclassed.
	"""
	
	#--------Meta Information----------
	_name = "Modusa Signal"
	_description = "Base class for any signal types in the Modusa framework."
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-06-23"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self):
		self._plugin_chain = []
	

	