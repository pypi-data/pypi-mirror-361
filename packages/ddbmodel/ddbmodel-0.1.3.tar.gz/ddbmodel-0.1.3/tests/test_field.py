import time
import random
import datetime
from unittest import TestCase

from ddbmodel.field import StringField, IntField, PasswordField, EmailField, TimestampNowField

field_values = [
    [
        str(type(value)),
        type(value),
        value
    ]
    for value in ['test', 1, 1.1, [], {}, True, None, -1, b'\x01\x02\x03']
]


def _test_invalid_types(unit_test_self, field, valid_type):
    for [value_type_name, value_type, value] in field_values:
        if value_type != valid_type:
            with unit_test_self.assertRaises(
                    ValueError,
                    msg=f"{field.__class__.__name__}.validate did not raise ValueError for: "
                        f"{value_type} value: {value}"
            ):
                field.validate(value)
        else:
            print(
                f"Info: Testing {field.__class__.__name__}.validate() with "
                f"{value_type_name} value: {value}: same type"
            )


class TestStringField(TestCase):
    def test_validate_happy_path(self):
        field = StringField()
        self.assertEqual(field.validate('test'), 'test')

    def test_validate_invalid_types(self):
        _test_invalid_types(self, StringField(), str)

    def test_validate_regex(self):
        field = StringField(validation_regex=r'^[a-z]+$')
        self.assertEqual(field.validate('test'), 'test')
        with self.assertRaises(
                ValueError,
                msg=f"{field.__class__.__name__}.validate did not raise ValueError for: "
                    f"invalid value: 'TEST'"
        ):
            field.validate('TEST')


class TestIntField(TestCase):
    def test_validate_happy_path(self):
        field = IntField()
        self.assertEqual(field.validate(0), 0)

    def test_validate_invalid_types(self):
        _test_invalid_types(self, IntField(), int)


class TestPasswordField(TestCase):
    def test_validate_happy_path(self):
        field = PasswordField()
        self.assertEqual(field.validate('test'), 'test')

    def test_validate_invalid_types(self):
        _test_invalid_types(self, PasswordField(), str)

    def test_password_hash_and_check(self):
        password = 'XXXX'
        hashed_password = PasswordField.hash_password(password)
        self.assertTrue(PasswordField.check_password(password, hashed_password))


class TestEmailField(TestCase):
    def test_validate_happy_path(self):
        field = EmailField()
        self.assertEqual(field.validate('bob@example.com'), 'bob@example.com')
        self.assertEqual(field.validate('bob@sub.example.com'), 'bob@sub.example.com')
        self.assertEqual(field.validate('bob@sub.sub.example.com'), 'bob@sub.sub.example.com')

    def test_invalid_emails(self):
        invalid_emails = {
            'bob', 'bob@', 'bob@.', 'bob@.com', 'bob@example', 'bob@example.',
            'bob@@example.com', 'bob@example..com', 'bob@example.c'
            'bob@example.com.', 'bob@example.com..', 'bob@example.com.c0m..',
            'bob @example.com'
        }

        field = EmailField()
        for email in invalid_emails:
            with self.assertRaises(
                    ValueError,
                    msg=f'{field.__class__.__name__}.validate did not raise ValueError for: "{email}"'
            ):
                field.validate(email)

    def test_validate_invalid_types(self):
        _test_invalid_types(self, EmailField(), str)


class TestTimestampNowField(TestCase):
    def test_validate_happy_path(self):
        field = TimestampNowField()

        valid_timestamps = [
            0,
            1,
            # Current time should always work
            int(datetime.datetime.now(datetime.UTC).timestamp() * 1000),
            # Fixed date 2023-01-01T00:00:00.000Z should work
            int(datetime.datetime(
                2023, 1, 1,
                0, 0, 0, 0,
                datetime.UTC
            ).timestamp() * 1000),
            # Fixed date 2100-01-01T00:00:00.000Z should work
            int(datetime.datetime(
                2100, 1, 1,
                0, 0, 0, 0,
                datetime.UTC
            ).timestamp() * 1000),
        ]

        for timestamp in valid_timestamps:
            print(f"Info: Testing {field.__class__.__name__}.validate() with timestamp: {timestamp}")
            self.assertEqual(field.validate(timestamp), timestamp)

    def test_validate_not_negative(self):
        field = TimestampNowField()
        self.assertRaises(ValueError, field.validate, -1)

    def test_validate_invalid_types(self):
        _test_invalid_types(self, TimestampNowField(), int)

    def test_validate_growing_timestamps(self):
        # Expect timestamps to be monotonically increasing

        timestamps_to_generate = 30
        timestamps = []

        for _ in range(timestamps_to_generate):
            field = TimestampNowField()
            timestamp = field.generate()
            timestamps.append(timestamp)
            time.sleep(random.randint(10000, 100000)/10000000.0)

        self.assertTrue(len(timestamps)>10)
        self.assertEqual(sorted(timestamps), timestamps)
        self.assertEqual(len(timestamps), len(set(timestamps))) # todo: jjb check math, is this always true?
        print(timestamps)
