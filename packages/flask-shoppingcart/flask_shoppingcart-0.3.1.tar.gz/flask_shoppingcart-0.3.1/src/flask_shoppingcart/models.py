from numbers import Number
from typing import TypedDict

#* We could use NotRequired from typing, but it is only available in Python 3.11+
#* -> https://peps.python.org/pep-0655/ <-
#* So, as we're tring to add support for this library to Python 3.9+, we will use this approach

class _CartITem(TypedDict):
    extra: dict

class CartItem(_CartITem, total=False):
    quantity: Number
