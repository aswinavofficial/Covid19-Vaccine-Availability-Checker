import requests
import datetime
import json
from json2html import *
import os

jsonFile = open('settings.json',)

settings = json.load(jsonFile)


mailgun_apikey = os.environ['MAIL_GUN_APIKEY']


def send_mail(subject, data):
	return requests.post(
		settings["mail_gun_url"],
		auth=("api", mailgun_apikey),
		data={"from": settings["from"],
			"to":     settings["to"],
			"subject": subject,
			"text": "No centres",
			"html": data})
			
base = datetime.datetime.today()
date_list = [base + datetime.timedelta(days=x) for x in range(0,30,7)]
date_str = [x.strftime("%d-%m-%Y") for x in date_list]
print(date_str)

response_list = []

for date in date_str:
	url = settings["cowin_api_base_url"] + "district_id=" + settings["district_id"] + "&date=" + date

	response = requests.get(url)
	print(response.status_code)

	if response.status_code == 200:
		resultJson = response.json()
		response_list.append(resultJson["centers"])
		print("Success for date : " + date)

	else:
		print("Error for date : " + date)

 

under_45_centers = []
all_available_centers = []

for center_list in response_list:

	for center in center_list:
		sessions = center["sessions"]
		under_45_center = False
		available_center = False
		for session in sessions:
			if session["min_age_limit"] < 45 and session["available_capacity"] >0:
				under_45_center = True
			if  session["available_capacity"] >0:
				available_center = True

		if under_45_center == True:
			under_45_centers.append(center)

		if available_center == True:
			all_available_centers.append(center)
		

print("Number Of Available Centers : " + str(len(all_available_centers)))
print("Number Of Under 45 Centers : " + str(len(under_45_centers)))


#Sending Mail for all available centers
if len(all_available_centers) > 0:
  htmlTable = json2html.convert(json = all_available_centers)
  print(send_mail("Vaccine Availability Notification - All Available Centers",htmlTable))

