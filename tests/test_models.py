# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        'Read a product from the database'
        product: Product = ProductFactory()
        app.logger.debug(f'product: {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        db_product = Product.find(product.id)
        self.assertEqual(product.id, db_product.id)
        self.assertEqual(product.name, db_product.name)
        self.assertEqual(product.description, db_product.description)
        self.assertEqual(product.available, db_product.available)
        self.assertEqual(product.category, db_product.category)

    def test_update_a_product(self):
        'Update a product in the database'
        product = ProductFactory()
        app.logger.debug(f'product: {product}')
        product.id = None
        product.create()
        app.logger.debug(f'product: {product}')
        product.description = description = "new description!"
        prev_id = product.id
        product.update()
        self.assertEqual(prev_id, product.id)
        self.assertEqual(description, product.description)
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, product.id)
        self.assertEqual(products[0].description, product.description)

    def test_update_a_nonexistent_product(self):
        'Error when updating a nonexistent product in the database'
        product = ProductFactory()
        app.logger.debug(f'product: {product}')
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        'Delete a product in the database'
        product = ProductFactory()
        app.logger.debug(f'product: {product}')
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        'List all products'
        self.assertEqual(len(Product.all()), 0)
        for product in ProductFactory.create_batch(5):
            product.create()
        self.assertEqual(len(Product.all()), 5)

    def test_find_product_by_name(self):
        'Find a product by name'
        products = ProductFactory.create_batch(50)  # 5 is too small to get multiple of same type reliably
        for product in products:
            product.create()

        name0 = products[0].name
        count = sum(1 for product in products if product.name == name0)
        db_products = Product.find_by_name(name0)
        self.assertEqual(db_products.count(), count)
        for product in db_products:
            self.assertEqual(product.name, name0)

    def test_find_product_by_availability(self):
        'Find a product by availability'
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        available0 = products[0].available
        count = sum(1 for product in products if product.available == available0)
        db_products = Product.find_by_availability(available0)
        self.assertEqual(db_products.count(), count)
        for product in db_products:
            self.assertEqual(product.available, available0)

    def test_find_product_by_category(self):
        'Find a product by category'
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        category0 = products[0].category
        count = sum(1 for product in products if product.category == category0)
        db_products = Product.find_by_category(category0)
        self.assertEqual(db_products.count(), count)
        for product in db_products:
            self.assertEqual(product.category, category0)

    def test_find_product_by_price(self):
        'Find a product by price'
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        price0 = products[0].price
        count = sum(1 for product in products if product.price == price0)
        db_products = Product.find_by_price(price0)
        self.assertEqual(db_products.count(), count)
        for product in db_products:
            self.assertEqual(product.price, price0)

    def test_find_product_by_price_str(self):
        'Find a product by price'
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        price0 = products[0].price
        count = sum(1 for product in products if product.price == price0)
        db_products = Product.find_by_price(str(price0))
        self.assertEqual(db_products.count(), count)
        for product in db_products:
            self.assertEqual(product.price, price0)

    def test_deserialize_bad_bool(self):
        'Error when deserializing a string to "available: bool" field'
        product = ProductFactory()
        json = product.serialize()
        json['available'] = 'Cassandra'  # not a valid bool string!
        self.assertRaises(DataValidationError, lambda: Product().deserialize(json))

    def test_deserialize_bad_price(self):
        'Error when deserializing a string to "price: Decimal" field'
        product = ProductFactory()
        json = product.serialize()
        json['price'] = 'Cassandra'  # not a valid bool string!
        self.assertRaises(Exception, lambda: Product().deserialize(json))

    def test_deserialize_missing_attribute(self):
        'Error when deserializing due to missing attribute "description"'
        product = ProductFactory()
        json = product.serialize()
        self.assertIn('description', json)
        json.pop('description')
        self.assertIsNotNone('description', json)
        self.assertRaises(DataValidationError, lambda: Product().deserialize(json))

    def test_deserialize_garbage_none(self):
        'Error when deserializing garbage None"'
        self.assertRaises(DataValidationError, lambda: Product().deserialize(None))

    def test_deserialize_garbage_list(self):
        'Error when deserializing garbage list"'
        self.assertRaises(DataValidationError, lambda: Product().deserialize([]))
