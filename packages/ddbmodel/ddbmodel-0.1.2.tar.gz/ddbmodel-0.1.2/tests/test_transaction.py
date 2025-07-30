import os
from unittest import TestCase

from ddbmodel.field import StringField, TimestampNowField
from ddbmodel.key import Key
from ddbmodel.transaction import TransactionRecord, View

TEST_TABLE_NAME = os.environ.get('TEST_TABLE_NAME', "ddbmodel-test")

class ContactRecord(TransactionRecord):
    class Meta:
        table_name = TEST_TABLE_NAME

        default_view = 'ContactIdView'

        ContactIdView = View(
            pk=Key().constant('ContactId'),
            sk=Key().field('contact_id')
        )

        EmailView = View(
            pk=Key().constant('Email'),
            sk=Key().field('contact_email')
        )

        NameView = View(
            pk=Key().constant('Name'),
            sk=Key().field('contact_name')
        )

    contact_id = StringField(should_update=False)
    contact_email = StringField(should_update=False)
    contact_name = StringField(should_update=False)
    last_updated = TimestampNowField(should_update=True)
    created_at = TimestampNowField(should_update=False)


class TestTransactionRecord(TestCase):
    def test_ddb_get_item_all_happy_path_simple(self):

        contact1 = ContactRecord(
            contact_id='contact_id_1',
            contact_email='contact_1@example.com',
            contact_name='Contact1 Name'
        )
        contact1.put_item()

        contact2 = ContactRecord(
            contact_id='contact_id_2',
            contact_email='contact_2@example.com',
            contact_name='Contact2 Name'
        )
        contact2.put_item()

        contact3 = ContactRecord(
            contact_id='contact_id_3',
            contact_email='contact_3@example.com',
            contact_name='Contact3 Name'
        )
        contact3.put_item()

        contact_list = [
            contact1,
            contact2,
            contact3
        ]

        ddb_contact_map = {
            contact.contact_id: contact
            for contact in ContactRecord.ddb_get_item_all()
        }

        for contact in contact_list:
            self.assertEqual(
                contact.contact_id,
                ddb_contact_map[contact.contact_id].contact_id
            )
            self.assertEqual(
                contact.contact_name,
                ddb_contact_map[contact.contact_id].contact_name
            )
            self.assertEqual(
                contact.contact_email,
                ddb_contact_map[contact.contact_id].contact_email
            )

        contact1.delete_item()
        contact2.delete_item()
        contact3.delete_item()
