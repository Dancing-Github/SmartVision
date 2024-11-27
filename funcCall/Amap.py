import requests
import json

KEY = 'a77b206d15695a65f7a616142923aa39'


def query(url, params):
    ans = json.loads(requests.get(url, params).content)
    print(ans)
    return ans


def address2location(address, city=''):
    url = 'http://restapi.amap.com/v3/geocode/geo?parameters'
    params = {
        'city': None if city == '' else city,
        'address': address,
        'key': KEY,
        "output": "json"
    }
    answer = query(url, params)
    # {
    # 'status': '1', 'info': 'OK', 'infocode': '10000', 'count': '1',
    # 'geocodes': [{
    #   'formatted_address': '广东省广州市番禺区华南理工大学大学城校区', 'country': '中国', 'province': '广东省',
    #   'citycode': '020', 'city': '广州市', 'district': '番禺区', 'township': [],
    #   'neighborhood': {'name': [], 'type': []},
    #   'building': {'name': [], 'type': []},
    #   'adcode': '440113', 'street': [], 'number': [],
    #   'location': '113.405216,23.046336', 'level': '住宅区'}]
    # }
    return {"location": answer["geocodes"][0]["location"], "citycode": answer["geocodes"][0]["citycode"]}


def walking(origin, destination):
    url = 'https://restapi.amap.com/v5/direction/walking?parameters'
    params = {
        "origin": origin["location"],
        "destination": destination["location"],
        "key": KEY,
        "output": "json"
    }
    answer = query(url, params)
    # {
    # 'status': '1', 'info': 'OK', 'infocode': '10000', 'count': '1',
    # 'route': {'origin': '113.405216,23.046336', 'destination': '113.405216,23.046336',
    #   'paths': [{
    #     'distance': '1', 'cost': {'duration': '1'},
    #     'steps': [{'instruction': '向南步行1米到达目的地', 'orientation': '南', 'road_name': '', 'step_distance': '1'}]
    #   }]
    #  }
    # }
    return answer["route"]["paths"][0]["steps"]


def transit(origin, destination):
    url = 'https://restapi.amap.com/v5/direction/transit/integrated?parameters'
    params = {
        "origin": origin["location"],
        "destination": destination["location"],
        "key": KEY,
        "city1": origin["citycode"],
        "city2": destination["citycode"],
        "strategy": "0",  # 0-8 https://lbs.amap.com/api/webservice/guide/api/newroute#t9
        "AlternativeRoute": "1",
        "output": "json"
    }
    answer = query(url, params)
    # {'status': '1', 'info': 'OK', 'infocode': '10000',
    #  'route': {'origin': '113.405216,23.046336', 'destination': '113.404791,23.011307', 'distance': '3587',
    #            'transits': [{'distance': '8442', 'walking_distance': '1809', 'nightflag': '0',
    #                          'segments': [{
    #                              'walking': {
    #                                  'destination': '113.400482,23.043407',
    #                                  'distance': '978',
    #                                  'origin': '113.405533,23.046045',
    #                                  'steps': [
    #                                      {'instruction': '步行48米右转','road': '','distance': '48'},
    #                                      { 'instruction': '步行174米到达大学城南',  'road': '', 'distance': '174'}]},
    #                              'bus': {
    #                                  'buslines': [
    #                                      {
    #                                          'departure_stop': {
    #                                              'name': '大学城南',
    #                                              'id': '440100023035008',
    #                                              'location': '113.400478,23.043408',
    #                                              'entrance': {
    #                                                  'name': 'C口',
    #                                                  'location': '113.401039,23.043346'}},
    #                                          'arrival_stop': {
    #                                              'name': '新造',
    #                                              'id': '440100023035009',
    #                                              'location': '113.415714,23.028182',
    #                                              'exit': {
    #                                                  'name': 'A1口',
    #                                                  'location': '113.414970,23.028315'}},
    #                                          'name': '地铁4号线(黄村--南沙客运港)',
    #                                          'id': '440100023035',
    #                                          'type': '地铁线路',
    #                                          'distance': '2504',
    #                                          'bus_time_tips': '',
    #                                          'bustimetag': '0',
    #                                          'start_time': '0600',
    #                                          'end_time': '2315',
    #                                          'via_num': '0',
    #                                          'via_stops': []}]}},
    #                              {
    #                                  'walking': {
    #                                      'destination': '113.415001,23.028772',
    #                                      'distance': '175',
    #                                      'origin': '113.415710,23.028177',
    #                                      'steps': [
    #                                          {
    #                                              'instruction': '步行111米左转',
    #                                              'road': '',
    #                                              'distance': '111'},
    #                                          {
    #                                              'instruction': '步行64米到达地铁新造站',
    #                                              'road': '',
    #                                              'distance': '64'}]},
    #                                  'bus': {
    #                                      'buslines': [
    #                                          {
    #                                              'departure_stop': {
    #                                                  'name': '地铁新造站',
    #                                                  'id': '900000129530003',
    #                                                  'location': '113.414996,23.028767'},
    #                                              'arrival_stop': {
    #                                                  'name': '华工国际校区南门',
    #                                                  'id': '900000129530006',
    #                                                  'location': '113.407586,23.007883'},
    #                                              'name': '番87路(地铁新造站--华工国际校区公交总站)',
    #                                              'id': '900000129530',
    #                                              'type': '普通公交线路',
    #                                              'distance': '4129',
    #                                              'bus_time_tips': '',
    #                                              'bustimetag': '0',
    #                                              'start_time': '',
    #                                              'end_time': '',
    #                                              'via_num': '1',
    #                                              'via_stops': [
    #                                                  {
    #                                                      'name': '暨南大学南校区', 'id': '900000129530004',
    #                                                      'location': '113.417746,23.014865'}]}]}},
    #                              {
    #                                  'walking': {
    #                                      'destination': '113.404831,23.011345',
    #                                      'distance': '656',
    #                                      'origin': '113.407372,23.007799',
    #                                      'steps': [
    #                                          {'instruction': '沿兴业大道步行68米右转', 'road': '兴业大道', 'distance': '68'},
    #                                          { 'instruction': '步行52米',   'road': '',  'distance': '52'}]}}]}]},
    #                                          'count': '1'}

    return answer["route"]["transits"][0]["segments"]


def path_from_org_to_dst(origin, destination, mode='walking'):
    if mode == 'walking':
        return walking(address2location(origin),
                       address2location(destination))
    elif mode == 'transit' or mode == 'bus' or mode == 'subway':
        return transit(address2location(origin),
                       address2location(destination))
    else:
        return None


if __name__ == '__main__':
    org = address2location('中山大学大学城校区', '广州')
    dst = address2location('华南理工大学国际校区', '广州')

    print(walking(org, dst))
    print(transit(org, dst))

    print(path_from_org_to_dst('广州塔', '广州大剧院'))
