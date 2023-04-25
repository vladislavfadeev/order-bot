from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
from bot_keyboard import client_kb
from data_base import sqlite_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import datetime
from handlers import admin


### Переменные для передачи callback_data инлайн кнопками в хендлеры.
set_quantity_order_cb = CallbackData("addtocart", "order_id", "product_id", "quantity", "action")
add_order_db_cb = CallbackData("enter_order", "action")
edit_user_cart_cb = CallbackData("edit_ucart", "product_id", "action")
edit_quntity_item_in_order_cb = CallbackData("edit_qucart", "product_id", "q", "action")


class FSMOrder(StatesGroup):
    open_order = State()
    set_items = State()




''' Блок ответа на иформационные кнопки вне состояния '''
### Вывод информации о истории заказов.
### Функтия не имеет соответсвующей кнопки в блоке кнопок! Для вывода потребуется команда "История заказов", либо установка кнопки на панель.
async def show_order_history(message: types.Message):
    value = await sqlite_db.sql_show_order_history(message.from_user.id)
    op = ''
    summ = 0
    for i in value:
        for r in i:
            char = f'Заказ № {i[2]} | Дата: {i[3]} | Сумма {i[5]} руб.\nАдрес самовывоза: {i[4]}\n\n'
        op += char
        summ += float(i[5])
    await bot.send_message(message.from_user.id, text=f'История ваших заказов:\n\n{op}\n\nОбщая сумма ваших заказов: {summ} руб.')




''' Блок ответа на информационные кнопки в состоянии open_order  '''
### Вывод справочной информации о том, как делать заказ.
async def show_help_in_order_state(message: types.Message):
    await bot.send_message(message.from_user.id, 'Тут подробная информация о правильном использовании бота в заказе')




''' Блок добавления товаров в корзину '''
### Выбор категории меню.
async def start_order(message : types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Еслу у вас есть вопросы по оформлению заказа,\
 вы можете ознакомиться с справочной информацией в разделе 'Помощь'" , reply_markup = client_kb.kb_order_1)
    await bot.send_message(message.from_user.id, 'Выберете категорию меню:' , reply_markup = client_kb.inline_kb_set_category_order)
    session_id = str(uuid.uuid4())[:7]
    async with state.proxy() as data:
        data['order_id'] = session_id
        data['user_id'] = message.from_user.id
    await FSMOrder.open_order.set()

### Вывод категорий меню для их смены в процессе заказа.
async def show_category_to_order_again(message: types.Message, state=FSMOrder.open_order):
    await bot.send_message(message.from_user.id, 'Выберете категорию меню:' , reply_markup = client_kb.inline_kb_set_category_order)

### Вывод товаров, содержащихся в выбранной категории с присвеоением инлайн кнопок.
@dp.callback_query_handler(client_kb.category_order_cb.filter(action = ["set_cat"]), state=FSMOrder.open_order)
async def show_category_fo_order(callback_query: types.CallbackQuery,  callback_data: dict, state: FSMContext):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, 'Продукты из категории', reply_markup= client_kb.kb_order_2)
    data = await state.get_data()
    session_id = data.get('order_id')
    items = await sqlite_db.sql_read_user_order(callback_data.get("set_cat"))
    for ret in items:
        await bot.send_photo(callback_query.from_user.id, ret[2], f'{ret[3]}\nОписание: {ret[4]}\nЦена {ret[5]}\n\n Выбере количество, которое хотите добать в корзину:', \
            reply_markup=InlineKeyboardMarkup(row_width = 6).add(
                    InlineKeyboardButton(f'1', callback_data=set_quantity_order_cb.new(order_id = session_id, product_id = ret[0], quantity = 1, action = "set_q")),
                    InlineKeyboardButton(f'2', callback_data=set_quantity_order_cb.new(order_id = session_id, product_id = ret[0], quantity = 2, action = "set_q")),
                    InlineKeyboardButton(f'3', callback_data=set_quantity_order_cb.new(order_id = session_id, product_id = ret[0], quantity = 3, action = "set_q")),
                    InlineKeyboardButton(f'4', callback_data=set_quantity_order_cb.new(order_id = session_id, product_id = ret[0], quantity = 4, action = "set_q")),
                    InlineKeyboardButton(f'5', callback_data=set_quantity_order_cb.new(order_id = session_id, product_id = ret[0], quantity = 5, action = "set_q")),
                    InlineKeyboardButton(f'6', callback_data=set_quantity_order_cb.new(order_id = session_id, product_id = ret[0], quantity = 6, action = "set_q"))
            ))
            # reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text='В корзину', callback_data=cart_cb.new\
            # (order_id = session_id[:7], product_id = ret[0], action = 'add_to_cart'))))

