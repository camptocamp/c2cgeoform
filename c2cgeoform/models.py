from sqlalchemy import Column, Integer, LargeBinary, Text
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from .ext import colander_ext

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class FileData():
    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=True)
    data = Column(LargeBinary, nullable=False, info={
        'colanderalchemy': {
            'typ': colander_ext.BinaryData()
        }})
