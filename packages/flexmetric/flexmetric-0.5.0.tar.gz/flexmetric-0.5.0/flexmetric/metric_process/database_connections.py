import clickhouse_connect
import sqlite3
from flexmetric.logging_module.logger import get_logger
import os

logger = get_logger(__name__)

logger.info("database logs")

def create_clickhouse_client(db_conf):
    id = db_conf.get('id')
    host = db_conf.get('host', 'localhost')
    port = db_conf.get('port', 9440)
    username = db_conf.get('username', 'default')
    password = db_conf.get('password', '')

    client_cert = db_conf.get('client_cert')
    client_cert_key = db_conf.get('client_key')
    ca_cert = db_conf.get('ca_cert')

    secure = bool(client_cert and client_cert_key and ca_cert)

    settings = {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'secure': secure,
        'verify': True
    }

    if secure:
        settings.update({
            'client_cert': client_cert,
            'client_cert_key': client_cert_key,
            'ca_cert': ca_cert,
        })

    client = clickhouse_connect.get_client(**settings)
    logger.info(f"Clickhouse connection '{id}' created")
    return client


def create_sqlite_client(db_conf: dict):
    db_path = db_conf.get('db_connection')
    db_name = db_conf.get('db_name', 'default_sqlite_db')

    if not db_path or not os.path.isfile(db_path):
        raise FileNotFoundError(f"SQLite database file not found at {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        logger.info(f"SQLite connection '{db_name}' created")
        return conn
    except Exception as e:
        raise ConnectionError(f"Failed to create SQLite client: {e}")
