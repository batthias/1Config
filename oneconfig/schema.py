# Validate schema
import json_schema

# the schema is just a json_schema, so we use this

# TODO: inherit or use json_schema
class Schema(object):

    def __init__(self, filename: str) -> None:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()
