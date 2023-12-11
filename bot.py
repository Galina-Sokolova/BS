import setting_commands
from aiogram import Bot, executor, Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from keyboards import *
from config import TOKEN_BOT
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Временный буфер
from User import *


import db

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())#storage=MemoryStorage() создали объект хранилища, хранилище MemoryStorage будет терять все данные после перезагрузи приложения
#т.к. все данные будут храниться в оперативной памяти
messages_choice_by_masters = []

async def on_startup(_):
    await setting_commands.set_default_commands(bot)
    # регистрация функций в диспетчере перед запуском бота
    dp.register_message_handler(load_telephone_number, state=UserProfile.telephone_number)#load_telephone_number - эта функция будет вызвана, когда польз. отправит сообщение
    dp.register_message_handler(load_name, state=UserProfile.name)
    dp.register_callback_query_handler(back, state='*', text_startswith='Cancel')
    dp.register_callback_query_handler(load_date_month, state=UserProfile.record_date_month)#load_date - эта функция будет вызвана, когда польз. нажмет на кнопку - выберет дату
    dp.register_callback_query_handler(load_date_day, state=UserProfile.record_date_day)
    dp.register_callback_query_handler(load_date_time, state=UserProfile.record_date_time)
    await db.db_start()
    # await bot.send_message('Для запуска бота нажми на /start')
    print('БОТ ЗАПУЩЕН!')
    # await setting_commands.set_default_commands(bot)


# Навешиваем обработчик, который будет давать функции start_command реагировать только на сообщение start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_photo(chat_id=message.chat.id,
                         photo=open('resourсes/images/start.jpg', 'rb'),
                         caption='Добро пожаловать в нашу студию!',
                         reply_markup=ikb_start)
    await message.delete()


@dp.callback_query_handler(text='Слоты')
async def get_free_slots(callback: types.CallbackQuery):#callback словарь
    masters = await db.get_masters()#лежит список кортежей мастеров
    for master in masters:
        ikb_register_to_master = InlineKeyboardMarkup()#создали клавиатуру из одной кнопки
        ikb_register_to_master.add(InlineKeyboardButton(text='Запись на прием', callback_data='Запись на прием'+f'|{master[0]}|{master[1]}'))
        # photo_by_master = open('resourсes/images/master1.jpg', 'rb')

        photo_by_master = open(master[4], 'rb')

        message_photo = await bot.send_photo(chat_id=callback['message']['chat']['id'],
                             photo=photo_by_master,
                             caption=f'{master[1]}',#имя мастера под фото
                             reply_markup=ikb_register_to_master
                             )
        messages_choice_by_masters.append(message_photo)
        # print(message_photo)
        photo_by_master.close()

@dp.callback_query_handler(text='Отмена записи')
async def delete_record(callback:types.CallbackQuery):
    await callback.message.answer("Введите номер телефона для отмены записи")

@dp.message_handler(filters.Regexp(regexp=r"\d+"))#Если мы встречаем
async def get_telephone_numbers(msg: types.Message):
    google_table=GoogleTable()#создаем экз класса
    master = await db.get_client(msg.text)
    google_table.deleteData(master[2], msg.text)


@dp.callback_query_handler(filters.Text(contains="Запись на прием"))
async def register_to_master(callback: types.CallbackQuery, state: FSMContext):
    for msg in messages_choice_by_masters:
        await bot.delete_message(chat_id=callback['message']['chat']['id'],#.from_user.id
                                message_id=msg["message_id"])  # нажав на кнопку запись на прием предыдущее сообщение удаляется, чтобы не захламлять чат
    messages_choice_by_masters.clear()
    await start_FSM(callback, state)#в переменной callback хранится вся информация о мастере


if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,#параметр используется чтобы пропустить старые сообщения
        on_startup=on_startup#фунция, которая будет вызвана при запуске бота
    )
