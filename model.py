#this model will  include all the general databse interaction

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError
from configuration import RDB_HOST, RDB_PORT , UDIO_DB

riders='riders'
senders='senders'

#databse setup function . Run only once at the beginning
def dbSetUp():
     connection = r.connect(host=RDB_HOST, port=RDB_PORT)
     try:
        r.db_create(UDIO_DB).run(connection)
        r.db(UDIO_DB).table_create('users').run(connection)
        r.db(UDIO_DB).table_create('rides').run(connection)
        r.db('udio').table_create('packages').run(connection)
        r.db('udio').table_create('messages').run(connection)
        print( "Database setup completed")
     except RqlRuntimeError:
        print ("Database already exists")
     finally :
        connection.close()

def create_connection():
    connection=r.connect(host=RDB_HOST,port=RDB_PORT)
    return connection


def close_connection(conn):
    conn.close()


