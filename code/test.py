from math import cos
import os
import re
import time
import webbrowser
import math
import random
import folium
from folium.features import ColorLine
import numpy as np
import pandas as pd


def batch(folder_path):
    r = re.compile('[0-9]*.txt')
    files = os.listdir(folder_path)
    for file in files:
        if re.match(r, file):
            process(os.path.join(folder_path, file))
            print("finish:", file)
            return 0



def process(file):
    taxi = pd.read_csv(file, sep=',', names=['id', 'time', 'lng', 'lat'])
    taxi.drop_duplicates("time", inplace=True)  # 删除time相同的元素

    taxi.time = pd.to_datetime(taxi.time, format='%Y-%m-%d %H:%M:%S')

    taxi["time2"] = taxi.time.shift(1)
    taxi["lng2"] = taxi.lng.shift(1)
    taxi["lat2"] = taxi.lat.shift(1)

    taxi["dt"] = taxi.time - taxi.time2
    taxi["dlng"] = taxi.lng - taxi.lng2
    taxi["dlat"] = taxi.lat - taxi.lat2

    taxi.dt = (taxi.dt.apply(lambda x: x.days) * 12 *
               3600 + taxi.dt.apply(lambda x: x.seconds))
    taxi["newstart"] = 0
    taxi.newstart[taxi.dt > 3600] = 1  # 获取时间间隔大于1小时的定义为一个新的起点

    taxi["dis"] = np.sqrt(np.power(
        taxi.dlng * np.cos(taxi.lat / 180 * math.pi) * 111000, 2) + np.power(taxi.dlat * 111000, 2))  # 距离

    taxi["speed"] = taxi.dis / taxi.dt * 3.6  # 汽车速度

    # 误差数据和停车数据删除，给出move_car数据
    move_car = pd.DataFrame(taxi[(taxi.speed <= 200) & (taxi.speed != 0)])
    jam_car = pd.DataFrame(taxi[taxi.speed == 0])

    # 绘制movecar和jamcar
    draw_jam_and_move(move_car, jam_car)

    # 给出超速数据
    overspeed_car = pd.DataFrame(taxi[taxi.speed > 80])


def draw_speed(taxi):
    color_split = 200/(255-150)/3
    color_base=(50,100,150)

    for idx, row in taxi.iterrows():
        if taxi.speed >= 0 and taxi.speed <= 200:
            # 删除五成点
            if random.random() > 0.5:
                c=(taxi.speed,taxi.speed*2,taxi.speed*3)
                folium.Circle(
                    radius=15,
                    location=[taxi.lat, taxi.lng],
                    color=list(map(lambda  x:x[0]+x[1],zip(c,color_base)))
                ).add_to(velocity_tapering)

def draw_overspeed(taxi):
    color_base=(100,100,0)

    color_split=(200-80)/(255-100)
    for idx,row in taxi.iterrows():
        if taxi.speed>80:
            c=(taxi.speed*color_split,0,0)
            folium.Circle(radius=15,
                          location=[taxi.lat,taxi.lng],
                          color =list(map(lambda x:x[0]+x[1],zip(c,color_base)))
                          ).add_to(overspeed)

def draw_jam_and_move(move_car, jam_car):
    # 做一下点的删除，不然显示不全，对于运动点删除7成，堵车点删除3成
    for idx, row in move_car.iterrows():
        if random.random() > 0.7:
            folium.Circle(
                radius=15,
                location=[row.lat, row.lng],
                color="4D7186"
            ).add_to(jam_move)

    for idx, row in jam_car.iterrows():
        if random.random() > 0.3:
            folium.Circle(
                radius=15,
                location=[row.lat, row.lng],
                color="E0542E"
            ).add_to(jam_move)


if __name__ == "__main__":
    folder = '../Taxi'
    jam_move = folium.Map(center=[39.90732, 116.45353])
    velocity_tapering = folium.Map(center=[39.90732, 116.45353])
    overspeed=folium.Map(center=[39.90732, 116.45353])
    batch(folder)
    jam_move.save("jam_move.html")
    velocity_tapering.save("velocity.html")
    overspeed.save("overspeed.html")

