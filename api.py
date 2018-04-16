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
        pass
    @property
    def is_empty(self):
        if not self.fields:
            return True
        return False
        

class ErrorFields(object):
    """класс обработчик ошибок валидации"""
    errors = []
    def add(self,error_field):
        self.errors.append(error_field[1:])

    def clean(self):
        self.errors[:] = []

    @property    
    def is_error(self):
        if self.errors:
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
                ErrorFields().add(self.name)
                return
        if EmptyFields().check(self.name, value):
            if not self.nullable:
                ErrorFields().add(self.name)
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
            ErrorFields().add(self.name)
    
class ArgumentsField(Field):
    def validate(self, instance, value):
        if isinstance(value, dict):
            setattr(instance, self.name, value)
        else:
            ErrorFields().add(self.name)

class EmailField(CharField):
    def validate(self, instance, value):
        if value.count('@') == 1:
            setattr(instance, self.name, value)
        else:
            ErrorFields().add(self.name)

class PhoneField(Field):
    def validate(self, instance, value):
        value = str(value)
        if value.isdigit() and value[0] == '7' or len(value) == 11:
            setattr(instance, self.name, value)
        else:
            ErrorFields().add(self.name)

class DateField(Field):
    def validate(self, instance, value):
        try:
            date_field = datetime.datetime.strptime(value,"%d.%m.%Y")
        except:
            ErrorFields().add(self.name)
        else:
            setattr(instance, self.name, date_field)

class BirthDayField(DateField):
    def validate(self, instance, value):
        super(BirthDayField, self).__set__(instance, value)
        if DateField().date_field is not None:
            delta = int((datetime.datetime.now() - DateField().date_field).days/365.25)
            if delta > 70:
                setattr(instance, self.name, DateField().date_field)
            else:
                ErrorFields().add(self.name)


class GenderField(Field):
    def validate(self, instance, value):
        if isinstance(value,int) and value in (UNKNOWN,MALE,FEMALE):
            setattr(instance, self.name, value)
        else:
            ErrorFields().add(self.name)

class ClientIDsField(Field):
    def validate(self, instance, value):
        if isinstance(value, list):
            setattr(instance, self.name, value)
        else:
            ErrorFields().add(self.name)

class Request(type):
    """docstring for Request"""
    def __new__(meta, classname, supers, attrs):
        attrs['fields'] = []
        for attr_name, attr_value in attrs.items():
            if attr_name[0] != "_" and attr_name != "fields":
                attrs['fields'].append(attr_name)
        return type.__new__(meta, classname, supers, attrs)

def clients_interests_handler(arguments,admin=False):
    ErrorFields().clean()
    ci = ClientsInterestsRequest()
    for attr_name in ci.fields:
        try:
            setattr(ci, attr_name, arguments[attr_name])
        except:
            setattr(ci, attr_name, None)

    if ErrorFields().is_error:
        response, code = {"Not valid fields": ErrorFields().errors}, INVALID_REQUEST
        return response, code

    response = { ids: get_interests("", ids) for ids in ci.client_ids  }    
    return response, OK

def online_score_handler(arguments, admin):
    ErrorFields().clean()
    EmptyFields().clean()
    os = OnlineScoreRequest()
    for attr_name in os.fields:
        try:
            if not EmptyFields().check(arguments[attr_name]):
                setattr(os, attr_name, arguments[attr_name])
        except:
            setattr(os, attr_name, None)

    if ErrorFields().is_error:
        response, code = {"Not valid fields": ErrorFields().errors}, INVALID_REQUEST
        return response, code
    
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


def method_handler(request, ctx, store):
    ErrorFields().clean()
    
    metod_router = {
        "online_score": online_score_handler,
        "clients_interests": clients_interests_handler
    }

    mr = MethodRequest()
    for attr in ('account','login','token','arguments','method'):
        try:
            setattr(mr, attr, request['body'][attr])
        except:
            setattr(mr, attr, None)
        
    if ErrorFields().is_error:
        response, code = {"Not valid fields": ErrorFields().errors}, INVALID_REQUEST
        return response, code

    if not check_auth(mr):
        response, code = "Forbidden", FORBIDDEN
        return response, code

    response, code = metod_router[mr.method](mr.arguments, mr.is_admin)

    response, code = {}, OK
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
                except Exception, e:
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
