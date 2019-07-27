from pymongo import MongoClient

import os
import configparser


def init_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    config = configparser.ConfigParser()
    config.read(f'{dir_path}/config.ini')

    return config


def init_mongodb_conn(config=None, database=None):
    if config is None:
        raise SystemExit('Error: need config to know witch database config you will use')

    host = config['mongodb']['host']
    port = config['mongodb']['port']

    try:
        client = MongoClient(f'{host}:{port}')
        mongodb_conn = client[database if database is not None else config['mongodb']['database']]
    except ValueError as e:
        print('MongoDB connection to {host}:{port} is refused')
        print(e)
        raise SystemExit()

    return mongodb_conn, client

