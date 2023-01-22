# Описание структуры JSON-файлов бота.

## Файлы конфигурации логгеров.

В данном файле продемонстрирована структура всех основных **JSON**-файлов бота, хранящихся в директории *"data/logger_configs"*,
а также отображены и пояснены все их основные параметры.

> **ВАЖНО!** Желательно во избежание лишних проблем не редактировать данные файлы, а оставить их в
  неизменном виде.


```json
{
    "config": {
        "handlers": [
            {
                "sink": "Logs/LogBuilder.log",
                "format": "[TIME: {time:YYYY-MM-DD at HH:mm:ss}] {level} | {message}",
                "level": "DEBUG",
                "serialize": false
            }
        ],
        "extra": {"object": "LogBuilder"}
    }
}
```
**ИЛИ**
```json
{
    "configs": {
        "handler": {
            "handlers": [
                {
                    "sink": "logs/handlers.log",
                    "format": "[TIME: {time:YYYY-MM-DD at HH:mm:ss}] {level} | {message}",
                    "level": "DEBUG",
                    "serialize": false
                }
            ],
            "extra": {"object": "Handler"}
        },
        "main_handler": {
            "handlers": [
                {
                    "sink": "logs/handlers.log",
                    "format": "[TIME: {time:YYYY-MM-DD at HH:mm:ss}] MAIN HANDLER | {level} | {message}",
                    "level": "DEBUG",
                    "serialize": false
                }
            ],
            "extra": {"object": "MainHandler"}
        }
    }  
}
```

**Объяснение параметров файла:**
- *"config" (или "configs", в зависимости от файла)* – основной блок, в котором хранятся конфигурации логгеров.
  - "(имя_логгера)" – в файлах с несколькими логгерами (*второй код*) конфигурация хранится именно в таком блоке. В файлах с одним
    логгером такой блок отсутствует.
    - *"handlers"* – данный блок содержит в себе основные пункты конфигурации логгера.
      - *"sink"* – путь к будущему файлу, в который будет вестись запись.<br><br>
      - *"format"* – строка, определяющая форматирование вывода.<br><br>
      - *"level"* – строка, обозначающая уровень логирования.<br><br>
      - *"serialize"* – если **true**, то логирование будет вестись в сериализованном формате, похожем на **JSON**.<br><br>
  - *"extra"* – дополнительная информация о логгере в **JSON**-формате.