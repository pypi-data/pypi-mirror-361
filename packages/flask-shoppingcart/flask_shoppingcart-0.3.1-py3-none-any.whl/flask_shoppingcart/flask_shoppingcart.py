from functools import partial
from numbers import Number
from typing import Any, Optional, Union

from ._shoppingcart import ShoppingCartBase
from .exceptions import OutOfStokError, ProductNotFoundError, QuantityError
from .manage_cart_item_extra_data import ManageCartItemExtraData
from .models import CartItem


class FlaskShoppingCart(ShoppingCartBase):
	@property
	def cart(self) -> dict[str, CartItem]:
		"""
		Get the cart data.
		
		Returns:
			dict: The cart data.
		"""
		return self.get_cart()

	def _validate_stock(self, current_stock: Optional[Number], quantity_to_add: Number, current_quantity: Number) -> None:
		"""
		Validates if the stock is sufficient for the quantity to be added.
		
		Args:
			ignore_stock (bool): Flag to ignore stock validation.
			current_stock (Number): The current stock available.
			quantity_to_add (Number): The quantity of items to add.
			current_quantity (Number): The current quantity of items in the cart.
			
		Raises:
			OutOfStockError: If the total quantity exceeds the current stock.
		"""
		if (
			(current_stock is not None)
			and ((current_quantity + quantity_to_add) > current_stock)  # type: ignore
		):
			raise OutOfStokError()

	def get_cart(self) -> dict[str, CartItem]:
		"""
		Get the cart data.
		
		Returns:
			dict: The cart data.
		"""
		return self._get_cart()

	def add(self,
         product_id: str,
         quantity: Number = 1,  # type: ignore
         overwrite_quantity: bool = False,
         current_stock: Optional[Number] = None,
         extra: Optional[dict] = None,
         allow_negative: Optional[bool] = None,
         overwrite_extra: bool = False
         ) -> None:
		"""
		Add a product to the cart or update the quantity of an existing product.
		
		Args:
			product_id (str): The ID of the product to add.
			quantity (Number): The quantity of the product to add.
			overwrite_quantity (bool): If True, the quantity will be overwritten instead of added.
			current_stock (Number, optional): The current stock of the product. If set, the stock will be validated.
			extra (dict, optional): Extra data to store in the product.
			allow_negative (bool, optional): If True, the quantity can be negative.
			overwrite_extra (bool): If True, the extra data will be overwritten instead of added.

		Raises:
			OutOfStokError: If the product is out of stock. This error is raise if the ignore_stock is True and the quantity exceeds the current stock.
		"""
		cart: dict[str, CartItem] = self._get_cart()

		_allow_negative = allow_negative or self.allow_negative_quantity

		if not _allow_negative and quantity <= 0:  # type: ignore
			raise ValueError("Quantity must be greater than 0.")

		product: Optional[CartItem] = cart.get(product_id, None)

		_data: CartItem = {
			"quantity": quantity,
		}

		_validate_stock: partial = partial(
			self._validate_stock, current_stock, quantity)

		# Product data
		if product:
			_validate_stock(product["quantity"])

			if overwrite_quantity:
				product.update(_data)

			else:
				product["quantity"] += quantity  # type: ignore

		else:
			product = _data
			_validate_stock(0)

		# Extra data
		if extra:
			manage_extra_data = ManageCartItemExtraData(product)
			product = manage_extra_data.add(extra, overwrite=overwrite_extra)

		cart[product_id] = product

		self._set_cart(cart)

	def remove(self, product_id: str, silent: bool = True) -> None:
		"""
		Removes a product from the cart.
		
		Args:
			product_id (str): The ID of the product to remove.
			silent (bool): If True, no error will be raised if the product is not found in the cart.

		Raises:
			ProductNotFoundError: If the product with the given ID is not found in the cart and silent is False.
		"""
		cart = self._get_cart()

		if (
			not product_id in cart
			and not silent
		):
			raise ProductNotFoundError("Product not found in the cart.")

		cart.pop(product_id, None)
		self._set_cart(cart)

	def clear(self) -> None:
		"""
		Clears the cart.
		"""
		self._set_cart(dict())

	def subtract(self,
              product_id: str,
              quantity: Number = 1,  # type: ignore
              allow_negative: bool = False,
              autoremove_if_0: bool = True
              ) -> None:
		"""
		Substracts a quantity from a product in the cart.
		
		Args:
			product_id (str): The ID of the product to substract from.
			quantity (Number): The quantity to substract.
			allow_negative (bool): If True, the quantity can be negative.
			autoremove_if_0 (bool): If True, the product will be removed if the quantity reaches 0 or less. This flag is only valid if allow_negative is False.
		"""
		cart = self._get_cart()

		_allow_negative = allow_negative or self.allow_negative_quantity

		if not product_id in cart:
			raise ProductNotFoundError()

		else:
			product = cart[product_id]
			product["quantity"] -= quantity  # type: ignore

			if (
				_allow_negative
				and autoremove_if_0
			):
				raise ValueError(
					"The autoremove_if_0 flag cannot be set to True when allow_negative is True."
				)

			if (
				not _allow_negative
				and product["quantity"] <= 0
			):
				if autoremove_if_0:
					cart.pop(product_id)

				else:
					raise QuantityError(
						"Product quantity cannot be negative or 0. "
						"To allow negative quantities, set the allow_negative flag to True. "
						"0 values are not allowed; use the remove method instead or set autoremove_if_0 to True."
					)

			self._set_cart(cart)

	def get_product(self, product_id: str) -> CartItem:
		"""
		Retrieve a product from the shopping cart by its product ID.
		
		Args:
			product_id (str): The unique identifier of the product to retrieve.
		
		Returns:
			dict: A dictionary containing the product details.
		
		Raises:
			ProductNotFoundError: If the product with the given ID is not found in the cart.
		"""
		product = self._get_cart().get(product_id, None)

		if product is None:
			raise ProductNotFoundError()

		return product

	def get_product_or_none(self, product_id: str) -> Union[CartItem, None]:
		"""
		Get a product from the cart.
		
		Args:
			product_id (str): The ID of the product to get.
		
		Returns:
			dict: The product data.
		"""
		return self._get_cart().get(product_id, None)

	def add_extra_data(self, product_id: str, data: dict, overwrite: bool = False) -> None:
		"""
		Add extra data to the cart item.
		
		Args:
			product_id (str): The unique identifier of the product to which extra data should be added.
			data (dict): A dictionary containing extra data to add to the cart item.
			overwrite (bool, optional): If True, replaces any existing extra data with the provided data.
				If False, updates the existing extra data with the provided data; if a key already exists, it will be updated with the new value. Defaults to False.

		Raises:
			TypeError: If the provided data is not a dictionary.
			ProductNotFoundError: If the specified product_id is not found in the cart.
		"""
		cart = self._get_cart()

		if product_id not in cart:
			raise ProductNotFoundError()

		manage_extra = ManageCartItemExtraData(cart[product_id])
		cart[product_id] = manage_extra.add(data, overwrite=overwrite)

		self._set_cart(cart)

	def remove_extra_data(self, product_id: str, key: str, silent: bool = True) -> None:
		"""
		Remove extra data associated with a specific product in the cart.

		Args:
			product_id (str): The unique identifier of the product whose extra data should be removed.
			key (str): The key of the extra data to remove from the product.
			silent (bool, optional): If True, suppress errors if the key does not exist. Defaults to True.

		Raises:
			ProductNotFoundError: If the specified product_id is not found in the cart.
			ProductExtraDataNotFoundError: If the key does not exist in the product's extra data and silent is False.
		"""
		cart = self._get_cart()

		if product_id not in cart:
			raise ProductNotFoundError()

		manage_extra = ManageCartItemExtraData(cart[product_id])
		cart[product_id] = manage_extra.remove(key, silent=silent)

		self._set_cart(cart)

	def get_extra_data(self, product_id: str, key: Optional[str] = None) -> Union[Any, dict, None]:
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
			ProductNotFoundError: If the specified product_id does not exist in the cart.
			ProductExtraDataNotFoundError: If the specified key is not found in the product's extra data.
		"""
		cart = self._get_cart()

		if product_id not in cart:
			raise ProductNotFoundError()

		manage_extra = ManageCartItemExtraData(cart[product_id])
		return manage_extra.get(key)

	def clear_extra_data(self, product_id: str) -> None:
		"""
		Removes any extra data associated with a specific product in the shopping cart.

		Args:
			product_id (str): The unique identifier of the product whose extra data should be cleared.

		Raises:
			ProductNotFoundError: If the specified product_id does not exist in the cart.
		"""
		cart = self._get_cart()

		if product_id not in cart:
			raise ProductNotFoundError()

		manage_extra = ManageCartItemExtraData(cart[product_id])
		cart[product_id] = manage_extra.clear()

		self._set_cart(cart)
