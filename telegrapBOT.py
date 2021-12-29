from options import API_TOKEN, userID
from aiogram import Bot, Dispatcher, executor, types
import keyboards as kb
from datetime import datetime
import SQLfunction
from time import sleep

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



@dp.message_handler(commands=['start'])
async def process_hello(message: types.Message):
    if message.chat.id in userID:
        await bot.send_message(message.chat.id, str(message.chat.first_name) + ', привет. \nТебя приветствует система SmartCore! \nAЧто пожелаешь?',
                               reply_markup=kb.start)
    else:
        await bot.send_message(message.chat.id, 'Херня якась! А ты ваще кто? Тебя сюда не звали!')


@dp.message_handler(commands=['Home_Dashboard'])
async def Home_Dashboard(message: types.Message):
    queryString_cur = """SELECT 
                        ROUND(temp0, 1), ROUND(temp1, 1), ROUND(temp2, 1), ROUND(temp3, 1), ROUND(temp4, 1), 
                        ROUND(gydro0, 1), ROUND(gydro1, 1), ROUND(gydro2, 1), ROUND(gydro3, 1), ROUND(gydro4, 1), 
                        baro
                        
                        FROM avg_sensors ORDER BY id DESC LIMIT 1"""
    temp_sensorsLast_cur = SQLfunction.sqlfuncselect(queryString=queryString_cur)

    queryString_cur = """SELECT * FROM (SELECT trig, val FROM activity WHERE trig = 'humidifier 0' ORDER BY dttm DESC LIMIT 1) AS tab1
                                UNION all
                                SELECT * FROM (SELECT trig, val FROM activity WHERE trig = 'humidifier 1' ORDER BY dttm DESC LIMIT 1) AS tab2
                                UNION all
                                SELECT * FROM (SELECT trig, val FROM activity WHERE trig = 'humidifier 2' ORDER BY dttm DESC LIMIT 1) AS tab3"""
    hums = SQLfunction.sqlfuncselect(queryString=queryString_cur)

    data1 =   'Гостинная' + ' ' + str(temp_sensorsLast_cur[0][0]) + ' , °C;   ' + str(temp_sensorsLast_cur[0][5]) + ' , %'
    data2 =  'Спальня'   + ' ' + str(temp_sensorsLast_cur[0][1]) + ' , °C;   ' + str(temp_sensorsLast_cur[0][6]) + ' , %'
    data3 =  'Детская'   + ' ' + str(temp_sensorsLast_cur[0][2]) + ' , °C;   ' + str(temp_sensorsLast_cur[0][7]) + ' , %'
    data4 = 'Балкон'    + ' ' + str(temp_sensorsLast_cur[0][3]) + ' , °C;   ' + str(temp_sensorsLast_cur[0][8]) + ' , %'
    data5 =  'Улица'     + ' ' + str(temp_sensorsLast_cur[0][4]) + ' , °C;   ' + str(temp_sensorsLast_cur[0][9]) + ' , %'
    data6 = 'Давление' + ' ' + str(temp_sensorsLast_cur[0][10]) + ' , мм.рт.ст'

    if hums[0][1] == 1:
        data7 = 'Увлажнитель в гостинной активен'
    else:
        data7 = 'Увлажнитель в гостинной неактивен'

    if hums[1][1] == 1:
        data8 = 'Увлажнитель в спальне активен'
    else:
        data8 = 'Увлажнитель в спальне неактивен'

    if hums[2][1] == 1:
        data9 = 'Увлажнитель в детской активен'
    else:
        data9 = 'Увлажнитель в детской неактивен'


    await message.answer(data1)
    await message.answer(data2)
    await message.answer(data3)
    await message.answer(data4)
    await message.answer(data5)
    await message.answer(data6)
    await message.answer(data7)
    await message.answer(data8)

    await message.answer(data9, reply_markup=kb.start)


