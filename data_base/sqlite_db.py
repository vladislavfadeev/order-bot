import sqlite3 as sq
import uuid
from create_bot import dp, bot





''' Подключение к базе данных при запуске бота '''
def sql_start():
    global base, cur
    base = sq.connect('data_base/db/order_bot.db')
    cur = base.cursor()
    if base:
        print('Data base connected!')
    base.execute('CREATE TABLE IF NOT EXISTS menu(product_id TEXT PRIMARY KEY, category TEXT , img TEXT, name TEXT, description TEXT, price TEXT)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS orders(user_id TEXT, order_id TEXT, product_id TEXT, name TEXT, quantity TEXT, price_item TEXT)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS orders_list(user_id TEXT, order_id TEXT, order_no TEXT PRIMARY KEY, date TEXT, time TEXT, adress TEXT, order_summ TEXT)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS operator_list(No TEXT, user_id TEXT, name TEXT PRIMARY KEY, last_name TEXT, location TEXT)')
    base.commit()



''' Внесение нового товара в базу данных '''
### Внесение производится в режиме администратора в модуле admin.py
async def sql_add_command(state):
    char = str(uuid.uuid4())[:7]
    async with state.proxy() as data:
        data1 = tuple(data.values())
        cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?, ?, ?)', (char, data1[0], data1[1], data1[2], data1[3], data1[4]))
        base.commit()




''' Удаление выбранного товара из корзины в режиме администратора '''
### Удаление производится в режиме администратора в модуле admin.py
async def sql_delete_command(product_id):
    cur.execute('DELETE FROM menu WHERE product_id == ?', (product_id,))
    base.commit()




''' Методы работы со списком товаров '''
### Вывод товаров из указанных категорий в режиме администратора без редактирования и ввода в какое-либо состояние.
### В идеале убрать, и оставить только функцию ниже, но необходимо добавить в ссылающуюся функцию возможность отправки сообщений через цикл.
async def sql_read_user(data, user):
    for ret in cur.execute('SELECT * FROM menu WHERE category == ?', (data,)).fetchall():
        await bot.send_photo(user, ret[2], f'{ret[3]}\nОписание: {ret[4]}\nЦена {ret[5]}')

### Вывод всех товаров из указанных категорий.
async def sql_read_user_order(data):
    return cur.execute('SELECT * FROM menu WHERE category == ?', (data,)).fetchall()
    # for ret in cur.execute('SELECT * FROM menu WHERE category == ?', (data,)).fetchall():
    #     await bot.send_photo(user, ret[1], f'{ret[2]}\nОписание: {ret[3]}\nЦена {ret[4]}',\
    #         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Добавить в корзину', callback_data=f'add_to_cart {ret[2]}')))




''' Методы работы с содержимым корзины '''
### Добавление выбранных товаров в корзину. Товары добавляются по одному. Это только состав корзины.
async def sql_add_to_cart( user_id, order_id, product_id, quantity):
    char = cur.execute('SELECT * FROM menu WHERE product_id == ?', (product_id,))
    for i in char:
        cur.execute('INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)', (user_id, order_id, product_id, i[3], quantity, i[5],))
        base.commit()

### Вывод содержимого корзины единым списком для просмотра.
async def sql_open_user_cart(order_id):
    return cur.execute('SELECT * FROM orders WHERE order_id == ?', (order_id, ))

### Вывод содержимого корзины попозиционно для редактирования.
async def sql_open_user_cart_for_edit(order_id):
    item_list = []
    quantity_list = []
    for i in cur.execute('SELECT * FROM orders WHERE order_id == ?', (order_id, )).fetchall():
        item_list.append(cur.execute('SELECT * FROM menu WHERE product_id == ?', (i[2],) ).fetchall())
        quantity_list.append(i[4])
    return item_list, quantity_list

### Удаление позиции из корзины.
async def sql_del_item_from_cart(order_id, product_id):
    cur.execute('DELETE FROM orders WHERE order_id == ? AND product_id == ?', (order_id, product_id, ))
    base.commit()

### Удаление заказа целиком.
async def sql_del_order_from_cart(order_id):
    cur.execute('DELETE FROM orders WHERE order_id == ?', (order_id, ))
    base.commit()

### Изменение количества определенного товара в корзине.
async def sql_replace_item_q_from_cart(order_id, product_id, new_q):
    cur.execute('UPDATE orders SET quantity = ? WHERE order_id == ? AND product_id == ?', (new_q, order_id, product_id, ))
    base.commit()

### Зпись сформированного заказа в базу данных.
async def sql_add_ready_order(user_id, order_id, date, time, adress, order_sum):
    order_no = len(tuple(cur.execute('SELECT order_no FROM orders_list')))
    order_no += 1
    cur.execute('INSERT INTO orders_list VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, order_id, order_no, date, time, adress, order_sum,))
    base.commit()




''' Работа с блоком радактирования данных товаров в admin.py '''
### Замена фото товара.
async def sql_replace_new_foto_admin(photo_id, product_id):
    cur.execute('UPDATE menu SET img = ? WHERE product_id == ?', (photo_id, product_id, ))
    base.commit()

### Замена названия товара.
async def sql_replace_new_name_admin(name, product_id):
    cur.execute('UPDATE menu SET name = ? WHERE product_id == ?', (name, product_id, ))
    base.commit()

### Замена описания товара.
async def sql_replace_new_description_admin(text, product_id):
    cur.execute('UPDATE menu SET description = ? WHERE product_id == ?', (text, product_id, ))
    base.commit()

### Замена цены товара.
async def sql_replace_new_price_admin(n_price, product_id):
    cur.execute('UPDATE menu SET price = ? WHERE product_id == ?', (n_price, product_id, ))
    base.commit()




''' Выбока информации из базы данных для оповещения оператора о новом заказе '''
### Оповещение оператора производится в модуле admin.py
async def sql_read_new_order_for_operator(order_id, location_id):
    item_info = cur.execute('SELECT * FROM orders WHERE order_id == ?', (order_id, )).fetchall()
    operator_info = cur.execute('SELECT * FROM operator_list WHERE location == ?', (location_id,)).fetchall()
    order_info = cur.execute('SELECT * FROM orders_list WHERE order_id == ?', (order_id, )).fetchall()
    return operator_info, item_info, order_info 




''' Вывод истории заказа запрашивающего юзера '''
async def sql_show_order_history(user_id):
    return cur.execute('SELECT * FROM orders_list WHERE user_id == ?', (user_id, ))






### Не используется. Внесение информации в БД из текущего состояния.
async def sql_open_order(state):
    async with state.proxy() as data:
        cur.execute(('INSERT INTO orders VALUES (?, ?, ?, ?, ?)', tuple(data.values())))
        base.commit()

### Не используется. Вывод абсолютно всех товаров из всех категорий.
async def sql_read2():
    return cur.execute('SELECT * FROM menu').fetchall()
