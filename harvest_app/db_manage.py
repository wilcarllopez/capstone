import psycopg2

import logging

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT





def create_db(user, password, host, dbname):

    try:

        connection = psycopg2.connect(user=user,

                                      password=password,

                                      host=host,

                                      port="54320",

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

        # print("Table created successfully in PostgreSQL ")



    except (Exception, psycopg2.DatabaseError) as error:

        print("Error while creating PostgreSQL table", error)

    finally:

        # closing database connection.

        if (connection):

            cursor.close()

            connection.close()

            print("PostgreSQL connection is closed")





def establish_connection(user, password, host, dbname):

    create_db(user, password, host, dbname)

    connection = psycopg2.connect(user=user,

                                  password=password,

                                  host=host,

                                  port="54320",

                                  database=dbname)

    return connection





def create_table_details(user, password, host, dbname):

    try:

        connection = establish_connection(user, password, host, dbname)

        cursor = connection.cursor()



        create_table_query = '''CREATE TABLE IF NOT EXISTS downloadpages

              (ID SERIAL PRIMARY KEY     NOT NULL,

              Name           VARCHAR    NOT NULL,

              Version        VARCHAR); '''



        cursor.execute(create_table_query)

        connection.commit()

        # print("Table created successfully in PostgreSQL ")



    except (Exception, psycopg2.DatabaseError) as error:

        print("Error while creating PostgreSQL table", error)

    finally:

        # closing database connection.

        if (connection):

            cursor.close()

            connection.close()

            # print("PostgreSQL connection is closed")





def create_table_links(user, password, host, dbname):

    try:

        connection = establish_connection(user, password, host, dbname)



        cursor = connection.cursor()



        create_table_query = '''CREATE TABLE IF NOT EXISTS downloadlinks

              (ID SERIAL PRIMARY KEY     NOT NULL,

              Link         VARCHAR    NOT NULL); '''



        cursor.execute(create_table_query)

        connection.commit()

        # print("Table created successfully in PostgreSQL ")



    except (Exception, psycopg2.DatabaseError) as error:

        print("Error while creating PostgreSQL table", error)

    finally:

        # closing database connection.

        if (connection):

            cursor.close()

            connection.close()

            # print("PostgreSQL connection is closed")





def create_table_translations(user, password, host, dbname):

    try:

        connection = establish_connection(user, password, host, dbname)



        cursor = connection.cursor()



        create_table_query = '''CREATE TABLE IF NOT EXISTS downloadtranslations

              (ID SERIAL PRIMARY KEY     NOT NULL,

              Link         VARCHAR    NOT NULL,

              Version      VARCHAR    NOT NULL); '''



        cursor.execute(create_table_query)

        connection.commit()

        # print("Table created successfully in PostgreSQL ")



    except (Exception, psycopg2.DatabaseError) as error:

        print("Error while creating PostgreSQL table", error)

    finally:

        # closing database connection.

        if (connection):

            cursor.close()

            connection.close()

            # print("PostgreSQL connection is closed")





#  CREATE

def insert_links(user, password, host, dbname, link):

    try:

        create_table_links(user, password, host, dbname)

        connection = establish_connection(user, password, host, dbname)



        # connection.autocommit = True

        # connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)



        cursor = connection.cursor()

        insert_query = "INSERT INTO downloadlinks (Link)" \

                       " VALUES(%s)"

        cursor.execute(insert_query, (link,))

        print(link)

        connection.commit()

    except (Exception, psycopg2.Error) as error:

        # logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)

        print(error)

    finally:

        # closing database connection.

        if (connection):

            cursor.close()

            connection.close()

            # logger.info("PostgreSQL connection is closed")





def insert_details(user, password, host, dbname, dl_dict):

    try:

        create_table_details(user, password, host, dbname)

        connection = establish_connection(user, password, host, dbname)



        connection.autocommit = True

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)



        cursor = connection.cursor()

        insert_query = "INSERT INTO downloadpages(Name, Version)" \

                       " VALUES(%(name)s,%(version)s)"

        cursor.execute(insert_query, dl_dict)

        connection.commit()

    except (Exception, psycopg2.Error) as error:

        # logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)

        print(error)

    finally:

        # closing database connection.

        if (connection):

            cursor.close()

            connection.close()

            # logger.info("PostgreSQL connection is closed")





def insert_translations(user, password, host, dbname, translation_dict):

    try:

        create_table_details(user, password, host, dbname)

        connection = establish_connection(user, password, host, dbname)



        connection.autocommit = True

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)



        cursor = connection.cursor()

        insert_query = "INSERT INTO downloadtranslations(Link, Version)" \

                       " VALUES(%(language)s,%(version)s)"

        cursor.execute(insert_query, translation_dict)

        connection.commit()

    except (Exception, psycopg2.Error) as error:

        # logger.error('Error while connecting to PostgreSQL: ' + str(error), exc_info=True)

        print(error)

    finally:

        # closing database connection.

        if (connection):

            cursor.close()

            connection.close()

            # logger.info("PostgreSQL connection is closed")





#  READ

def select_links(user, password, host, dbname, link):  # check if the link is already in the table 'downloadlinks'

    try:

        create_table_links(user, password, host, dbname)

        connection = establish_connection(user, password, host, dbname)

        cursor = connection.cursor()



        search_query = "SELECT * FROM downloadlinks WHERE Link = '{}'".format(link)

        cursor.execute(search_query)

        result = cursor.fetchone()

        if result is None:

            return True

        else:

            return False

    except (Exception, psycopg2.Error) as error:

        print(error)

    # finally:

    #     if (connection):

    #         cursor.close()

    #         connection.close()





def select_details(user, password, host, dbname, detail_dict):

    try:

        create_table_details(user, password, host, dbname)

        connection = establish_connection(user, password, host, dbname)

        cursor = connection.cursor()



        search_query = "SELECT * FROM downloadpages WHERE Name='{}' and Version ='{}'".format(detail_dict["name"],

                                                                                              detail_dict["version"])

        cursor.execute(search_query)

        result = cursor.fetchone()

        if result is None:

            return True

        else:

            return False

    except (Exception, psycopg2.Error) as error:

        print(error)

    finally:

        if (connection):

            cursor.close()

            connection.close()





def select_translations(user, password, host, dbname, translation_dict):

    try:

        create_table_translations(user, password, host, dbname)

        connection = establish_connection(user, password, host, dbname)

        cursor = connection.cursor()



        search_query = "SELECT * " \

                       "FROM downloadtranslations " \

                       "WHERE Link='{}' and Version ='{}'".format(translation_dict["language"], translation_dict["version"])

        cursor.execute(search_query)

        result = cursor.fetchone()

        if result is None:

            return True

        else:

            return False

    except (Exception, psycopg2.Error) as error:

        print(error)

    finally:

        if (connection):

            cursor.close()

            connection.close()

