from aiogram import types, Dispatcher
from create_bot import dp, bot




''' Ответ бота на незнакомые ему команды '''
async def echo_send(message : types.Message):
    # await message.answer('Прости, я всего лишь программа, и такая команда мне не знакома. Для коммуникации со мной воспользуйся кнопками ниже.')
    await message.reply('Прости, я всего лишь программа, и такая команда мне не знакома. Для коммуникации со мной воспользуйся кнопками ниже.')




### Регистрируем хендлеры
def register_handlers_other(dp : Dispatcher):
    dp.register_message_handler(echo_send)
