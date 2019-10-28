# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import os
import time


app = Flask(__name__) 

# База данных
cur_dir = os.path.abspath(os.path.dirname(__file__)) #получаем текущий каталог в котором лежит запускаемый .py-файл
db_file_path = os.path.join(cur_dir, 'DataBase.sqlite') #путь к sqlite-файлу базы данных

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_base = SQLAlchemy(app)


class Article(data_base.Model): # Модель записи в базе данных
    id = data_base.Column(data_base.Integer, primary_key=True)
    author = data_base.Column(data_base.String(200))
    created = data_base.Column(data_base.String(100))
    updated = data_base.Column(data_base.String(100))
    content = data_base.Column(data_base.Text)
    
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.created = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.updated = time.strftime("%Y-%m-%dT%H:%M:%S")




if not os.path.exists(db_file_path): # Если файл sqlite-базы данных не существует, создать его
    print('creating database file...')
    data_base.create_all() #если файла sqlite-базы не существует, создаем его по модели класса Article


def get_article_dict(article_object): # получить словарь из SQL-объекта Article 
    article_dict = article_object.__dict__
    if '_sa_instance_state' in article_dict:
        del article_dict['_sa_instance_state'] #удалить служебный элемент из словаря объекта
    return article_dict

# Добавить статью в БД
@app.route('/api/articles', methods = ['POST'])
def add_article():
    try:
        author = request.json['author']
        content = request.json['content']
        
        new_article = Article(author, content)
    except Exception as e:
        return jsonify({'message' : 'wrong input, cant create new article'}), 400

    
    try:    
        data_base.session.add(new_article)
        data_base.session.commit()
        data_base.session.refresh(new_article) # Чтобы получить(синхронизировать) id и другие значения добавленного в Д объекта
    except exc.SQLAlchemyError:
        return jsonify({'message' : 'SQL error: cant create new articles'}), 404
    
    return jsonify(get_article_dict(new_article))
    
    
# Получить все статьи в БД
@app.route('/api/articles', methods = ['GET'])
def get_all_articles():
    try:
        all_articles = Article.query.all() # получение списка объектов Article из БД
    except exc.SQLAlchemyError:
        return jsonify({'message' : 'SQL error: cant get all articles'}), 404
    

    json_list = []
    for row in all_articles: # создать список словарей из запроса БД  
        json_list.append(get_article_dict(row))
    json_articles = {}
    json_articles['objects'] = json_list
    
    return jsonify(json_articles)


# Получить статью по id
@app.route('/api/articles/<id>', methods = ['GET'])
def get_id_article(id): 
    try:
        cur_article = Article.query.get(id) # получение статьи с указанным id
    except exc.SQLAlchemyError:
        return jsonify({'message' : 'SQL error at getting article ' + id}), 404
    
    if cur_article is None: # Если статья с таким id существует
        return jsonify({'message' : 'article ' + id + ' not found'}), 404
    article_json = get_article_dict(cur_article)
    
    return jsonify(article_json)

# Изменить статью по id
@app.route('/api/articles/<id>', methods = ['PUT', 'PATCH'])
def patch_id_article(id): 
    try:
        cur_article = Article.query.get(id) # получение статьи с указанным id
    except exc.SQLAlchemyError:
        return jsonify({'message' : 'SQL error at getting article ' + id}), 404

    if cur_article is None: # Если статья с таким id существует
        return jsonify({'message' : 'article ' + id + ' not found'}), 404
    
    #частичное изменение сущностей
    author = None
    content = None
    
    try:
        if 'author' in request.json:
            author = request.json['author']
        if 'content' in request.json:
            content = request.json['content']        
        updated = time.strftime("%Y-%m-%dT%H:%M:%S")
                
    except Exception as e:
        return jsonify({'message' : 'wrong input, cant update article ' + id}), 404
    
    if author != None: 
        cur_article.author = author
    if content != None:  
        cur_article.content = content
    cur_article.updated = updated
    #частичное изменение сущностей
    
    data_base.session.commit()
    data_base.session.refresh(cur_article)
    
    article_json = get_article_dict(cur_article)
    
    return jsonify(article_json)

# Удалить статью из БД 
@app.route('/api/articles/<id>', methods = ['DELETE'])
def delete_id_article(id): 
    try:
        cur_article = Article.query.get(id) # получение статьи с указанным id
    except exc.SQLAlchemyError:
        return jsonify({'message' : 'SQL error at getting article ' + id}), 404
    
    if cur_article is None: # Если статья с таким id существует
        return jsonify({'message' : 'article ' + id + ' not found'}), 404

    try:
        data_base.session.delete(cur_article)
        data_base.session.commit()
    except exc.SQLAlchemyError:
        return jsonify({'message' : 'SQL error at deleting article ' + id}), 404    

    
    return jsonify({'message' : 'ok'}) # Удачно удалено


if __name__ == '__main__':
    app.run()