### Ловим нажатия на кнопки и добавляем выбранные товары в указанном количестве в корзину. (корзина в БД)
@dp.callback_query_handler(set_quantity_order_cb.filter(action = ["set_q"]), state=FSMOrder.open_order)
async def add_to_cart(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    order_id, product_id, quantity = callback_data.get('order_id'), callback_data.get('product_id'), callback_data.get('quantity')
    await sqlite_db.sql_add_to_cart(callback_query.from_user.id, order_id, product_id, quantity)                    # Записываем в БД
    await callback_query.answer(f'{quantity} шт добавлено в корзину')# , show_alert=True)




''' Блок работы с корзиной. Оформление заказа либо предварительное редактирование, а так же его отмена. '''
### Вывод содержимого корзины списком, с присвоением кнопок редактирования содержимого.
async def show_cart(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    value = await sqlite_db.sql_open_user_cart(order_id)
    op = ''
    summ = 0
    for i in value:
        for r in i:
            char = f'{i[3]} | {i[4]} шт | сумма {float(i[4]) * float(i[5])} руб.\n'
        op += char
        summ += float(f'{float(i[4]) * float(i[5])}')
    async with state.proxy() as data:
        data['order_sum'] = summ
    await bot.send_message(message.from_user.id, text=f'Ваша корзина:\n\n{op}\nОбщая сумма заказа: {summ} руб.', \
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(f'Оформить и оплатить заказ', callback_data= add_order_db_cb.new(action = 'place_order'))).add(
            InlineKeyboardButton(f'Редактировать корзину', callback_data= add_order_db_cb.new(action = 'edit_order'))
            ))


### Оформление заказа.

### Ловим нажатие на кнопку "Оформить заказ". Записываем заказ в БД и отправляем информацию в функцию оповещения менеджера о новом заказе.
@dp.callback_query_handler(add_order_db_cb.filter(action = ["place_order"]), state=FSMOrder.open_order)
async def place_an_order(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    date, time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).split()
    data = await state.get_data()
    order_id = data.get('order_id')
    user_id = data.get('user_id')
    order_sum = data.get('order_sum')
    adress = 'Воронежская 142'
    location_id = '1'
    await sqlite_db.sql_add_ready_order(user_id, order_id, date, time, adress, order_sum)                   # Записываем заказ в БД
    await admin.operator_notifier(order_id, location_id)                                                    # Оповещаем менеджера в admin.py
    await bot.send_message(user_id, f'Спасибо ваш заказ!\nСреднее время приготовления составляет 20 минут.\
Вы получите сообщение о готовности. \n\nАдрес самовывоза: {adress}', reply_markup= client_kb.kb_client)
    await state.finish()


### Редактирование корзины.

### Ловим нажатие на кнопку "Редактировать корзину". Выводим содержимое попозиционно с присвеонием кнопок для редактирования.
@dp.callback_query_handler(add_order_db_cb.filter(action = ["edit_order"]), state=FSMOrder.open_order)
async def start_edit_cart(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    order_id = data.get('order_id')
    cart_list, quantity_list = await sqlite_db.sql_open_user_cart_for_edit(order_id)
    index= 0
    for ret in cart_list:
        for r in ret:
            await bot.send_photo(callback_query.from_user.id, r[2], f'{r[3]}\n\nЦена {r[5]} | Количество: {quantity_list[index]}\n\n Выберите действие:', \
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(f'Изменить количество', callback_data= edit_user_cart_cb.new(product_id = r[0], action = 'edit_quantity'))).add(
                    InlineKeyboardButton(f'Удалить из корзины', callback_data= edit_user_cart_cb.new(product_id = r[0], action = 'delete_from_cart'))
                    ))
            index += 1

### Ловим нажатие на кнопку "Удалить из корзины".
@dp.callback_query_handler(edit_user_cart_cb.filter(action = ['delete_from_cart']), state=FSMOrder.open_order)
async def del_item_from_cart(callback_query: types.CallbackQuery, callback_data: dict, state:FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    product_id = callback_data.get('product_id')
    await sqlite_db.sql_del_item_from_cart(order_id, product_id)                # Удаляем из корзины в БД
    await callback_query.answer('Удалено из корзины', show_alert=True)

### Ловим нажатие на кнопку "Изменить количество".
@dp.callback_query_handler(edit_user_cart_cb.filter(action= ['edit_quantity']), state=FSMOrder.open_order)
async def edit_quntity_item_in_order(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback_query.answer()
    item_id = callback_data.get('product_id')
    await bot.send_message(callback_query.from_user.id, 'Выберете нужное количество', \
        reply_markup= InlineKeyboardMarkup(row_width = 5).add(
            InlineKeyboardButton(f'1', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '1', action = 'set_n_q')),
            InlineKeyboardButton(f'2', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '2', action = 'set_n_q')),
            InlineKeyboardButton(f'3', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '3', action = 'set_n_q')),
            InlineKeyboardButton(f'4', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '4', action = 'set_n_q')),
            InlineKeyboardButton(f'5', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '5', action = 'set_n_q')),
            InlineKeyboardButton(f'6', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '6', action = 'set_n_q')),
            InlineKeyboardButton(f'7', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '7', action = 'set_n_q')),
            InlineKeyboardButton(f'8', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '8', action = 'set_n_q')),
            InlineKeyboardButton(f'9', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '9', action = 'set_n_q')),
            InlineKeyboardButton(f'10', callback_data= edit_quntity_item_in_order_cb.new(product_id = item_id, q = '10', action = 'set_n_q'))
                    ))

