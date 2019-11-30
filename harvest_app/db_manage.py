import configparser
import getpass
import logging
import os
import psycopg2

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


def create_db(db_name, username, hostname):
    """
    Check for and create a database.
    :param db_name: DB name.
    :param username: DB username.
    :param hostname: DB hostname.
    :return: Connection object.
    """
    password = getpass.getpass("Password: ")
    connection = connect_to_db(username, hostname, password, "postgres")
    cursor = connection.cursor()

    logger.info("Checking for existing database")
    cursor.execute(f"SELECT exists(SELECT 1 from pg_catalog.pg_database WHERE datname = '{db_name}');")
    if cursor.fetchone():
        logger.info("Database exists")
    else:
        logger.info("Database does not exist, creating new one")
        cursor.execute(f"CREATE DATABASE {db_name};")
    cursor.close()
    connection.close()

    return connect_to_db(username, hostname, password, db_name)


def write_to_db(row, db_name, username, hostname):
    """
    Insert list of file to database.
    :param file_list: List of files.
    :param username: DB username.
    :param hostname: DB hostname.
    :return: None
    """
    config = configparser.ConfigParser()
    path = os.path.abspath(os.path.dirname(__file__))
    config.read(f"{path}{os.sep}config.ini")
    connection = create_db(db_name, username, hostname)
    cursor = connection.cursor()
    connection.commit()
    logger.info("Checking for existing table")
    query = f"SELECT to_regclass('{config['database']['table_name']}');"
    cursor.execute(query)
    if cursor.fetchone()[0]:
        logger.info("Table found")

    else:
        logger.info("Table missing, creating new one")
        tb_name = config['database']['table_name']
        create_table_query = f"CREATE TABLE IF NOT EXISTS {tb_name} (ID SERIAL PRIMARY KEY, " \
                             f"APP_NAME TEXT NOT NULL, APP_VERSION TEXT NOT NULL);"
        cursor.execute(create_table_query)
        logger.info(f"Table {tb_name} created")

    logger.info(f"Writing to {db_name} database")
    query = '''INSERT INTO output
            (APP_NAME, APP_VERSION) 
            VALUES (%s, %s)'''

    cursor.execute(query, row)
    cursor.close()
    connection.close()
