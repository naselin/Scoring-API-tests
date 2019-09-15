#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from api import api
from tests.cases import cases


class TestMethodRequest(unittest.TestCase):
    @cases([
        {},
        {"token": "qwerty", "arguments": {}, "method": "online_score"},
        {"login": "h&f", "arguments": {}, "method": "online_score"},
        {"login": "h&f", "token": "qwerty", "method": "online_score"},
        {"login": "h&f", "token": "qwerty", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f", "token": "qwerty", "arguments": {}, "method": ""},
        {"account": "horns&hoofs", "login": "h&f", "token": 12, "arguments": {}, "method": "online_score"}
    ])
    def test_method_invalid_values(self, request):
        req = api.MethodRequest()
        self.assertRaises(
            ValueError, req.check_data, request)

    @cases([
        {"login": "h&f", "token": "qwerty", "arguments": {}, "method": "online_score"},
        {"account": "horns&hoofs", "login": "", "token": "qwerty", "arguments": {"phone": 79991234567}, "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "token": "", "arguments": {}, "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "token": "qwerty", "arguments": {"phone": 79991234567}, "method": "online_score"},
        {"account": "horns&hoofs", "login": "admin", "token": "qwerty", "arguments": {"phone": 79991234567}, "method": "clients_interests"}
    ])
    def test_method_valid_values(self, request):
        req = api.MethodRequest()
        req.check_data(request)
        for key in request:
            self.assertEqual(request[key], getattr(req, key))


class TestClientsInterestsRequest(unittest.TestCase):
    @cases([
        {},
        {"date": "20.07.2017"},
        {"client_ids": 1, "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"}
    ])
    def test_interests_invalid_values(self, arguments):
        self.assertRaises(
            TypeError, api.ClientsInterestsRequest.check_data, arguments)

    @cases([
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]}
    ])
    def test_interests_valid_values(self, arguments):
        req = api.ClientsInterestsRequest()
        req.check_data(arguments)
        for key in arguments:
            self.assertEqual(arguments[key], getattr(req, key))


class TestOnlineScoreRequest(unittest.TestCase):
    @cases([
        {},
        {"phone": "79991234567"},
        {"phone": "+79991234567", "email": "user@domain.ru"},
        {"phone": "79991234567", "email": "userdomainru"},
        {"phone": "79991234567", "email": "user@domain.ru", "first_name": ["Василий"]},
        {"phone": "79991234567", "email": "user@domain.ru", "first_name": "Василий", "last_name": -1},
        {"phone": "79991234567", "email": "user@domain.ru", "first_name": "Василий", "last_name": "Алибабаевич", "gender": 99},
        {"phone": "79991234567", "email": "user@domain.ru", "first_name": "Василий", "last_name": "Алибабаевич", "gender": 1, "birthday": "XXX"},
        {"phone": "79991234567", "email": "user@domain.ru", "first_name": "Василий", "last_name": "Алибабаевич", "gender": 1, "birthday": "01.01.1900"}
    ])
    def test_score_invalid_values(self, arguments):
        def test_interests_invalid_values(self, arguments):
            self.assertRaises(
                TypeError, api.OnlineScoreRequest.check_data, arguments)

    @cases([
        {"phone": "79991234567", "email": "user@domain.ru"},
        {"first_name": "Василий", "last_name": "Алибабаевич"},
        {"gender": 1, "birthday": "01.01.1970"},
        {"phone": "79991234567", "email": "user@domain.ru", "first_name": "Василий", "last_name": "Алибабаевич", "gender": 1, "birthday": "01.01.1970"}
    ])
    def test_score_valid_values(self, arguments):
        req = api.OnlineScoreRequest()
        req.check_data(arguments)
        for key in arguments:
            self.assertEqual(arguments[key], getattr(req, key))


if __name__ == "__main__":
    unittest.main()
