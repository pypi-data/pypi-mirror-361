from unittest import TestCase

from ddbmodel.key import Key
from ddbmodel.record import Record
from ddbmodel.field import StringField



class TestKey(TestCase):
    def test_ddb_const_value_happy(self):
        class TestContactRecord(Record):
            class Meta:
                table_name = 'test'
                pk = Key().constant('testtest')
                sk = Key().constant('name').field('first_name').field('last_name')

            first_name = StringField()
            last_name = StringField()

        self.assertEqual(TestContactRecord.primary_key().ddb_const_value(), 'testtest')
        test_record = TestContactRecord(first_name='John', last_name='Doe')
        self.assertEqual(test_record.sort_key().ddb_const_value(), 'name')

    def test_ddb_const_value_only_fields(self):
        class TestContactRecord(Record):
            class Meta:
                table_name = 'test'
                pk = Key().field('first_name').field('last_name')
                sk = Key().constant('testtest')

            first_name = StringField()
            last_name = StringField()

        self.assertEqual(TestContactRecord.primary_key().ddb_const_value(), "")

    def test_ddb_value_happy(self):
        class TestContactRecord(Record):
            class Meta:
                table_name = 'test'
                pk = Key().constant('testtest')
                sk = Key().field('first_name').field('last_name')

            first_name = StringField()
            last_name = StringField()

        test_record = TestContactRecord(first_name='John', last_name='Doe')
        self.assertEqual(test_record.primary_key().ddb_value(test_record), 'testtest')
        self.assertEqual(test_record.sort_key().ddb_value(test_record), 'John#Doe')

    def test_ddb_value_happy_mixed(self):
        class TestContactRecord(Record):
            class Meta:
                table_name = 'test'
                pk = Key().constant('testtest')
                sk = Key().field('first_name').constant('1234').field('last_name')

            first_name = StringField()
            last_name = StringField()

        test_record = TestContactRecord(first_name='John', last_name='Doe')
        self.assertEqual(test_record.primary_key().ddb_value(test_record), 'testtest')
        self.assertEqual(test_record.sort_key().ddb_value(test_record), 'John#1234#Doe')




