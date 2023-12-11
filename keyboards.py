from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from calendar import monthrange

# start_keyboard_button = KeyboardButton('/start')
# start_keyboard = ReplyKeyboardMarkup().add(start_keyboard_button)#создали клавиатуру и добавили туда одну кнопку
cancel_messages_ikb = InlineKeyboardMarkup()
back_inline_button = InlineKeyboardButton(text='Назад', callback_data='Cancel')
cancel_messages_ikb.add(back_inline_button)

ikb_start = InlineKeyboardMarkup(row_width=2)
ib1 = InlineKeyboardButton(text='Палитра', callback_data='Палитра')
ib2 = InlineKeyboardButton(text='Свободные слоты', callback_data='Слоты')
ib3 = InlineKeyboardButton(text='Прайс на услуги', callback_data='Прайс')
ib4 = InlineKeyboardButton(text='Важная информация', callback_data='Информация')
ib5 = InlineKeyboardButton(text='Наш сайт', url="http://crystal-spa.ru/index.php")
ib6 = InlineKeyboardButton(text='Отменить запись', callback_data='Отмена записи')
ikb_start.add(ib1, ib2).add(ib3).add(ib4, ib5).add(ib6)



months_list = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август',
               'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
days_months = [0]
current_year = datetime.now().year
for i in range(1, 13):
    days_months.append(monthrange(current_year, i)[1])#заполняем список правильным количеством дней

back_inline_button = InlineKeyboardButton(text='Назад', callback_data='Cancel')

def gen_ikb_months():  # создается клавиатура месяцев в текст попадает название месяца а в callback - номер месяца
    ikb_months = InlineKeyboardMarkup()
    for i in range(datetime.now().month, 13):
        ikb_months.add(InlineKeyboardButton(text=months_list[i], callback_data=months_list[i]))
    ikb_months.add(back_inline_button)
    return ikb_months


def gen_ikb_days(name_month):
    ikb_days = InlineKeyboardMarkup(row_width=5)
    for i in range(1, days_months[months_list.index(name_month)]+1):
        ikb_days.add(InlineKeyboardButton(text=i, callback_data=i))
    ikb_days.add(back_inline_button)
    return ikb_days


def gen_time_ikb(times):
    ikb_times = InlineKeyboardMarkup(row_width=3)
    for time in times:
        ikb_times.add(InlineKeyboardButton(text=time, callback_data=time))
    ikb_times.add(back_inline_button)
    return ikb_times
