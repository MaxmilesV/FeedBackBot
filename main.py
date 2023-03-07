import logging
import sqlite3
import buttons
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Токен бота
API_TOKEN = ''

# Конфигурация входа
logging.basicConfig(level=logging.INFO)

# Инициализация хранилища и подключение БД
storage = MemoryStorage()
connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


# Работа с БД
def user_cheak(chat_id):
    cursor.execute(f"SELECT * FROM users WHERE user_id = {chat_id}")
    result = cursor.fetchall()
    if len(result) == 0:
        cursor.execute(
            f"INSERT INTO users (user_id, is_baned, is_admin) VALUES ({chat_id}, 0, 0)")
        connection.commit()


# Инициализация состояний
class st(StatesGroup):
    answer = State()
    mail = State()
    ban = State()
    unban = State()
    add_admin = State()
    remove_admin = State()


# Приветственное сообщение
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            await message.answer('Добро пожаловать!',
                                 reply_markup=buttons.menu)
        else:
            await message.answer(
                'Напишите ваше сообщение!\nОно будет передано администратору!')
    else:
        await message.answer(
            'Вы были заблокированны!')


# Список забаненных
@dp.message_handler(content_types=['text'], text='Бан-список')
async def ban_list(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            cursor.execute(f"SELECT * FROM users WHERE is_baned == 1")
            result = cursor.fetchall()
            sl = []
            for index in result:
                i = index[0]
                sl.append(i)
            ids = '\n'.join(map(str, sl))
            await message.answer(f'ID пользователей находящихся в ЧС:\n{ids}')


# Блокировка пользователя
@dp.message_handler(content_types=['text'], text='Забанить')
async def ban(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            await message.answer(
                'Введите id пользователя', reply_markup=buttons.cancel)
            await st.ban.set()


# Функция бана
@dp.message_handler(state=st.ban)
async def ban_process(message: types.Message, state: FSMContext):
    if message.text == 'Отменить':
        await message.answer('Отмена!', reply_markup=buttons.menu)
        await state.finish()
    else:
        if message.text.isdigit():
            cursor.execute(
                f"SELECT is_baned FROM users WHERE user_id = {message.text}")
            result = cursor.fetchall()
            connection.commit()
            if len(result) == 0:
                await message.answer(
                    'Такой пользователь не найден в базе данных.',
                    reply_markup=buttons.menu)
                await state.finish()
            else:
                if result[0] == 0:
                    cursor.execute(
                        f"UPDATE users SET is_baned = 1 WHERE user_id = {message.text}")
                    connection.commit()
                    await message.answer('Пользователь успешно заблокирован.',
                                         reply_markup=buttons.menu)
                    await state.finish()
                    await bot.send_message(message.text,
                                           'Вы были заблокированны!')
                else:
                    await message.answer(
                        'Данный пользователь уже заблокирован!',
                        reply_markup=buttons.menu)
                    await state.finish()
        else:
            await message.answer(
                'Не вводите буквы, нужен ID.\nВведите id пользователя')


# Разблокировать пользователя
@dp.message_handler(content_types=['text'], text='Разбанить')
async def unban(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            await message.answer(
                'Введите id пользователя', reply_markup=buttons.cancel)
            await st.unban.set()


# Функция разбана
@dp.message_handler(state=st.unban)
async def unban_process(message: types.Message, state: FSMContext):
    if message.text == 'Отменить':
        await message.answer('Отмена!', reply_markup=buttons.menu)
        await state.finish()
    else:
        if message.text.isdigit():
            cursor.execute(
                f"SELECT is_baned FROM users WHERE user_id = {message.text}")
            result = cursor.fetchall()
            connection.commit()
            if len(result) == 0:
                await message.answer(
                    'Такой пользователь не найден в базе данных.',
                    reply_markup=buttons.menu)
                await state.finish()
            else:
                if result[0] == 1:
                    cursor.execute(
                        f"UPDATE users SET is_baned = 0 WHERE user_id = {message.text}")
                    connection.commit()
                    await message.answer('Пользователь успешно разблокирован.',
                                         reply_markup=buttons.menu)
                    await state.finish()
                    await bot.send_message(message.text,
                                           'Вы были разблокированны!')
                else:
                    await message.answer(
                        'Данный пользователь не заблокирован!',
                        reply_markup=buttons.menu)
                    await state.finish()
        else:
            await message.answer(
                'Не вводите буквы, нужен ID.\nВведите id пользователя')


# Список администраторов
@dp.message_handler(content_types=['text'], text='Админ-список')
async def admin_list(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            cursor.execute(f"SELECT * FROM users WHERE is_admin == 1")
            result = cursor.fetchall()
            sl = []
            for index in result:
                i = index[0]
                sl.append(i)
            ids = '\n'.join(map(str, sl))
            await message.answer(f'ID администраторов:\n{ids}')


# Повышение пользователя
@dp.message_handler(content_types=['text'], text='Повысить')
async def add_admin(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            await message.answer(
                'Введите id пользователя', reply_markup=buttons.cancel)
            await st.add_admin.set()


# Функция повышения
@dp.message_handler(state=st.add_admin)
async def add_admin_process(message: types.Message, state: FSMContext):
    if message.text == 'Отменить':
        await message.answer('Отмена!', reply_markup=buttons.menu)
        await state.finish()
    else:
        if message.text.isdigit():
            cursor.execute(
                f"SELECT is_admin FROM users WHERE user_id = {message.text}")
            result = cursor.fetchall()
            connection.commit()
            if len(result) == 0:
                await message.answer(
                    'Такой пользователь не найден в базе данных.',
                    reply_markup=buttons.menu)
                await state.finish()
            else:
                if result[0] == 0:
                    cursor.execute(
                        f"UPDATE users SET is_admin = 1 WHERE user_id = {message.text}")
                    connection.commit()
                    await message.answer('Пользователь успешно повышен.',
                                         reply_markup=buttons.menu)
                    await state.finish()
                    await bot.send_message(message.text,
                                           'Вы были повышены!')
                else:
                    await message.answer(
                        'Данный пользователь уже администратор!',
                        reply_markup=buttons.menu)
                    await state.finish()
        else:
            await message.answer(
                'Не вводите буквы, нужен ID.\nВведите id пользователя')


# Понизить пользователя
@dp.message_handler(content_types=['text'], text='Разбанить')
async def remove_admin(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            await message.answer(
                'Введите id пользователя', reply_markup=buttons.cancel)
            await st.remove_admin.set()


# Функция понижения
@dp.message_handler(state=st.remove_admin)
async def remove_admin_process(message: types.Message, state: FSMContext):
    if message.text == 'Отменить':
        await message.answer('Отмена!', reply_markup=buttons.menu)
        await state.finish()
    else:
        if message.text.isdigit():
            cursor.execute(
                f"SELECT is_admin FROM users WHERE user_id = {message.text}")
            result = cursor.fetchall()
            connection.commit()
            if len(result) == 0:
                await message.answer(
                    'Такой пользователь не найден в базе данных.',
                    reply_markup=buttons.menu)
                await state.finish()
            else:
                if result[0] == 1:
                    cursor.execute(
                        f"UPDATE users SET is_admin = 0 WHERE user_id = {message.text}")
                    connection.commit()
                    await message.answer('Пользователь успешно понижен.',
                                         reply_markup=buttons.menu)
                    await state.finish()
                    await bot.send_message(message.text,
                                           'Вы были понижены!')
                else:
                    await message.answer(
                        'Данный пользователь не администратор!',
                        reply_markup=buttons.menu)
                    await state.finish()
        else:
            await message.answer(
                'Не вводите буквы, нужен ID.\nВведите id пользователя')


# Рассылка
@dp.message_handler(content_types=['text'], text='Рассылка')
async def mail(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            await message.answer(
                "Введите текст для рассылки", reply_markup=buttons.cancel)
            await st.mail.set()


# Функция рассылки
@dp.message_handler(state=st.mail)
async def mail_process(message: types.Message, state: FSMContext):
    cursor.execute(f'SELECT user_id FROM users')
    row = cursor.fetchall()
    connection.commit()
    text = message.text
    if message.text == 'Отменить':
        await message.answer('Отмена!', reply_markup=buttons.menu)
        await state.finish()
    else:
        await message.answer('Рассылка начата!', reply_markup=buttons.menu)
        for i in range(len(row)):
            try:
                await bot.send_message(row[i][0], str(text))
            except Exception:
                pass
        await message.answer('Рассылка завершена!', reply_markup=buttons.menu)
        await state.finish()


# Уведомление о вопросе
@dp.message_handler(content_types=['text'])
async def question(message: types.Message):
    user_cheak(chat_id=message.chat.id)
    cursor.execute(
        f"SELECT is_baned FROM users WHERE user_id = {message.chat.id}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(
            f"SELECT is_admin FROM users WHERE user_id = {message.chat.id}")
        result = cursor.fetchone()
        if result[0] == 1:
            pass
        else:
            await message.answer('Сообщение успешно отправленно!')
            cursor.execute(f'SELECT user_id FROM users WHERE is_admin = 1')
            row = cursor.fetchall()
            connection.commit()
            for i in range(len(row)):
                await bot.send_message(row[i][0],
                                       f"<b>Получен новый "
                                       f"вопрос!</b>\n<b>От:</b> "
                                       f"{message.from_user.mention}\nID: "
                                       f"{message.chat.id}\n<b>Сообщение:</b> {message.text}",
                                       reply_markup=buttons.answer_function(
                                           message.chat.id),
                                       parse_mode='HTML')
    else:
        await message.answer('Вы заблокированны в боте.')


# Ответ пользователю
@dp.callback_query_handler(lambda call: True)
async def answer(call, state: FSMContext):
    if 'ans' in call.data:
        a = call.data.index('-ans')
        ids = call.data[:a]
        await call.message.answer('Введите ответ:',
                                  reply_markup=buttons.cancel)
        await st.answer.set()
        await state.update_data(uid=ids)
    elif 'ignor' in call.data:
        await call.answer('Удалено')
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await state.finish()


# Функция ответа пользователю
@dp.message_handler(state=st.answer)
async def answer_process(message: types.Message, state: FSMContext):
    if message.text == 'Отменить':
        await message.answer('Отмена!', reply_markup=buttons.menu)
        await state.finish()
    else:
        await message.answer('Сообщение отправлено.',
                             reply_markup=buttons.menu)
        data = await state.get_data()
        id = data.get("uid")
        await state.finish()
        await bot.send_message(id,
                               f'Вам поступил ответ от администратора:\nТекст: {message.text}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
