# pip3 install OrangePi.GPIO
import OPi.GPIO as GPIO
from options import host, user, password, db
import pymysql
import time
from datetime import datetime
from aiogram.utils import executor
from alarm_mess_send import broadcaster, dp
from core_sensors import temperature

GPIO.setwarnings(False)
GPIO.setboard(GPIO.PCPCPLUS)
GPIO.setmode(GPIO.BOARD)  # по номеру пина на плате от 1 до 40

GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Alarm Input

GPIO.setup(8, GPIO.OUT)  # G1
GPIO.setup(10, GPIO.OUT)  # G2
GPIO.setup(11, GPIO.OUT)  # G3

# GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # IO_4 Lock control не работает
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)  # IO_5 Cooler

# GPIO.setup(8,  GPIO.IN, pull_up_down=GPIO.PUD_UP) #IO_1 Уровень жидкости в увлажнителе
# GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP) #IO_2 Уровень жидкости в увлажнителе
# GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP) #IO_3 Уровень жидкости в увлажнителе


GPIO.setup(15, GPIO.OUT)  # r1
GPIO.setup(16, GPIO.OUT)  # r2
GPIO.setup(18, GPIO.OUT)  # r3
GPIO.setup(22, GPIO.OUT)  # r4
GPIO.setup(26, GPIO.OUT)  # r5
GPIO.setup(27, GPIO.OUT)  # r6
GPIO.setup(28, GPIO.OUT)  # r7
GPIO.setup(29, GPIO.OUT)  # r8
GPIO.setup(31, GPIO.OUT)  # r9
GPIO.setup(32, GPIO.OUT)  # r10
GPIO.setup(33, GPIO.OUT)  # r11
GPIO.setup(35, GPIO.OUT)  # r12 не работает
GPIO.setup(36, GPIO.OUT)  # r13
GPIO.setup(37, GPIO.OUT)  # r14
GPIO.setup(38, GPIO.OUT)  # r15
GPIO.setup(40, GPIO.OUT)  # r16

relayports = [15, 16, 18, 22, 26, 27, 28, 29, 31, 32, 33, 35, 36, 37, 38, 40]

con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
sql = con.cursor()
old = {0:0, 1:0, 2:0}


# Определение уровня влажности и активация/деактивация увлажнителей
def gydroactivation():
    sql = con.cursor()
    try:
        sql.execute("""SELECT gydro0, gydro1, gydro2 FROM avg_sensors ORDER BY id DESC LIMIT 1""")
    except Exception as E:
        param = (datetime.now(), 'GPIO', str(E))
        sql.execute(("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)"""), param)
        con.commit()
    else:
        gydro = sql.fetchone() # УБРАТЬ КОММЕНТАРИЙ
        sql.execute("""select VALUE FROM options WHERE NAME = 'zimalimit'""")
        zimalimit = sql.fetchone()[0]

        sql.execute("""select VALUE FROM options WHERE NAME = 'letolimit'""")
        letolimit = sql.fetchone()[0]

        # Словарь соответствия номеру увлажнителя к пину реле
        G = {0: 8, 1: 10, 2: 11}
        if datetime.now().month in [1, 2, 3, 9, 10, 11, 12]:
            for i in range(3):
                if gydro[i] == None:
                    GPIO.output(G.get(i), 1)  # 0 - выкл
                    humidifier(i, 0)  # 0 - выкл
                else:
                    if gydro[i] <= zimalimit:
                        GPIO.output(G.get(i), 0)  # 0 - вкл
                        humidifier(i, 1)  # 1 - вкл
                    else:
                        GPIO.output(G.get(i), 1)  # 0 - выкл
                        humidifier(i, 0)  # 0 - выкл
        else:
            for i in range(3):

                if gydro[i] == None:
                    # param = (datetime.now(), str(i), 'Проверь датчик вложности ' + str(i))
                    # sql.execute(("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)"""), param)
                    # con.commit()
                    pass
                else:
                    if gydro[i] <= letolimit:
                        GPIO.output(G.get(i), 0)  # 0 - вкл
                        humidifier(i, 1)  # 1 - вкл

                    else:
                        GPIO.output(G.get(i), 1)  # 0 - выкл
                        humidifier(i, 0)  # 0 - выкл

