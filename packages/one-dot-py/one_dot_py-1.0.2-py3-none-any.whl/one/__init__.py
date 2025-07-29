exec(  # In order not to create any false typehints
	"""
import sys
from . import one
sys.modules[__name__] = one
"""[1:-1]
)
