# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import event
from sqlalchemy import exc
from app import log
from app import config

import os
import json

LOG = log.get_logger()


def get_engine(uri):
    LOG.info('Connecting to database..')
    options = {
        'pool_recycle': 3600,
        'pool_size': 500,
        'pool_timeout': 60,
        'max_overflow': 500,
        # 'echo': config.DB_ECHO,
        'echo': True,
        'execution_options': {
            'autocommit': config.DB_AUTOCOMMIT
        }#,
        #'pool_pre_ping': True
    }
    return create_engine(uri, **options)


def _add_process_guards(engine):
    """Add multiprocessing guards.

    Forces a connection to be reconnected if it is detected
    as having been shared to a sub-process.

    """

    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        connection_record.info['pid'] = os.getpid()
        LOG.info("#-listens_for-Connect")

    @event.listens_for(engine, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        pid = os.getpid()
        LOG.info("#-listens_for-Checkout")
        if connection_record.info['pid'] != pid:
            LOG.info((
                "Parent process %(orig)s forked (%(newproc)s) with an open "
                "database connection, "
                "which is being discarded and recreated."),
                {"newproc": pid, "orig": connection_record.info['pid']})
            connection_record.connection = connection_proxy.connection = None
            raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
            )


db_session = scoped_session(sessionmaker())
engine = get_engine(config.DATABASE_URL)


def init_session():
    _add_process_guards(engine)
    db_session.configure(bind=engine)

    from app.model import Base

    Base.metadata.create_all(engine)


def new_alchemy_encoder():
    # http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    fields[field] = obj.__getattribute__(field)
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder
