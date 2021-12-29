from options import host, user, password, db
import pymysql
from datetime import datetime


def sqlfuncselect(*args, **kwargs):
    """
    Общая функция чтения из таблиц
    :param args: pass
    :param kwargs: queryString, param
    :return: resault
    """
    for i in args:
        pass
    param = kwargs.get('param')
    if param == None:
        param = ''
    queryString = kwargs.get('queryString')
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    sql = con.cursor()
    queryString = queryString + param
    sql.execute(queryString)
    resault = sql.fetchall()
    con.commit()
    con.close()
    return resault

def sqlfuncupdateoptions(*args, **kwargs):
    """
    Общая функция записи настроек
    :param args: pass
    :param kwargs: queryString, param
    :return: resault
    """
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    value = kwargs.get('value')
    name = kwargs.get('name')
    param = []
    param.append(value)
    param.append(name)
    sql = con.cursor()
    sql.execute("""UPDATE options SET VALUE = %s WHERE NAME = %s""", param)

    con.commit()
    con.close()

    return None

def sqlfuncupdateswitches(*args, **kwargs):
    """
    Обновляем состояния кнопок
    :param args:
    :param kwargs:
    :return:
    """
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    state = kwargs.get('state')
    name = kwargs.get('name')
    param = []
    param.append(state)
    param.append(name)
    sql = con.cursor()
    sql.execute("""UPDATE switches SET state = %s WHERE name = %s""", param)

    param.insert(0, datetime.now())
    sql.execute("""insert into log (dttm, state, element) values (%s, %s, %s)""", param)
    con.commit()
    con.close()
    return None


def WriteToLogTable(element):
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    param = (datetime.now(), element, 1)
    con.cursor().execute("""insert into log (dttm, element, state) values (%s, %s, %s)""", param)
    con.commit()

def WriteToADS1115Table(value):
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    param = (datetime.now(), value[0], value[1], value[2], value[3])
    con.cursor().execute("""insert into ADS1115_sensors (dt, port0, port1, port2, port3) 
                            values (%s, %s, %s, %s, %s)""", param)
    con.commit()

def temp_clear_options_light(queryString):
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    con.cursor().execute(queryString)
    con.commit()

def update_options_light(queryString, param):
    con = pymysql.connect(host=host, user=user, password=password, db=db, use_unicode=True, charset='utf8')
    con.cursor().execute(queryString, param)
    con.commit()



def sqlfuncinsert(*args, **kwargs):
    pass




