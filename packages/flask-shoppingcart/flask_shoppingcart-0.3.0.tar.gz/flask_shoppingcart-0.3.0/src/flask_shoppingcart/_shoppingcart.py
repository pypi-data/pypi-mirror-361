import json

from flask import Flask, Response, session, request

from .models import CartItem

from typing import Optional

from .config import (FLASK_SHOPPING_CART_ALLOW_NEGATIVE_QUANTITY,
                     FLASK_SHOPPING_CART_COOKIE_NAME)


class ShoppingCartBase:
	def __init__(self, app: Optional[Flask] = None) -> None:
		if app is not None:
			self.init_app(app)

	def init_app(self, app: Flask) -> None:
		app.after_request(self._after_request)
		self.cookie_name: str = str(app.config.get("FLASK_SHOPPING_CART_COOKIE_NAME", FLASK_SHOPPING_CART_COOKIE_NAME))  # noqa
		self.allow_negative_quantity: bool = bool(app.config.get("FLASK_SHOPPING_CART_ALLOW_NEGATIVE_QUANTITY", FLASK_SHOPPING_CART_ALLOW_NEGATIVE_QUANTITY))  # noqa

	def _after_request(self, response: Response) -> Response:
		self._set_cookie(response)
		return response

	def _set_cookie(self, response: Response):
		"""
		Set the cookie with the shopping cart data.
		This method will serialize the shopping cart data to JSON and set it as a cookie in the response headers.
		
		Args:
			response (Response): The response object to set the cookie in.
		"""
		if not session.get(self.cookie_name):
			self._set_cart({})

		response.set_cookie(self.cookie_name, json.dumps(self._get_cart()))

	def _get_cart(self) -> dict[str, CartItem]:
		"""
		Get the cart data.
		
		Returns:
			dict: The cart data.
		"""
		return session.get(self.cookie_name, dict())

	def _set_cart(self, cart: dict[str, CartItem]) -> None:
		"""
		Set the cart data.
		
		Args:
			cart (dict): The cart data to set.
		"""
		session[self.cookie_name] = cart

	def _get_cookie_cart(self) -> str:
		return request.cookies.get(self.cookie_name, str(dict()))