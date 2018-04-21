#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from scoring import get_interests, get_score
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

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

class EmptyFields(object):
    """проверка на пустое value"""
    empty_values = ([], {}, (), '', None)
    fields = []
    def check(self, name, value):
        if value in self.empty_values:
            self.fields.append(name)
            return True
        return False
    def clean(self):
        self.fields[:] = []

    @property
    def is_empty(self):
        if not self.fields:
            return True
        return False
        
class Field(object):
    """Класс предок для всех дескрипторов"""
    def __init__(self, required, nullable=True, name=''):
        super(Field, self).__init__()
        self.required = required
        self.nullable = nullable
        self.name = '_' + name

    def __set__(self, instance, value):
        if self.required:
            if value is None:
                raise ValueError(self.name)
                return
        if EmptyFields().check(self.name, value):
            if not self.nullable:
                raise ValueError(self.name)
                return
            setattr(instance, self.name, value)
        else:
            self.validate(instance, value)

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def validate(self, instance, value):
        pass
        
class CharField(Field):
    def validate(self, instance, value):
        if isinstance(value, (str, unicode)):
            setattr(instance, self.name, value)
        else:
            raise ValueError(self.name)
    
class ArgumentsField(Field):
    def validate(self, instance, value):
        if isinstance(value, dict):
            setattr(instance, self.name, value)
        else:
            raise ValueError(self.name)

class EmailField(CharField):
    def validate(self, instance, value):
        if value.count('@') == 1:
            setattr(instance, self.name, value)
        else:
            raise ValueError(self.name)

class PhoneField(Field):
    def validate(self, instance, value):
        value = str(value)
        if value.isdigit() and value[0] == '7' or len(value) == 11:
            setattr(instance, self.name, value)
        else:
            raise ValueError(self.name)

class DateField(Field):
    date_in_datetime = None
    def convert_to_datetime(self, value):
        try:
            self.date_in_datetime = datetime.datetime.strptime(value,"%m.%d.%Y")
        except Exception:
            raise ValueError(self.name)

    def validate(self, instance, value):
        self.convert_to_datetime(value)
        if self.date_in_datetime is not None:
            setattr(instance, self.name, self.date_in_datetime )

class BirthDayField(DateField):
    def validate(self, instance, value):
        self.convert_to_datetime(value)
        if self.date_in_datetime is not None:
            try:
                delta_in_year = int((datetime.datetime.now() - self.date_in_datetime).days/365.25)
            except Exception as e:
                logging.info(e)

            if delta_in_year < 70:
                setattr(instance, self.name, self.date_in_datetime)
            else:
                raise ValueError(self.name)

class GenderField(Field):
    def validate(self, instance, value):
        if isinstance(value,int) and value in (UNKNOWN,MALE,FEMALE):
            setattr(instance, self.name, value)
        else:
            raise ValueError(self.name)

class ClientIDsField(Field):
    def validate(self, instance, value):
        if isinstance(value, list):
            setattr(instance, self.name, value)
        else:
            raise ValueError(self.name)

class Request(type):
    """docstring for Request"""
    def __new__(meta, classname, supers, attrs):
        attrs['fields'] = []
        for attr_name, attr_value in attrs.items():
            if attr_name[0] != "_" and attr_name != "fields":
                attrs['fields'].append(attr_name)
        return type.__new__(meta, classname, supers, attrs)

def clients_interests_handler(arguments,admin=False):
    ci = ClientsInterestsRequest()
    for attr_name in ci.fields:
        try:
            value = arguments[attr_name]
        except KeyError:
            value = None
        try:
            setattr(ci, attr_name, value)
        except ValueError as error:
            return {"Not valid field": error.args[0][1:]}, INVALID_REQUEST
        except Exception as exception:
            logging.info(exception)
            return {"Invalid request"}, INVALID_REQUEST

    response = { ids: get_interests("", ids) for ids in ci.client_ids}
    return response, OK

def online_score_handler(arguments, admin):
    EmptyFields().clean()
    os = OnlineScoreRequest()
    for attr_name in os.fields:

        try:
            value = arguments[attr_name]
        except KeyError:
            value = None

        try:
            setattr(os, attr_name, value)
        except ValueError as error:
            #Не прошли валидацию
            return {"Not valid field": error.args[0][1:]}, INVALID_REQUEST
        except Exception as exception:
            logging.info(exception)
            return {"Invalid request"}, INVALID_REQUEST

    if ("first_name" not in EmptyFields().fields and "last_name" not in EmptyFields().fields) or ("email" not in EmptyFields().fields and "phone" not in EmptyFields().fields) or ("birthday" not in EmptyFields.fields and "gender" not in EmptyFields().fields):
        if admin:
            return {"score": 42}, OK
        else:
            return {"score": get_score("", os.phone,os.email, os.birthday, os.gender, os.first_name, os.last_name)}, OK
    else:
        response, code = {"Empty fields": EmptyFields().fields}, INVALID_REQUEST

class ClientsInterestsRequest(object):
    __metaclass__ = Request
    client_ids = ClientIDsField(required=True,name='client_ids')
    date = DateField(required=False, nullable=True,name='date')


class OnlineScoreRequest(object):
    __metaclass__ = Request
    first_name = CharField(required=False, nullable=True,name='first_name')
    last_name = CharField(required=False, nullable=True,name='last_name')
    email = EmailField(required=False, nullable=True,name='email')
    phone = PhoneField(required=False, nullable=True,name='phone')
    birthday = BirthDayField(required=False, nullable=True,name='birthday')
    gender = GenderField(required=False, nullable=True,name='gender')


class MethodRequest(object):
    account = CharField(required=False, nullable=True, name='account')
    login = CharField(required=True, nullable=True, name='login')
    token = CharField(required=True, nullable=True, name='token')
    arguments = ArgumentsField(required=True, nullable=True, name='arguments')
    method = CharField(required=True, nullable=False, name='method')

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, context, store):
    metod_router = {
        "online_score": online_score_handler,
        "clients_interests": clients_interests_handler
    }

    mr = MethodRequest()
    for attr_name in ('account', 'login', 'token', 'arguments', 'method'):

        try:
            value = request['body'][attr_name]
        except KeyError:
            value = None # Если нет такого ключа в request

        try:
            setattr(mr, attr_name, value)
        except ValueError as error:
            #Не прошли валидацию
            return {"Not valid field": error.args[0][1:]}, INVALID_REQUEST
        except Exception as exception:
            logging.info(exception)
            return {"Invalid request"}, INVALID_REQUEST

    if not check_auth(mr):
        response, code = "Forbidden", FORBIDDEN
        return response, code

    response, code = metod_router[mr.method](mr.arguments, mr.is_admin)
    return response, code

class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
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
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
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
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
