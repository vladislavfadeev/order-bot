from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData




b1 = KeyboardButton('Режим работы')
b2 = KeyboardButton('Расположение')
b3 = KeyboardButton('Справка')
b4 = KeyboardButton('Сделать заказ')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True).add(b1).insert(b2).add(b3).insert(b4)




b21 = KeyboardButton('Отмена')
b22 = KeyboardButton('Помощь')
b23 = KeyboardButton('Сменить категорию меню')
b24 = KeyboardButton('Корзина')

kb_order_1 = ReplyKeyboardMarkup(resize_keyboard=True).add(b21).insert(b22)
kb_order_2 = ReplyKeyboardMarkup(resize_keyboard=True).add(b21).insert(b22).add(b23).insert(b24)




# inline_kb_category = InlineKeyboardMarkup().add(InlineKeyboardButton(f'Бургеры', callback_data=f'btn Бургеры'))\
#         .insert(InlineKeyboardButton(f'Закуски', callback_data=f'btn Закуски')).add(InlineKeyboardButton(f'Горячее', callback_data=f'btn Горячее'))\
#             .insert(InlineKeyboardButton(f'Салаты', callback_data=f'btn Салаты')).add(InlineKeyboardButton(f'Горячие напитки', callback_data=f'btn Горячие напитки'))\
#                 .add(InlineKeyboardButton(f'Холодные напитки', callback_data=f'btn Холодные напитки'))




category_order_cb = CallbackData("catorder", "set_cat", "action")

inline_kb_set_category_order = InlineKeyboardMarkup().add(
        InlineKeyboardButton(f'Бургеры', callback_data=category_order_cb.new(set_cat = "1", action = "set_cat"))).insert(
        InlineKeyboardButton(f'Закуски', callback_data=category_order_cb.new(set_cat = "2", action = "set_cat"))).add(
        InlineKeyboardButton(f'Горячее', callback_data=category_order_cb.new(set_cat = "3", action = "set_cat"))).insert(
        InlineKeyboardButton(f'Салаты', callback_data=category_order_cb.new(set_cat = "4", action = "set_cat"))).add(
        InlineKeyboardButton(f'Горячие напитки', callback_data=category_order_cb.new(set_cat = "5", action = "set_cat"))).add(
        InlineKeyboardButton(f'Холодные напитки', callback_data=category_order_cb.new(set_cat = "6", action = "set_cat")))
