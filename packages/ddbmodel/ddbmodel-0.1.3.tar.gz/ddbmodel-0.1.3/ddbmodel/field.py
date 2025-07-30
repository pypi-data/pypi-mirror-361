import re
import time

import bcrypt
from logging import debug, warning, error, getLogger

from ddbmodel.base import FieldBase
from ddbmodel.record import Record

import logging

logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Field(FieldBase):
    def __init__(self, should_update=True, default_value=None):
        super().__init__(should_update, default_value)

    def __set_name__(self, owner, name):
        if logger.isEnabledFor(logging.DEBUG):
            debug(f"Field.__setname__({name},{owner})")
        self.name = name
        self.private_name = f"_{name}"
        self.owner = owner

    def __repr__(self):
        return (f"{self.__class__.__name__}(should_update={self.should_update},"
                f" default_value={self.default_value}, name={self.name}, owner={self.owner})")

    @classmethod
    def ddb_type(cls):
        debug(f"Field.ddb_type()")
        return "S"

    @classmethod
    def python_type(cls):
        return str

    def validate(self, value):
        debug(f"{self.__class__.__name__}.validate({value})")
        if type(value) is self.python_type():
            return value
        else:
            name = self.name if hasattr(self, 'name') else '*unknown*'
            raise ValueError(f'"{name}" must be a {self.python_type()} and not "{type(value)}"')

    def value(self, record: Record):
        if not hasattr(record, self.private_name):
            if self.default_value is not None:
                return self.default_value

            if self.dynamically_generated():
                new_value = self.generate()
                setattr(record, self.private_name, new_value)
                return new_value

            raise ValueError(f'"{record.__class__.__name__}" does not have a {self.name} field')

        if self.should_update and self.dynamically_generated(): # variable there, but we should update
            new_value = self.generate()
            setattr(record, self.private_name, new_value)
            return new_value

        return getattr(record, self.private_name)

    def dynamically_generated(self):
        return False


class StringField(Field):
    def __init__(self, **kwargs):
        self.validation_regex = kwargs.get('validation_regex')

        if self.validation_regex:
            del kwargs['validation_regex']

        super().__init__(**kwargs)

    def validate(self, value):
        value = super().validate(value)

        if self.validation_regex is not None:
            if not re.match(self.validation_regex, value):
                raise ValueError(f'"{self.private_name}" does not match regex "{self.validation_regex}"')

        return value


class IntField(Field):
    @classmethod
    def ddb_type(cls):
        return "N"

    @classmethod
    def python_type(cls):
        return int


class PasswordField(Field):
    #
    # def validate(self, value):    todo: jjb - do better validation for passwords
    #     return super().validate(value)
    #
    #     Consider difference for validation from ddb, front-end code, and back-end code.
    #     From ddb the password should always be salted bcrypt and an warn/error should be
    #     logged if that is not the case. From the user the password will be plaintext and
    #     a security decision needs to be made for crossings of the front-end/back-end
    #     service boundary... Should password validation (plain to salted-password) be done
    #     in the front-end or plain passwords passed to the back-end and validated there.
    #
    #     For simplicity, going with the back-end approach with duplicated password
    #     validation between front-end and back-end. This could require some refactoring
    #     work to fix.
    #

    @staticmethod
    def check_password(plain_text_password, encoded_password):
        if isinstance(plain_text_password, str):
            plain_text_password = plain_text_password.encode('utf-8')

        if isinstance(encoded_password, str):
            encoded_password = encoded_password.encode('utf-8')

        try:
            return bcrypt.checkpw(plain_text_password, encoded_password)
        except UnicodeEncodeError:
            return False  # or raise a custom exception

    @staticmethod
    def hash_password(plain_text_password):
        if isinstance(plain_text_password, str):
            plain_text_password = plain_text_password.encode('utf-8')

        return bcrypt.hashpw(plain_text_password, bcrypt.gensalt()).decode('utf-8')


class EmailField(Field):
    EMAIL_PATTERN = re.compile(
        r"^(?!\.)(?!.*\.\.)[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$"
    )

    def validate(self, value):
        #
        # todo: This uses a simplistic regular expression and may not be production ready
        #
        # Consider if the simple approach is the right one. Added a static function below
        # that can verify the email, but it does a DNS check. Email verification is a
        # tricky topic and this should be revisited before PRODUCTION.
        #
        # Did not add the external validation because it would introduce unexpected work
        # to the validate function which could be quietly called internally.
        #

        value = super().validate(value)

        if len(value) > 100:
            warning(f"EmailField.validate(): {value} is too long")
            raise ValueError("EmailField cannot be longer than 100 characters")

        if not self.EMAIL_PATTERN.match(value):
            warning(f"EmailField.validate(): {value} does not match pattern")
            raise ValueError("EmailField must be a valid email address")

        return value


    # @staticmethod
    # def external_email_validation(value, check_deliverability=False):
    #     #
    #     # NOTE: this does an external DNS lookup which can add seconds to calls.
    #     # If this is going to get called in volume, consider DNS caching and/or
    #     # API throttling
    #     #
    #
    #     try:
    #         validate_email(value, check_deliverability=check_deliverability)
    #         return True
    #     except EmailNotValidError as e:
    #         return False
    #

class TimestampNowField(IntField):
    def ddb_type(self):
        return "N"

    def python_type(self):
        return int

    def dynamically_generated(self):
        return True

    def validate(self, value):
        value = super().validate(value)

        if value >= 0:
            return value

        error(f"TimestampNowField.validate(): {value} is negative")
        raise ValueError("TimestampNowField must be a positive integer")

    def generate(self):
        return int(time.time_ns() * 1000)
