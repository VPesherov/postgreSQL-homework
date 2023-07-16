import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE table if not exists email (
                email_id serial PRIMARY KEY,
                email_address varchar(100) unique NOT NULL
            );
        """)
        cur.execute("""
            create table IF NOT EXISTS phone(
            phone_id serial primary key,
            phone_number varchar(30) unique not null
        );
        """)
        conn.commit()

        cur.execute("""
            create table if not exists client_info(
            client_id serial primary key,
            first_name varchar(50) not null,
            second_name varchar(50) not null,
            email_id integer references email(email_id),
            phone_id integer references phone(phone_id) 
        );
        """)
        conn.commit()


# def create_user_name(conn, first_name, second_name):
#     with conn.cursor() as cur:
#         cur.execute("""
#                     INSERT INTO user_name(first_name, second_name) VALUES(%s, %s) RETURNING full_name_id, first_name, second_name;
#                     """, (first_name, second_name))
#         print(cur.fetchone())  # запрос данных автоматически зафиксирует изменения

def add_email_address(conn, email_address):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO email(email_address) VALUES(%s) RETURNING email_id;
                    """, (email_address,))
        return cur.fetchone()[0]


def add_phone_number(conn, phone_number):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO phone(phone_number) VALUES(%s) RETURNING phone_id;
                    """, (phone_number,))
        return cur.fetchone()[0]


def add_client(conn, first_name, second_name, email_address, phone_number=""):
    # create_user_name(conn, first_name=first_name, second_name=second_name)
    email_id = add_email_address(conn, email_address=email_address)
    phone_id = None
    if phone_number != "":
        phone_id = add_phone_number(conn, phone_number=phone_number)

    # print(email_id, phone_id)
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO client_info(first_name, second_name, email_id, phone_id) VALUES(%s, %s, %s, %s) RETURNING first_name, second_name, email_id, phone_id;
                    """, (first_name, second_name, email_id, phone_id))
        # conn.commit()
        print(cur.fetchone())


def delete_tables(conn):
    with conn.cursor() as cur:
        # удаление таблиц
        cur.execute("""
        DROP TABLE client_info;
        DROP TABLE phone;
        DROP TABLE email;
        """)


def add_phone_to_client(conn, client_id, phone_number):
    new_phone_id = add_phone_number(conn, phone_number=phone_number)
    client_info = get_client_info(conn, client_id=client_id)
    client_id_temp, first_name, second_name, email_id, phone_id = client_info
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO client_info(first_name, second_name, email_id, phone_id) VALUES(%s, %s, %s, %s) RETURNING first_name, second_name, email_id, phone_id;
                    """, (first_name, second_name, email_id, new_phone_id))
        print(cur.fetchone())


def get_client_info(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT * FROM client_info WHERE client_id=%s;
                    """, (client_id,))
        client_info = cur.fetchone()
    return client_info


def change_client(conn, client_id, first_name=None, second_name=None, email=None, phone_number=None):
    client_info = get_client_info(conn, client_id=client_id)
    client_id_temp, first_name_temp, second_name_temp, email_id_temp, phone_id_temp = client_info
    if email is None:
        email_id = email_id_temp
    else:
        email_id = add_email_address(conn, email_address=email)
    if phone_number is None:
        phone_id = phone_id_temp
    else:
        phone_id = add_phone_number(conn, phone_number=phone_number)

    with conn.cursor() as cur:
        cur.execute("""
                UPDATE client_info SET first_name=coalesce(%s, %s), second_name=coalesce(%s, %s), email_id=coalesce(%s, %s)
                , phone_id=coalesce(%s, %s) WHERE client_id=%s
                RETURNING first_name,  second_name, email_id, phone_id,client_id;
                """, (first_name, first_name_temp, second_name, second_name_temp, email_id, email_id_temp
                                          , phone_id, phone_id_temp, client_id))
        print(cur.fetchone())  # запрос данных автоматически зафиксирует изменения


def delete_phone(conn, cliend_id, phone_number):
    with conn.cursor() as cur:
        cur.execute("""
            select phone_id from phone where phone_number = %s
        """, (phone_number,))
        phone_id = cur.fetchone()[0]

        cur.execute("""
        DELETE FROM client_info WHERE phone_id=%s and client_id=%s;
        """, (phone_id, cliend_id))
        conn.commit()


def delete_client(conn, cliend_id):
    with conn.cursor() as cur:
        cur.execute("""
                DELETE FROM client_info WHERE client_id=%s;
                """, (cliend_id,))
        conn.commit()


def all_clients_info(conn):
    with conn.cursor() as cur:
        cur.execute("""
            select * from client_info
        """)
        print(cur.fetchall())


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):

    with conn.cursor() as cur:
        cur.execute("""
                        select * from client_info as tbl
                        left join phone as src1 on src1.phone_id = tbl.phone_id
                        left join email as src2 on src2.email_id = tbl.email_id
                        where first_name=%s or second_name=%s or src2.email_address=%s or src1.phone_number=%s;
                        """, (first_name, last_name, email, phone))
        print(cur.fetchall()[0])


def main():
    with psycopg2.connect(database="client_control", user="postgres", password="123") as conn:
        print('Удаляем старые таблицы')
        delete_tables(conn)
        print('Создаём таблицы')
        create_db(conn)
        print('Добавляем клиентов')
        add_client(conn, first_name='Ivan', second_name='Ivanov', email_address='ivanivanov@ngs.ru',
                   phone_number='799999999')
        # add_client(conn, first_name='Ivan', second_name='Ivanov', email_address='ivanivanov1@ngs.ru', phone_number='799999998')
        add_client(conn, first_name='Petr', second_name='Petrov', email_address='petrpetrov@yandex.ru',
                   phone_number='76666666')
        add_client(conn, first_name='Without', second_name='Number', email_address='without@yandex.ru', phone_number="")
        print('Добавили номер телефона клиенту')
        add_phone_to_client(conn, 1, phone_number='799888888')
        print('Изменяем клиента')
        change_client(conn=conn, client_id=1, first_name='Kirill')
        change_client(conn=conn, client_id=1, phone_number='799923251')
        print('Удаляем телефон')
        delete_phone(conn, 1, '799923251')
        print('Проверяем что телефон удалился')
        all_clients_info(conn)
        print('Удаляем клиента')
        delete_client(conn, 2)
        print('Проверяем что клиент удалился')
        all_clients_info(conn)
        print('Ищем клиента')
        find_client(conn, first_name='Without')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
