#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Decode and encode model
import json


class Model:

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = data.copy()

        return data

    def to_dict(self):
        data = dict()

        for key in iter(self.__dict__):
            if key in ():
                continue

            value = self.__dict__[key]
            if value is not None:
                if hasattr(value, 'to_dict'):
                    data[key] = value.to_dict()
                else:
                    data[key] = value

        return data
