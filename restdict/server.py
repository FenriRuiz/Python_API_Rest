#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import urllib.parse
from multiprocessing import Process

from flask import Flask, jsonify, abort, make_response, request

API_ROOT = '/api/v1'
DEFAULT_PORT = 5001


def new_server(address):
    '''Factory'''
    address = urllib.parse.urlsplit(address)
    server = Process(target=_FLASK_APP_.run, kwargs={
        'host': address.hostname, 'port': address.port,
        # Flask cannot run in a thread with debug mode enabled:
        # https://stackoverflow.com/a/31265602/1062435
        'debug': False
    })
    return server


_FLASK_APP_ = Flask(__name__.split('.')[0])
_APP_DICT_ = {}



@_FLASK_APP_.route(f'{API_ROOT}/<dic_name>/keys', methods=['GET'])
def get_keys(dic_name):
    try:
        dic = _APP_DICT_[dic_name]
    except:
        dic = {}
    #print(dic.keys())
    return make_response(jsonify({'result': list(dic.keys())}), 200)

@_FLASK_APP_.route(f'{API_ROOT}/<dic_name>/keys/<key>', methods=['GET'])
def get_value(dic_name, key):
    if dic_name not in _APP_DICT_:
        abort(404)
    if key not in _APP_DICT_[dic_name]:
        abort(404)
    dic = _APP_DICT_[dic_name]
    return make_response(jsonify({'result': dic[key]}), 200)

@_FLASK_APP_.route(f'{API_ROOT}/<dic_name>/keys/<key>', methods=['PUT'])
def create_value(dic_name, key):
    if (not request.data):
        abort(400)
    dic = {}
    try: 
        dic = dict(_APP_DICT_[dic_name])
    except:
        pass
    dic[key] = request.data.decode()
    _APP_DICT_[dic_name] = dic
    # _APP_DICT_[dic_name] = {key: request.data.decode()}
    return make_response(jsonify({'result': {dic_name: {key: request.data.decode()}}}), 201)

@_FLASK_APP_.route(f'{API_ROOT}/<dic_name>/keys/<key>', methods=['POST'])
def set_value(dic_name, key):
    if (not request.data):
        abort(400)
    dic = {}
    try: 
        dic = dict(_APP_DICT_[dic_name])
    except:
        pass
    dic[key] = request.data.decode()
    _APP_DICT_[dic_name] = dic
    # _APP_DICT_[dic_name] = {key: request.data.decode()}
    return make_response(jsonify({'result': {dic_name: {key: request.data.decode()}}}), 200)

@_FLASK_APP_.route(f'{API_ROOT}/<dic_name>/keys/<key>', methods=['DELETE'])
def remove_value(dic_name, key):
    if dic_name not in _APP_DICT_:
        abort(404)
    if key not in _APP_DICT_[dic_name]:
        abort(404)
    dic = _APP_DICT_[dic_name]
    del dic[key]
    return make_response('', 204)

@_FLASK_APP_.route(f'{API_ROOT}/<dic_name>', methods=['DELETE'])
def remove_dic(dic_name):
    if dic_name not in _APP_DICT_:
        abort(404)
    del _APP_DICT_[dic_name]
    return make_response('', 204)


class DictServer:
    '''
        Flask application container
    '''
    def __init__(self, server_address):
        self._SERVER_ = new_server(server_address)
        self._started_ = False

    @property
    def started(self):
        return self._started_

    def start(self):
        if not self._started_:
            self._SERVER_.start()
            time.sleep(1.0)
            self._started_ = True

    def stop(self):
        if not self._started_:
            return
        self._SERVER_.terminate()
        self._SERVER_.join()
        self._started_ = False

    def __enter__(self):
        '''
        Start server
        '''
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Stop server
        '''
        self.stop()
        

if __name__ == '__main__':
    _FLASK_APP_.run(host='0.0.0.0', port=DEFAULT_PORT, debug=True)
