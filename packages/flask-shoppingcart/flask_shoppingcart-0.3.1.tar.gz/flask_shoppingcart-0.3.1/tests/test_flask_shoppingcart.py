# type: ignore

from decimal import Decimal

import pytest
from flask import Flask

from src.flask_shoppingcart import (FlaskShoppingCart,
                                                       OutOfStokError,
                                                       ProductNotFoundError,
                                                       QuantityError,
													   ProductExtraDataNotFoundError)


class TestShoppingCart:
	def test_get_cart_empty_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart_data = cart.get_cart()
			cart_data_as_property = cart.cart

			assert cart_data == {}
			assert cart_data_as_property == {}

	@pytest.mark.parametrize('quantity', [1, 1.0, Decimal('1.0')])
	def test_add_product_success(self, quantity, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1', quantity)
			cart_data = cart.get_cart()

			assert 'product_1' in cart_data
			assert cart_data['product_1']['quantity'] == quantity

	@pytest.mark.parametrize('quantity', [1, 1.0, Decimal('1.0')])
	def test_add_product_overwrite_quantity_success(self, quantity, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1', 2)
			cart.add('product_1', quantity, overwrite_quantity=True)

			cart_data = cart.get_cart()
			assert cart_data['product_1']['quantity'] == quantity

	def test_add_product_insufficient_stock_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			with pytest.raises(OutOfStokError):
				cart.add('product_1', 5, current_stock=3)

	def test_add_product_negative_quantity_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			with pytest.raises(ValueError):
				cart.add('product_1', -2)

	def test_add_product_negative_quantity_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', -2, allow_negative=True)
			cart_data = cart.get_cart()

			assert 'product_1' in cart_data
			assert cart_data['product_1']['quantity'] == -2

	def test_add_product_with_extra_data_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', 2, extra={'color': 'red'})
			cart.add('product_1', 2)
			cart.add('product_1', 2, extra={'size': 'large'})

			cart_data = cart.get_cart()
			assert 'extra' in cart_data['product_1']
			assert 'color' in cart_data['product_1']["extra"]
			assert 'size' in cart_data['product_1']["extra"]
			assert cart_data["product_1"]["quantity"] == 6

	def test_add_product_with_extra_data_is_not_dict_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			with pytest.raises(TypeError):
				cart.add('product_1', 2, extra='color:red')

	def test_remove_product_exists_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1')
			cart.remove('product_1')

			cart_data = cart.get_cart()
			assert 'product_1' not in cart_data

	def test_remove_product_not_exists_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.remove('product_1')

			cart_data = cart.get_cart()
			assert 'product_1' not in cart_data

	def test_remove_product_not_exists_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			with pytest.raises(ProductNotFoundError):
				cart.remove('product_1', silent=False)

	def test_clear_cart_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1', 2)
			cart.clear()

			cart_data = cart.get_cart()
			assert cart_data == {}

	def test_subtract_product_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1', 2)
			assert cart.get_cart()["product_1"]["quantity"] == 2

			cart.subtract('product_1')
			assert cart.get_cart()['product_1']['quantity'] == 1

	def test_subtract_product_allow_negative_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', 5)
			cart.subtract('product_1', 10, allow_negative=True, autoremove_if_0=False)

			assert cart.get_cart()['product_1']['quantity'] == -5

	def test_subtract_product_out_of_stock_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1', 2)
			with pytest.raises(QuantityError):
				cart.subtract('product_1', 3, autoremove_if_0=False)

	def test_subtract_product_autoremove_if_0_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1', 2)
			cart.subtract('product_1', 2, autoremove_if_0=True)

			assert 'product_1' not in cart.get_cart()

	def test_subtract_product_not_found_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			with pytest.raises(ProductNotFoundError):
				cart.subtract('product_1')

	def test_subtract_product_allow_negative_and_autoremove_if_0_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.add('product_1', 2)
			with pytest.raises(ValueError):
				cart.subtract('product_1', 1, allow_negative=True, autoremove_if_0=True)

	def test_get_product_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', 2)
			assert cart.get_product('product_1') == {"quantity": 2}

	def test_get_product_not_found_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			with pytest.raises(ProductNotFoundError):
				cart.get_product('product_1')

	def test_get_product_or_none_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			assert cart.get_product_or_none('product_1') is None

	# * --
	def test_add_extra_data_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1')
			cart.add_extra_data('product_1', {'color': 'blue'})
			product = cart.get_product('product_1')
			assert 'extra' in product
			assert product['extra'] == {'color': 'blue'}

	def test_add_extra_data_overwrite_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', extra={'color': 'blue'})
			product = cart.get_product('product_1')
			assert 'extra' in product
			assert product['extra'] == {'color': 'blue'}

			cart.add_extra_data('product_1', {'size': 'L'}, overwrite=True)
			product = cart.get_product('product_1')
			assert product['extra'] == {'size': 'L'}

	def test_add_extra_data_type_error(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1')
			with pytest.raises(TypeError):
				cart.add_extra_data('product_1', 'not_a_dict')

	def test_add_extra_data_product_not_found(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			with pytest.raises(ProductNotFoundError):
				cart.add_extra_data('product_2', {'color': 'blue'})

	def test_remove_extra_data_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', extra={'color': 'blue', 'size': 'M'})
			product = cart.get_product('product_1')
			assert 'extra' in product
			assert 'color' in product['extra']

			cart.remove_extra_data('product_1', 'color')
			product = cart.get_product('product_1')
			assert 'extra' in product
			assert 'color' not in product['extra']

	def test_remove_extra_data_key_not_found_silent(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', extra={'color': 'blue'})
			product = cart.get_product('product_1')
			assert 'extra' in product
			assert 'color' in product['extra']

			# Should not raise
			cart.remove_extra_data('product_1', 'size', silent=True)
			product = cart.get_product('product_1')
			assert 'extra' in product
			assert 'size' not in product['extra']

	def test_remove_extra_data_key_not_found_fail(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', extra={'color': 'blue'})
			product = cart.get_product('product_1')
			assert 'extra' in product
			assert 'color' in product['extra']

			with pytest.raises(ProductExtraDataNotFoundError):
				cart.remove_extra_data('product_1', 'size', silent=False)

	def test_remove_extra_data_product_not_found(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			with pytest.raises(ProductNotFoundError):
				cart.remove_extra_data('product_2', 'color')

	def test_get_extra_data_all_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', extra={'color': 'blue', 'size': 'M'})
			extra = cart.get_extra_data('product_1')
			assert extra == {'color': 'blue', 'size': 'M'}

	def test_get_extra_data_key_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', extra={'color': 'blue'})
			value = cart.get_extra_data('product_1', 'color')
			assert value == 'blue'

	def test_get_extra_data_key_not_found(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', extra={'color': 'blue'})
			with pytest.raises(ProductExtraDataNotFoundError):
				cart.get_extra_data('product_1', 'size')

	def test_get_extra_data_product_not_found(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			with pytest.raises(ProductNotFoundError):
				cart.get_extra_data('product_2')

	def test_clear_extra_data_success(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			cart.add('product_1', 2, extra={'color': 'blue', 'size': 'M'})
			cart.clear_extra_data('product_1')
			product = cart.get_product('product_1')
			assert 'extra' not in product

	def test_clear_extra_data_product_not_found(self, cart: FlaskShoppingCart, app: Flask):
		with app.test_request_context():
			cart.clear()
			with pytest.raises(ProductNotFoundError):
				cart.clear_extra_data('product_2')