@dp.message_handler(commands=['Core_Dashboard'])
async def Core_Dashboard(message: types.Message):
    # Запрос загрузки ядер процессора
    queryString = """SELECT round(((cpunum01) + (cpunum02) + (cpunum03) + (cpunum04)) / 4, 1) 
                                 FROM cpu_load 
                                 GROUP BY hour(dt) order BY dt desc LIMIT 1 """
    cpu = SQLfunction.sqlfuncselect(queryString=queryString)
    cpu = 'Загрузка CPU - ' + str(cpu[0][0]) + ' %'

    # # Запрос загрузки оперативной памяти
    queryString = ("""SELECT round((total/1048576), 1), 
                             round((available/1048576), 1), 
                             round((used/1048576), 1), 
                             round((free/1048576), 1)
                                   FROM RAM 
                                   GROUP BY hour(dt) order BY dt desc LIMIT 1""")
    RAM_all = SQLfunction.sqlfuncselect(queryString=queryString)
    RAM = []
    for i in RAM_all[0]:
        RAM.append(i)
    RAM_total = 'RAM_total - ' + str(RAM[0]) + ' Mb'
    RAM_available = 'RAM_available - ' + str(RAM[1]) + ' Mb'
    RAM_used = 'RAM_used - ' + str(RAM[2]) + ' Mb'
    RAM_free = 'RAM_free - ' + str(RAM[3]) + ' Mb'

    # # Запрос температуры
    queryString = ("""SELECT temp FROM core_temp WHERE DATE(dt) = DATE(CURDATE())
                                    GROUP BY hour(dt)
                                    order BY dt  """)
    temp_all = SQLfunction.sqlfuncselect(queryString=queryString)
    core_temp = 'Температура ядра - ' + str(temp_all[0][0]) + ' °C'

    # # Запрос размер баз MySQL
    queryString = ("""SELECT table_schema "smarthome", round(sum( data_length + index_length )/1024/1024, 2)
                                    FROM information_schema.TABLES GROUP BY table_schema;""")
    MySLQ_all = SQLfunction.sqlfuncselect(queryString=queryString)
    MySQL = 'Размер БД - ' + str(MySLQ_all[0][1]) + ' Mb'

    await message.answer(cpu)

    await message.answer(RAM_total)
    await message.answer(RAM_available)
    await message.answer(RAM_used)
    await message.answer(RAM_free)

    await message.answer(core_temp)

    await message.answer(MySQL, reply_markup=kb.start)


@dp.message_handler(commands=['Аварии'])
async def alerts(message: types.Message):
    queryString = """SELECT id, dttm, functionname, errortext FROM Errors order by id DESC limit 100"""
    Errorslog_all = SQLfunction.sqlfuncselect(queryString=queryString)

    if not any(Errorslog_all):
        await message.answer('Статус системы ОК!', reply_markup=kb.start)

    else:
        await message.answer(Errorslog_all, reply_markup=kb.start)




@dp.message_handler(commands=['Задания'])
async def tasks(message: types.Message):
    await message.answer('Задания', reply_markup=kb.start)


@dp.message_handler(commands=['Управление'])
async def Control(message: types.Message):
    await message.answer('Что прикажете?', reply_markup=kb.Control)


@dp.message_handler(commands=['Освещение'])
async def Osveshenie(message: types.Message):
    await message.answer('Переключить свет?', reply_markup=kb.svetbuttons)


@dp.message_handler(commands=['Свет1'])
async def Osveshenie_1(message: types.Message):
    switches_state = """SELECT state from switches where name = 'chek1'"""
    switches = SQLfunction.sqlfuncselect(queryString=switches_state)
    if switches[0][0] == 1:
        SQLfunction.sqlfuncupdateswitches(name='chek1', state=0)
        await message.answer('Свет1 выкл', reply_markup=kb.svetbuttons)
    else:
        SQLfunction.sqlfuncupdateswitches(name='chek1', state=1)
        await message.answer('Свет1 вкл', reply_markup=kb.svetbuttons)



@dp.message_handler(commands=['Свет2'])
async def Osveshenie_2(message: types.Message):
    switches_state = """SELECT state from switches where name = 'chek2'"""
    switches = SQLfunction.sqlfuncselect(queryString=switches_state)
    if switches[0][0] == 1:
        SQLfunction.sqlfuncupdateswitches(name='chek2', state=0)
    else:
        SQLfunction.sqlfuncupdateswitches(name='chek2', state=1)
    await message.answer('Свет2 изменен', reply_markup=kb.svetbuttons)


@dp.message_handler(commands=['Назад'])
async def back(message: types.Message):
    await message.answer('Главное меню', reply_markup=kb.start)


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def all_other_messages(message: types.Message):
    await message.answer("Я Вас не понял, хозяин", reply_markup=kb.start)


async def alarm_mess():
    await bot.send_message(1078017641, 'message')
    sleep(1)





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
