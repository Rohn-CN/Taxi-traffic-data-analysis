from math import cos
import os
import re
import time
import webbrowser
import math

import folium
from folium.features import ColorLine
import numpy as np
import pandas as pd


def batch(floder_path):
    r = re.compile('[0-9]*.txt')
    files = os.listdir(floder_path)
    for file in files:
        if re.match(r, file):
            return 0
            


def process(file):

    taxi = pd.read_csv(file, sep=',', names=['id', 'time', 'lng', 'lat'])
    taxi.drop_duplicates("time", inplace=True)  # 删除time相同的元素

    taxi.time = pd.to_datetime(taxi.time, format='%Y-%m-%d %H:%M:%S')

    taxi["time2"] = taxi.time.shift(1)
    taxi["lng2"] = taxi.lng.shift(1)
    taxi["lat2"] = taxi.lat.shift(1)

    taxi["dt"] = taxi.time-taxi.time2
    taxi["dlng"] = taxi.lng-taxi.lng2
    taxi["dlat"] = taxi.lat-taxi.lat2

    taxi.dt = (taxi.dt.apply(lambda x: x.days)*12 *
               3600+taxi.dt.apply(lambda x: x.seconds))
    taxi["newstart"] = 0
    taxi.newstart[taxi.dt > 3600] = 1  # 获取时间间隔大于1小时的定义为一个新的起点

    taxi["dis"] = np.sqrt(np.power(
        taxi.dlng*np.cos(taxi.lat/180*math.pi)*111000, 2)+np.power(taxi.dlat*111000, 2))  # 距离

    taxi["speed"] = taxi.dis/taxi.dt*3.6  # 汽车速度

    # 误差数据和停车数据删除，给出move_car数据
    move_car = pd.DataFrame(taxi[(taxi.speed < 200) & (taxi.speed != 0)])

    # 给出jam_car，move_car和jam_car两个不重叠，其并集是剔除误差数据的数据总和
    jam_car = pd.DataFrame(taxi[taxi.speed == 0])
    draw_jam_and_move(move_car,jam_car)

def draw_jam_and_move(move_car,jam_car):
    m=folium.Map(center=[39.90732, 116.45353])
    for idx,row in move_car.iterrows():
        folium.Circle(
            radius=15,
            location=[row.lat,row.lng],
            color='red'
        ).add_to(m)

    for idx,row in jam_car.iterrows():
        folium.Circle(
            radius=15,
            location=[row.lat,row.lng],
            color='blue'
        ).add_to(m)

    m.save('jam_move.html')

if __name__ == "__main__":
    floder = r'S:\作业\空间数据挖掘\data\Taxi\366.txt'
    process(floder)
