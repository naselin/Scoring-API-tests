# Scoring API
____
Cистема валидации запросов к HTTP API сервиса скоринга.
Обрабатывает POST-запросы в формате JSON по заданным шаблонам.

## Конфигурация.
При запуске может считывать параметры из командной строки:
```
-h, --help  вывод "help"-сообщения.
-p PORT, --port=PORT  Номер TCP-порта для отправки запроса. Значение по умолчанию: 8080.
-l LOG, --log=LOG  Путь к файлу для логгирования. Значение по умолчанию: None (вывод в консоль).
```

## Подключение хранилища.
```
$ pip2 install tarantool\>0.4
$ cd api
$ docker run \
--name store \
-d -p 33013:33013 \
-v $PWD/tt:/var/lib/tarantool \
tarantool/tarantool:2
$ docker exec -i -t store tarantool /var/lib/tarantool/store.lua
```

## Запуск.
```
$ python2 api.py [options]
```

## Тестирование.
```
$ python2 -m unittest discover tests/
```
