#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from tarantool import DatabaseError

from api import scoring
from tests.cases import cases


class MockedStore:
    connected = True

    def __init__(self):
        self.items = {
            "i:1": '["travel", "books"]',
            "i:2": '["cars", "pets"]'
        }

    def get(self, *args):
        key = args[0]
        if not self.connected or key not in self.items:
            raise DatabaseError
        return self.items.get(key)

    def cache_get(self, *args):
        key = args[0]
        if not self.connected or key not in self.items:
            return None
        return self.items.get(key)

    def cache_set(self, key, value, timeout=3600):
        if not self.connected or key not in self.items:
            return None
        self.items.update({key: value})
        return self

    def disconnect(self):
        self.connected = False
        return self


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.store = MockedStore()

    def tearDown(self):
        pass

    @cases([-1, "qwerty", None])
    def test_interests_get_nonexistent_cid(self, args):
        self.assertRaises(DatabaseError,
                          scoring.get_interests,
                          self.store, args)

    @cases([1, 2])
    def test_interests_get_existent_cid(self, args):
        ethalon = {
            1: [u'travel', u'books'],
            2: [u'cars', u'pets']
        }
        interests = scoring.get_interests(self.store, args)
        self.assertEqual(ethalon[args], interests)

    @cases([1, 2])
    def test_interests_disconnected_store(self, args):
        self.store.disconnect()
        self.assertRaises(DatabaseError,
                          scoring.get_interests,
                          self.store, args)

    @cases([
        {"phone": "79991234567", "email": "user@domain.com", "gender": 1, "first_name": "Vasiliy", "last_name": "Ivanov"}
    ])
    def test_score_get_connected_store(self, args):
        args.update({"store": self.store})
        score = scoring.get_score(**args)
        self.assertEqual(score, 3.5)

    @cases([
        {"phone": "79991234567", "email": "user@domain.com", "gender": 1, "first_name": "Vasiliy", "last_name": "Ivanov"}
    ])
    def test_score_get_disconnected_store(self, args):
        self.store.disconnect()
        args.update({"store": self.store})
        score = scoring.get_score(**args)
        self.assertEqual(score, 3.5)


if __name__ == "__main__":
    unittest.main()
