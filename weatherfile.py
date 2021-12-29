# https://github.com/csparpa/pyowm
from pyowm import OWM
from datetime import date
from pyowm.utils.config import get_default_config
from options import weatherAPItoken

sity = 'Odesa, UA'
config_dict = get_default_config()
config_dict['language'] = 'ru'

# w.detailed_status         # 'clouds'
# w.wind()                  # {'speed': 4.6, 'deg': 330}
# w.humidity                # 87
# w.temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
# w.rain                    # {}
# w.heat_index              # None
# w.clouds                  # 75
def direction():
    owm = OWM(weatherAPItoken, config_dict)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(sity)
    w = observation.weather
    if 0 < w.wind().get('deg') < 30:
        direction = 'южное'

    elif 30 <= w.wind().get('deg') < 60:
        direction = 'юго-восточное'

    elif 60 <= w.wind().get('deg') < 120:
        direction = 'восточное'

    elif 120 <= w.wind().get('deg') < 150:
        direction = 'северо-восточное'

    elif 150 <= w.wind().get('deg') < 210:
        direction = 'северное'

    elif 210 <= w.wind().get('deg') < 240:
        direction = 'северо-западное'

    elif 240 <= w.wind().get('deg') < 300:
        direction = 'западное'

    elif 300 <= w.wind().get('deg') < 330:
        direction = 'юго-западное'

    else:
        direction = 'южное'
    return direction
def status():
    owm = OWM(weatherAPItoken, config_dict)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(sity)
    w = observation.weather
    if w.detailed_status == 'ясно':
        widget = '''<div class="icon sunny"><div class="sun"><div class="rays"></div></div></div>'''
    elif w.detailed_status == 'пасмурно':
        widget = '''<div class="icon cloudy"><div class="cloud"></div><div class="cloud"></div></div>'''
    elif w.detailed_status == 'небольшая облачность':
        widget = '''<div class="icon cloudy"><div class="cloud"></div><div class="cloud"></div></div>'''
    elif w.detailed_status == 'небольшой дождь':
        widget = '''<div class="icon rainy">
                        <div class="cloud"></div>
                        <div class="rain"></div></div>'''
    elif w.detailed_status == 'небольшая морось':
        widget = '''<div class="icon rainy">
                        <div class="cloud"></div>
                        <div class="rain"></div></div>'''
    elif w.detailed_status == 'снег':
        widget = '''<div class="icon flurries">
                        <div class="cloud"></div>
                        <div class="snow">
                        <div class="flake"></div>
                    <div class="flake"></div></div></div>'''
    elif w.detailed_status == 'небольшой снег':
        widget = '''<div class="icon flurries">
                        <div class="cloud"></div>
                        <div class="snow">
                        <div class="flake"></div>
                    <div class="flake"></div></div></div>'''
    elif w.detailed_status == 'плотный туман':
        widget = '''<div class="icon rainy">
                      <div class="cloud"></div>
                      <div class="fog"></div>
                    </div>'''
    elif w.detailed_status == 'туман':
        widget = '''<div class="icon rainy">
                      <div class="cloud"></div>
                      <div class="fog"></div>
                    </div>'''
    elif w.detailed_status == 'переменная облачность':
        widget = '''<div class="icon cloudy"><div class="cloud"></div><div class="cloud"></div></div>'''
    elif w.detailed_status == 'облачно с прояснениями':
        widget = '''<div class="icon cloudy"><div class="cloud"></div><div class="cloud"></div></div>'''
    else:
        widget = ''''''
    return widget
def weatherfunc():
    owm = OWM(weatherAPItoken, config_dict)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(sity)
    w = observation.weather
    data = []
    data.append(sity)
    data.append(w.wind())
    data.append(w.humidity)
    data.append(w.temperature('celsius'))
    data.append(w.detailed_status)
    data.append(w.rain)
    data.append(w.heat_index)
    data.append(w.clouds)
    data.append(date.today())
    data.append(status())
    data.append(direction())
    if w.wind().get('speed') == 0:
        speed = 0
    else:
        speed = 10 / w.wind().get('speed')

    data.append(str(speed)+'s')
    return data

if __name__ == '__main__':
    weatherfunc()

