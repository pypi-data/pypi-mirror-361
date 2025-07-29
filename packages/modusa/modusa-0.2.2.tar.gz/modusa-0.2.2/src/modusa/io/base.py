#!/usr/bin/env python3

from abc import ABC, abstractmethod

class ModusaIO(ABC):
	"""
	Base class for all I/O components: loaders, savers, recorders, etc.
	
	>>> modusa-dev create io

	.. code-block:: python
		
		# General template of a subclass of ModusaIO
		from modusa.io import ModusaIO

		class MyCustomIOClass(ModusaIO):
			#--------Meta Information----------
			_name = "My Custom I/O"
			_description = "My custom class for I/O."
			_author_name = "Ankit Anand"
			_author_email = "ankit0.anand0@gmail.com"
			_created_at = "2025-07-06"
			#----------------------------------
			
			@staticmethod
			def do_something():
				pass
		
	
	Note
	----
	- This class is intended to be subclassed by any IO related tools built for the modusa framework.
	- In order to create an IO tool, you can use modusa-dev CLI to generate an IO template.
	- It is recommended to treat subclasses of ModusaIO as namespaces and define @staticmethods with control parameters, rather than using instance-level __init__ methods.
	"""
	
	#--------Meta Information----------
	_name: str = "Modusa I/O"
	_description: str = "Base class for any I/O in the Modusa framework."
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-06"
	#----------------------------------