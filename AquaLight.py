from options import host, user, password, db
import pymysql
from datetime import timedelta, datetime
import time
channels = 5

def lightTimeOn(num):
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    sql = con.cursor()
    dicton = []
    param = []
    param.append('minon'+str(num))
    param.append('houron'+str(num))
    queryString = """SELECT ((val*60*60) + (select (val*60) 
                    FROM AquaLight WHERE Selected = 1 AND NAME = %s)) AS time FROM AquaLight WHERE Selected = 1 AND NAME = %s"""
    sql.execute(queryString, param)
    resault = sql.fetchone()
    resault = timedelta(seconds=resault[0])
    dicton.append(resault)
    return dicton

def lightTimeOff(num):
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    sql = con.cursor()
    dictoff = []
    param = []
    param.append('minoff'+str(num))
    param.append('houroff'+str(num))
    queryString = """SELECT ((val*60*60) + (select (val*60) 
                    FROM AquaLight WHERE Selected = 1 AND NAME = %s)) AS time FROM AquaLight WHERE Selected = 1 AND NAME = %s"""
    sql.execute(queryString, param)
    resault = sql.fetchone()
    resault = timedelta(seconds=resault[0])
    dictoff.append(resault)
    return dictoff

def run():
    while True:
        for t in range(1, channels+1, 1):
            dataOn = lightTimeOn(t)
            dataOff = lightTimeOff(t)
            now = timedelta(hours=datetime.now().time().hour, minutes=datetime.now().time().minute, seconds=datetime.now().time().second)
            if (dataOn[0] < now) and (dataOff[0] > now):
                print(t, 'Activ') # Включаем канал t
            else:
                print(t, 'Desactiv') # Выключаем канал t

        time.sleep(10)
if __name__ == '__main__':
    run()