#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import logging
import api


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = None

    logging.basicConfig(filename="test.log", level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST , code)

    def test_type_field(self):
        self.assertEqual(isinstance(api.CharField(required=False, nullable=True), api.Field), True) 

    def test_Methodrequest(self):
        mr = api.MethodRequest()
        foo ={'body': {"account": "horns&hoofs", "login": "h&h","method": 35435, "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3","arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}}}
        setattr(mr, "login", foo["body"]["login"] )
        self.assertEqual(mr.login, 'h&h')

        foo ={'body': {"account": "horns&hoofs", "login": "","method": 35435, "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3","arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}}}
        setattr(mr, "login", foo["body"]["login"] )
        self.assertEqual(mr.login, '')

    def test_MethodHandler(self):

        foo ={'body': {"account": "horns&hoofs", "login": 123,"method": "online_score", "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95","arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}}}        
        response, code = api.method_handler(foo, "", "")
        self.assertEqual((response, code),({"Not valid field": "login"}, api.INVALID_REQUEST))

        foo ={'body': {"account": "horns&hoofs", "login": "h&h", "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3","arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}}}        
        response, code = api.method_handler(foo, "", "")
        self.assertEqual((response, code),({"Not valid field": "method"}, api.INVALID_REQUEST))

        foo ={'body': {"account": "horns&hoofs", "login": "h&h","method": "", "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95","arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}}}        
        response, code = api.method_handler(foo, "", "")
        self.assertEqual((response, code),({"Not valid field": "method"}, api.INVALID_REQUEST))

    def test_clients_interests_handler(self):
        foo = {"client_ids": [1,2,3,4], "date": "07.20.2017"}
        response, code = api.clients_interests_handler(foo)
        self.assertEqual(code, api.OK)

        foo = {"client_ids": (1,2,3), "date": "07.20.2017"}
        response, code = api.clients_interests_handler(foo)
        self.assertEqual(response, {"Not valid field": "client_ids"})
    
    def test_online_score_handler(self):
        foo = {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}
        response,code = api.online_score_handler(foo, True)
        self.assertEqual(response, {"score": 42})

        foo = {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}
        response,code = api.online_score_handler(foo, False)
        self.assertEqual(response, {"score": 5.0})

        foo = {"phone": "679175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}
        response,code = api.online_score_handler(foo, False)
        self.assertEqual((response, code), ({"Not valid field": "phone"}, api.INVALID_REQUEST))

        foo = {"phone": "", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}
        response,code = api.online_score_handler(foo, False)
        self.assertEqual(response, {"score": 3.5})

if __name__ == "__main__":
    unittest.main()
