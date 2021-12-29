from flask import Flask, render_template, request, session, redirect, flash, escape, make_response
from options import version, whiteIP, IPsensors
from datetime import datetime, timedelta
import subprocess
import SQLfunction
import requests
# import io
import sys
import os

from disc import discfunc, uptime

app = Flask(__name__)
app.secret_key = 'admin'


@app.route("/", methods=['POST', 'GET'])
def start():
    remote_ip = request.headers.get('X-Forwarded-For')
    if not remote_ip:
        remote_ip = request.remote_addr
    if remote_ip in whiteIP:
        return redirect("/weather")
    return redirect("/login")

@app.route("/logout", methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    flash('Вы вышли из системы')
    return redirect("/login")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form["user"] != 'admin' or request.form["password"] != app.secret_key:
            flash("Не верный логин или пароль")
            return redirect("/login")
        elif request.form["user"] == 'admin' and request.form["password"] == app.secret_key:
            session['user'] = request.form['user']
            return redirect("/weather")
    else:
        pass
    return render_template('login.html', version=version)


@app.route("/control", methods=['POST', 'GET'])
def control():
    if 'user' in session:
        queryString = """Select name, state from switches WHERE num BETWEEN 1 AND 16"""
        if request.method == 'GET':
            stateswitches = dict(SQLfunction.sqlfuncselect(queryString=queryString))  # Словарь
            return render_template('control.html', version=version, stateswitches=stateswitches)


        elif request.method == 'POST':
            if "change" in request.form:
                for i in range(1,17,1):

                    tempsw = request.form.get('switch-{}'.format(i))
                    if tempsw is None:
                        switch1 = 0
                    else:
                        switch1 = 1
                    SQLfunction.sqlfuncupdateswitches(name='chek{}'.format(i), state=switch1)


                stateswitches = dict(SQLfunction.sqlfuncselect(queryString=queryString))

            return render_template('control.html', version=version, stateswitches=stateswitches)
    else:
        flash("You are not logged in")
        return redirect("/login")



@app.route("/control2", methods=['POST', 'GET'])
def control2():
    if 'user' in session:
        queryString = """Select name, state from switches WHERE num BETWEEN 17 AND 32"""
        if request.method == 'GET':
            stateswitches = dict(SQLfunction.sqlfuncselect(queryString=queryString))  # Словарь
            return render_template('control2.html', version=version, stateswitches=stateswitches)


        elif request.method == 'POST':
            if "change" in request.form:
                for i in range(17,33,1):
                    tempsw = request.form.get('switch-{}'.format(i))
                    if tempsw is None:
                        switch1 = 0
                    else:
                        switch1 = 1
                    SQLfunction.sqlfuncupdateswitches(name='chek{}'.format(i), state=switch1)
                stateswitches = dict(SQLfunction.sqlfuncselect(queryString=queryString))
            return render_template('control2.html', version=version, stateswitches=stateswitches)
    else:
        flash("You are not logged in")
        return redirect("/login")




@app.route("/alerts", methods=['POST', 'GET'])
def alerts():

    if 'user' in session:
        if request.method == 'GET':
            queryString = """SELECT id, dttm, functionname, errortext
                                            FROM Errors order by id DESC limit 100"""
            Errorslog_all = SQLfunction.sqlfuncselect(queryString=queryString)
            return render_template('alerts.html', version=version, Errorslog_all=Errorslog_all)

        elif request.method == 'POST':
            if "btn" in request.form:
                queryString = """DELETE FROM Errors"""
                Errorslog_all = SQLfunction.sqlfuncselect(queryString=queryString)
                queryString = """SELECT id, dttm, functionname, errortext
                                                            FROM Errors order by id DESC limit 100"""
                Errorslog_all = SQLfunction.sqlfuncselect(queryString=queryString)
            return render_template('alerts.html', version=version, Errorslog_all=Errorslog_all)

    else:
        flash("You are not logged in")
        return redirect("/login")



@app.route("/activation", methods=['POST', 'GET'])
def activation():
    if 'user' in session:


        if request.method == 'GET':
            queryString = """select dttm, val from activity where trig = "cooler" and date(dttm) between (curdate() - interval 5 day) and curdate() order by dttm"""
            cooler = SQLfunction.sqlfuncselect(queryString=queryString)

            queryString = """select dttm, val from activity where trig = "humidifier 0" and date(dttm) between (curdate() - interval 1 day) and curdate() order by dttm"""
            humidifier0 = SQLfunction.sqlfuncselect(queryString=queryString)

            queryString = """select dttm, val from activity where trig = "humidifier 1" and date(dttm) between (curdate() - interval 1 day) and curdate() order by dttm"""
            humidifier1 = SQLfunction.sqlfuncselect(queryString=queryString)

            queryString = """select dttm, val from activity where trig = "humidifier 2" and date(dttm) between (curdate() - interval 1 day) and curdate() order by dttm"""
            humidifier2 = SQLfunction.sqlfuncselect(queryString=queryString)

            return render_template('activation.html', version=version, cooler=cooler, humidifier0=humidifier0, humidifier1=humidifier1, humidifier2=humidifier2)

        elif request.method == 'POST':
            pass

    else:
        flash("You are not logged in")
        return redirect("/login")



@app.route("/core_dashboard", methods=['POST', 'GET'])
def core_dashboard():
    if 'user' in session:
        if request.method == 'POST':
            pass

        elif request.method == 'GET':

            dttm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uptimestr = timedelta(minutes=uptime())

            discs = discfunc()
            disca = []

            disca.append(discs[0][0])
            disca.append(float(discs[0][1][:-1]))
            disca.append(float(discs[0][2][:-1]))
            disca.append(float(discs[0][3][:-1]))
            disca.append(discs[0][4])
            disca.append(discs[0][5])
            disca.append(discs[0][6])


            # Запрос загрузки ядер процессора
            queryString = """SELECT DATE_FORMAT(dt, '%k'),  cpunum01, cpunum02, cpunum03, cpunum04, cpufreq
                                   FROM cpu_load WHERE date(dt) = (curdate() - interval 1 day) GROUP BY hour(dt)
                                   UNION ALL
                                   SELECT DATE_FORMAT(dt, '%k'),  cpunum01, cpunum02, cpunum03, cpunum04, cpufreq
                                   FROM cpu_load WHERE date(dt) = curdate() GROUP BY hour(dt)"""
            cpu_load_all = SQLfunction.sqlfuncselect(queryString=queryString)

            # # Запрос загрузки оперативной памяти
            queryString = ("""SELECT DATE_FORMAT(dt, '%k'), (total/1048576), (available/1048576), 
                                   (used/1048576), (free/1048576) 
                                   FROM RAM  WHERE date(dt) = (curdate() - interval 1 day) GROUP BY hour(dt)
                                   UNION ALL
                                   SELECT DATE_FORMAT(dt, '%k'), (total/1048576), (available/1048576), 
                                   (used/1048576), (free/1048576) 
                                   FROM RAM  WHERE date(dt) = curdate() GROUP BY hour(dt)""")
            RAM_all = SQLfunction.sqlfuncselect(queryString=queryString)

            # # Запрос температуры
            queryString = ("""SELECT DATE_FORMAT(dt, '%k'), temp, cooler FROM core_temp  WHERE date(dt) = (curdate() - interval 1 day) GROUP BY hour(dt)
                                UNION ALL
                                SELECT DATE_FORMAT(dt, '%k'), temp, cooler FROM core_temp  WHERE date(dt) = curdate() GROUP BY hour(dt)""")
            temp_all = SQLfunction.sqlfuncselect(queryString=queryString)

            # # Запрос размер баз MySQL
            queryString = ("""SELECT table_schema "smarthome", round(sum( data_length + index_length )/1024/1024, 2)
                                FROM information_schema.TABLES GROUP BY table_schema;""")
            MySLQ_all = SQLfunction.sqlfuncselect(queryString=queryString)

            # # Запрос сработки сигнализации
            queryString = ("""SELECT dttm from (SELECT * FROM Alarm ORDER BY id DESC LIMIT 10) temp ORDER BY id""")
            Alarms = SQLfunction.sqlfuncselect(queryString=queryString)

            # # Запрос Аварий и ошибок
            queryString = ("""SELECT * from (SELECT * FROM Errors ORDER BY id DESC LIMIT 10) temp ORDER BY id""")
            Errorslog_all = SQLfunction.sqlfuncselect(queryString=queryString)

            return render_template('core_dashboard.html', version=version, disca=disca,
                                   uptimestr=uptimestr,
                                   cpu_load_all=cpu_load_all, RAM_all=RAM_all, temp_all=temp_all,
                                   MySLQ_all=MySLQ_all, dttm=dttm, Errorslog_all=Errorslog_all, Alarms=Alarms)

    else:
        flash("You are not logged in")
        return redirect("/login")


@app.route("/house_dashboard", methods=['POST', 'GET'])
def house_dashboard():

    if 'user' in session:
        if request.method == 'POST':
            pass

        elif request.method == 'GET':
            # Запрос temp_sensors
            queryString_0 = """SELECT DATE_FORMAT(dt, '%k'),    temp0,  baro, gydro0, 
                                                                temp1,        gydro1, 
                                                                temp2,        gydro2, 
                                                                temp3,        gydro3, 
                                                                temp4,        gydro4

                                FROM avg_sensors   WHERE date(dt) = (curdate() - interval 1 day) GROUP BY hour(dt)
                                UNION ALL
                                SELECT DATE_FORMAT(dt, '%k'),   temp0,  baro, gydro0, 
                                                                temp1,        gydro1, 
                                                                temp2,        gydro2, 
                                                                temp3,        gydro3, 
                                                                temp4,        gydro4

                                FROM avg_sensors   WHERE date(dt) = curdate() GROUP BY hour(dt)"""
            temp_sensor_0 = SQLfunction.sqlfuncselect(queryString=queryString_0)

            queryString_cur = """SELECT 
                                    ROUND(temp0, 1), ROUND(temp1, 1), ROUND(temp2, 1), ROUND(temp3, 1), ROUND(temp4, 1), 
                                    ROUND(gydro0, 1), ROUND(gydro1, 1), ROUND(gydro2, 1), ROUND(gydro3, 1), ROUND(gydro4, 1), 
                                    baro
                                    
                                    FROM avg_sensors ORDER BY id DESC LIMIT 1"""

            temp_sensorsLast_cur = SQLfunction.sqlfuncselect(queryString=queryString_cur)

            return render_template('house_dashboard.html',
                                   temp_sensor_0=temp_sensor_0,
                                   temp_sensorsLast_cur=temp_sensorsLast_cur,
                                   version=version)
    else:
        flash("You are not logged in")
        return redirect("/login")


@app.route("/masterlog", methods=['POST', 'GET'])
def masterlog():
    queryString = 'SELECT * FROM log order by id DESC limit 100'
    param = ''
    log = SQLfunction.sqlfuncselect(table='log', queryString = queryString, param = param)
    return render_template('masterlog.html', version=version, log=log)


@app.route("/aquarium", methods=['POST', 'GET'])
def aquarium():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        queryString = """SELECT hour(dt), round(PORT0,2), round(PORT1), round(PORT2), round(PORT3) FROM ADS1115_sensors 
        WHERE date(dt) = (CURDATE() - interval 1 DAY) GROUP BY hour(dt)
        UNION
        SELECT hour(dt), round(PORT0,2), round(PORT1), round(PORT2), round(PORT3) FROM ADS1115_sensors 
        WHERE date(dt) = CURDATE() GROUP BY hour(dt)"""
        param = ''
        data = SQLfunction.sqlfuncselect(table='ADS1115_sensors', queryString=queryString, param=param)

        queryString = 'SELECT dt, round(PORT0,2), round(PORT1), round(PORT2), round(PORT3) FROM ADS1115_sensors ORDER BY id DESC LIMIT 1'
        param = ''
        datanow = SQLfunction.sqlfuncselect(table='ADS1115_sensors', queryString=queryString, param=param)

        return render_template('aquarium.html', version=version, data=data, datanow=datanow)


@app.route("/options", methods=['POST', 'GET'])
def options():
    if 'user' in session:
        if request.method == 'GET':
            queryString = '''select VALUE FROM options WHERE NAME = "cooler" '''
            cooler = SQLfunction.sqlfuncselect(queryString=queryString)
            cooler = cooler[0][0]

            queryString = '''select VALUE FROM options WHERE NAME = "zimalimit" '''
            zimalimit = SQLfunction.sqlfuncselect(queryString=queryString)
            zimalimit = zimalimit[0][0]

            queryString = '''select VALUE FROM options WHERE NAME = "letolimit" '''
            letolimit = SQLfunction.sqlfuncselect(queryString=queryString)
            letolimit = letolimit[0][0]

            queryString = '''select VALUE FROM options WHERE NAME = "AquaHeater" '''
            AquaHeater = SQLfunction.sqlfuncselect(queryString=queryString)
            AquaHeater = AquaHeater[0][0]

            queryString = '''select VALUE FROM options WHERE NAME = "AquaCooler" '''
            AquaCooler = SQLfunction.sqlfuncselect(queryString=queryString)
            AquaCooler = AquaCooler[0][0]

            houron1 = []
            houron2 = []
            houron3 = []
            houron4 = []
            houron5 = []
            for i in range(1, 6, 1):
                param = "'" + 'houron' + str(i) + "'"
                queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                for kort in result:

                    if kort[0] == 'houron1':
                        d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houron1.append(d1)
                    elif kort[0] == 'houron2':
                        d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houron2.append(d2)
                    elif kort[0] == 'houron3':
                        d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houron3.append(d3)
                    elif kort[0] == 'houron4':
                        d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houron4.append(d4)
                    elif kort[0] == 'houron5':
                        d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houron5.append(d5)

            houroff1 = []
            houroff2 = []
            houroff3 = []
            houroff4 = []
            houroff5 = []
            for i in range(1, 6, 1):
                param = "'" + 'houroff' + str(i) + "'"
                queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                for kort in result:

                    if kort[0] == 'houroff1':
                        d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houroff1.append(d1)
                    elif kort[0] == 'houroff2':
                        d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houroff2.append(d2)
                    elif kort[0] == 'houroff3':
                        d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houroff3.append(d3)
                    elif kort[0] == 'houroff4':
                        d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houroff4.append(d4)
                    elif kort[0] == 'houroff5':
                        d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        houroff5.append(d5)

            minon1 = []
            minon2 = []
            minon3 = []
            minon4 = []
            minon5 = []
            for i in range(1, 6, 1):
                param = "'" + 'minon' + str(i) + "'"
                queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                for kort in result:

                    if kort[0] == 'minon1':
                        d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minon1.append(d1)
                    elif kort[0] == 'minon2':
                        d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minon2.append(d2)
                    elif kort[0] == 'minon3':
                        d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minon3.append(d3)
                    elif kort[0] == 'minon4':
                        d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minon4.append(d4)
                    elif kort[0] == 'minon5':
                        d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minon5.append(d5)

            minoff1 = []
            minoff2 = []
            minoff3 = []
            minoff4 = []
            minoff5 = []
            for i in range(1, 6, 1):
                param = "'" + 'minoff' + str(i) + "'"
                queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                for kort in result:

                    if kort[0] == 'minoff1':
                        d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minoff1.append(d1)
                    elif kort[0] == 'minoff2':
                        d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minoff2.append(d2)
                    elif kort[0] == 'minoff3':
                        d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minoff3.append(d3)
                    elif kort[0] == 'minoff4':
                        d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minoff4.append(d4)
                    elif kort[0] == 'minoff5':
                        d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                        minoff5.append(d5)




            # options = [
            #     {"Label": "Joe", "Selected": False},
            #     {"Label": "Ivan", "Selected": False},
            #     {"Label": "Steve", "Selected": True}
            # ]



            return render_template('options.html', version=version, cooler=cooler, zimalimit=zimalimit,
                                   letolimit=letolimit, AquaCooler=AquaCooler, AquaHeater=AquaHeater,

                                   houron1=houron1, houron2=houron2,
                                   houron3=houron3, houron4=houron4,
                                   houron5=houron5, houroff1=houroff1,
                                   houroff2=houroff2, houroff3=houroff3,
                                   houroff4=houroff4, houroff5=houroff5,

                                   minon1=minon1, minoff1=minoff1,
                                   minon2=minon2, minoff2=minoff2,
                                   minon3=minon3, minoff3=minoff3,
                                   minon4=minon4, minoff4=minoff4,
                                   minon5=minon5, minoff5=minoff5)


        elif request.method == 'POST':
            if "save" in request.form:

                cooler = request.form.get('Cooler')
                SQLfunction.sqlfuncupdateoptions(name='cooler', value=cooler)

                zimalimit = request.form.get('zimalimit')
                SQLfunction.sqlfuncupdateoptions(name='zimalimit', value=zimalimit)

                letolimit = request.form.get('letolimit')
                SQLfunction.sqlfuncupdateoptions(name='letolimit', value=letolimit)

                AquaHeater = request.form.get('AquaHeater')
                SQLfunction.sqlfuncupdateoptions(name='AquaHeater', value=AquaHeater)

                AquaCooler = request.form.get('AquaCooler')
                SQLfunction.sqlfuncupdateoptions(name='AquaCooler', value=AquaCooler)
                # Очищаем
                queryString = ('''UPDATE AquaLight SET Selected = 0''')
                SQLfunction.temp_clear_options_light(queryString=queryString)


                # Записываем часы
                houron1 = request.form.get('houron1')
                param = {'name': 'houron1', 'val': int(houron1)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houron2 = request.form.get('houron2')
                param = {'name': 'houron2', 'val': int(houron2)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houron3 = request.form.get('houron3')
                param = {'name': 'houron3', 'val': int(houron3)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houron4 = request.form.get('houron4')
                param = {'name': 'houron4', 'val': int(houron4)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houron5 = request.form.get('houron5')
                param = {'name': 'houron5', 'val': int(houron5)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houroff1 = request.form.get('houroff1')
                param = {'name': 'houroff1', 'val': int(houroff1)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houroff2 = request.form.get('houroff2')
                param = {'name': 'houroff2', 'val': int(houroff2)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houroff3 = request.form.get('houroff3')
                param = {'name': 'houroff3', 'val': int(houroff3)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houroff4 = request.form.get('houroff4')
                param = {'name': 'houroff4', 'val': int(houroff4)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                houroff5 = request.form.get('houroff5')
                param = {'name': 'houroff5', 'val': int(houroff5)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                # Записываем минуты
                minon1 = request.form.get('minon1')
                param = {'name': 'minon1', 'val': int(minon1)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minon2 = request.form.get('minon2')
                param = {'name': 'minon2', 'val': int(minon2)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minon3 = request.form.get('minon3')
                param = {'name': 'minon3', 'val': int(minon3)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minon4 = request.form.get('minon4')
                param = {'name': 'minon4', 'val': int(minon4)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minon5 = request.form.get('minon5')
                param = {'name': 'minon5', 'val': int(minon5)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minoff1 = request.form.get('minoff1')
                param = {'name': 'minoff1', 'val': int(minoff1)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minoff2 = request.form.get('minoff2')
                param = {'name': 'minoff2', 'val': int(minoff2)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minoff3 = request.form.get('minoff3')
                param = {'name': 'minoff3', 'val': int(minoff3)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minoff4 = request.form.get('minoff4')
                param = {'name': 'minoff4', 'val': int(minoff4)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)

                minoff5 = request.form.get('minoff5')
                param = {'name': 'minoff5', 'val': int(minoff5)}
                queryString = ('''UPDATE AquaLight SET Selected = 1 WHERE NAME = %(name)s AND val = %(val)s''')
                SQLfunction.update_options_light(queryString, param)




                minon1 = request.form.get('minon1')
                minon2 = request.form.get('minon2')
                minon3 = request.form.get('minon3')
                minon4 = request.form.get('minon4')
                minon5 = request.form.get('minon5')

                minoff1 = request.form.get('minoff1')
                minoff2 = request.form.get('minoff2')
                minoff3 = request.form.get('minoff3')
                minoff4 = request.form.get('minoff4')
                minoff5 = request.form.get('minoff5')




                queryString = '''select VALUE FROM options WHERE NAME = "cooler" '''
                cooler = SQLfunction.sqlfuncselect(queryString=queryString)
                cooler = cooler[0][0]

                queryString = '''select VALUE FROM options WHERE NAME = "zimalimit" '''
                zimalimit = SQLfunction.sqlfuncselect(queryString=queryString)
                zimalimit = zimalimit[0][0]

                queryString = '''select VALUE FROM options WHERE NAME = "letolimit" '''
                letolimit = SQLfunction.sqlfuncselect(queryString=queryString)
                letolimit = letolimit[0][0]

                queryString = '''select VALUE FROM options WHERE NAME = "AquaHeater" '''
                AquaHeater = SQLfunction.sqlfuncselect(queryString=queryString)
                AquaHeater = AquaHeater[0][0]

                queryString = '''select VALUE FROM options WHERE NAME = "AquaCooler" '''
                AquaCooler = SQLfunction.sqlfuncselect(queryString=queryString)
                AquaCooler = AquaCooler[0][0]

                houron1 = []
                houron2 = []
                houron3 = []
                houron4 = []
                houron5 = []
                for i in range(1, 6, 1):
                    param = "'" + 'houron' + str(i) + "'"
                    queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                    result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                    for kort in result:

                        if kort[0] == 'houron1':
                            d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houron1.append(d1)
                        elif kort[0] == 'houron2':
                            d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houron2.append(d2)
                        elif kort[0] == 'houron3':
                            d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houron3.append(d3)
                        elif kort[0] == 'houron4':
                            d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houron4.append(d4)
                        elif kort[0] == 'houron5':
                            d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houron5.append(d5)

                houroff1 = []
                houroff2 = []
                houroff3 = []
                houroff4 = []
                houroff5 = []
                for i in range(1, 6, 1):
                    param = "'" + 'houroff' + str(i) + "'"
                    queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                    result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                    for kort in result:

                        if kort[0] == 'houroff1':
                            d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houroff1.append(d1)
                        elif kort[0] == 'houroff2':
                            d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houroff2.append(d2)
                        elif kort[0] == 'houroff3':
                            d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houroff3.append(d3)
                        elif kort[0] == 'houroff4':
                            d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houroff4.append(d4)
                        elif kort[0] == 'houroff5':
                            d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            houroff5.append(d5)

                minon1 = []
                minon2 = []
                minon3 = []
                minon4 = []
                minon5 = []
                for i in range(1, 6, 1):
                    param = "'" + 'minon' + str(i) + "'"
                    queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                    result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                    for kort in result:

                        if kort[0] == 'minon1':
                            d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minon1.append(d1)
                        elif kort[0] == 'minon2':
                            d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minon2.append(d2)
                        elif kort[0] == 'minon3':
                            d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minon3.append(d3)
                        elif kort[0] == 'minon4':
                            d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minon4.append(d4)
                        elif kort[0] == 'minon5':
                            d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minon5.append(d5)

                minoff1 = []
                minoff2 = []
                minoff3 = []
                minoff4 = []
                minoff5 = []
                for i in range(1, 6, 1):
                    param = "'" + 'minoff' + str(i) + "'"
                    queryString = ('''SELECT name, val, 'Selected', Selected from AquaLight WHERE NAME =''')
                    result = SQLfunction.sqlfuncselect(queryString=queryString, param=param)
                    for kort in result:

                        if kort[0] == 'minoff1':
                            d1 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minoff1.append(d1)
                        elif kort[0] == 'minoff2':
                            d2 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minoff2.append(d2)
                        elif kort[0] == 'minoff3':
                            d3 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minoff3.append(d3)
                        elif kort[0] == 'minoff4':
                            d4 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minoff4.append(d4)
                        elif kort[0] == 'minoff5':
                            d5 = {kort[0]: str(kort[1]), kort[2]: kort[3]}
                            minoff5.append(d5)

            if "reset" in request.form:
                SQLfunction.WriteToLogTable(element='reboot')
                subprocess.check_call('reboot')
            if "shutdown" in request.form:
                SQLfunction.WriteToLogTable(element='poweroff')
                subprocess.check_call('poweroff')

            return render_template('options.html', version=version, cooler=cooler, zimalimit=zimalimit,
                                   letolimit=letolimit, AquaCooler=AquaCooler, AquaHeater=AquaHeater,
                                   houron1=houron1, houron2=houron2,
                                   houron3=houron3, houron4=houron4,
                                   houron5=houron5, houroff1=houroff1,
                                   houroff2=houroff2, houroff3=houroff3,
                                   houroff4=houroff4, houroff5=houroff5,

                                   minon1=minon1, minoff1=minoff1,
                                   minon2=minon2, minoff2=minoff2,
                                   minon3=minon3, minoff3=minoff3,
                                   minon4=minon4, minoff4=minoff4,
                                   minon5=minon5, minoff5=minoff5)
    else:
        flash("You are not logged in")
        return redirect("/login")


@app.route("/weather", methods=['POST', 'GET'])
def weather():
    import weatherfile
    data = weatherfile.weatherfunc()
    queryString_cur = """SELECT baro FROM avg_sensors ORDER BY id DESC LIMIT 1"""
    temp_sensorsLast_cur = SQLfunction.sqlfuncselect(queryString=queryString_cur)
    if temp_sensorsLast_cur == ():
        temp_sensorsLast_cur = (0, 0)
    return render_template('weather.html', version=version, data=data, temp_sensorsLast_cur=temp_sensorsLast_cur)


if __name__ == '__main__':

    app.run(host='192.168.3.150')

    # app.run(host='0.0.0.0')

