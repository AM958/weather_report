#! /usr/bin python
#
# XWeatherReport - Tweeting weather conditions in the Greek region
#
# Copyright (c) 2016, w.bot2017@yandex.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pprint import pprint
from pyowm import OWM
from datetime import datetime
import tweepy
import time
import os
import optparse

API_key = os.environ.get('OWM_API_KEY')
owm = OWM(API_key)

consumer_key = os.environ.get('TWEEPY_CONSUMER_KEY')
consumer_secret = os.environ.get('TWEEPY_CONSUMER_SECRET')
access_token = os.environ.get('TWEEPY_TOKEN')
access_token_secret = os.environ.get('TWEEPY_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
print ('authenticating...')
api = tweepy.API(auth)

HAZARD_CODES = [202, 212, 221, 231, 232, 302, 312, 314, 321, 503, 504, 511, \
	522, 531, 602, 622, 960, 961, 962, 762, 771, 781, \
	900,901, 902, 903, 904, 905, 906]

D = {"NWN":348.75, "NW":325.25, "WNW": 303.75, "W":281.25, "WSW":258.75,\
	 "SW":236.25, "SSW":213.75, "S":191.25, "SSE":168.75, "SE":146.25,\
	"ESE":123.75, "E":101.25, "ENE":78.75, "NE":56.25, "NNE":33.75}

def deg_to_direction(degrees):
	if degrees >= 348.75 or degrees < 11.25:
		return "N"
	elif degrees >= 11.25  and degrees < 33.75:	
		return "NNE"
	elif degrees >= 33.75 and degrees < 56.25:
		return "NE"	
	elif degrees >= 56.25 and degrees < 78.75:
		return "ENE"	
	elif degrees >= 78.75 and degrees < 101.25:
		return "E"
	elif degrees >= 101.25 and degrees < 123.75:
		return "ESE"
	elif degrees >= 123.75 and degrees < 146.25:
		return "SE"
	elif degrees >= 146.25 and degrees < 168.75:
		return "SSE"
	elif degrees >= 168.75 and degrees < 191.25:
		return "S"
	elif degrees >= 191.25 and degrees < 213.75:
		return "SSW"
	elif degrees >= 213.75 and degrees < 236.25:
		return "SW"
	elif degrees >= 236.25 and degrees < 258.75:
		return "WSW"
	elif degrees >= 258.75 and degrees < 281.25:
		return "W"
	elif degrees >= 281.25 and degrees < 303.75:
		return "WNW"
	elif degrees >= 303.75 and degrees < 326.25:
		return "NW"
	elif degrees >= 326.25 and degrees < 348.75:
		return "NNW"
	else:
		return ""

def mps_to_kmph(mps):
	return (mps * 3600)/1000		

def main():

	parser = optparse.OptionParser()

	parser.add_option('-c', '--city',
	    action="store", dest="city",
	    help="city string", default="all")

	parser.add_option('-i', '--cityid',
	    action="store", dest="city_id",
	    help="city id string", default="0")

	parser.add_option('-r', '--reply',
	    action="store_true", dest="reply",
	    help="reply to tweets?")

	options, args = parser.parse_args()

	if options.city_id == "0":
		with open('greek_cities.owm') as f:
			content = f.read().splitlines()
	else:
		content = options.city_id
	counter = 0
	hazard = False
	max_temp = -273
	min_temp = 100
	max_loc = ''
	min_loc = ''
	print deg_to_direction(44)
	print mps_to_kmph(77)
	for city in content:
		counter += 1
		if counter%50 == 0:
			time.sleep(60)
		try:
			obs = owm.weather_at_id(int(city))
			w = obs.get_weather()	
			condition = w.get_weather_code()
			location = obs.get_location()
			location_name = location.get_name()[0:20]
			location_name = location_name.replace(" ", "_")
			temperature = w.get_temperature(unit='celsius')['temp']
			
			if temperature > max_temp:
				max_temp = temperature
				max_loc = location_name
			if temperature < min_temp:
				min_temp = temperature
				min_loc = location_name

			if condition in HAZARD_CODES:
				temperature = w.get_temperature(unit='celsius')['temp']
				status = w.get_detailed_status()
				temperature = w.get_temperature(unit='celsius')['temp']
				wind = mps_to_kmph(w.get_wind()['speed'])
				if 'deg' in w.get_wind():
					wind_dir = deg_to_direction(w.get_wind()['deg'])
				else:
					wind_dir = ''
				humidity = w.get_humidity()
				pressure = w.get_pressure()['press']
				hazard = True
				tweet = "Hazardous Weather in #" + location_name + '\n' + \
					status.upper() + '\n' + \
					"Temp: " + str(int(temperature)) + u"\u2103" + '\n' \
					"Wind: " + str(wind) + " km/h" + " " + wind_dir + '\n' + \
					"Humidity: " + str(humidity) + " %" + '\n' + \
					"Time: " + datetime.now().strftime("%H:%M:%S")
				api.update_status(tweet)
				time.sleep(10)
		except Exception, e:
			print e

	tweet = "Warmest Greek location is #" + max_loc + ": " + \
			str(int(max_temp)) + u"\u2103" + '\n' + \
			"Coldest is #" + min_loc + ": " + \
			str(int(min_temp)) + u"\u2103" + '\n'

	ts = 	"Time: " + datetime.now().strftime("%H:%M:%S")	

	if hazard == False:
			tweet += "No hazardous weather conditions reported" + '\n' + ts		
	else:
		tweet += ts
		
	api.update_status(tweet)
	exit()

if __name__ == '__main__':
	main()

