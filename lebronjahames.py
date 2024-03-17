#!/usr/bin/python3
import Adafruit_DHT
import time
import requests
from datetime import datetime
import os
import csv
import shutil
import requests
import json
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

def multiple(m,n):
    return True if m % n == 0 else False

lat = 40.600592
lon = -74.343371
part = 'alerts'
API_Key = '2bb600d0a46e09995cd0d2ab71e1a3b6'
# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)
#API_Key = 'Key1'
#'f54b400919e97f5cf3c475301f4b396d'
api_url = 'https://api.openweathermap.org/data/3.0/onecall?lat='+str(lat)+'&lon='+str(lon)+'&exclude='+part+'&appid='+API_Key
#response = requests.get(api_url).json()
#response_dict = json.loads(str(response.json()))
print("Program called")
filename = '/home/pi/Desktop/data.csv'
getValues = lambda key,inputData: [subVal[key] if key in subVal else 0 for subVal in inputData]
file_size = os.stat(filename).st_size/(1024*1024)
if file_size >= 5:
    source = '/home/pi/Desktop/data.csv'
    archive_fileName = 'data_'+str(datetime.now())
    dest = '/home/pi/Desktop/Archive/'+archive_fileName
    shutil.move(source,dest)
    f = open(filename, 'x')
with open(filename, 'a', newline='') as csvfile:
    i = 0
    while i <= 5:

        csv_writer = csv.writer(csvfile)
    #        if(multiple(time.localtime().tm_min,1)):
    #    current_time = datetime.now()

        min_vol = 0
        max_vol = 2.45
        humidity_old, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        volt_val = round(chan.voltage,2)
        humidity = ((1-(volt_val-min_vol)/(max_vol-min_vol)))*100
        if humidity is not None and temperature is not None:
            print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
            try:
                response  = requests.get(api_url).json()
                #print(response)
                #print(response['current']['temp'],response['current']['humidity'])
                #print(getValues('snow',response['hourly']))
                #print(response['hourly'][0]['rain']['1h'])
                if abs(temperature - (response['current']['temp']-273.15)) >=10:
                    location_value = "indoor"
                else:
                    location_value = "outdoor"
                csv_writer.writerow([datetime.now(),round(humidity,2),volt_val,round(humidity_old,2),round(temperature,2),response['current']['temp'],response['current']['humidity'],getValues('temp',response['hourly']),getValues('humidity',response['hourly']),location_value,getValues('rain',response['hourly']),getValues('snow',response['hourly'])])
                print("appended")
                break
            except Exception as e:
                print("exception")
                time.sleep(1)
        else:
            print("are you sped")
            i = i+1
            time.sleep(1);
     #       else:
     #           print("not the right time")
