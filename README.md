# REST API на Python 2.7 с использованием Python+SQLAlchemy+Flask

## Для Python нужно установить:
```
pip install flask
pip install flask-sqlalchemy
```

При запуске **restapi.py**, программа ищет файл **DataBase.sqlite** в том же каталоге. Если базы данных нет, автоматически создается новая пустая sqlite-БД по модели:

```python
class Article(data_base.Model):
    id = data_base.Column(data_base.Integer, primary_key=True)
    author = data_base.Column(data_base.String(200))
    created = data_base.Column(data_base.String(100))
    updated = data_base.Column(data_base.String(100))
    content = data_base.Column(data_base.Text)
```

В репозитории уже есть база данных, в которую добавлена 1 статья с автором **Pushkin A.S.**
