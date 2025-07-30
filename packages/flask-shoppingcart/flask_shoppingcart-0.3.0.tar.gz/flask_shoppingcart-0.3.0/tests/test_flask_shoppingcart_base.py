from flask import Flask

from src.flask_shoppingcart._shoppingcart import ShoppingCartBase


class TestShoppingCartBaseTestCase():
	def test_after_request_sets_cookie(self, cart_base: ShoppingCartBase, app: Flask):
		with app.test_request_context():
			response = app.test_client().get('/')

			print(response.headers.get('Set-Cookie', {}))

			assert 'test_cart' in response.headers.get('Set-Cookie', {})

	def test_get_cookie_cart(self, cart_base: ShoppingCartBase, app: Flask):
		with app.test_request_context():
			cookie_cart = cart_base._get_cookie_cart()

			assert cookie_cart == str(dict())
