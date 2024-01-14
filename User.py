import aiogram
from aiogram.types import CallbackQuery, Message
from db import create_client, get_client, connect_client_By_master_db, get_data_masters_and_clients

from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import gen_ikb_days, gen_ikb_months, gen_time_ikb, days_months, months_list, cancel_messages_ikb
from googlesheet_table import GoogleTable
import re


class FSMUserProfile(StatesGroup):  # класс создан чтобы вести диалог поэтапно
    master = State()
    telephone_number = State()
    name = State()
    record_date_month = State()
    record_date_day = State()
    record_date_time = State()


async def start_FSM(callback: CallbackQuery, state: FSMContext):
    '''
    Запуск конечного автомата
    '''
    await state.update_data(master=callback.data.split('|')[1:])
    await state.set_state(
        FSMUserProfile.telephone_number)  # установка нового состояния конечного автомата, в зависимости от этого состояния запускается нуужная функция load_telephon_number
    await callback.message.answer('Введите свой номер телефона', reply_markup=cancel_messages_ikb)  #


messages = {
    FSMUserProfile.telephone_number.state: "Введите свой номер телефона",
    FSMUserProfile.name.state: "Введите имя и фамилию",
    FSMUserProfile.record_date_month.state: "Выберите дату записи",
    # переменная state коорая возвращает строковое представление названия состояния
    FSMUserProfile.record_date_day.state: "Выберите день записи",
    FSMUserProfile.record_date_time.state: "Выберите время записи"
}


async def load_telephone_number(message: Message, state: FSMContext):
    '''
    Ожидание ввода телефонного номера
    '''
    data = message.text  # хранится номер телефона - str
    if data := is_valid_tel_number(data):
        client = await get_client(data)  # получи кортеж
        await state.update_data(tel=data)
        if client:  # если кортеж не пустой, значит правда
            await state.update_data(name=client[1])  # 1позиция это имя фамилия клиента
            await state.set_state(FSMUserProfile.record_date_month)  # Устанавливаем состояние ожидания ввода месяца
            await message.answer(messages[FSMUserProfile.record_date_month.state], reply_markup=gen_ikb_months())
        else:  # если клиента нет в БД
            await state.set_state(FSMUserProfile.name)  # Устанавливаем состояние ожидания ввода имени
            await message.answer(messages[FSMUserProfile.name.state], reply_markup=cancel_messages_ikb)
    else:
        await message.reply('Некорректный номер телефона, повторите ввод')


async def load_name(message: Message, state: FSMContext):
    '''
    Ожидание ввода имени
    '''
    data = message.text  # имя фамилия клиента
    await state.update_data(name=data)
    await state.set_state(FSMUserProfile.record_date_month)
    await message.answer(messages[FSMUserProfile.record_date_month.state], reply_markup=gen_ikb_months())  #


google_table = GoogleTable()
times = {}


async def back(callback: CallbackQuery, state: FSMContext):
    '''
    Функция возврата к предыдущему состоянию конечного автомата
    '''
    user_state_data = await state.get_data()  # словарь с данными, буфер из стейта
    current_state = await state.get_state()
    if current_state == FSMUserProfile.record_date_day.state:
        await state.set_state(FSMUserProfile.record_date_month)
        await callback.message.edit_text(messages[FSMUserProfile.record_date_month.state],
                                         reply_markup=gen_ikb_months())
    if current_state == FSMUserProfile.record_date_time.state:
        await state.set_state(FSMUserProfile.record_date_day)
        await callback.message.edit_text(messages[FSMUserProfile.record_date_day.state],
                                         reply_markup=gen_ikb_days(user_state_data['date']['month']))
    if current_state == FSMUserProfile.record_date_month.state:
        await state.set_state(FSMUserProfile.telephone_number)
        await callback.message.edit_text(messages[FSMUserProfile.telephone_number.state])
    if current_state == FSMUserProfile.name.state:
        await state.set_state(FSMUserProfile.telephone_number)
        await callback.message.edit_text(messages[FSMUserProfile.telephone_number.state],
                                         reply_markup=cancel_messages_ikb)
    if current_state == FSMUserProfile.telephone_number.state:
        await state.finish()  # завершаем конечный автомат
        await callback.message.edit_text('Для того, чтобы повторить диалог с ботом, нажмите /start')


