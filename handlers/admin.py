from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from create_bot import dp, bot
from data_base import sqlite_db
from bot_keyboard import admin_kb, client_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




ID = None
char_cb = CallbackData('del_item', 'product_id', 'action')
edit_item_admin_cb = CallbackData('edit_item', 'product_id', 'column', 'action')




class FSMAdmin(StatesGroup):
    category_set = State()
    photo = State()
    name = State()
    description = State()
    price = State()
    edit_item = State()
    edit_photo = State()
    edit_name = State()
    edit_description = State()
    edit_price = State()
    edit_choice = State()
    del_state = State()

    
''' Вход в режим администратора '''
### Получаем ID текущего модератора
# @dp.message_handler(commands=['login'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Здравствуй хозяин!', reply_markup= admin_kb.button_case_admin)
    await message.delete()




''' Блок редактирования товаров '''

'''Модуль внесения нового товара в базу данных '''
### Определение категории внесения нового товара
async def cm_start(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.category_set.set()
        await message.answer('Выберите категорию меню, в которую будет добавлена новая позиция', reply_markup=admin_kb.inline_kb_set_category_admin)

### Начало диалога загрузки новой позиции меню
@dp.callback_query_handler(admin_kb.category_admin_cb.filter(action=['set_cat']), state=FSMAdmin.category_set)
async def cm_load_photo(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback_query.answer()
    if callback_query.from_user.id == ID:
        async with state.proxy() as data:
            data['category'] = callback_data.get("set_cat")      
        await FSMAdmin.next()
        await bot.send_message(callback_query.from_user.id, 'Загрузи фото', reply_markup= admin_kb.button_case_admin_inprocess)

### Ловим первый ответ от админа и пишем в словарь
async def load_photo(message: types.Message, state : FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.reply('Теперь введи название')

### Ловим ответ на вопрос 'Теперь введи название'
async def load_name(message: types.Message, state=FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.reply('Введи описание')

### Ловим ответ на вопрос 'Введи описание'
async def load_despription(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await message.reply('Теперь укажи цену')

### Ловим ответ на последний вопрос 'Укажи цену' и записываем информацию в БД
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['price'] = float(message.text)
        await sqlite_db.sql_add_command(state)
        await state.finish()
        await bot.send_message(message.from_user.id, 'Готово!\nКарточка успешно сохранена.', reply_markup= admin_kb.button_case_admin)




''' Модуль удаления товара из базы данных '''
### Выбор категории, в которой будет произведено удаление
async def delete_item_stage1(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.del_state.set()
        await bot.send_message(message.from_user.id, 'Выберете категорию, в которой собираетесь произвести удаление', \
            reply_markup= client_kb.inline_kb_set_category_order)
        
### Выбор товара для последующего удаления
@dp.callback_query_handler(client_kb.category_order_cb.filter(action=['set_cat']), state=FSMAdmin.del_state)
async def del_item_stage2(callback_query: types.CallbackQuery, callback_data: dict):
    await callback_query.answer()
    if callback_query.from_user.id == ID:
        await bot.send_message(callback_query.from_user.id, 'Что удаляем?', reply_markup= admin_kb.button_case_admin_inprocess)
        category = callback_data.get('set_cat')
        read = await sqlite_db.sql_read_user_order(category)
        for ret in read:
            await bot.send_photo(callback_query.from_user.id, ret[2], f'{ret[3]}\nОписание: {ret[4]}\nЦена {ret[5]}', \
                reply_markup= InlineKeyboardMarkup().add(InlineKeyboardButton(f'Удалить {ret[3]}', callback_data=char_cb.new(product_id = ret[0], action = 'del'))))

### Ловим нажатие кнопок и удаляем выбранный товар из базы данных. Действие не циклично, что бы удалить другой товар нужно
### снова активировать режим удаления.
@dp.callback_query_handler(char_cb.filter(action=['del']), state=FSMAdmin.del_state)
async def callback_del_item(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    product_id = callback_data.get('product_id')
    await sqlite_db.sql_delete_command(product_id)
    await callback_query.answer(f'Карточка удалена', show_alert=True)
    await state.finish()




''' Модуль редактирования данных кождого товара по отдельности '''
### Выбор категории для редактирования товара
async def start_update_item_admin(message: types.Message, state=FSMAdmin.edit_item):
    if message.from_user.id == ID:
        await FSMAdmin.edit_item.set()
        await bot.send_message(message.from_user.id, 'Выберете категорию, в которой собираетесь произвести редактирование', \
            reply_markup= client_kb.inline_kb_set_category_order)

### Вывод списка товаров из выбранной категории. К карточке каждого товара присваиваются свои инлайн-кнопки с уникальными значениями.
@dp.callback_query_handler(admin_kb.category_admin_cb.filter(action=['set_cat']), state = FSMAdmin.edit_item)
async def set_cat_for_edit_item(callback_query: types.CallbackQuery, callback_data: dict):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, 'Что редактируем?', reply_markup= admin_kb.button_case_admin_inprocess)
    category = callback_data.get('set_cat')
    read = await sqlite_db.sql_read_user_order(category)
    for ret in read:
        await bot.send_photo(callback_query.from_user.id, ret[2], f'{ret[3]}\nОписание: {ret[4]}\nЦена {ret[5]}\n\nЧто редактируем?:', \
             reply_markup= InlineKeyboardMarkup(row_width = 2).add(
                InlineKeyboardButton(f'Фото', callback_data=edit_item_admin_cb.new(product_id = ret[0], column = 'img', action = 'edit_ph')),
                InlineKeyboardButton(f'Название', callback_data=edit_item_admin_cb.new(product_id = ret[0], column = 'name', action = 'edit_n')),
                InlineKeyboardButton(f'Описание', callback_data=edit_item_admin_cb.new(product_id = ret[0], column = 'description', action = 'edit_d')),
                InlineKeyboardButton(f'Цена', callback_data=edit_item_admin_cb.new(product_id = ret[0], column = 'price', action = 'edit_p'))
                    ))


### Ловим нажатие на кнопку "Редактировать фото".
@dp.callback_query_handler(edit_item_admin_cb.filter(action=['edit_ph']), state= FSMAdmin.edit_item)
async def edit_item_foto(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await FSMAdmin.edit_photo.set()
    async with state.proxy() as data:
        data['product_id'] = callback_data.get('product_id')
    await bot.send_message(callback_query.from_user.id, 'Отравьте новое фото', reply_markup=admin_kb.button_case_admin_inprocess)

### Получаем ID нового фото и сохраняем его в базу данных.
async def edit_new_photo_admin(message: types.Message, state : FSMContext):
    if message.from_user.id == ID:
        data = await state.get_data()
        product_id = data.get('product_id')
        await sqlite_db.sql_replace_new_foto_admin(message.photo[0].file_id, product_id)
        await FSMAdmin.edit_choice.set()
        await bot.send_message(message.from_user.id, 'Фото успешно изменено.\nХотите продолжить редактирование?', reply_markup=admin_kb.keyboard_choice_admin_cd)


### Ловим нажатие на кнопку "Редактировать название".
@dp.callback_query_handler(edit_item_admin_cb.filter(action=['edit_n']), state= FSMAdmin.edit_item)
async def edit_item_name(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await FSMAdmin.edit_name.set()
    async with state.proxy() as data:
        data['product_id'] = callback_data.get('product_id')
    await bot.send_message(callback_query.from_user.id, 'Укажите новое название', reply_markup=admin_kb.button_case_admin_inprocess)

### Получаем новое название из сообщения и сохраняем в базу данных.
async def edit_new_name_admin(message: types.Message, state : FSMContext):
    if message.from_user.id == ID:
        data = await state.get_data()
        product_id = data.get('product_id')
        await sqlite_db.sql_replace_new_name_admin(message.text, product_id)
        await FSMAdmin.edit_choice.set()
        await bot.send_message(message.from_user.id, 'Название успешно изменено.\nХотите продолжить редактирование?', reply_markup=admin_kb.keyboard_choice_admin_cd)


### Ловим нажатие на кнопку "Редактировать описание".
@dp.callback_query_handler(edit_item_admin_cb.filter(action=['edit_d']), state= FSMAdmin.edit_item)
async def edit_item_description(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await FSMAdmin.edit_description.set()
    async with state.proxy() as data:
        data['product_id'] = callback_data.get('product_id')
    await bot.send_message(callback_query.from_user.id, 'Укажите новое описание', reply_markup=admin_kb.button_case_admin_inprocess)

### Получаем новое описание из сообщения и сохраняем в базу данных.
async def edit_new_description_admin(message: types.Message, state : FSMContext):
    if message.from_user.id == ID:
        data = await state.get_data()
        product_id = data.get('product_id')
        await sqlite_db.sql_replace_new_description_admin(message.text, product_id)
        await FSMAdmin.edit_choice.set()
        await bot.send_message(message.from_user.id, 'Описание успешно изменено.\nХотите продолжить редактирование?', reply_markup=admin_kb.keyboard_choice_admin_cd)


### Ловим нажатие на кнопку "Редактировать цену".
@dp.callback_query_handler(edit_item_admin_cb.filter(action=['edit_p']), state= FSMAdmin.edit_item)
async def edit_item_price(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await FSMAdmin.edit_price.set()
    async with state.proxy() as data:
        data['product_id'] = callback_data.get('product_id')
    await bot.send_message(callback_query.from_user.id, 'Укажите новую цену', reply_markup=admin_kb.button_case_admin_inprocess)

### Получаем новую цену из сообщения, приводим к float и сохраняем в базу данных.
async def edit_new_price_admin(message: types.Message, state : FSMContext):
    if message.from_user.id == ID:
        data = await state.get_data()
        product_id = data.get('product_id')
        await sqlite_db.sql_replace_new_price_admin(float(message.text), product_id)
        await FSMAdmin.edit_choice.set()
        await bot.send_message(message.from_user.id, 'Цена успешно изменена.\nХотите продолжить редактирование?', reply_markup=admin_kb.keyboard_choice_admin_cd)


### Заключаем редактирование данных в цикл.
### Если ответ на вопрос продолжении редактирования положительный - запускаем все заново, если отрицательный - завершаем текущее состояние. 
@dp.callback_query_handler(admin_kb.choice_admin_cd.filter(action=['Y']), state=FSMAdmin.edit_choice)
async def edit_item_admin_again(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await FSMAdmin.edit_item.set()
    await bot.send_message(callback_query.from_user.id, 'Выберете категорию, в которой собираетесь произвести редактирование', \
            reply_markup= client_kb.inline_kb_set_category_order)

@dp.callback_query_handler(admin_kb.choice_admin_cd.filter(action=['N']), state=FSMAdmin.edit_choice)
async def cancel_edit_item_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.finish()
    await bot.send_message(callback_query.from_user.id,'Редактирование завершено', reply_markup= admin_kb.button_case_admin)




''' Блок показа всех категорий и товаров в режиме администратора без редактирования и ввода в какое-либо состояние '''

### Отправка инлайн-кнопок с категориями.
async def show_menu_item(message: types.Message):
    await message.answer('Выберите категорию меню:', reply_markup = admin_kb.inline_kb_set_category_admin)

### Ловим нажатие кнопок и вывоим содержимое категорий.
@dp.callback_query_handler(admin_kb.category_admin_cb.filter(action=['set_cat']))
async def show_category(callback_query: types.CallbackQuery, callback_data: dict):
    await callback_query.answer()
    cat = callback_data.get('set_cat')
    await sqlite_db.sql_read_user(cat, callback_query.from_user.id)




''' Блок выхода из любого состояния в начальное '''

### Выход из машины состояний вручную
async def cancel_handler(message: types.Message, state=FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('Завершено', reply_markup= admin_kb.button_case_admin)




''' Блок выхода из режима администратора '''

async def admin_logout(message: types.Message, state=FSMContext):
    if message.from_user.id == ID:
        await state.finish()
        await message.reply('Вы вышли из режима администратора', reply_markup= client_kb.kb_client)




''' Функция оповещения ответственного оператора о создании нового заказа '''
### Данные для оповещения прилетают из модуля order.py при создании заказа.
### Данные оператора есть в БД в таблице operator_list
async def operator_notifier(order_id, location_id):
    operator_info, item_info, order_info = await sqlite_db.sql_read_new_order_for_operator(order_id, location_id)
    send_order = ''
    op_info= f'{operator_info[0][2]} {operator_info[0][3]}\nК вам поступил заказ:\n\n'
    ord_info = f'ID заказа {order_info[0][1]} | Дата: {order_info[0][3]}\nАдрес самовывоза: {order_info[0][4]}\n\n'
    for i in item_info:
            char = f'{i[3]} | {i[4]} шт | {i[5]} р.\n'
            send_order += char
    await bot.send_message(operator_info[0][1], \
                text=f'{op_info}{ord_info}{send_order}\n\nИтоговая сумма: {order_info[0][6]} руб.\nЗаказ оплачен онлайн')





### Регистрируем хендлеры
def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['login'], is_chat_admin=True)
    dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state="*")
    dp.register_message_handler(admin_logout, Text(equals='logout', ignore_case=True), state=None)
    dp.register_message_handler(cm_start, Text(equals='upload', ignore_case=True), state=None)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_despription, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_message_handler(delete_item_stage1, Text(equals='del', ignore_case=True), state=None)
    dp.register_message_handler(show_menu_item, Text(equals='all item', ignore_case=True), state=None)
    dp.register_message_handler(start_update_item_admin, Text(equals=['edit item'], ignore_case=True), state=None)
    dp.register_message_handler(edit_new_photo_admin, content_types=['photo'], state=FSMAdmin.edit_photo)
    dp.register_message_handler(edit_new_name_admin, state=FSMAdmin.edit_name)
    dp.register_message_handler(edit_new_description_admin, state=FSMAdmin.edit_description)
    dp.register_message_handler(edit_new_price_admin, state=FSMAdmin.edit_price)
    

