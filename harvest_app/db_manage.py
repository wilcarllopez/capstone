import configparser
import logging
import logging.config
import os
import psycopg2
import sys
import yaml
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
path = os.path.abspath(os.path.dirname(__file__))
config.read(f"{path}{os.sep}config.ini")


def setup_logging(default_path='logging_config.yml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Seting up logging config
    :param default_path:
    :param default_level:
    :param env_key:
    :return:
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print('Error in Logging Configuration. Using default configs', e)
                logging.basicConfig(level=default_level, stream=sys.stdout)
    else:
        logging.basicConfig(level=default_level, stream=sys.stdout)
        print('Failed to load configuration file. Using default configs')


def create_db(user, password, host, port, dbname ):
    try:
        connection = psycopg2.connect(user=user,
                                      password=password,
                                      host=host,
                                      port=port,
                                      database="postgres")
        connection.autocommit = True
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        find_db_query = "SELECT datname FROM pg_catalog.pg_database WHERE datname = '{}';".format(dbname)
        cursor.execute(find_db_query)
        if cursor.fetchone():
            pass
        else:
            create_db_query = "CREATE DATABASE {};".format(dbname)
            cursor.execute(create_db_query)
            connection.commit()
            cursor.close()
            connection.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def establish_connection(user, password, host, port, dbname):
    create_db(user, password, host, port, dbname)
    connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  database=dbname,
                                  port=port)
    return connection


def create_table_details(user, password, host, port, dbname):
    try:
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS {}
              (ID SERIAL PRIMARY KEY     NOT NULL,
              Name           VARCHAR    NOT NULL,
              Version        VARCHAR); '''.format(config['database']['tb_details'])

        cursor.execute(create_table_query)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def create_table_links(user, password, host, port, dbname):
    try:
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        create_table_query = f'''CREATE TABLE IF NOT EXISTS {config['database']['tb_download']}
                             (ID SERIAL PRIMARY KEY     NOT NULL,
                                           Link         VARCHAR    NOT NULL);'''
        cursor.execute(create_table_query)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def create_table_translations(user, password, host, port, dbname):
    try:
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS {}
              (ID SERIAL PRIMARY KEY     NOT NULL,
              Link         VARCHAR    NOT NULL,
              Version      VARCHAR    NOT NULL); '''.format(config['database']['tb_translation'])
        cursor.execute(create_table_query)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


#  CREATE
def insert_links(user, password, host, port, dbname, link):
    try:
        create_table_links(user, password, host, dbname, port)
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        insert_query = "INSERT INTO {config['database']['download']} (Link)" \
                       " VALUES(%s)"
        cursor.execute(insert_query, (link,))
        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def insert_details(user, password, host, port, dbname, dict):
    try:
        create_table_details(user, password, host, port, dbname)
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        insert_query = "INSERT INTO {}(Name, Version)" \
                       " VALUES(%(name)s,%(version)s)".format(config['database']['tb_details'])
        cursor.execute(insert_query, dict)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def insert_translations(user, password, host, port, dbname, dict):
    try:
        create_table_details(user, password, host, port, dbname)
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        insert_query = "INSERT INTO {}(Link, Version)" \
                       " VALUES(%(language)s,%(version)s)".format(config['database']['tb_translation'])
        cursor.execute(insert_query, dict)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


#  READ
def select_links(user, password, host, port, dbname, link):  # check if the link is already in the table '{config['database']['download']}'
    try:
        create_table_links(user, password, host, port, dbname)
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        search_query = f"SELECT * FROM {config['database']['tb_download']} WHERE Link = '{link}'"
        cursor.execute(search_query)
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            connection.close()
            return True
        else:
            cursor.close()
            connection.close()
            return False
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def select_all_links(user, password, host, port, dbname):
    try:
        create_table_links(user, password, host, port, dbname)
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        search_query = f"SELECT * FROM {config['database']['tb_download']}"
        cursor.execute(search_query)
        links_list = [r[1] for r in cursor.fetchall()]
        cursor.close()
        connection.close()
        return links_list
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def select_details(user, password, host, port, dbname, dict):
    try:
        create_table_details(user, password, host, port, dbname)
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        search_query = "SELECT * FROM {} WHERE Name='{}' and Version ='{}'".\
            format(config['database']['tb_details'],
                   dict["name"],
                   dict["version"])
        cursor.execute(search_query)
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            connection.close()
            return True
        else:
            cursor.close()
            connection.close()
            return False
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


def select_translations(user, password, host, port, dbname, dict):
    try:
        create_table_translations(user, password, host, port, dbname )
        connection = establish_connection(user, password, host, port, dbname)
        connection.autocommit = True
        cursor = connection.cursor()
        search_query = "SELECT * " \
                       "FROM {} " \
                       "WHERE Link='{}' and Version ='{}'".format(config['database']['tb_translation'],dict["language"],
                                                                  dict["version"])
        cursor.execute(search_query)
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            connection.close()
            return True
        else:
            cursor.close()
            connection.close()
            return False
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)


# Initializes logging file
setup_logging()
