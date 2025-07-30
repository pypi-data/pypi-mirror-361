import os
import logging
from logging import debug, info
from unittest import TestCase

import boto3

from ddbmodel.record import Record
from ddbmodel.field import StringField, IntField, TimestampNowField
from ddbmodel.key import Key

ddb_resource = boto3.resource('dynamodb')

# logging.basicConfig(level=logging.DEBUG)

TEST_TABLE_NAME = os.environ.get('TEST_TABLE_NAME', "ddbmodel-test")

TEST_PRIMARY_KEY = 'CONTACTNAME'
TEST_FIRST_NAME = 'John'
TEST_LAST_NAME = 'Doe'
TEST_LEVEL = 0
TEST_AGE = 30
TEST_SORT_KEY = TEST_FIRST_NAME + '#' + TEST_LAST_NAME
TEST_PHONE_TYPE1 = 'HOME'
TEST_PHONE_NUMBER1 = '9165551212'
TEST_PHONE_TYPE2 = 'CELL'
TEST_PHONE_NUMBER2 = '5305551212'

def clear_test_database():
    table = ddb_resource.Table(TEST_TABLE_NAME)
    response = table.scan()

    while True:
        for item in response.get('Items', []):
            info(f'Deleting pk="{item['pk']}", sk="{item['sk']}"')
            delete_response = table.delete_item(Key={
                'pk': item['pk'],
                'sk': item['sk']
            })

            info(f'Delete response: {delete_response}')

        if 'LastEvaluatedKey' not in response:
            break

        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])

#
# Static test record
#


class ContactRecord(Record):
    class Meta:
        table_name = TEST_TABLE_NAME
        pk = Key().constant(TEST_PRIMARY_KEY)
        sk = Key().field('first_name').field('last_name')

    first_name = StringField(should_update=False)
    last_name = StringField(should_update=False)
    level = IntField(default_value=TEST_LEVEL)
    first_updated = TimestampNowField(should_update=False)

test_contact_record = ContactRecord(first_name=TEST_FIRST_NAME, last_name=TEST_LAST_NAME)

class ContactPhone(Record):
    class Meta:
        table_name = TEST_TABLE_NAME
        pk = Key().field('first_name').field('last_name')
        sk = Key().constant('ADDRESS').field('phone_type')

    first_name = StringField(should_update=False)
    last_name = StringField(should_update=False)
    phone_type = StringField(should_update=False)
    phone_number = StringField()
    last_updated = TimestampNowField(should_update=True)


