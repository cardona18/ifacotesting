from odoo.tests import common

class TestStringMethods(common.TransactionCase):

    def setup(self):
        print ("executing setup . . .")

        super(TestStringMethods, self).setUp()

    def test_upper(self):
        print ("executing test upper. . . ")

        self.assertEqual('foo'.upper(), 'FOO')