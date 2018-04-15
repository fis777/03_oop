import http.client
import json

connection = http.client.HTTPConnection('localhost:8080')

headers = {'Content-type': 'application/json'}

foo = {"account": "horns&hoofs", "login": "h&f","method": "online_score", "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3","arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Станислав","last_name": "Ступников", "birthday": "01.15.1990", "gender": 1}}
#foo = {}
json_foo = json.dumps(foo)

connection.request('POST', '/method', json_foo, headers)

response = connection.getresponse()
print(response.read().decode())