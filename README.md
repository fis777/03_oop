Система валидации запросов к HTTP API сервиса скоринга.  
Код разработан под версию Python 2.7  
Для включения логирования нужно указать в командной строке параметр `--log имя лог файла`   Для проверки работы системы в целом запустить web сервер для обработки HTTP запросов командй `python api.py --log api.log` и в другом shell запустить `python client.py`  
Запуск тестов выполняется с остановленым web сервером командой `python -m unittest test.TestSuite`