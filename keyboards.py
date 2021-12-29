from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# start
control = KeyboardButton("/Управление")
button2 = KeyboardButton("/Core_Dashboard")
button3 = KeyboardButton("/Home_Dashboard")
button4 = KeyboardButton("/Аквариум")
button5 = KeyboardButton("/Аварии")
button6 = KeyboardButton("/Задания")

start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(control).row(button2, button3).add(
    button4).row(button5, button6)



# Кнопки отправки контакта и геолокации
markup_requests = ReplyKeyboardMarkup(resize_keyboard=True) \
    .add(KeyboardButton('Отправить свой контакт', request_contact=True)).add(
    KeyboardButton('Отправить свою геолокацию', request_location=True))

svet = KeyboardButton("/Освещение")
rozetki = KeyboardButton("/Электропитание")
avtomatica = KeyboardButton("/Автоматика")
back = KeyboardButton("/Назад")

chek1 = KeyboardButton("/Свет1")  # Свет 1
chek2 = KeyboardButton("/Свет2")  # Свет 2
chek3 = KeyboardButton("/Свет3")  # Свет 3
chek4 = KeyboardButton("/Свет4")  # Свет 4
chek5 = KeyboardButton("/Свет5")  # Свет 5
chek6 = KeyboardButton("/Свет6")  # Свет 6
svetbuttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .row(chek1, chek2).row(chek3, chek4).row(chek5, chek6).add(control)
chek6 = KeyboardButton("/chek6")
chek7 = KeyboardButton("/chek7")
chek8 = KeyboardButton("/chek8")
chek9 = KeyboardButton("/chek9")
chek10 = KeyboardButton("/chek10")
chek11 = KeyboardButton("/chek11")
chek12 = KeyboardButton("/chek12")
chek13 = KeyboardButton("/chek13")
chek14 = KeyboardButton("/chek14")
chek15 = KeyboardButton("/chek15")
chek16 = KeyboardButton("/chek16")
back = KeyboardButton("/Назад")

Control = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(svet).add(rozetki).add(avtomatica).add(back)