class TestRecord(TestCase):
    #
    # __init_subclass__ tests
    #
    # A record subclass will raise an error if Meta class is not defined or if
    # the subclass does not have a table, pk, or sk fields define with the appropriate values
    #

    def test_key_no_meta(self):
        with self.assertRaises(Record.InvalidRecordClass) as e:
            class TestEmptyKeyRecord(Record):
                first_name = StringField()
                last_name = StringField()
        print('test_key_no_meta: pass:', e.exception)

    def test_key_no_table_name(self):
        with self.assertRaises(Record.InvalidRecordClass) as e:
            class TestEmptyKeyRecord(Record):
                class Meta:
                    pk = Key().field('first_name').field('last_name')
                    sk = Key().constant("NAME")

                first_name = StringField()
                last_name = StringField()
        print('test_key_no_table_name: pass:', e.exception)


    def test_key_empty_record(self):
        try:
            class TestEmptyKeyRecord(Record):
                class Meta:
                    table_name = TEST_TABLE_NAME
                    pk = Key().constant("abc")
                    sk = Key().constant("def")
        except Record.InvalidRecordClass:
            self.fail('test_key_empty_record: pass: Empty key record should not raise an exception')


    def test_key_empty_pk_record(self):
        with self.assertRaises(Record.InvalidRecordClass) as e:
            class TestEmptyKeyRecord(Record):
                class Meta:
                    table_name = TEST_TABLE_NAME
                    sk = Key().field('first_name').field('last_name')
        print('test_key_empty_pk_record: pass:', e.exception)


    def test_key_empty_sk_record(self):
        with self.assertRaises(Record.InvalidRecordClass) as e:
            class TestEmptyKeyRecord(Record):
                class Meta:
                    table_name = TEST_TABLE_NAME
                    pk = Key().field('first_name').field('last_name')
        print('test_key_empty_sk_record: pass:', e.exception)


    def test_key_nonkey_pk_record(self):
        with self.assertRaises(Record.InvalidRecordClass) as e:
            class TestEmptyKeyRecord(Record):
                class Meta:
                    table_name = TEST_TABLE_NAME
                    pk = 'Key'
                    sk = Key().field('first_name').field('last_name')
        print('test_key_nonkey_pk_record: pass:', e.exception)


    def test_key_nonkey_sk_record(self):
        with self.assertRaises(Record.InvalidRecordClass) as e:
            class TestEmptyKeyRecord(Record):
                class Meta:
                    table_name = TEST_TABLE_NAME
                    pk = Key().field('first_name').field('last_name')
                    sk = 'Key'
        print('test_key_nonkey_sk_record: pass:', e.exception)

    #
    # Variable accessors
    #

    def test_getattr_happy_path(self):
        self.assertEqual(test_contact_record.first_name, TEST_FIRST_NAME)

        test_contact_record2 = ContactRecord(first_name=TEST_FIRST_NAME, age=TEST_AGE)
        self.assertEqual(test_contact_record2.age, TEST_AGE)

        test_contact_record2.last_name = TEST_LAST_NAME
        self.assertEqual(test_contact_record2.last_name, TEST_LAST_NAME)

    def test_ddb_primary_key_happy_path(self):
        self.assertEqual(test_contact_record.ddb_primary_key(), TEST_PRIMARY_KEY)

    def test_ddb_sort_key_happy_path(self):
        self.assertEqual(test_contact_record.ddb_sort_key(), TEST_SORT_KEY)

    #
    # Convenience Functions
    #

    def test_fields_happy_path(self):
        self.assertEqual(test_contact_record.fields(), {
            'first_name': TEST_FIRST_NAME,
            'last_name': TEST_LAST_NAME,
            'first_updated': test_contact_record.first_updated
        })

    def test_fields_with_too_few_in_constructor(self):
        test_contact_record2 = ContactRecord(first_name=TEST_FIRST_NAME)
        self.assertEqual(test_contact_record2.fields(), {'first_name': TEST_FIRST_NAME})

    def test_fields_with_too_many_in_constructor(self):
        test_contact_record_with_extra = ContactRecord(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            age=TEST_AGE
        )

        self.assertEqual(test_contact_record_with_extra.fields(), {
            'first_name': TEST_FIRST_NAME,
            'last_name': TEST_LAST_NAME
        })

    def test_fields_edges(self):
        test_contact_record2 = ContactRecord(first_name=TEST_FIRST_NAME, age=TEST_AGE)
        self.assertEqual(test_contact_record2.fields(), {'first_name': TEST_FIRST_NAME})

        test_contact_record2.last_name = TEST_LAST_NAME
        self.assertEqual(test_contact_record2.fields(), {
            'first_name': TEST_FIRST_NAME,
            'last_name': TEST_LAST_NAME
        })

        test_contact_record2.nick_name = "Jon"
        self.assertEqual(test_contact_record2.fields(), {
            'first_name': TEST_FIRST_NAME,
            'last_name': TEST_LAST_NAME
        })

    def test_record_fields_happy_path(self):
        self.assertEqual(test_contact_record.record_fields(), {
            'first_name': test_contact_record.__class__.first_name,
            'last_name': test_contact_record.__class__.last_name,
            'level': test_contact_record.__class__.level,
            'first_updated': test_contact_record.__class__.first_updated
        })

    def test_table_name_happy_path(self):
        self.assertEqual(test_contact_record.table_name(), TEST_TABLE_NAME)
        self.assertEqual(test_contact_record.table_name("override_contacts"), "override_contacts")

    def test_ddb_fields_happy_path(self):
        # Note: this is testing when level is not present in constructor or assigned
        self.assertEqual(test_contact_record.ddb_fields(), {
            'first_name': {'S': TEST_FIRST_NAME},
            'last_name': {'S': TEST_LAST_NAME},
            'level': {'N': str(TEST_LEVEL)},
            'first_updated': {'N': str(test_contact_record.first_updated) }
        })

    def test_ddb_fields_with_too_few_in_constructor(self):
        test_contact_record2 = ContactRecord(first_name=TEST_FIRST_NAME)

        with self.assertRaises(ValueError) as e:
            test_contact_record2.ddb_fields()
        print(e)

    def test_ddb_fields_with_too_many_in_constructor(self):
        test_contact_record_with_extra = ContactRecord(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            age=TEST_AGE
        )

        self.assertEqual(test_contact_record_with_extra.ddb_fields(), {
            'first_name': {'S': TEST_FIRST_NAME},
            'last_name': {'S': TEST_LAST_NAME},
            'level': {'N': str(TEST_LEVEL)},
            'first_updated': {'N': str(test_contact_record_with_extra.first_updated)}
        })

    #
    # DDB Command Generation
    #

    def test_get_item_command_happy_path(self):
        self.assertEqual(test_contact_record.ddb_get_item_command(), {
            'TableName': TEST_TABLE_NAME,
            'Key': {
                'pk': {'S': TEST_PRIMARY_KEY},
                'sk': {'S': TEST_SORT_KEY}
            }
        })

    def test_put_item_command_happy_path(self):
        self.assertEqual(test_contact_record.ddb_put_item_command(), {
            'TableName': TEST_TABLE_NAME,
            'Item': {
                'pk': {'S': TEST_PRIMARY_KEY},
                'sk': {'S': TEST_SORT_KEY},
                'first_name': {'S': TEST_FIRST_NAME},
                'last_name': {'S': TEST_LAST_NAME},
                'level': {'N': str(TEST_LEVEL)},
                'first_updated': {'N': str(test_contact_record.first_updated)}
            },
            'ConditionExpression': 'attribute_not_exists(pk) AND attribute_not_exists(sk)'
        })

    def test_update_item_command_happy_path(self):
        self.assertEqual(test_contact_record.ddb_update_item_command(), {
            'TableName': TEST_TABLE_NAME,
            'Key': {
                'pk': {'S': TEST_PRIMARY_KEY},
                'sk': {'S': TEST_SORT_KEY}
            },
            'AttributeUpdates': {
                'level': {'Value': {'N': str(TEST_LEVEL)}},
            },
            'ReturnValues': 'UPDATED_NEW',
        })

    def test_delete_item_command_happy_path(self):
        self.assertEqual(test_contact_record.ddb_delete_item_command(), {
            'TableName': TEST_TABLE_NAME,
            'Key': {
                'pk': {'S': TEST_PRIMARY_KEY},
                'sk': {'S': TEST_SORT_KEY}
            },
            'ReturnValues': 'ALL_OLD'
        })

    def test_get_all_items_command_happy_path(self):
        self.assertEqual(test_contact_record.ddb_get_item_all_command(), {
            'TableName': TEST_TABLE_NAME,
            'KeyConditionExpression': 'pk = :pk',
            'ExpressionAttributeValues': {
                ':pk': {'S': TEST_PRIMARY_KEY}
            }
        })

    def test_get_all_sk_command_happy_path(self):
        self.assertEqual(test_contact_record.ddb_get_item_all_sk_command(), {
            'TableName': TEST_TABLE_NAME,
            'KeyConditionExpression': 'pk = :pk AND begins_with(sk, :sk)',
            'ExpressionAttributeValues': {
                ':pk': {'S': TEST_PRIMARY_KEY},
                ':sk': {'S': ''}
            }
        })

    #
    # DDB Interactive Commands
    #

    def test_put_and_get_item_happy_path(self):
        clear_test_database()
        test_contact_record.put_item()
        test_contact_record2 = ContactRecord(first_name=TEST_FIRST_NAME, last_name=TEST_LAST_NAME).get_item()

        for field in test_contact_record.fields():
            self.assertEqual(test_contact_record.fields()[field], test_contact_record2.fields()[field])

    def test_put_item_twice(self):
        clear_test_database()
        test_contact_record.put_item()
        with self.assertRaises(ValueError) as e:
            test_contact_record.put_item()
        print(e)

    def test_get_item_not_found(self):
        clear_test_database()
        self.assertEqual(test_contact_record.get_item(), None)

    def test_get_item_invalid_table(self):
        self.assertEqual(test_contact_record.get_item(table_override="invalid_table"), None)

    def test_update_item_happy_path(self):
        clear_test_database()
        test_contact_record.put_item()
        test_contact_record.level = TEST_LEVEL + 1
        test_contact_record.update_item()

        test_contact_record2 = ContactRecord(first_name=TEST_FIRST_NAME, last_name=TEST_LAST_NAME).get_item()
        self.assertEqual(test_contact_record2.level, TEST_LEVEL + 1)

    def test_delete_item_happy_path(self):
        clear_test_database()
        test_contact_record.put_item()
        test_contact_record.delete_item()

        self.assertEqual(test_contact_record.get_item(), None)

    def test_delete_item_not_found(self):
        clear_test_database()
        self.assertEqual(test_contact_record.delete_item(),test_contact_record)

    def test_get_item_all_happy_path(self):
        clear_test_database()
        test_contact_record.put_item()

        test_contact_record2 = ContactRecord(
            first_name='Jane',
            last_name='Doe',
        )
        test_contact_record2.put_item()

        items = ContactRecord.ddb_get_item_all()

        self.assertEqual(len(items), 2)

        for item in items:
            if item.first_name == TEST_FIRST_NAME:
                self.assertEqual(item.last_name, TEST_LAST_NAME)
                self.assertEqual(item.level, TEST_LEVEL)
            elif item.first_name == 'Jane':
                self.assertEqual(item.last_name, 'Doe')
                self.assertEqual(item.level, TEST_LEVEL)
            else:
                self.fail('test_get_item_all_happy_path: unexpected first name: ' + item.first_name)

    def test_get_item_all_no_items(self):
        clear_test_database()
        self.assertEqual(ContactRecord.ddb_get_item_all(), [])

    def test_get_all_sk_happy_path(self):
        clear_test_database()

        class LoginRecord(Record):
            class Meta:
                table_name = TEST_TABLE_NAME
                pk = Key().constant('LOGIN')
                sk = Key().constant('LOGIN').field('login')

            login = StringField()

        LoginRecord(login='johndoe').put_item()
        LoginRecord(login='janedoe').put_item()

        items = LoginRecord().ddb_get_item_all_sk()

        self.assertEqual(len(items), 2)

        if items[0].login == 'johndoe':
            self.assertEqual(items[1].login, 'janedoe')
        else:
            self.assertEqual(items[0].login, 'janedoe')
            self.assertEqual(items[1].login, 'johndoe')

    def test_get_all_sk_happy_path_simple(self):
        clear_test_database()

        contact_phone = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone_type = TEST_PHONE_TYPE1,
            phone_number=TEST_PHONE_NUMBER1
        )
        contact_phone.put_item()

        contact_phones = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        ).ddb_get_item_all_sk()

        self.assertEqual(len(contact_phones), 1)
        self.assertEqual(contact_phones[0].phone_type, TEST_PHONE_TYPE1)
        self.assertEqual(contact_phones[0].phone_number, TEST_PHONE_NUMBER1)

    def test_get_all_sk_happy_path_complex(self):
        clear_test_database()

        contact_phone1 = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone_type = TEST_PHONE_TYPE1,
            phone_number=TEST_PHONE_NUMBER1
        )
        contact_phone1.put_item()

        contact_phone2 = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone_type = TEST_PHONE_TYPE2,
            phone_number=TEST_PHONE_NUMBER2
        )
        contact_phone2.put_item()

        contact_phones = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        ).ddb_get_item_all_sk()

        self.assertEqual(len(contact_phones), 2)

        for contact_phone in contact_phones:
            if contact_phone.phone_type == TEST_PHONE_TYPE1:
                self.assertEqual(contact_phone.phone_number, TEST_PHONE_NUMBER1)
            elif contact_phone.phone_type == TEST_PHONE_TYPE2:
                self.assertEqual(contact_phone.phone_number, TEST_PHONE_NUMBER2)
            else:
                self.fail('test_get_all_sk_happy_path_complex: unexpected phone type: ' + contact_phone.phone_type)

    def test_phone_last_updated(self):
        clear_test_database()

        contact_phone1 = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone_type = TEST_PHONE_TYPE1,
            phone_number=TEST_PHONE_NUMBER1
        )
        contact_phone1.put_item()

        contact_phone2 = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone_type = TEST_PHONE_TYPE2,
            phone_number=TEST_PHONE_NUMBER2
        )
        contact_phone2.put_item()

        contact_phones = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        ).ddb_get_item_all_sk()

        self.assertEqual(len(contact_phones), 2)

        self.assertTrue(contact_phone1.last_updated < contact_phone2.last_updated)

        old_last_updated = contact_phone1.last_updated
        contact_phone1.put_item(overwrite=True)

        self.assertTrue(old_last_updated < contact_phone1.last_updated)

        contact_phone_retrieved = ContactPhone(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone_type = TEST_PHONE_TYPE2,
        ).get_item()

        self.assertTrue(contact_phone2.last_updated < contact_phone_retrieved.last_updated)

    def test_get_item_all_sk_no_items(self):
        clear_test_database()

        class LoginRecord(Record):
            class Meta:
                table_name = TEST_TABLE_NAME
                pk = Key().constant('LOGIN')
                sk = Key().constant('LOGIN').field('login')

            login = StringField()

        self.assertEqual(LoginRecord().ddb_get_item_all_sk(), [])

