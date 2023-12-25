import setting_commands
from aiogram import Bot, executor, Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from keyboards import *
from config import TOKEN_BOT
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Временный буфер
from User import *

import db

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())
messages_choice_by_masters = []


async def on_startup(_):
    '''
    регистрация функций в диспетчере перед запуском бота
    '''
    await setting_commands.set_default_commands(bot)
    # регистрация функций в диспетчере перед запуском бота
    dp.register_message_handler(load_telephone_number, state=FSMUserProfile.telephone_number)
    dp.register_message_handler(load_name, state=FSMUserProfile.name)
    dp.register_callback_query_handler(back, state='*', text_startswith='Cancel')
    dp.register_callback_query_handler(load_date_month,
                                       state=FSMUserProfile.record_date_month)  # load_date - эта функция будет вызвана, когда польз. нажмет на кнопку - выберет дату
    dp.register_callback_query_handler(load_date_day, state=FSMUserProfile.record_date_day)
    dp.register_callback_query_handler(load_date_time, state=FSMUserProfile.record_date_time)
    await db.db_start()
    print('БОТ ЗАПУЩЕН!')


# Навешиваем обработчик, который будет давать функции start_command реагировать только на сообщение start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    '''
    Обработчик команды /start
    '''
    await bot.send_photo(chat_id=message.chat.id,
                         photo=open('resourсes/images/start.jpg', 'rb'),
                         caption='Добро пожаловать в нашу студию!',
                         reply_markup=ikb_start)
    await message.delete()


@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    '''
    Обработчик команды /cancel
    '''
    await state.finish()
    await start_command(message)


@dp.callback_query_handler(text='Информация')
async def info(callback: types.CallbackQuery):
    '''
    Обработчик кнопки "Важная информация"
    '''
    await bot.send_message(chat_id=callback['message']['chat']['id'],
                           text='Время работы: '
                                '9-00 - 22-00  '
                                'без перерывов и выходных'
                           )


@dp.callback_query_handler(text='Слоты')
async def get_free_slots(callback: types.CallbackQuery):  # callback словарь
    '''
    Выведет информацию о всех мастерах из БД
    '''
    masters = await db.get_masters()  # лежит список кортежей мастеров
    for master in masters:
        ikb_register_to_master = InlineKeyboardMarkup()  # создали клавиатуру из одной кнопки
        ikb_register_to_master.add(InlineKeyboardButton(text='Запись на прием',
                                                        callback_data='Запись на прием' + f'|{master[0]}|{master[1]}'))
        photo_by_master = open(master[4], 'rb')

        message_photo = await bot.send_photo(chat_id=callback['message']['chat']['id'],
                                             photo=photo_by_master,
                                             caption=f'{master[1]}  tel: {master[0]}',  # имя и телефон мастера под фото
                                             reply_markup=ikb_register_to_master
                                             )
        messages_choice_by_masters.append(message_photo)
        photo_by_master.close()


@dp.callback_query_handler(text='Отменить запись')
async def delete_record(callback: types.CallbackQuery):
    await callback.message.answer("Введите номер телефрна для отмены записи")


@dp.message_handler(
    filters.Regexp(regexp=r"\d+"))  # Если мы встречаем номер телефона сразу запускается эта функция r"\d+"
async def get_telephone_numbers(msg: types.Message):
    '''
    Функция обработки введенного телефонного номера при отмене записи
    '''
    if is_valid_tel_number(msg.text):
        await send_data_masters(msg)
    else:
        await msg.reply('Некорректный номер телефона, повторите ввод')


@dp.callback_query_handler(filters.Text(contains='del'))
async def cancel_record_to_master(callback: types.CallbackQuery):
    '''
    Отмена записи к мастеру
    '''
    for msg in messages_choice_by_masters:
        await bot.delete_message(chat_id=callback['message']['chat']['id'],  # .from_user.id
                                 message_id=msg[
                                     "message_id"])
    messages_choice_by_masters.clear()
    google_table = GoogleTable()
    data = callback.data.split('|')
    if google_table.deleteData(data[1], data[2]):
        text = "Запись успешно отменена"
    else:
        text = "Запись к мастеру не была найдена или произошла другая ошибка"
    await bot.send_message(chat_id=callback['message']['chat']['id'], text=text)


@dp.callback_query_handler(filters.Text(contains="Запись на прием"))
async def register_to_master(callback: types.CallbackQuery, state: FSMContext):
    '''
    Регистрация к мастеру, запуск конечного автомата
    '''
    for msg in messages_choice_by_masters:
        await bot.delete_message(chat_id=callback['message']['chat']['id'],  # .from_user.id
                                 message_id=msg[
                                     "message_id"])  # нажав на кнопку запись на прием предыдущее сообщение удаляется, чтобы не захламлять чат
    messages_choice_by_masters.clear()
    await start_FSM(callback, state)  # в переменной callback хранится вся информация о мастере


async def send_data_masters(message: types.Message):
    '''
    Функция отправления информации о всех мастерах в чат по тел. номеру клиента при отмене записи
    '''
    records = await db.get_masters_by_client(message.text)
    if len(records) == 0:
        await bot.send_message(chat_id=message.chat.id,
                               text='Вы не записаны ни к одному мастеру')
    for record in records:
        ikb_del_record = InlineKeyboardMarkup()  # создали клавиатуру из одной кнопки
        ikb_del_record.add(
            InlineKeyboardButton(text='Отменить запись',
                                 callback_data='del' + f'|{record[1]}|{message.text}'))  # к кнопке будут прикреплены данные и они отправятся в функцию cancel_record...
        photo_by_master = open(record[4], 'rb')
        message_photo = await bot.send_photo(chat_id=message.chat.id,
                                             photo=photo_by_master,
                                             caption=f'{record[1]}',  # имя мастера под фото
                                             reply_markup=ikb_del_record
                                             )
        messages_choice_by_masters.append(message_photo)
        # print(message_photo)
        photo_by_master.close()


if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,  # параметр используется чтобы пропустить старые сообщения
        on_startup=on_startup  # фунция, которая будет вызвана при запуске бота
    )
