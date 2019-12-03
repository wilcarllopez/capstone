import psycopg2
import logging
import configparser
import logging
import logging.config
import os
import sys
import yaml
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

config = configparser.ConfigParser()
path = os.path.abspath(os.path.dirname(__file__))
config.read(f"{path}{os.sep}config.ini")
logger = logging.getLogger(__name__)


def connect_to_db(username, hostname, password, database):
    """
    Connect to a database.
    :param username: DB username.
    :param hostname: DB hostname.
    :param password: DB password.
    :param database: DB name.
    :return: Connection object.
    """
    logger.info(f"Connecting to {database} database")
    try:
        logger.info(f"Connected to {database} database")
        connection = psycopg2.connect(user=username,
                                      password=password,
                                      host=hostname,
                                      port="5432",
                                      database=database)
        connection.autocommit = True
        return connection

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")


def create_db(db_name, username, hostname, password):
    """
    Check for and create a database.
    :param db_name: DB name.
    :param username: DB username.
    :param hostname: DB hostname.
    :return: Connection object.
    """
    connection = connect_to_db(username, hostname, password, "postgres")
    cursor = connection.cursor()

    logger.info("Checking for existing database")
    cursor.execute(f"SELECT datname FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
    if cursor.fetchone():
        logger.info("Database exists")
    else:
        logger.info("Database does not exist, creating new one")
        cursor.execute(f"CREATE DATABASE {db_name};")
    cursor.close()

    connection.close()

    return connect_to_db(username, hostname, password, db_name)


# def establish_connection(user, password, host, dbname):
#     create_db(dbname, user, host, password)
#     connection = psycopg2.connect(user=user,
#                                   password=password,
#                                   host=host,
#                                   port="5432",
#                                   database=dbname)
#     return connection


def create_table_details(user, password, host, dbname):
    global connection
    global cursor
    try:
        connection = connect_to_db(user, password, host, dbname)
        cursor = connection.cursor()

        create_table_query = f"CREATE TABLE IF NOT EXISTS {config['database']['tb_details']}" \
                             f"              (ID SERIAL PRIMARY KEY     NOT NULL," \
                             f"              Name           VARCHAR    NOT NULL," \
                             f"              Version        VARCHAR); "

        cursor.execute(create_table_query)
        connection.commit()
        # logger.info("Table created successfully in PostgreSQL")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating PostgreSQL table", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")


def create_table_links(user, password, host, db_name):
    global connection
    global cursor
    try:
        connection = connect_to_db(user, password, host, db_name)

        cursor = connection.cursor()

        create_table_query = f"CREATE TABLE IF NOT EXISTS {config['database']['tb_download']}" \
                             f"(ID SERIAL PRIMARY KEY     NOT NULL," \
                             f"Link         VARCHAR    NOT NULL);"

        cursor.execute(create_table_query)
        connection.commit()
        logger.info(f"Table {config['database']['tb_download']} created successfully in PostgreSQL ")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating PostgreSQL table", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")


def create_table_translations(user, password, host, db_name):
    global connection
    global cursor
    try:
        connection = connect_to_db(user, password, host, db_name)

        cursor = connection.cursor()

        create_table_query = f"CREATE TABLE IF NOT EXISTS {config['database']['tb_translation']}" \
                             f"              (ID SERIAL PRIMARY KEY     NOT NULL," \
                             f"              Link         VARCHAR    NOT NULL," \
                             f"              Version      VARCHAR    NOT NULL); "

        cursor.execute(create_table_query)
        connection.commit()
        # print("Table created successfully in PostgreSQL ")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating PostgreSQL table", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()


#  CREATE
def insert_links(user, password, host, db_name, link):
    global connection
    global cursor
    try:
        create_table_links(user, password, host, db_name)
        connection = connect_to_db(user, password, host, db_name)

        # connection.autocommit = True
        # connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()
        insert_query = f"INSERT INTO {config['database']['tb_download']}(Link) VALUES(%s)"
        cursor.execute(insert_query, (link,))
        print(link)
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # logger.info("PostgreSQL connection is closed")


def insert_details(user, password, host, db_name, dl_dict):
    global connection
    global cursor
    try:
        create_table_details(user, password, host, db_name)
        connection = connect_to_db(user, password, host, db_name)

        connection.autocommit = True
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()
        insert_query = f"INSERT INTO {config['database']['tb_details']}(Name, Version)" \
                       " VALUES(%(name)s,%(version)s)"
        cursor.execute(insert_query, dl_dict)
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")


def insert_translations(user, password, host, dbname, translation_dict):
    global connection
    global cursor
    try:
        create_table_details(user, password, host, dbname)
        connection = connect_to_db(user, password, host, dbname)

        connection.autocommit = True
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()
        insert_query = f"INSERT INTO {config['database']['tb_translation']}(Link, Version)" \
                       f" VALUES(%(language)s,%(version)s)"
        cursor.execute(insert_query, translation_dict)
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")


#  READ
def select_links(user, password, host, dbname, link):  # check if the link is already in the table 'downloadlinks'
    global connection
    global cursor
    try:
        create_table_links(user, password, host, dbname)
        connection = connect_to_db(user, password, host, dbname)
        cursor = connection.cursor()

        search_query = f"SELECT * FROM {config['database']['tb_download']} WHERE Link = '{link}'"
        cursor.execute(search_query)
        result = cursor.fetchone()
        if result is None:
            return True
        else:
            return False
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")


def select_details(user, password, host, dbname, detail_dict):
    global connection
    global cursor
    try:
        create_table_details(user, password, host, dbname)
        connection = connect_to_db(user, password, host, dbname)
        cursor = connection.cursor()

        search_query = "SELECT * FROM {config['database']['tb_details']} " \
                       "WHERE Name='{}' and Version ='{}'".format(config['database']['tb_details'],
                                                                  detail_dict["name"], )
        cursor.execute(search_query)
        result = cursor.fetchone()
        if result is None:
            return True
        else:
            return False
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")


def select_translations(user, password, host, dbname, translation_dict):
    global connection
    global cursor
    try:
        create_table_translations(user, password, host, dbname)
        connection = connect_to_db(user, password, host, dbname)
        cursor = connection.cursor()

        search_query = "SELECT * " \
                       "FROM {} " \
                       "WHERE Link='{}' and Version ='{}'"\
            .format(config['database']['tb_translation'],
                    translation_dict["language"],
                    translation_dict["version"])
        cursor.execute(search_query)
        result = cursor.fetchone()
        if result is None:
            return True
        else:
            return False
    except (Exception, psycopg2.Error) as error:
        logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")


def setup_logging(default_path='logging_config.yml', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setting up the logging config"""
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


# Initialize logger
setup_logging()
