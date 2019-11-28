import psycopg2
import getpass
import logging

logger = logging.get_logger(__name__)

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
                                      port="54320",
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
    cursor.execute(f"SELECT datname FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
    if cursor.fetchone():
        logger.info("Database exists")
    else:
        logger.info("Database does not exist, creating new one")
        cursor.execute(f"CREATE DATABASE {db_name};")
    cursor.close()
    connection.close()

    return connect_to_db(username, hostname, password, db_name)

def write_to_db(file_list, username, hostname):
    """
    Insert list of file to database.
    :param file_list: List of files.
    :param username: DB username.
    :param hostname: DB hostname.
    :return: None
    """
    connection = create_db("listdir", username, hostname)
    cursor = connection.cursor()

    logger.info("Checking for existing table")
    query = '''SELECT to_regclass('public.output');'''
    cursor.execute(query)
    if cursor.fetchone()[0]:
        logger.info("Table found")

    else:
        logger.info("Table missing, creating new one")

        create_table_query = '''CREATE TABLE output
                          (ID SERIAL PRIMARY KEY,
                          FILE              TEXT    NOT NULL,
                          DIRECTORY         TEXT    NOT NULL,
                          SIZE              TEXT    NOT NULL,
                          MD5               TEXT    NOT NULL,
                          SHA1              TEXT    NOT NULL); '''

        cursor.execute(create_table_query)
        logger.info("Table created")



    logger.info("Writing to database")
    query = '''INSERT INTO 

                    output

                    (FILE, DIRECTORY, SIZE, MD5, SHA1) 

                VALUES 

                    (%(file_name)s, %(parent_path)s, %(file_size)s, %(md5)s, %(sha1)s)'''

    cursor.executemany(query, file_list)
    cursor.close()
    connection.close()