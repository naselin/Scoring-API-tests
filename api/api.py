#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import logging
import hashlib
import uuid
import re
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import scoring
from store import Store

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class CommonField(object):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    def validate_value(self, value):
        if type(value) not in self.f_type:
            raise TypeError("Invalid type")
        if "pattern" in dir(self):
            if not re.match(self.pattern, str(value)):
                raise ValueError("Invalid format")
        return value


class CharField(CommonField):
    f_type = [str, unicode]


class ArgumentsField(CommonField):
    f_type = [dict]


class EmailField(CharField):
    pattern = r".+@.+\..+"


class PhoneField(CommonField):
    f_type = [str, unicode, int]
    pattern = r"^7\d{10}$"


class DateField(CommonField):
    def validate_value(self, value):
        try:
            datetime.datetime.strptime(value, "%d.%m.%Y")
        except Exception:
            raise ValueError("Invalid date")
        return value


class BirthDayField(DateField):
    def validate_value(self, value):
        super(BirthDayField, self).validate_value(value)
        birth_year = int(value[-4:])
        today = datetime.datetime.now()
        age_limit = 70
        if today.year - birth_year > age_limit:
            raise ValueError("Birthday is more than 70 years ago")
        return value


class GenderField(CommonField):
    def validate_value(self, value):
        if value not in GENDERS:
            err = "Gender %s, must be in %s" % (value, GENDERS)
            raise ValueError(err)
        return value


class ClientIDsField(CommonField):
    f_type = [list]

    def validate_value(self, value):
        err_values = []
        super(ClientIDsField, self).validate_value(value)
        for i in value:
            if type(i) is not int:
                err_values.append(i)
        if err_values:
            err = "ClientIDs %s are not digits" % err_values
            raise ValueError(err)
        return value


class CommonRequestMeta(type):
    def __new__(meta, name, bases, dct):
        data_fields = []
        for val in dct:
            if isinstance(dct[val], CommonField):
                data_fields.append(val)
        inst = super(CommonRequestMeta, meta).__new__(meta, name, bases, dct)
        inst.data_fields = data_fields
        return inst


class CommonRequest(object):
    __metaclass__ = CommonRequestMeta
    null_values = (None, "", [], (), {})

    def check_data(self, request):
        self.errors_list = []
        self.filled_fields = []
        for f in self.data_fields:
            field = getattr(self, f)
            value = None
            try:
                value = request[f]
            except Exception:
                if field.required:
                    self.errors_list.append("%s is required" % f)
            if not value and not field.nullable:
                self.errors_list.append("%s is empty" % f)
            try:
                setattr(self, f, value)
                if value not in self.null_values:
                    field.validate_value(value)
                    self.filled_fields.append(f)
            except Exception as e:
                self.errors_list.append("'%s' error: %s" % (f, e))
        if self.errors_list:
            err = ", ".join(self.errors_list)
            raise ValueError(err)


class ClientsInterestsRequest(CommonRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(CommonRequest):
    pairs = (
        ("phone", "email"),
        ("first_name", "last_name"),
        ("gender", "birthday")
    )
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def check_data(self, request):
        super(OnlineScoreRequest, self).check_data(request)
        pair_exists = False
        for p0, p1 in self.pairs:
            if p0 in self.filled_fields and p1 in self.filled_fields:
                pair_exists = True
        if not pair_exists:
            err = "No pairs %s found" % str(self.pairs)
            raise ValueError(err)


class MethodRequest(CommonRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") +
                                ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account +
                                request.login +
                                SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = None, None
    handlers = {
        "online_score": online_score_handler,
        "clients_interests": clients_interests_handler
    }
    try:
        method_request = MethodRequest()
        method_request.check_data(request["body"])
        if not check_auth(method_request):
            return "", FORBIDDEN
        response, code =\
            handlers[method_request.method](method_request, ctx, store)
    except Exception as e:
        logging.info("MethodRequest validation error: %s" % request)
        return str(e), INVALID_REQUEST
    return response, code


def online_score_handler(request, ctx, store):
    score_request = OnlineScoreRequest()
    score_request.check_data(request.arguments)
    if request.is_admin:
        score = 42
    else:
        scoring_args = {"store": store}
        for arg in score_request.filled_fields:
            if arg == "gender":
                scoring_args[arg] = GENDERS[request.arguments[arg]]
            elif arg == "birthday":
                scoring_args[arg] = datetime.datetime.strptime(
                    request.arguments[arg], "%d.%m.%Y")
            elif arg == "phone":
                scoring_args[arg] = str(request.arguments[arg])
            else:
                scoring_args[arg] = request.arguments[arg].encode("utf-8")
        score = scoring.get_score(**scoring_args)
    ctx["has"] = score_request.filled_fields
    return {"score": score}, OK


def clients_interests_handler(request, ctx, store):
    interests_request = ClientsInterestsRequest()
    interests_request.check_data(request.arguments)
    response = {}
    try:
        for cid in interests_request.client_ids:
          response[str(cid)] = scoring.get_interests(store=store, cid=cid)
    except Exception as e:
        return str(e), INTERNAL_ERROR
    num_clients = len(interests_request.client_ids)
    ctx["nclients"] = num_clients
    return response, OK


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store()

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" %
                         (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers},
                        context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(
                code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
