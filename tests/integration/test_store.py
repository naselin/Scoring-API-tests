#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from tarantool import DatabaseError

from api import store
from tests.cases import cases


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = store.Store()
        if "test_cache_get" in self._testMethodName:
            self.score = 5.0
            self.store.cache_set("uid:permanent_uid", self.score, 3600)

    def tearDown(self):
        if "test_cache_get" in self._testMethodName:
            self.store.cache_delete("permanent_uid")

    @cases(["i:-1", "i:qwerty", "i:None"])
    def test_get_nonexistent_cid(self, args):
        self.assertRaises(DatabaseError, self.store.get, args)

    @cases(["i: 1"])
    def test_get_existent_cid(self, args):
        interests = self.store.get(args)
        self.assertEqual(interests, '["travel", "books"]')

    @cases(["uid: -1"])
    def test_cache_get_nonexistent_uid(self, args):
        score = self.store.cache_get(args)
        self.assertIsNone(score)

    @cases(["uid:permanent_uid"])
    def test_cache_get_permanent_uid(self, args):
        score = self.store.cache_get(args)
        self.assertEqual(score, self.score)

    @cases(["i: 1"])
    def test_get_disconnected_store(self, args):
        self.store.disconnect()
        self.assertRaises(DatabaseError, self.store.get, args)

    @cases(["uid:permanent_uid"])
    def test_cache_get_disconnected_store(self, args):
        self.store.disconnect()
        score = self.store.cache_get(args)
        self.assertIsNone(score)


if __name__ == "__main__":
    unittest.main()
