from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
import os.path
import sqlite3

class DatabaseManager:
    def __init__(self, db_name, schema):
        # Create file from schema if it does not exist
        self.safely_create_database(db_name, schema)

        # Create engine and get the metadata
        self.Base = declarative_base()
        self.engine = create_engine('sqlite:///' + db_name)
        self.metadata = MetaData(bind=self.engine)

    # Create database file if it does not exist
    def safely_create_database(self, db_name, statements):
        if not os.path.isfile(db_name):
            try:
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                with open(statements, 'r') as statements:
                    statementlist = statements.read().split(";")
                    for statement in statementlist:
                        cursor.execute(statement+";")
                conn.commit()
            except Error as e:
                print(e)
            finally:
                conn.close()

    # Get base of the manager
    def get_base(self):
        return self.Base

    # Get metadata
    def get_metadata(self):
        return self.metadata

    # Get engine used to connect to database
    def get_engine(self):
        return self.engine
