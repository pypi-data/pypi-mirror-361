#!/usr/bin/env python3

from modusa import excp
from typing import Any
import numpy as np

class SignalOps:
	"""
	Performs arithmetic and NumPy-style ops on ModusaSignal instances.

	Note
	----
	- Shape-changing operations like reshape, transpose, etc. are not yet supported. Use only element-wise or aggregation ops for now. 
	- Index alignment must be handled carefully in future extensions.
	"""
	
	def _axes_match(a1: tuple[np.ndarray, ...], a2: tuple[np.ndarray, ...]) -> bool:
		"""
		To check if two axes are same.
		"""
		if len(a1) != len(a2):
			return False
		return all(np.allclose(x, y, atol=1e-8) for x, y in zip(a1, a2))
	
	
	#----------------------------------
	# To handle basic math operations like
	# +, -, *, **, / ...
	#----------------------------------
	
	@staticmethod
	def add(data: np.ndarray, other: np.ndarray) -> np.ndarray:
		return np.add(data, other)
	
	@staticmethod
	def subtract(signal: "ModusaSignal", other: Any) -> "ModusaSignal":
		return SignalOps._apply_binary_op(signal, other, np.subtract, "subtract")
		
	@staticmethod
	def multiply(signal: "ModusaSignal", other: Any):
		return SignalOps._apply_binary_op(signal, other, np.multiply, "multiply")

	@staticmethod
	def divide(signal: "ModusaSignal", other: Any):
		return SignalOps._apply_binary_op(signal, other, np.divide, "divide")

	@staticmethod
	def power(signal: "ModusaSignal", other: Any):
		return SignalOps._apply_binary_op(signal, other, np.power, "power")	
	
	@staticmethod
	def floor_divide(signal: "ModusaSignal", other: Any):
		return SignalOps._apply_binary_op(signal, other, np.floor_divide, "floor_divide")
	
	
		
	#----------------------------------
	# To handle numpy aggregator ops
	# mean, sum, ...
	# TODO: Add dimension select option
	#----------------------------------
	@staticmethod
	def mean(signal: "ModusaSignal") -> float:
		"""Return the mean of the signal data."""
		return float(np.mean(signal._data))
	
	@staticmethod
	def std(signal: "ModusaSignal") -> float:
		"""Return the standard deviation of the signal data."""
		return float(np.std(signal._data))
	
	@staticmethod
	def min(signal: "ModusaSignal") -> float:
		"""Return the minimum value in the signal data."""
		return float(np.min(signal._data))
	
	@staticmethod
	def max(signal: "ModusaSignal") -> float:
		"""Return the maximum value in the signal data."""
		return float(np.max(signal._data))
	
	@staticmethod
	def sum(signal: "ModusaSignal") -> float:
		"""Return the sum of the signal data."""
		return float(np.sum(signal._data))
	
	#----------------------------------
	# To handle numpy ops where the
	# shapes are unaltered
	# sin, cos, exp, log, ...
	#----------------------------------
	
	@staticmethod
	def _apply_unary_op(signal: "ModusaSignal", op_func, op_name: str):
		from modusa.signals.base import ModusaSignal  # avoid circular import
		
		if not isinstance(signal, ModusaSignal):
			raise excp.InputTypeError(f"`signal` must be a ModusaSignal, got {type(signal)}")
			
		try:
			result = op_func(signal._data)
		except Exception as e:
			raise excp.SignalOpError(f"{op_name} failed: {e}")
			
		if not isinstance(result, np.ndarray):
			raise excp.SignalOpError(f"{op_name} did not return a NumPy array, got {type(result)}")
			
		if result.shape != signal._data.shape:
			raise excp.SignalOpError(f"{op_name} changed shape: {signal._data.shape} → {result.shape}")
			
		return signal.replace(data=result)
	
	
	@staticmethod
	def sin(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.sin, "sin")
	
	@staticmethod
	def cos(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.cos, "cos")
	
	@staticmethod
	def exp(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.exp, "exp")
	
	@staticmethod
	def tanh(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.tanh, "tanh")
	
	@staticmethod
	def log(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.log, "log")
	
	@staticmethod
	def log10(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.log10, "log10")
	
	@staticmethod
	def log2(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.log2, "log2")
	
	@staticmethod
	def log1p(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.log1p, "log1p")
	
	
	@staticmethod
	def sqrt(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.sqrt, "sqrt")
	
	@staticmethod
	def abs(signal: "ModusaSignal"):
		return SignalOps._apply_unary_op(signal, np.abs, "abs")
	
	#------------------------------------
	# TODO: Add shape-changing ops like 
	# reshape, transpose, squeeze later
	#------------------------------------