# -*- coding: utf-8 -*-

import datetime
import pytest
import api

		
@pytest.fixture(params=["Станислав", "1234" ,"", pytest.param(123, marks=pytest.mark.xfail)])
def char_field_fix(request):
	return request.param

@pytest.fixture(params=["stupnikov@otus.ru", "", pytest.param("yandex.ru", marks=pytest.mark.xfail)])
def email_field_fix(request):
	return request.param

@pytest.fixture(params=["79175002040", "", pytest.param("879175002040", marks=pytest.mark.xfail)])
def phone_field_fix(request):
	return request.param

@pytest.fixture(params=["01.15.1990", pytest.param("01.32.1990", marks=pytest.mark.xfail)])
def birthday_field_fix(request):
	return request.param

@pytest.fixture(params=[0, 1, 2, pytest.param(3, marks=pytest.mark.xfail)])
def gender_field_fix(request):
	return request.param

@pytest.fixture(params=[{"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}, {}, pytest.param([], marks=pytest.mark.xfail)])
def arguments_field_fix(request):
	return request.param

@pytest.fixture(params=[[1,2,3,4], [], pytest.param((1,2,3,4), marks=pytest.mark.xfail)])
def client_ids_field_fix(request):
	return request.param

@pytest.fixture(params=["07.20.2017", pytest.param("13.20.2017", marks=pytest.mark.xfail)])
def date_ids_field_fix(request):
	return request.param

def test_char_field(char_field_fix):
	tf = api.OnlineScoreRequest()
	value = char_field_fix
	setattr(tf, "first_name", value)
	assert tf.first_name == value

def test_email_field(email_field_fix):
	tf = api.OnlineScoreRequest()
	value = email_field_fix
	setattr(tf, "email", value)
	assert tf.email == value

def test_phone_field(phone_field_fix):
	tf = api.OnlineScoreRequest()
	value = phone_field_fix
	setattr(tf, "phone", value)
	assert tf.phone == value

def test_birthday_field(birthday_field_fix):
	tf = api.OnlineScoreRequest()
	value = birthday_field_fix
	setattr(tf, "birthday", value)
	assert tf.birthday == datetime.datetime.strptime(birthday_field_fix,"%m.%d.%Y")

def test_gender_field(gender_field_fix):
	tf = api.OnlineScoreRequest()
	value = gender_field_fix
	setattr(tf, "gender", value)
	assert tf.gender == value

def test_arguments_field(arguments_field_fix):
	tf = api.MethodRequest()
	value = arguments_field_fix
	setattr(tf, "arguments", value)
	assert tf.arguments == value

def test_client_ids_field(client_ids_field_fix):
	tf = api.ClientsInterestsRequest()
	value = client_ids_field_fix
	setattr(tf, "client_ids", value)
	assert tf.client_ids == value

def test_date_field(date_ids_field_fix):
	tf = api.ClientsInterestsRequest()
	value = date_ids_field_fix
	setattr(tf, "date", value)
	assert tf.date == datetime.datetime.strptime(date_ids_field_fix,"%m.%d.%Y")

@pytest.fixture(params=[{"client_ids": [1,2], "date": "07.20.2017"}, pytest.param({"client_ids": (1,2), "date": "07.20.2017"}, marks=pytest.mark.xfail)])
def client_interests_handler_fix(request):
	return request.param

def test_client_interests_handler(client_interests_handler_fix):
	foo = client_interests_handler_fix
	response, code = api.clients_interests_handler(foo)
	assert code == api.OK

@pytest.fixture(params=[{"arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}, "response": {"score": 5.0}}, \
		{"arguments": {"phone": "", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}, "response": {"score": 3.5}}, \
	 	pytest.param({"arguments": {"phone": "979175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}, "response": {"score": 3.5}}, marks=pytest.mark.xfail)])
def online_score_handler_fix(request):
	return request.param

def online_score_handler(online_score_handler_fix):
	foo = online_score_handler_fix
	response, code = api.online_score_handler(foo["arguments"],False)
	assert (response, code) == (foo["response"], api.OK)

def test_MethodHandler():
	pass
