from sqlalchemy import Table
from sqlalchemy.orm import sessionmaker
from database.DatabaseManager import DatabaseManager

databaseManagerII = DatabaseManager('database/inverted-index.db', 'database/inverted-index.sql')
BaseII = databaseManagerII.get_base()
metadataII = databaseManagerII.get_metadata()
engineII = databaseManagerII.get_engine()

databaseManagerD = DatabaseManager('database/documents.db', 'database/documents.sql')
BaseD = databaseManagerD.get_base()
metadataD = databaseManagerD.get_metadata()
engineD = databaseManagerD.get_engine()

# Reflect each database table using metadata
class IndexWord(BaseII):
    __table__ = Table('IndexWord', metadataII, autoload=True)

class Posting(BaseII):
    __table__ = Table('Posting', metadataII, autoload=True)

class Document(BaseD):
    __table__ = Table('Document', metadataD, autoload=True)

# Create a sessionmaker function for each Database to use the tables
SessionII = sessionmaker(bind=engineII)
SessionD  = sessionmaker(bind=engineD)