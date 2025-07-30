from logging import debug, info, error

from ddbmodel.base import FieldBase, KeyBase, RecordBase, dbclient, ClientError

# import logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

class Record(RecordBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __init_subclass__(cls, **kwargs):
        debug(f"Record.__init_subclass__({kwargs})")

        cls._record_definitions_cache = {
            field_name: field
            for field_name, field in cls.__dict__.items()
            if isinstance(field, FieldBase)
        }

        try:
            meta_class = getattr(cls, 'Meta')
            getattr(meta_class, 'pk')
            getattr(meta_class, 'sk')
            getattr(meta_class, 'table_name')
        except AttributeError:
            raise cls.InvalidRecordClass(f"{cls.__name__} Meta class must exist and have primary and sort keys")

        if not isinstance(meta_class.pk, KeyBase):
            raise cls.InvalidRecordClass(f"{cls.__name__} Meta class primary key must be a Key")

        if not isinstance(meta_class.sk, KeyBase):
            raise cls.InvalidRecordClass(f"{cls.__name__} Meta class sort key must be a Key")

    def __repr__(self):
        fields = ",".join([
            f"{field_name}={field.value(self)}"
            for field_name, field in self.record_fields().items()
        ])
        return f"{self.__class__.__name__}({fields})"


    def ddb_primary_key(self):
        debug(f"Record.ddb_primary_key(): {self.__class__.Meta.pk}")
        return self.primary_key().ddb_value(self)


    def ddb_sort_key(self):
        debug(f"Record.ddb_sort_key(): {self.__class__.Meta.sk}")
        return self.sort_key().ddb_value(self)


    def ddb_get_item_command(self, view=None, table_override=None):
        if view is not None:
            error(f"Record.ddb_get_item_command(): view is not supported")
            raise NotImplementedError

        return {
            'TableName': self.table_name(table_override=table_override),
            'Key': {
                'pk': {'S': self.primary_key().ddb_value(self)},
                'sk': {'S': self.sort_key().ddb_value(self)}
            },
        }

    def ddb_put_item_command(self, overwrite=False, table_override=None):
        ddb_put = {
            'TableName': self.table_name(table_override=table_override),
            'Item': self.ddb_fields()
        }

        ddb_put['Item'].update({'pk': {'S': self.primary_key().ddb_value(self)}})
        ddb_put['Item'].update({'sk': {'S': self.sort_key().ddb_value(self)}})

        if not overwrite:
            ddb_put.update({'ConditionExpression': 'attribute_not_exists(pk) AND attribute_not_exists(sk)'})

        return ddb_put


    def put_item(self, overwrite=False, table_override=None):
        debug(f"Record.put_item({overwrite}, {table_override})")
        ddb_put = self.ddb_put_item_command(overwrite=overwrite, table_override=table_override)

        try:
            print(f"ddb_put: {ddb_put}")
            response = dbclient.put_item(**ddb_put)
            debug(f"Record.put_item(): {response}")
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return self
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"Record already exists")
            else:
                raise

        return self


    def ddb_update_item_command(self, table_override=None, transaction=False):
        debug(f"Record.ddb_update_item_command({table_override}, {transaction})")

        if transaction:
            update_expression = 'SET' + ', '.join(
                f" #{field_name} = :{field_name}"
                for field_name, field in self.record_fields().items()
                if field.should_update
            )

            expression_attribute_names = {
                '#'+field_name: field_name
                for field_name, field in self.record_fields().items()
                if field.should_update
            }

            expression_attribute_values = {
                ':'+field_name: {
                    field.ddb_type(): str(field.value(self))
                }
                for field_name, field in self.record_fields().items()
                if field.should_update
            }

            return {
                'TableName': self.table_name(table_override=table_override),
                'Key': {
                    'pk': {'S': self.primary_key().ddb_value(self)},
                    'sk': {'S': self.sort_key().ddb_value(self)}
                },
                'UpdateExpression': update_expression,
                'ExpressionAttributeNames': expression_attribute_names,
                'ExpressionAttributeValues': expression_attribute_values
            }
        else:
            fields = {
                field_name: {
                    'Value': { field.ddb_type(): str(field.value(self)) }
                }
                for field_name, field in self.record_fields().items()
                if field.should_update
            }

            return {
                'TableName': self.table_name(table_override=table_override),
                'Key': {
                    'pk': {'S': self.primary_key().ddb_value(self)},
                    'sk': {'S': self.sort_key().ddb_value(self)}
                },
                'AttributeUpdates': fields,
                'ReturnValues': 'UPDATED_NEW'
            }


    def update_item(self, table_override=None):
        debug(f"RecordBase.update({table_override})")
        ddb_update = self.ddb_update_item_command(table_override=table_override)

        try:
            response = dbclient.update_item(**ddb_update)
            debug(f"RecordBase.update_item(): {response}")
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return self
        except ClientError  as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"Record does not exist")
            else:
                raise

        return self


    def ddb_delete_item_command(self, table_override=None, transaction=False):
        if transaction:
            return {
                'TableName': self.table_name(table_override=table_override),
                'Key': {
                    'pk': {'S': self.primary_key().ddb_value(self)},
                    'sk': {'S': self.sort_key().ddb_value(self)}
                }
            }
        else:
            return {
                'TableName': self.table_name(table_override=table_override),
                'Key': {
                    'pk': {'S': self.primary_key().ddb_value(self)},
                    'sk': {'S': self.sort_key().ddb_value(self)}
                },
                'ReturnValues': 'ALL_OLD'
            }


    def delete_item(self, table_override=None):
        debug(f"Record.delete({table_override})")
        ddb_delete = self.ddb_delete_item_command(table_override=table_override)

        response = dbclient.delete_item(**ddb_delete)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return self

        #
        # todo: jjb: Is returning None the right thing to do?
        #

        return None


    @classmethod
    def ddb_get_item_all_command(cls, table_override=None):
        return {
            'TableName': cls.table_name(table_override=table_override),
            'KeyConditionExpression': 'pk = :pk',
            'ExpressionAttributeValues': {
                ':pk': {'S': cls.primary_key().ddb_const_value()}
            }
        }


    @classmethod
    def ddb_get_item_all(cls, table_override=None):
        debug(f"Record.ddb_get_all({table_override})")
        get_item_all = cls.ddb_get_item_all_command(table_override=table_override)

        response = dbclient.query(**get_item_all)
        debug(f"Record.ddb_get_all(): {response}")

        if 'Items' not in response:
            return []

        return [
            cls(**{
                field_name: next(iter(field_value.values()))
                for field_name, field_value in item.items()
                if field_name != 'pk' and field_name != 'sk'
            })
            for item in response['Items']
        ]


    def ddb_get_item_all_sk_command(self, table_override=None):
        return {
            'TableName': self.table_name(table_override=table_override),
            'KeyConditionExpression': 'pk = :pk AND begins_with(sk, :sk)',
            'ExpressionAttributeValues': {
                ':pk': {'S': self.primary_key().ddb_value(self)},
                ':sk': {'S': self.sort_key().ddb_const_value()}
            }
        }


    def ddb_get_item_all_sk(self, table_override=None):
        debug(f"Record.ddb_get_all_sk({table_override})")
        get_all_sk = self.ddb_get_item_all_sk_command(table_override=table_override)

        response = dbclient.query(**get_all_sk)
        debug(f"Record.ddb_get_all_sk(): {response}")

        if 'Items' not in response:
            return []

        return [
            self.__class__(**{
                field_name: next(iter(field_value.values()))
                for field_name, field_value in item.items()
                if field_name != 'pk' and field_name != 'sk'
            })
            for item in response['Items']
        ]
