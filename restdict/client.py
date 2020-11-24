#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pickle
import random
import binascii
import uuid
from collections.abc import MutableMapping

import requests


def _marshall_(value):
    return binascii.b2a_base64(pickle.dumps(value))


def _unmarshall_(value):
    return pickle.loads(binascii.a2b_base64(value))


class RestDict(MutableMapping):
    def __init__(self, base_api_uri, name):
        self._uri_ = base_api_uri
        if self._uri_.endswith('/'):
            self._uri_ = self._uri_[:-1]
        self._name_ = name
        if self._name_ is None:
            self._name_ = uuid.uuid1()

    def keys(self):
        result = requests.get(f'{self._uri_}/{self._name_}/keys')
        if result.status_code != 200:
            raise ValueError(f'Cannot get keys, status code: {result.status_code}')
        try:
            result = json.loads(result.content.decode()).get('result', [])
            # print(result)
        except Exception as error:
            raise ValueError(f'Cannot get keys: {error}')
        return result

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    def __getitem__(self, key):
        result = requests.get(f'{self._uri_}/{self._name_}/keys/{key}')
        if not isinstance(key, str):
            raise TypeError(key)
        if result.status_code == 404:
            raise KeyError(key)
        try:
            result = json.loads(result.content.decode())['result']
        except Exception as error:
            raise ValueError(f'Cannot get item: {error}')
        try:
            return _unmarshall_(result)
        except Exception as error:
            raise ValueError(f'Unmarshalling error: {error}')

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(key)
        if key in self.keys():
            result = requests.post(f'{self._uri_}/{self._name_}/keys/{key}', data=_marshall_(value))
        else:
            result = requests.put(f'{self._uri_}/{self._name_}/keys/{key}', data=_marshall_(value))
        if result.status_code not in [200, 201]:
            raise ValueError(f'Cannot set item: {result.status_code}')

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(key)
        result = requests.delete(f'{self._uri_}/{self._name_}/keys/{key}')
        if result.status_code == 404:
            raise KeyError(key)

    def deldic(self):
        result = requests.delete(f'{self._uri_}/{self._name_}')
        if result.status_code == 404:
            raise ValueError('Cannot delete dictionary')
        
    def _keytransform(self, key):
        return key
