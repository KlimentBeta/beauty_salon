# Салон красоты — умное приложение для современного салона красоты

Цифровое решение, созданное для автоматизации повседневных процессов в салонах красоты: от онлайн-записи клиентов и управления расписанием мастеров до учёта услуг, продуктов и лояльности.

### Установка

Для установки проекта на Linux требуется использовать следующие команды:

```
git clone https://github.com/KlimentBeta/beauty_salon
```

```
cd beauty_salon
```

```
python3 -m venv venv
```

```
source ./venv/bin/activate
```

```
pip install -r requirements.txt
```

Затем используйте дамп  MYSQL БД, предварительно создав БД и заполнив данные в config.py

```
cd ./utils/data/
```

```
mysql -u USERNAME -p DB_NAME < my.sql
```

Следующим шагом запустите скрипт по настройке БД также из utils/data/

```
python3 db_script.py
```

БД успешно настроена и в корне проекта теперь можно запускать

```
python3 main.py
```

## Авторы

* **Evgeniy Light** - *Initial work* - [Kliment_beta](https://github.com/KlimentBeta)
