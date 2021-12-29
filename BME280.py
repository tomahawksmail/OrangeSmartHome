#!/usr/bin/env python
# i2cdetect -y 0
# sudo pip install pimoroni-bme280 smbus
#https://github.com/pimoroni/bme280-python
#______________________________
from options import host, user, password, db
from datetime import datetime
import pymysql
#______________________________
import time
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

from bme280 import BME280
import smbus

bus = 0
bme280 = BME280(i2c_dev=smbus.SMBus(bus))

def main():
    delay = 300

    try:
        con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    except Exception as E:
        param = (datetime.now(), 'tasks', str(E))
        sql = con.cursor()
        sql.execute(("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)"""), param)
        con.commit()
    else:
        try:
            pressure = int(round(bme280.get_pressure() * 0.75, 0))
        except Exception as E:
            pressure = 0
        values = []
        values.append(datetime.now())
        values.append(pressure)
        sql = con.cursor()
        sqlrequest_temp_sensors = "INSERT INTO BME280_sensor (dt, pressure) values (%s, %s)"
        sql.execute(sqlrequest_temp_sensors, values)
        con.commit()
        time.sleep(delay)
    finally:
        con.close()


if __name__ == '__main__':
    while True:
        main()


