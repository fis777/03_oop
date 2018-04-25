# -*- coding: utf-8 -*-

import pytest
import api


@pytest.fixture(params=["Станислав", "1234" ,""])
def char_test_fix(request):
	return request.param

class TestFieldClass():
	test_char_field = api.CharField(required=False, nullable=True, name='account')

def test_char_field(char_test_fix):
	tf = api.OnlineScoreRequest()
	value = char_test_fix
	print(type(value))
	setattr(tf, "first_name", value)
	print(tf.first_name)
	assert tf.first_name == value

	