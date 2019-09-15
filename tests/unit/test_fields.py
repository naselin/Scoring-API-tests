#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from api import api
from tests.cases import cases


class TestCharField(unittest.TestCase):
    @cases([None, 0, 1.2, [3], {"a": "b"}])
    def test_char_invalid_type(self, value):
        self.assertRaises(TypeError, api.CharField(
            required=True, nullable=False).validate_value, value)

    @cases(["", "Vasiliy", "Василий", u"彭德怀", "a" + "b"])
    def test_char_valid_value(self, value):
        checked_value = api.CharField(
            required=True, nullable=True).validate_value(value)
        self.assertIs(checked_value, value)


class TestArgumentsField(unittest.TestCase):
    @cases([None, 0, 1.2, [3], "qwerty"])
    def test_arguments_invalid_type(self, value):
        self.assertRaises(TypeError, api.ArgumentsField(
            required=True, nullable=False).validate_value, value)

    @cases([{"a": "b"}, {}])
    def test_arguments_valid_value(self, value):
        checked_value = api.ArgumentsField(
            required=True, nullable=True).validate_value(value)
        self.assertIs(checked_value, value)


class TestEmailField(unittest.TestCase):
    @cases(["user@", "@domain.com", "qwerty"])
    def test_email_invalid_value(self, value):
        self.assertRaises(ValueError, api.EmailField(
            required=True, nullable=False).validate_value, value)

    @cases(["user@domain.com", "another.user@another.domain.com"])
    def test_email_valid_value(self, value):
        checked_value = api.EmailField(
            required=True, nullable=True).validate_value(value)
        self.assertIs(checked_value, value)


class TestPhoneField(unittest.TestCase):
    @cases([None, 0.1, [2], {"a": "b"}])
    def test_phone_invalid_type(self, value):
        self.assertRaises(TypeError, api.PhoneField(
            required=True, nullable=False).validate_value, value)

    @cases(["89991234567", u"7999123456", 7999123456])
    def test_phone_invalid_value(self, value):
        self.assertRaises(ValueError, api.PhoneField(
            required=True, nullable=False).validate_value, value)

    @cases(["79991234567", u"79991234567", 79991234567])
    def test_phone_valid_value(self, value):
        checked_value = api.PhoneField(
            required=True, nullable=False).validate_value(value)
        self.assertIs(checked_value, value)


class TestDateField(unittest.TestCase):
    @cases([None, 10102019, ["10.10.2019"], "2019.10.10"])
    def test_date_invalid_value(self, value):
        self.assertRaises(ValueError, api.DateField(
            required=True, nullable=False).validate_value, value)

    @cases(["10.10.2019", "1.1.1900"])
    def test_date_valid_value(self, value):
        checked_value = api.DateField(
            required=True, nullable=True).validate_value(value)
        self.assertIs(checked_value, value)


class TestBirthDayField(unittest.TestCase):
    @cases(["10.10.1900"])
    def test_birthday_invalid_value(self, value):
        self.assertRaises(ValueError, api.BirthDayField(
            required=True, nullable=False).validate_value, value)

    @cases(["1.1.1970"])
    def test_birthday_valid_value(self, value):
        checked_value = api.BirthDayField(
            required=True, nullable=True).validate_value(value)
        self.assertIs(checked_value, value)


class TestGenderField(unittest.TestCase):
    @cases([None, -1, "0", 1.2, 3, "a"])
    def test_gender_invalid_value(self, value):
        self.assertRaises(ValueError, api.GenderField(
            required=True, nullable=False).validate_value, value)

    @cases([0, 1, 2])
    def test_gender_valid_value(self, value):
        checked_value = api.GenderField(
            required=True, nullable=True).validate_value(value)
        self.assertIs(checked_value, value)


class TestClientIDsField(unittest.TestCase):
    @cases([None, 0, 1.2, {3: 4}, "a"])
    def test_clientids_invalid_type(self, value):
        self.assertRaises(TypeError, api.ClientIDsField(
            required=True, nullable=False).validate_value, value)

    @cases([[0, {1: 2}], [3, 4.5], [6, "a"]])
    def test_clientids_invalid_value(self, value):
        self.assertRaises(ValueError, api.ClientIDsField(
            required=True, nullable=False).validate_value, value)

    @cases([[0], [1, 2]])
    def test_clientids_valid_value(self, value):
        checked_value = api.ClientIDsField(
            required=True, nullable=False).validate_value(value)
        self.assertIs(checked_value, value)


if __name__ == "__main__":
    unittest.main()
