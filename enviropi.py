############################################
# Created by The Machine Shop 2019         #
# Visit our website TheMachineShop.uk      #
# This script interfaces the Zio Qwiic     #
# Temperature and Humidity sensor (SHT31), #
# Full Spectrum Light sensor (TSL2561) and #
# PM2.5-1.0-10.0 Particulate Matter sensor #
# to a Raspberry Pi over i2c and converts  #
# the data.  			           #
# requires python-smbus to be installed:   #
# sudo apt-get install python-smbus        #
############################################

# Import the required libraries
import smbus
import time
from flask import Flask, render_template
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure, Stream 
from plotly.graph_objs.layout import YAxis
import datetime

username = 'machineshopuk'
api_key = '####################'
stream_token_temp = '##########'
stream_token_humid = '##########'
stream_token_light = '##########'
stream_token_PM1 = '##########'
stream_token_PM25 = '##########'
stream_token_PM10 = '##########'

py.sign_in(username, api_key)

trace1 = Scatter(
    	x=[],
    	y=[],
	name="Temperature (Celcius)",
    	stream=dict(
        	token=stream_token_temp,
		maxpoints=10000
    	),
)
trace2 = Scatter(
	x=[],
	y=[],
	name="Humidity (%)",
	stream=dict(
		token=stream_token_humid,
		maxpoints=10000
	),
)
trace3 = Scatter(
        x=[],
        y=[],
	name="Light (Lux)",
        stream=dict(
                token=stream_token_light,
		maxpoints=10000
        ),
)
trace4 = Scatter(
        x=[],
        y=[],
        name="PM1.0",
        stream=dict(
                token=stream_token_PM1,
		maxpoints=10000
        ),
)
trace5 = Scatter(
        x=[],
        y=[],
        name="PM2.5",
        stream=dict(
                token=stream_token_PM25,
		maxpoints=10000
        ),
)
trace6 = Scatter(
        x=[],
        y=[],
        name="PM10.0",
        stream=dict(
                token=stream_token_PM10,
		maxpoints=10000
        ),
)

layout = Layout(
    	title='EnviroPi with ZIO QWIIC Sensors',
	yaxis=YAxis(
		title='Value'
	),
	yaxis2=YAxis(
		title='%'
	),
	yaxis3=YAxis(
		title='Lux'
	),
	yaxis4=YAxis(
                title='PM1'
        ),
        yaxis5=YAxis(
                title='PM25'
        ),
        yaxis6=YAxis(
                title='PM10'
        )
)
data = [trace1, trace2, trace3, trace4, trace5, trace6]
fig = Figure(data=data, layout=layout)

print py.plot(fig, filename='EnviroPi with ZIO QWIIC sensors',fileopt='extend')

stream_temp = py.Stream(stream_token_temp)
stream_temp.open()

stream_humid = py.Stream(stream_token_humid)
stream_humid.open()

stream_light = py.Stream(stream_token_light)
stream_light.open()

stream_PM1 = py.Stream(stream_token_PM1)
stream_PM1.open()

stream_PM25 = py.Stream(stream_token_PM25)
stream_PM25.open()

stream_PM10 = py.Stream(stream_token_PM10)
stream_PM10.open()





# Start the i2c bus and label as 'bus'
bus = smbus.SMBus(1)
while True:
	# Send the start converstion command to the SHT31
	bus.write_i2c_block_data(0x44, 0x2C, [0x06])
	# Setup the control register on the TSL2561
	bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
	# Setup the timing register on the TSL2561
	bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)
	# PM sensor does not require any setup

	# Wait for the conversions to complete
	time.sleep(0.5)

	# Read the data back from the sensors
	tempData = bus.read_i2c_block_data(0x44, 0x00, 6)
	lightData = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
	lightData1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)
	PMData = bus.read_i2c_block_data(0x12, 0x00, 32)

	# Convert the raw data
	temp = tempData[0] * 256 + tempData[1]
	cTemp = -45 + (175 * temp) / 65535.0
	humidity = 100 * (tempData[3] * 256 + tempData[4]) / 65535.0
	lightCh0 = lightData[1] * 256 + lightData[0]
	lightCh1 = lightData1[1] * 256 + lightData1[0]
	PM1 = PMData[4] * 256 + PMData[5]
	PM25 = PMData[6] * 256 + PMData[7]
	PM10 = PMData[8] * 256 + PMData[9]

	# Print the data
	# print ('Temp: {:.2f}*C Humdity: {:.2f}%'.format(cTemp,humidity)) 
	# print ('Full Spectrum(IR + Visible): {:d}lux Infrared Value: {:d}lux Visible Value:{:d}lux'.format(lightCh0, lightCh1, lightCh0 - lightCh1))
	# print ('PM1.0: {:d} PM2.5: {:d} PM10.0: {:d}'.format(PM1, PM25, PM10))

        sensor_data = [cTemp,humidity,lightCh0] 
	dateT = datetime.datetime.now()
        stream_temp.write({'x': dateT, 'y': cTemp})
	stream_humid.write({'x': dateT, 'y': humidity})
	stream_light.write({'x': dateT, 'y': lightCh0})
	stream_PM1.write({'x': dateT, 'y': PM1})
        stream_PM25.write({'x': dateT, 'y': PM25})
        stream_PM10.write({'x': dateT, 'y': PM10})
	time.sleep(29.5)
