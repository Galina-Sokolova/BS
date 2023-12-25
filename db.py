import sqlite3 as sq

cursor = None
connection = None


async def db_start():
    '''
    Создание БД
    '''
    global cursor, connection
    connection = sq.connect('resourсes/users.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE if not exists clients (
         "tel_number"    TEXT NOT NULL UNIQUE,
         "name"    TEXT NOT NULL,
         PRIMARY KEY("tel_number")
    )  ''')
    cursor.execute('''CREATE TABLE if not exists masters (
        "tel_number"    TEXT NOT NULL UNIQUE,
        "name"    TEXT NOT NULL,
        "status"    INTEGER DEFAULT 1,
        "rate"    INTEGER DEFAULT 10,
        "image"    TEXT NOT NULL,
        PRIMARY KEY("tel_number")
    ) ''')
    cursor.execute('''CREATE TABLE if not exists masters_and_clients (
	    "master"	TEXT,
	    "client"	TEXT,
	    PRIMARY KEY("master","client"),
	    FOREIGN KEY("client") REFERENCES "clients"("tel_number"),
	    FOREIGN KEY("master") REFERENCES "masters"("tel_number") ON DELETE CASCADE
    ) ''')
    connection.commit()


async def create_client(client: dict) -> None:
    '''
    Создание новой записи в таблице clients
    '''
    tel_number_client = client['tel']
    result = cursor.execute(f'Select * from clients where tel_number="{tel_number_client}"').fetchone()
    if not result:
        cursor.execute(f'Insert into clients(tel_number, name) values("{client["tel"]}","{client["name"]}")')
        connection.commit()


async def get_client(
        telephone_number) -> tuple:  # возвращается кортеж номер телефона, фамилия имя клиента, имя фамилия мастера
    '''
    Получение данных о пользователе по номеру телефона
    '''
    result = cursor.execute(
        f'Select * from clients where tel_number="{telephone_number}"').fetchone()  # execute возвращает список кортежей, fetchone берет кортеж по номеру телефона
    return result


async def get_masters() -> tuple:
    '''
    Получение данных о всех мастерах
    '''
    result = cursor.execute(
        f'Select * from masters where status=1').fetchall()  # execute - берем все строки из таблицы, fetchall - берем все записи из всех строк
    return result


async def get_masters_by_client(client) -> tuple:  # получить по определенному клиенту всех мастеров которых он посещал
    '''
    Функция получения данных о мастерах к которым записан определенный клиент
    '''
    result = cursor.execute(
        f'''Select * from masters where tel_number in (Select master from masters_and_clients where client="{client}")''').fetchall()
    return result


async def connect_client_By_master_db(master, client):
    '''
    Функция добавления в таблицу masters_and_clients новой уникальной записи
    '''
    cursor.execute(
        f'Insert into masters_and_clients (master, client) values("{master}", "{client}")').fetchone()  # execute возвращает список кортежей, fetchone берет кортеж по номеру телефона
    connection.commit()


async def get_data_masters_and_clients(
        client) -> tuple:  # получить по определенному клиенту всех мастеров которых он посещал
    '''
        Функция получения данных о всех клиентах у всех мастеров
    '''
    result = cursor.execute(f'''Select * from masters_and_clients where client = "{client}"''').fetchall()
    return result
