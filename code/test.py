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
import matplotlib.pyplot as plt


def RGB2Hex(rgb):
    R, G, B = rgb
    c = "#"
    r16 = str(hex(R))[-2:].replace('x', '0').upper()
    g16 = str(hex(G))[-2:].replace('x', '0').upper()
    b16 = str(hex(B))[-2:].replace('x', '0').upper()
    return c+r16+g16+b16


def batch(folder_path):
    r = re.compile('[0-9]*.txt')
    files = os.listdir(folder_path)
    for file in files:
        if re.match(r, file):
            process(os.path.join(folder_path, file))
            print("finish:", file)


def process(file):
    global speed_list
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
    overspeed_car=pd.DataFrame(move_car[move_car.speed>80])
    action_car = pd.DataFrame(taxi[taxi.speed<=200])
    speed_list=speed_list+list(action_car.speed)
    # 绘制movecar和jamcar
    draw_jam_and_move(move_car, jam_car)
    draw_speed(taxi)
    draw_overspeed(overspeed_car)
    count_jam_time(taxi)
    #计算车的运行时间和堵车时间
    return taxi

def count_jam_time(taxi):
    global jam_time,whole_time,overspeed_time,rest_time
    rest_time.append((sum(taxi[taxi.newstart==1].dt)))
    whole_time.append(sum(taxi[taxi.speed <= 200 ].dt))
    jam_time.append(sum(taxi[taxi.speed == 0].dt))
    overspeed_time.append(sum((taxi[(taxi.speed>80) & (taxi.speed<=200)].dt)))




def draw_speed(taxi):
    color_base = (50, 100, 150)
    k = 155/3/120/2
    for idx, row in taxi.iterrows():    
        if row.speed >= 0 and row.speed <= 200: 
            # 删除五成点    
            if random.random() > 0.7:
                c = (int(0+k*(row.speed-80)), int(100+2*k *
                                                   (row.speed-80)), int(150+3*k*(row.speed-80)))
                color16 = RGB2Hex(c)
                folium.Circle(
                    radius=15,
                    location=[row.lat, row.lng],
                    color=color16
                ).add_to(velocity_tapering)

def draw_overspeed(overspeed_car):
    k = (255-100)/(200-80)
    b = 155-200*k
    for idx,row in overspeed_car.iterrows():
        c = (int(row.speed*k+b)+100, 0, 0)
        color16 = RGB2Hex(c)
        folium.Circle(radius=15,
                        location=[row.lat, row.lng],
                        color=color16
                        ).add_to(overspeed)


def draw_jam_and_move(move_car, jam_car):
    # 做一下点的删除，不然显示不全，对于运动点删除7成，堵车点删除3成
    for idx, row in move_car.iterrows():
        if random.random() > 0.7:
            folium.Circle(
                radius=15,
                location=[row.lat, row.lng],
                color="#E0542E"
            ).add_to(jam_move)

    for idx, row in jam_car.iterrows():
        if random.random() > 0.55:
            folium.Circle(
                radius=15,
                location=[row.lat, row.lng],
                color="#4D7186"
            ).add_to(jam_move)

def speed_hist(speed_list):
    plt.subplot(2,1,1)
    plt.xlabel('Speed')
    plt.ylabel('Probability')
    plt.hist(speed_list,bins=20)

    move_list=[x for x in speed_list if x>5]
    plt.subplot(2,1,2)
    plt.xlabel('Speed')
    plt.ylabel('Probability')
    plt.hist(move_list,bins=20)

    plt.savefig(os.path.join(savefile,'fig.png'))


if __name__ == "__main__":
    folder = '../Taxi'
    savefile=r"G:\3result"
    jam_move = folium.Map(location=[39.90732, 116.45353])
    velocity_tapering = folium.Map(location=[39.90732, 116.45353])
    overspeed = folium.Map(location=[39.90732, 116.45353])
    speed_list=list()
    rest_time,whole_time,jam_time,overspeed_time =list(),list(),list(),list()
    batch(folder)
    jam_move.save(os.path.join(savefile,"jam_move.html"))
    print("1")
    velocity_tapering.save(os.path.join(savefile,"velocity.html"))
    print("2")
    overspeed.save(os.path.join(savefile,"overspeed.html"))
    print("3")
    speed_hist(speed_list)
    print(whole_time)
    print(jam_time)
    print(overspeed_time)
    print(rest_time)