async def load_date_month(callback: CallbackQuery, state: FSMContext):  # Загружаем дату
    '''
    Ожидание выбора месяца
    '''
    data = callback.data
    user_state_data = await state.get_data()  # получаем данные из буффера в виде словаря
    selected_date = {'month': data}
    await state.update_data(date=selected_date)
    await state.set_state(FSMUserProfile.record_date_day)
    await callback.message.edit_text(messages[FSMUserProfile.record_date_day.state])
    await callback.message.edit_reply_markup(reply_markup=gen_ikb_days(data))


async def load_date_day(callback: CallbackQuery, state: FSMContext):
    '''
    Ожидание выбора дня
    '''
    data = callback.data
    user_state_data = await state.get_data()  # 2 этап добавляем в буфер выбранный день
    user_state_data['date']['day'] = data
    await state.update_data(date=user_state_data['date'])
    range_columns = 'BCDEFGHIJK'
    slots = google_table.getData(user_state_data['master'][1], f'B1:K1')

    for i in range(len(slots)):
        if slots[i] != '':
            times[slots[i]] = range_columns[i]
    await state.set_state(FSMUserProfile.record_date_time)
    await callback.message.edit_text(messages[FSMUserProfile.record_date_time.state])
    await callback.message.edit_reply_markup(reply_markup=gen_time_ikb(times))

    # Подключаемся к гугл таблицы для получения времени
    # Отправим набор свободного времени в виде клавиатуры нашему клиенту в чат


async def load_date_time(callback: CallbackQuery, state: FSMContext):
    '''
    Ожидание выбора времени
    '''
    data = callback.data
    user_state_data = await state.get_data()
    user_state_data['date']['time'] = data  # выбранное время
    await state.update_data(date=user_state_data['date'])
    # if 'name' in user_state_data:
    await create_client(user_state_data)
    name_month = user_state_data['date']['month']
    number_day = user_state_data['date']['day']
    # номер строки таблицы где находятся даты записи к мастеру в определенный день
    number_row = sum(days_months[:months_list.index(name_month)]) + int(number_day) + months_list.index(
        name_month) + 1  # номер выбранной строки строки в гугл таблице
    # адрес ячейки куда будем вносить данные о клиенте
    address_cell_for_record = f'{times[data]}{number_row}:{times[data]}{number_row}'
    # вносить будем телефонный номер и имя клиента
    value = user_state_data['tel'] + '\n' + user_state_data['name']  # телефонный номер клиента+ имя фамилия клиента
    # получаем данные из ячейки куда будем записываться
    book_time = google_table.getData(user_state_data['master'][1], address_cell_for_record)
    # делаем проверку на пустую ячейку
    if book_time:  # получим True если ячейка занята
        await callback.message.reply('Это время занято, попробуйте выбрать другое время')
        await state.set_state(FSMUserProfile.telephone_number)
        await callback.message.answer(messages[FSMUserProfile.telephone_number.state])
    else:
        google_table.updateData(user_state_data['master'][1], address_cell_for_record, value)
        if (user_state_data['master'][0], user_state_data['tel']) not in await get_data_masters_and_clients(
                user_state_data['tel']):
            await connect_client_By_master_db(user_state_data['master'][0], user_state_data['tel'])
        await callback.message.reply(f'''{user_state_data['name']}, Вы успешно записаны к мастеру {user_state_data['master'][1]}!
               \nМесяц: {user_state_data['date']['month']}
               \nЧисло: {user_state_data['date']['day']}
               \nВремя: {user_state_data['date']['time']}
               ''')
        await state.finish()


def is_valid_tel_number(message):
    '''
    Проверка валидности номера телефона
    '''
    if re.match(r'[+]?[78]{1}\d{10}$', message):
        if '+' in message:
            message = "8" + message[2:]
        return message
    return False