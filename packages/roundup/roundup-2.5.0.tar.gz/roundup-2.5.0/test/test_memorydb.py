import unittest, os, shutil, time

from roundup import hyperdb

from .db_test_base import DBTest, ROTest, SchemaTest, config, setupSchema
from roundup.test import memorydb

from roundup.anypy import strings

class memorydbOpener:
    module = memorydb

    def nuke_database(self):
        # really kill it
        memorydb.db_nuke('')
        self.db = None

    db = None
    def open_database(self, user='admin'):
        if self.db:
            self.db.close()
        self.db = self.module.Database(config, user)
        return self.db

    def setUp(self):
        self.open_database()
        setupSchema(self.db, 1, self.module)

    def tearDown(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        self.nuke_database()

    # nuke and re-create db for restore
    def nukeAndCreate(self):
        self.db.close()
        self.nuke_database()
        self.db = self.module.Database(config, 'admin')
        setupSchema(self.db, 0, self.module)


class memorydbDBTest(memorydbOpener, DBTest, unittest.TestCase):
    pass


class memorydbROTest(memorydbOpener, ROTest, unittest.TestCase):
    def setUp(self):
        self.db = self.module.Database(config)
        setupSchema(self.db, 0, self.module)


class memorydbSchemaTest(memorydbOpener, SchemaTest, unittest.TestCase):
    pass


from .session_common import SessionTest
class memorydbSessionTest(memorydbOpener, SessionTest, unittest.TestCase):
    s2b = lambda x,y: strings.s2b(y)

    def setUp(self):
        self.db = self.module.Database(config, 'admin')
        setupSchema(self.db, 1, self.module)
        self.sessions = self.db.sessions
        self.db.Session = self.sessions
        self.otks = self.db.otks
        self.db.Otk = self.otks

    def get_ts(self):
        return (self.sessions.get('random_session', '__timestamp'),)

    def testDbType(self):
        self.assertIn("memorydb", repr(self.db))
        self.assertIn("{}", repr(self.db.Session))

# vim: set filetype=python ts=4 sw=4 et si

