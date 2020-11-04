import folium
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas
import datetime

class TaxiTrack(object):
    def __init__(self,id,date,time,lng,lat):
        self.id=id
        self.date=int(date.split('-')[2])
        self.time=
ada