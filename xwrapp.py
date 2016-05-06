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

API_key = ''
owm = OWM(API_key)

consumer_key = "" 
consumer_secret = ""
access_token = "" 
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
print ('authenticating...')
api = tweepy.API(auth)

HAZARD_CODES = [202, 212, 221, 231, 232, 302, 312, 314, 321, 503, 504, 511, \
	522, 531, 602, 622, 960, 961, 962, 762, 771, 781, \
	900,901, 902, 903, 904, 905, 906]

def main():
	with open('greek_cities.owm') as f:
		content = f.read().splitlines()
	counter = 0
	hazard = False
	max_temp = -273
	min_temp = 100
	max_loc = ''
	min_loc = ''

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
				wind = w.get_wind()['speed']
				humidity = w.get_humidity()
				pressure = w.get_pressure()['press']
				hazard = True
				tweet = "Hazardous Weather in #" + location_name + '\n' + \
					status.upper() + '\n' + \
					"Temp: " + str(int(temperature)) + u"\u2103" + '\n' \
					"Wind: " + str(wind) + " m/s" + '\n' + \
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
