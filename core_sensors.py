#!/usr/bin/python3
from options import host, user, password, db
from datetime import datetime
import sys
import time
import psutil
import pymysql



if not hasattr(psutil.Process, "cpu_num"):
    sys.exit("platform not supported")

# Обработчик загрузки процессора, возвращает список cpu_load
def cpuload():
    num_cpus = psutil.cpu_count()
    cpus_percent = psutil.cpu_percent(percpu=True)
    cpu_load = []
    for _ in range(num_cpus):
        cpu_load.append(cpus_percent.pop(0))
    cpu_load.insert(0, datetime.now())
    cpufreq = int(psutil.cpu_freq()[0])
    cpu_load.append(cpufreq)
    return cpu_load

# Обработчик оперативки, возвращает список RAM
def memload():
    virtual_memory = psutil.virtual_memory()
    RAM = list(virtual_memory)
    RAM.insert(0, datetime.now())
    return RAM

# Обработчик температуры, возвращает список temp
def temperature():
    temp = []
    if not hasattr(psutil, "sensors_temperatures"):
        sys.exit("platform not supported")
    temps = psutil.sensors_temperatures()
    if not temps:
        sys.exit("can't read any temperature")
    for name, entries in temps.items():
        for entry in entries:
            temp.append(datetime.now())
            temp.append(entry.current)
            return temp




def insert_in_db(cpuload, memload, temperature):

    try:
        con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    except Exception as E:
        param = (datetime.now(), 'tasks', str(E))
        sql = con.cursor()
        sql.execute(("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)"""), param)
        con.commit()
    else:
        sql = con.cursor()
        sql.execute("""SELECT VALUE FROM options WHERE NAME = 'cooler'""")
        cooler = sql.fetchone()


        cpuload = cpuload()
        memload = memload()

        temp = temperature()
        # print(temp)
        param = []
        param.append(temp[0])
        param.append(temp[1])
        param.append(cooler[0])
        # print(param)

        if temp[1] > 50:
            sql = con.cursor()
            param = (datetime.now(), 'core_sensors', 'cpu temperature is too high, ' + str(round(temp[1], 0)) + ' °C')
            sql.execute("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)""", param)
        con.commit()


        sql = con.cursor()
        sqlrequestCPU = "INSERT INTO cpu_load (dt, cpunum01, cpunum02, cpunum03, cpunum04, cpufreq) values (%s, %s, %s, %s, %s, %s)"
        sql.execute(sqlrequestCPU, cpuload)
        con.commit()


        sql = con.cursor()
        sqlrequestRAM = "INSERT INTO RAM (dt, total, available, percent, used, free, active, inactive, buffers, cached, SHAR, slab) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sql.execute(sqlrequestRAM, memload)
        con.commit()

        sql = con.cursor()
        sqlrequestTemp = "INSERT INTO core_temp (dt, temp, cooler) values (%s, %s, %s)"
        sql.execute(sqlrequestTemp, param)
        con.commit()

    finally:
        con.close()

def run():
    while True:
        insert_in_db(cpuload, memload, temperature)
        time.sleep(300)

if __name__ == '__main__':
    run()