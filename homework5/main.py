import sqlalchemy
import os
import dotenv
from sqlalchemy.orm import sessionmaker
from models import create_tables, Book, Stock, Sale, Shop, Publisher
import json


def load_json_data(directory):
    with open('fixtures/tests_data.json', encoding='UTF-8', newline="") as f:  # открыли наш json файл
        json_data = json.load(f)  # сохранили все его данные в переменную

    return json_data


def add_json_data_in_table(session, data):
    for record in data:
        # print(record)
        # print(record.get('model'), [record.get('model')])
        model = {
            'publisher': Publisher,
            'shop': Shop,
            'book': Book,
            'stock': Stock,
            'sale': Sale,
        }[record.get('model')]
        # print(model)
        session.add(model(id=record.get('pk'), **record.get('fields')))
    session.commit()
    # for data in json_data:
    #     if data['model'] == 'publisher':
    #         # print(fixtures['fields']['name'])
    #         publisher = Publisher(id=data['pk'], name=data['fields']['name'])
    #         session.add(publisher)
    #     if data['model'] == 'book':
    #         # print(fixtures['fields']['name'])
    #         book = Book(id=data['pk'], title=data['fields']['title'], id_publisher=data['fields']['id_publisher'])
    #         session.add(book)
    #
    #     if data['model'] == 'shop':
    #         shop = Shop(id=data['pk'], name=data['fields']['name'])
    #         session.add(shop)
    #
    #     if data['model'] == 'stock':
    #         stock = Stock(id=data['pk'], id_book=data['fields']['id_book'], id_shop=data['fields']['id_shop'],
    #                       count=data['fields']['count'])
    #         session.add(stock)
    #
    #     if data['model'] == 'sale':
    #         sale = Sale(id=data['pk'], price=data['fields']['price'], date_sale=data['fields']['date_sale']
    #                     , id_stock=data['fields']['id_stock'], count=data['fields']['count'])
    #         session.add(sale)
    #     session.commit()


current = os.getcwd()
folder = 'fixtures'
file_name = 'test_data.json'
full_path = os.path.join(current, folder, file_name)

json_data = load_json_data(full_path)

dotenv.load_dotenv()

login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')
bd_name = os.getenv('BD_NAME')

DSN = f'postgresql://{login}:{password}@localhost:5432/{bd_name}'
engine = sqlalchemy.create_engine(DSN)

create_tables(engine)
Session = sessionmaker(bind=engine)

item_list = []

with Session() as session:
    add_json_data_in_table(session, json_data)

    publisher = input('Введите имя или индетификатор издателя: ')
    if publisher.isdigit():
        publisher_name = session.query(Publisher).filter(Publisher.id == publisher).all()
        if publisher_name == []:
            publisher_name = None
        else:
            publisher_name = publisher_name[0]

    # сначала создаём подзапрос, который мы будем использовать в нём мы находим все домашки с буквой "з"
    # subq = session.query(Stock).subquery()
    #print(subq)
    # теперь создаём сам запрос и запишем его в переменную для простоты
    # создаём запрос с той таблицей из которой нам нужен результат делаем join
    # передаём в этот join подзапрос и соединяем их по id
    # в данном случае subq.c.course_id - "с" в данном случае это обязательная переменная которую надо указывать
    # всегда
    #iterable = session.query(Sale).join(subq, Sale.id_stock == subq.c.id).all()
    #print(iterable)

    q = session.query(Sale, Stock).filter(Sale.id_stock == Stock.id).all()

    for i in q:
        print(i.id)

    #for c in iterable:
    #    print(c)

