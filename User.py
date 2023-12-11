import aiogram
from aiogram.types import CallbackQuery
# from router import Router

# from aiogram import Router
from db import create_client, get_client

from aiogram.dispatcher import FSMContext, Dispatcher  # Конечный автомат
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import gen_ikb_days, gen_ikb_months, gen_time_ikb, days_months, months_list, cancel_messages_ikb
from googlesheet_table import GoogleTable



# user_router = Router()


class UserProfile(StatesGroup):#класс создан чтобы вести диалог поэтапно
    name = State()  # встроенный класс запоминает последнее отправленное сообщение
    telephone_number = State()
    master = State()
    record_date_month = State()#
    record_date_day = State()
    record_date_time = State()


async def start_FSM(callback, state: FSMContext):#state экземпляр класса FSMContext
    await state.update_data(master=callback.data.split('|')[2])#обновили словарь в state - буфер
    await state.set_state(UserProfile.telephone_number)#установка нового состояния конечного автомата, в зависимости от этого состояния запускается нуужная функция load_telephon_number
    await callback.message.answer('Введите свой номер телефона', reply_markup=cancel_messages_ikb)#

messages = {
    UserProfile.telephone_number.state:"Введите свой номер телефона",
    UserProfile.name.state:"Введите имя и фамилию",
    UserProfile.record_date_month.state:"Выберите дату записи",#переменная state коорая возвращает строковое представление названия состояния
    UserProfile.record_date_day.state:"Выберите день записи",
    UserProfile.record_date_time.state:"Выберите время записи"
}
async def load_telephone_number(message, state: FSMContext):
    data = message.text# хранится номер телефона - str
    await state.update_data(tel=data)
    client = await get_client(data)#получи кортеж
    if client:  # если ортеж не пустой, значит правда
        await state.update_data(name=client[1])#1позиция это имя фамилия клиента
        await state.set_state(UserProfile.record_date_month)
        await message.answer(messages[UserProfile.record_date_month.state], reply_markup=gen_ikb_months())
    else:  # если клиента нет в БД
        await state.set_state(UserProfile.name)
        await message.answer(messages[UserProfile.name.state], reply_markup=cancel_messages_ikb)


async def load_name(message, state):
    data = message.text  # имя фамилия клиента
    await state.update_data(name=data)
    await state.set_state(UserProfile.record_date_month)
    await message.answer(messages[UserProfile.record_date_month.state], reply_markup=gen_ikb_months())  #


# фукнция будет вызываться 3 раза для месяца, дня, времени
google_table = GoogleTable()
times = {}
async def back(callback, state):
    user_state_data = await state.get_data()#словарь с данными, буфер из стейта
    current_state = await state.get_state()
    if current_state == UserProfile.record_date_day.state:
        await state.set_state(UserProfile.record_date_month)
        await callback.message.edit_text(messages[UserProfile.record_date_month.state], reply_markup=gen_ikb_months())
        # await callback.message.answer(messages[UserProfile.record_date_month.state], reply_markup=gen_ikb_months())
    if current_state == UserProfile.record_date_time.state:
        await state.set_state(UserProfile.record_date_day)
        await callback.message.edit_text(messages[UserProfile.record_date_day.state], reply_markup=gen_ikb_days(user_state_data['date']['month']))
    if current_state == UserProfile.record_date_month.state:
        await state.set_state(UserProfile.telephone_number)
        await callback.message.edit_text(messages[UserProfile.telephone_number.state])
    if current_state == UserProfile.name.state:
        await state.set_state(UserProfile.telephone_number)
        await callback.message.edit_text(messages[UserProfile.record_date_day.state], reply_markup=cancel_messages_ikb)
    if current_state == UserProfile.telephone_number.state:
        await state.finish()#завершаем конечный автомат
        await callback.message.edit_text('Для того, чтобы повторить диалог с ботом, нажмите /start')

async def load_date_month(callback, state):  # Загружаем дату
    data = callback.data
    user_state_data = await state.get_data()  # получаем данные из буффера в виде словаря
    # user_state_data = {
    #      'master':['+5645378123','Анна Москалева'],
    #     'tel': '+734903853',
    #     'name': 'Юлия Арзамасова',
    #     'date':
    #         {
    #             'month': 'Апрель'
    #
    #         }
    # }

    # if 'date' not in user_state_data:  # 1 этап добавляем в буфер выбранный месяц, если такоготключа в словаре не было
    selected_date = {'month': data}
    await state.update_data(date=selected_date)
    await state.set_state(UserProfile.record_date_day)
    await callback.message.edit_text(messages[UserProfile.record_date_day.state])
    await callback.message.edit_reply_markup(reply_markup=gen_ikb_days(data))

async def load_date_day(callback, state):
    data = callback.data
    user_state_data = await state.get_data() # 2 этап добавляем в буфер выбранный день
    user_state_data['date']['day'] = data
    await state.update_data(date=user_state_data['date'])
    range_columns = 'BCDEFGHIJK'
    slots = google_table.getData(user_state_data['master'], f'B1:K1')

    for i in range(len(slots)):
        if slots[i] != '':
            times[slots[i]] = range_columns[i]
    await state.set_state(UserProfile.record_date_time)
    await callback.message.edit_text(messages[UserProfile.record_date_time.state])
    await callback.message.edit_reply_markup(reply_markup=gen_time_ikb(times))

        # Подключаемся к гугл таблицы для получения времени
        # Отправим набор свободного времени в виде клавиатуры нашему клиенту в чат
async def load_date_time(callback, state):
    data = callback.data
    # elif 'time' not in user_state_data['date']:  # 3 этап добавляем в буфер выбранное время
    user_state_data = await state.get_data()
    user_state_data['date']['time'] = data #выбранное время
    await state.update_data(date=user_state_data['date'])
    if 'name' in user_state_data:
        await create_client(user_state_data)
    name_month = user_state_data['date']['month']
    number_day = user_state_data['date']['day']
    #номер строки таблицы где находятся даты записи к мастеру в определенный день
    number_row = sum(days_months[:months_list.index(name_month)]) + int(number_day) + months_list.index(name_month)# номер выбранной строки строки в гугл таблице
    #адрес ячейки куда будем вносить данные о клиенте
    address_cell_for_record = f'{times[data]}{number_row}:{times[data]}{number_row}'
    #вносить будем телефонный номер
    value = user_state_data['tel']+'\n'+user_state_data['name']# телефонный номер клиента+ имя фамилия клиента
    #получаем данные из ячейки куда будем записываться
    book_time = google_table.getData(user_state_data['master'], address_cell_for_record)
    #делаем проверку на пустую ячейку
    if book_time:#получим True если ячейка занята
        await callback.message.reply('Это время занято, попробуйте выбрать другое время')
        await state.set_state(UserProfile.telephone_number)
        await callback.message.answer(messages[UserProfile.telephone_number.state])
    else:
        google_table.UpdateData(user_state_data['master'], address_cell_for_record, value)
        await callback.message.reply(f'''Вы успешно записаны к мастеру!
               \nМесяц:{user_state_data['date']['month']}
               \nЧисло:{user_state_data['date']['day']}
               \nВремя:{user_state_data['date']['time']}
               ''')
        await state.finish()




