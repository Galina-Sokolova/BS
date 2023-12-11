import sqlite3 as sq

cursor = None
connection = None


async def db_start():
    global cursor, connection
    connection = sq.connect('resourсes/users.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE if not exists clients (
     "tel_number"    TEXT NOT NULL UNIQUE,
     "name"    TEXT NOT NULL,
     "master"    TEXT,
     FOREIGN KEY("master") REFERENCES "masters"("tel_number"),
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
    connection.commit()


async def create_client(client: dict) -> None:
    tel_number_client = client['tel']
    result = cursor.execute(f'Select * from clients where tel_number="{tel_number_client}"').fetchone()
    if not result:
        cursor.execute(f'Insert into clients(tel_number, name, master) values("{client["tel"]}","{client["name"]}","{client["master"]}")')
        connection.commit()


async def get_client(telephone_number) -> tuple:#возвращается кортеж номер телефона, фамилия имя клиента, имя фамилия мастера
    result = cursor.execute(f'Select * from clients where tel_number="{telephone_number}"').fetchone()#execute возвращает список кортежей, fetchone берет кортеж по номеру телефона
    return result


async def get_masters() -> tuple:
    result = cursor.execute(f'Select * from masters where status=1').fetchall() # execute - берем все строки из таблицы, fetchall - берем все записи из всех строк
    return result