### Ловим информацию из кнопок с количеством и вносим коррективы в БД.
@dp.callback_query_handler(edit_quntity_item_in_order_cb.filter(action= ['set_n_q']), state=FSMOrder.open_order)
async def det_new_item_qantity_in_cart(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    item_id = callback_data.get('product_id')
    new_q = callback_data.get('q')
    await sqlite_db.sql_replace_item_q_from_cart(order_id, item_id, new_q)                  # Меняем количество в БД
    await callback_query.answer(f'Количество изменено на {new_q}', show_alert=True)


### Полная отмена заказа и его удаление из БД.
async def cancel_order_handler(message: types.Message, state:FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    await sqlite_db.sql_del_order_from_cart(order_id)                   # Удаление из БД
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ваш заказ отменен', reply_markup= client_kb.kb_client)



### Регистрируем хендлеры.
def register_handlers_orders(dp : Dispatcher):
    dp.register_message_handler(cancel_order_handler, Text(equals='Отмена', ignore_case=True), state=FSMOrder)
    dp.register_message_handler(show_help_in_order_state, Text(equals='Помощь', ignore_case=True), state=FSMOrder)
    dp.register_message_handler(show_category_to_order_again, Text(equals='Сменить категорию меню', ignore_case=True), state=FSMOrder.open_order)
    dp.register_message_handler(show_cart, Text(equals='Корзина', ignore_case=True), state=FSMOrder.open_order)
    dp.register_message_handler(place_an_order, Text(equals='Провести', ignore_case=True), state=FSMOrder.open_order)
    dp.register_message_handler(start_order, Text(equals='Сделать заказ',  ignore_case=True))
    dp.register_message_handler(show_order_history, Text(equals= 'История заказов', ignore_case=True), state=None)
    

