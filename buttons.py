from aiogram import types

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    types.KeyboardButton('Бан-список'),
    types.KeyboardButton('Забанить'),
    types.KeyboardButton('Разбанить')
)
menu.add(
    types.KeyboardButton('Админ-список'),
    types.KeyboardButton('Повысить'),
    types.KeyboardButton('Понизить')
)
menu.add(types.KeyboardButton('Рассылка'))

cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add(
    types.KeyboardButton('Отменить')
)


def answer_function(user_id):
    answer = types.InlineKeyboardMarkup(row_width=3)
    answer.add(
        types.InlineKeyboardButton(text='Ответить',
                                   callback_data=f'{user_id}-ans'),
        types.InlineKeyboardButton(text='Пропустить', callback_data='ignor')
    )
    return answer
