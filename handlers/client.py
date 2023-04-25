from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
from bot_keyboard import client_kb




### Реакция на команду /start
async def command_start(message : types.Message):
    await bot.send_message(message.from_user.id, 'Погнали!', reply_markup=client_kb.kb_client)

### Реакция на "Справка"
async def command_help(message: types.Message):
    await bot.send_message(message.from_user.id, 'Тут подробная информация о правильном использовании бота')

### Реакиция на "Режим работы"
async def pizza_working_hours(message : types.Message):
    await message.answer('Мы работаем круглосуточно, 24/7 !!!')

### Реакция на "Расположение"
async def pizza__location(message : types.Message):
    await message.answer('Наш ларек находится на ул. Воронежская 142')




# async def all_menu_category(message : types.Message):
#     await message.answer('Выберите категорию меню:',reply_markup= client_kb.inline_kb_category)

# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('btn'))
# async def show_category(callback_qwery: types.CallbackQuery):
#     await sqlite_db.sql_read_user(callback_qwery.data.replace('btn ', ''), callback_qwery.from_user.id)


### Регистрируем хендлеры.
def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_help, Text(equals='Справка', ignore_case=True))
    dp.register_message_handler(pizza_working_hours, Text(equals='Режим работы', ignore_case=True))
    dp.register_message_handler(pizza__location, Text(equals='Расположение', ignore_case=True))
    # dp.register_message_handler(all_menu_category, Text(equals='Показать меню', ignore_case=True))

