import json
import re

import requests

KEY = 'f0e5cfcaf749fb949c31d5afec15a729'


def query(url, params):
    ans = json.loads(requests.get(url, params).content)
    return ans


# 获取地理编码
def get_location(address):
    url = 'https://restapi.amap.com/v3/geocode/geo'
    params = {'key': KEY, 'address': address}
    ans = query(url, params)
    # print(ans)
    data = {
        "location": ans['geocodes'][0]['location'],
        "citycode": ans['geocodes'][0]['citycode'],
        "adcode": ans['geocodes'][0]['adcode']
    }
    return data


# 获取地理逆编码
def get_address(location):
    url = 'https://restapi.amap.com/v3/geocode/regeo'
    params = {'key': KEY, 'location': location}
    ans = query(url, params)
    data = {
        "address": ans['regeocode']['formatted_address'],
        "adcode": ans['regeocode']['addressComponent']['adcode'],
        "citycode": ans['regeocode']['addressComponent']['citycode']
    }
    return data


# 步行导航
def walking(origin, destination):
    url = 'https://restapi.amap.com/v3/direction/walking'
    if not re.match(r'^(\d{1,3}\.\d{1,6},\d{1,3}\.\d{1,6})$', origin):
        origin = get_location(origin)['location']
    if not re.match(r'^(\d{1,3}\.\d{1,6},\d{1,3}\.\d{1,6})$', destination):
        destination = get_location(destination)['location']
    params = {'key': KEY, 'origin': origin, 'destination': destination}
    ans = query(url, params)
    data = {
        'total_distance': ans['route']['paths'][0]['distance'],
        'total_duration': ans['route']['paths'][0]['duration'],
        'steps': ans['route']['paths'][0]['steps']
    }
    return data


# 公交导航
def transits(origin, destination):
    url = 'https://restapi.amap.com/v5/direction/transit/integrated'
    get_origin = get_location(origin)
    get_destination = get_location(destination)
    origin = get_origin['location']
    destination = get_destination['location']
    city1 = get_origin['citycode']
    city2 = get_destination['citycode']
    params = {'key': KEY, 'origin': origin, 'destination': destination, 'city1': city1, 'city2': city2, 'strategy': 0}
    ans = query(url, params)
    return ans['route']['transits'][0]['segments']


# 周边搜索
def get_surrounding(address, keywords):
    url = 'https://restapi.amap.com/v5/place/around'
    if not re.match(r'^(\d{1,3}\.\d{1,6},\d{1,3}\.\d{1,6})$', address):
        temp = get_location(address)
        location = temp['location']
        region = temp['adcode']
    else:
        location = address
        region = get_address(address)['adcode']
    params = {'key': KEY, 'keywords': keywords, 'region': region, 'city_limit': True, 'location': location}
    ans = query(url, params)
    data = {
        "name": ans['pois'][0]['name'],
        'address': ans['pois'][0]['address'],
        'location': ans['pois'][0]['location'],
        'distance': ans['pois'][0]['distance'],
    }
    statement = data['address'] + "附近的" + keywords + "是" + data['name'] + "，地址是" + data['address']
    return statement


# 天气查询
def get_current_weather(address):
    url = 'https://restapi.amap.com/v3/weather/weatherInfo'
    if not re.match(r'^(\d{1,3}\.\d{1,6},\d{1,3}\.\d{1,6})$', address):
        city = get_location(address)['adcode']
    else:
        city = get_address(address)['adcode']
    params = {'key': KEY, 'city': city}
    ans = query(url, params)
    # print(ans)
    text = ans['lives'][0]
    ''' 
    {'province': '广东', 'city': '番禺区', 'adcode': '440113',
     'weather': '多云', 'temperature': '13',
     'winddirection': '西北', 'windpower': '≤3',
     'humidity': '61', 'reporttime': '2024-02-27 16:30:52',
     'temperature_float': '13.0', 'humidity_float': '61.0'}
    '''
    statement = text['city'] + "的天气是" + text['weather'] + ",温度为" + text['temperature'] + "摄氏度。"

    if '晴' in text['weather']:
        if float(text['temperature']) > 25:
            if float(text['humidity']) < 50:
                statement += '晴天炎热，记得防晒！'
            else:
                statement += '晴天炎热，记得防晒，并保持身体水分。'
        else:
            statement += '晴天宜人，适合户外活动！'
    elif '云' in text['weather']:
        if float(text['temperature']) > 20:
            if float(text['humidity']) > 70:
                statement += '多云天气，湿度较大，出行请带伞！'
            else:
                statement += '多云天气，适合外出活动。'
        else:
            statement += '多云天气，凉爽舒适。'
    elif '雨' in text['weather']:
        if '小' in text['weather']:
            statement += '小雨蒙蒙，注意防雨并携带雨具。'
        elif '中' in text['weather'] or '阵' in text['weather']:
            statement += '雨天出行，注意安全。'
        elif '大' in text['weather']:
            statement += '大雨倾盆，请尽量避免外出，确保安全。'
    elif '雪' in text['weather']:
        statement = '雪花飘飘，注意保暖防滑，出行需谨慎。'
    elif '霾' in text['weather']:
        if float(text['humidity']) > 50:
            statement += '空气质量差，尽量减少户外活动，外出时请戴口罩。'
        else:
            statement += '有轻微霾，空气不太清新，出门记得戴口罩。'
    elif '阴' in text['weather']:
        statement += '阴天阴沉沉的，出行注意保暖哦！'
    else:
        statement += '请持续关注气象预警信息。'

    return statement


# 公交导航（返回语句）
def transits_statement(origin, destination):
    res = transits(origin, destination)
    print(res)
    statement = ''
    for i in range(len(res)):
        try:
            in0 = "步行" + res[i]["walking"]["distance"] + "米。"
        except:
            in0 = ''
        if i == len(res) - 1:
            in1 = "到达目的地."
            in2 = ''
        else:
            try:
                in1 = "从" + res[i]['bus']['buslines'][0]['departure_stop']['name'] + "乘坐" + \
                      res[i]['bus']['buslines'][0][
                          'name']
                in2 = ",在" + res[i]['bus']['buslines'][0]['arrival_stop']['name'] + "下车"
            except:
                in1, in2 = '', ''

        statement = statement + in0 + in1 + in2
    return statement


if __name__ == '__main__':
    print(get_location('广州华南理工大学麦当劳'))
    print(transits_statement('花城汇', '珠江新城'))
