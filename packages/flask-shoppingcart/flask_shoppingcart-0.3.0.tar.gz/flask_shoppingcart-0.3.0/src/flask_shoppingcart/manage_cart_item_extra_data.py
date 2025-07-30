from typing import Any, Optional, Union

from .exceptions import (ProductExtraDataNotFoundError)
from .models import CartItem


class ManageCartItemExtraData:
	def __init__(self, product: CartItem):
		self.product = product

	def add(self, data: dict, overwrite: bool = False) -> CartItem:
		"""
		Add extra data to the cart item.
		- If `overwrite` is False, it updates the existing extra data with the provided data; if a key already exists, it will be updated with the new value.

		Args:
			data (dict): A dictionary containing extra data to add to the cart item.
			overwrite (bool, optional): If True, replaces any existing extra data with the provided data.
				If False, updates the existing extra data with the provided data; if a key already exists, it will be updated with the new value. Defaults to False.

		Returns:
			CartItem: The updated cart item with the extra data.

		Raises:
			TypeError: If the provided data is not a dictionary.
		"""
		if not isinstance(data, dict):
			raise TypeError("Data must be a dictionary.")

		if overwrite or not self.product.get("extra"):
			self.product["extra"] = data

		else:
			self.product["extra"].update(data)  # type: ignore

		return self.product

	def remove(self, key: str, silent: bool = True) -> CartItem:
		"""
		Removes an extra data entry from the product by its key.

		Args:
			key (str): The key of the extra data to remove.
			silent (bool, optional): If False, raises an error when the key is not found. Defaults to True.

		Returns:
			CartItem: The updated product after removing the extra data.

		Raises:
			ProductExtraDataNotFoundError: If the key does not exist in the product's extra data and silent is False.
		"""
		if (
			not self.product.get("extra", dict()).get(key, None)
			and not silent
		):
			raise ProductExtraDataNotFoundError()

		self.product["extra"].pop(key, None)  # type: ignore

		return self.product

	def get(self, key: Optional[Any] = None) -> Union[None, Any, dict[Any, Any]]:
		"""
		Retrieve extra data associated with the product.
		- If `key` is **not** provided, and the returns is `None`, it means that the product has no extra data.
		- If `key` is provided, it returns the value associated with that key in the product's extra data, even if it is `None`.
		- If `key` is provided and it does not exists or the product has no extra data, it raises a `ProductExtraDataNotFoundError`.

		Args:
			key (Optional[Any], optional): The key to look up in the product's extra data. 
				If None, returns the entire extra data dictionary. Defaults to None.

		Returns:
			Union[None, Any, dict[Any, Any]]: The value associated with the given key in the extra data,
				or the entire extra data dictionary if key is not provided.

		Raises:
			ProductExtraDataNotFoundError: If the specified key is not found in the product's extra data.
		"""
		if key is None:
			return self.product.get("extra", None)  # type: ignore

		if (
			not self.product.get("extra")
			or not self.product["extra"].get(key, None)  # type: ignore
		):
			raise ProductExtraDataNotFoundError()

		return self.product["extra"][key]  # type: ignore

	def clear(self) -> CartItem:
		"""
		Removes the 'extra' key from the product dictionary if it exists.

		Returns:
			CartItem: The updated product dictionary after removing the 'extra' key.
		"""
		self.product.pop("extra", None)
		return self.product
