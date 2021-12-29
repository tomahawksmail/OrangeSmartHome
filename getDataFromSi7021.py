import requests
from options import host, user, password, db, IPsensors
from time import sleep
import pymysql
from datetime import datetime
import SQLfunction

delay = 300


def append_to_list(num, humidity, temperature, IP):
    values = []
    values.append(num)
    values.append(datetime.now())
    values.append(temperature)
    values.append(humidity)
    values.append(IP)
    # print(values)
    return values


def senddata():
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    sql = con.cursor()
    for IPadres in IPsensors:
            num = IPsensors.index(IPadres)
            IPadres = IPadres + '/data'
            try:
                data = requests.get(IPadres).content.decode('UTF-8').split(',')
            except Exception as E:
                # Раскомментировать когда будет 5 датчикофф
                # if type(E) == requests.exceptions.ConnectionError:
                #     param = (datetime.now(), "getDataFromSi7021", f"Connection failed with host {IPadres[7:-5]}")
                #     sql.execute(("""INSERT INTO Errors (dttm, functionname, errortext) values (%s, %s, %s)"""), param)
                #     con.commit()
                list = append_to_list(num, humidity=0, temperature=0, IP=IPadres[7:-5])
            else:
                ip, humidity, temperature = data
                if temperature == 'nan':
                    continue
                temperature = round(float(float(temperature)-0.9), 2)
                list = append_to_list(num, humidity, temperature, IP=ip)
            sql.execute("""INSERT INTO Si7021_sensors (num, dt, temp, gydro, IPadr) values (%s, %s, %s, %s, %s)""", list)
            con.commit()


if __name__ == '__main__':
    while True:
        senddata()
        sleep(delay)