def humidifier(i, val):

    if i == 0:
        if old.get(0) != val:
            old[0] = val
            # print(i, old[i])
            humidifierInsertInDB(i, old[i])

    elif i == 1:
        if old.get(1) != val:
            old[1] = val
            # print(i, old[i])
            humidifierInsertInDB(i, old[i])
    elif i == 2:
        if old.get(2) != val:
            old[2] = val
            # print(i, old[i])
            humidifierInsertInDB(i, old[i])

def humidifierInsertInDB(i, val):

    humidifier = 'humidifier ' + str(i)
    param = (datetime.now(), humidifier, val)
    sql.execute(("""INSERT INTO activity (dttm, trig, val) values (%s, %s, %s)"""), param)
    con.commit()

def GPIORelay():
    try:
        # print('Start listening...')
        state = con.cursor()
    except KeyboardInterrupt:
        GPIO.cleanup()  # Clean GPIO
        con.close()
        # print("Bye.")
    except Exception as E:
        param = (datetime.now(), 'GPIO', str(E))
        sql = con.cursor()
        sql.execute(("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)"""), param)
        con.commit()
    else:
        tm = .5
        state.execute("""select NAME, state from switches ORDER BY num""")
        stateswitches = state.fetchall()
        stateswitches = dict(stateswitches)
        con.commit()

        for i in range(1, 17, 1):
            port = 'chek' + str(i)
            if stateswitches.get(port) == 1:
                GPIO.output(relayports[i - 1], 0)
                # print('port', i, 'включен')
            else:
                GPIO.output(relayports[i - 1], 1)
                # print('port', i, 'выключен')
        time.sleep(tm)

        # Сработка сигнализации. Сообщение в telegram
        if GPIO.input(7) == GPIO.LOW:
            param = (datetime.now())
            sql = con.cursor()
            sql.execute(("""INSERT INTO Alarm (dttm) values (%s)"""), param)
            con.commit()
            executor.start(dp, broadcaster('<b>Внимание! Сработка сигнализации!</b>'))


        # if GPIO.input(12) == GPIO.LOW:
        #     print("LOW")
        # else:
        #     print("HIGH")
        #     # param = (datetime.now())
        #     # sql = con.cursor()
        #     # sql.execute(("""INSERT INTO Alarm (dttm) values (%s)"""), param)
        #     # con.commit()
        #     # executor.start(dp, broadcaster('<b>Внимание! Сработка сигнализации!</b>'))

def cooler():
    try:
        # print('Start listening...')
        sql = con.cursor()
    except KeyboardInterrupt:
        GPIO.output(13, 1)
    except Exception as E:
        param = (datetime.now(), 'GPIO', str(E))
        sql = con.cursor()
        sql.execute(("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)"""), param)
        con.commit()
    else:
        sql.execute("""select VALUE FROM options WHERE NAME = 'cooler'""")
        templimit = sql.fetchone()[0] # Граница температуры активация кулера
        if templimit == None:
            templimit = 30
        temp = temperature()[1]

        sql.execute("""select val from activity ORDER BY dttm DESC LIMIT 1""")
        result = sql.fetchone()
        if result == None:
            btemp = 30
        else:
            btemp = result[0]

        if temp < (templimit - 5):
            GPIO.output(13, 1)
            if btemp == 0:
                param = (datetime.now(), 'cooler', 1)
                sql.execute(("""INSERT INTO activity (dttm, trig, val) values (%s, %s, %s)"""), param)
                con.commit()
        elif temp > (templimit + 5):
            GPIO.output(13, 0)
            if btemp == 1:
                param = (datetime.now(), 'cooler', 0)
                sql.execute(("""INSERT INTO activity (dttm, trig, val) values (%s, %s, %s)"""), param)
                con.commit()
        else:
            pass


def run():

    while True:
        gydroactivation()
        GPIORelay()
        cooler()
        time.sleep(.1)



        # if GPIO.input(8) == GPIO.LOW:
        #     executor.start(dp, broadcaster('Низкий уровень жидкости в увлажнителе воздуха "спальня"'))
        #
        # if GPIO.input(10) == GPIO.LOW:
        #     executor.start(dp, broadcaster('Низкий уровень жидкости в увлажнителе воздуха "гостинная"'))
        #
        # if GPIO.input(11) == GPIO.LOW:
        #     executor.start(dp, broadcaster('Низкий уровень жидкости в увлажнителе воздуха "детская"'))
        #
        # time.sleep(tm)


if __name__ == '__main__':
    run()
