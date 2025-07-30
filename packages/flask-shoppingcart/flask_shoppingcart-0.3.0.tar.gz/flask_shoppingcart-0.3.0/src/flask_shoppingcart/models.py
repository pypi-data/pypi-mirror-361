from numbers import Number
from typing import TypedDict, NotRequired

class CartItem(TypedDict):
    quantity: Number
    extra: NotRequired[dict]
