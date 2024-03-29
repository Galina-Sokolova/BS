# **Тема проекта**: Создание телеграм-бота для студии ногтевого сервиса. 
## **Цель**: Создать бота помощника для студии ногтевого сервиса в мессенджере Telegram.  

### **Задачи**:   

1. Изучить литературу, касающуюся темы исследования;    

2. Проанализировать выбранную предметную область; 

3. Изучить технологии и среды разработки для создания чат-ботов; 

4. Выбрать технологию и среду разработки;

5.  Разработать чат-бот на платформе Telegram. 

### **Инструменты**: PyCharm, Python, SQLite, Git, Google Sheets   

### **Структура дипломного проекта**:   

_Содержание_  

_Введение_ 

**Глава 1. Обзор предметной области**  

1.1 Telegram  

1.2 Telegram Bot API  

**Глава 2. Выбор технологий и среды разработки**  

2.1   Язык программирования Python  

2.1.1 Библиотека Aiogramm  

2.2   Google таблицы  

2.3.1 Понятие базы данных и системы управления базами данных

2.3.2   СУБД SQLite  

2.4 Среда разработки PyCharm  

**Глава 3. Создание и настройка проекта** 

3.1 Создание структуры проекта  

**Глава 4. Реализация чат-бота**

4.1 Регистрация бота   

4.2 Подключаем библиотеки 

4.3 Организация старта бота

4.4 Первый тестовый запуск бота

4.5 Описание функционала бота

4.6 Создание БД

4.7 Подключение к Google Sheets

4.8 Работа с данными в Google Sheets

4.9 Реализация основного функционала бота - запись на прием

4.10 Конечный автомат, регистрация пользователя

4.11 Отмена записи

_Заключение_ 

_Список используемой литературы_ 

- Telegram-бот доступен по адресу: https://t.me/PtichkaBeauty_bot 

## Запуск проекта

- клонировать репозиторий

```bash
git clone https://github.com/Galina-Sokolova/BS.git
```
- в папке BS создать файл config.py
- в файле config.pyпрописать константу TOKEN_BOT='token', вместо token вставить токен своего телеграм-бота
- прописать константу ID_SPREADSHEET='id google sheet', вместо id google sheet вставить id  своей гугл таблицы
- необходимо уставить пакетный менеджер pipenv
```bash
pip install pipenv
```
- активировать виртуальное окружение
```bash
pipenv shell
```
- установить в виртуальное окружение все зависимости
```bash
pip install -r requirements.txt
```