from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




button_load = KeyboardButton('upload')
button_delete = KeyboardButton('del')
button_cancel_st = KeyboardButton('cancel')
button_menu = KeyboardButton('all item')
button_logout = KeyboardButton('logout')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)\
            .insert(button_delete).insert(button_cancel_st).add(button_menu).insert(button_logout)

button_case_admin_inprocess = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel_st)




butt_cat_burgers = KeyboardButton('Бургеры')
butt_cat_snacks = KeyboardButton('Закуски')
butt_cat_hot = KeyboardButton('Горячее')
butt_cat_salads = KeyboardButton('Салаты')
butt_cat_hot_drinks = KeyboardButton('Горячие напитки')
butt_cat_cold_drinks = KeyboardButton('Холодные напитки')

button_set_cat_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(butt_cat_burgers)\
            .insert(butt_cat_snacks).insert(butt_cat_hot).insert(butt_cat_salads).add(butt_cat_hot_drinks).insert(butt_cat_cold_drinks)




category_admin_cb = CallbackData("catorder", "set_cat", "action")

inline_kb_set_category_admin = InlineKeyboardMarkup().add(
        InlineKeyboardButton(f'Бургеры', callback_data=category_admin_cb.new(set_cat = "1", action = "set_cat"))).insert(
        InlineKeyboardButton(f'Закуски', callback_data=category_admin_cb.new(set_cat = "2", action = "set_cat"))).add(
        InlineKeyboardButton(f'Горячее', callback_data=category_admin_cb.new(set_cat = "3", action = "set_cat"))).insert(
        InlineKeyboardButton(f'Салаты', callback_data=category_admin_cb.new(set_cat = "4", action = "set_cat"))).add(
        InlineKeyboardButton(f'Горячие напитки', callback_data=category_admin_cb.new(set_cat = "5", action = "set_cat"))).add(
        InlineKeyboardButton(f'Холодные напитки', callback_data=category_admin_cb.new(set_cat = "6", action = "set_cat"))
        )




choice_admin_cd = CallbackData("choice", "action")

keyboard_choice_admin_cd = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Да', callback_data=choice_admin_cd.new(action = 'Y')),
        InlineKeyboardButton('Нет', callback_data=choice_admin_cd.new(action = 'N'))
        )

