# https://mcdonald-s.en.aptoide.com/versions?offset=30
# https://quizlet.en.aptoide.com/versions?offset=30

import sys
import os
import bs4
import requests
import brotli 
import time
import csv
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import subprocess
import json
import re

def get_html_content(url, path):
	
	time.sleep(5) #delay for 5 seconds
	#url = "https://www.apkmirror.com/apk/samsung-electronics-co-ltd/artcanvas/artcanvas-1-0-41-release/artcanvas-draw-paint-1-0-41-android-apk-download/"
	print("URL: " + url)
	print("path: " + path)

	querystring = {}
	if "?" in path:
		temp = path.replace("/?","")
		temp_list = temp.split("&")

		for a in temp_list:
			str_split = a.split("=")
			querystring[str_split[0]] = str_split[1]


	print querystring

	headers = {
		"authority" : url.replace("https://","").replace("/",""),
		"method": "GET",
		"path": path,
		"scheme": "https",
		"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		"accept-encoding": "gzip, deflate, br",
		"accept-language": "en-US,en;q=0.9",
		"cache-control": "max-age=0",
		"cookie": "language=%22en%22; session_id=%223b91137ecdc7038c5b08b5f4eaeb57cf3a9b88%22; _ga=GA1.2.52943900.1539319665; _gid=GA1.2.594160758.1539319665; entry_point=apkfy_desktop; cookie_accepted=true",
		"upgrade-insecure-requests": "1",
		"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    }
	if "?" in path:
		response = requests.request("GET", url, headers=headers, params=querystring)
	else:
		response = requests.request("GET", url, headers=headers)

	#print response.content
	#print response.status
	return response.content

if __name__ == '__main__':
	
	url = sys.argv[3]
	#url = "https://quizlet.en.aptoide.com/versions"
	Category = sys.argv[1]
	app = sys.argv[2]
	#max_items = sys.argv[4]

	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	fileDir = os.path.join(fileDir,Category) 

	if not os.path.exists(fileDir):
		print("Creating " + fileDir)
		os.mkdir(fileDir)
	
	fileDir = os.path.join(fileDir,app) 
	
	if not os.path.exists(fileDir):
		print("Creating " + fileDir)
		os.mkdir(fileDir)


	apps_to_download = {}

	csv_path = fileDir + "/" + app + "_url_links"+".csv"
	if not os.path.exists(csv_path):


		days_count = 0
		last_app_days = 0
		
		today = datetime.strptime("January 1, 2016", "%B %d, %Y")
		last_appDate = datetime.now()
		difference_in_months = 2
		Year = 2018

		content = get_html_content(url,"/versions")
		isdone = False
		Next = True


		csv = "Version,Link\n"

		while Next:
			soup = BeautifulSoup(content, "html.parser")
			items = soup.find_all("div", attrs={"class" : "bundle-item"})
			i = 0
			apk_count = 0
			for it in items:
				t =  it.find("div", attrs={"class" : "bundle-item__info"})
				date_span =  it.find("span", attrs={"class" : "bundle-info--date"})
				
				date =  date_span.string
				print "date: " + date
				#print it
				

				download_page = t.a.get("href")
				url_list = download_page.split('?')
				print "Version url: "  + download_page
				content = get_html_content(url_list[0],"/?" + url_list[1])
				
				soup_app = BeautifulSoup(content, "html.parser")
				stats = soup_app.find("div", attrs={"class" : "header__stats"})
				version = stats.contents[3].contents[3].string
				list = stats.contents[3].contents[5].string.split(' ')
				value = int(list[0])
				unit = list[1]

				print "Version " + str(version)
				print "Version " + str(unit)

				if unit == "years" or unit == "year":	
					Year -= value

				print("Date: " + date + "/" + str(Year))
				appDate = datetime.strptime(date + "/" + str(Year), "%d/%m/%Y")
				date_diff = relativedelta(today, appDate)

				print("Dates Difference: Years(" + str(date_diff.years) + "), Months(" +str(date_diff.months)+")")

				if date_diff.years >= 2 and date_diff.months >= 6:
					isdone = apk_count >= 18

					if isdone:
						print("Information collected for 2 years stopping process")
						break


				if last_appDate != today:		
					difference_in_months = relativedelta(last_appDate, appDate).months
					print("Months Difference: " + str(difference_in_months))

				if(difference_in_months < 1):
					print("Less than 1 months ignoring")
					continue

				last_appDate = 	appDate

		#		daystoadd= 0

				#if unit == "days" or unit == "day":
				#	days_count = value 
				#elif unit == "week" or unit == "weeks" :
				#	days_count = 7 * value 
				#elif unit == "month" or unit == "months":
				#	days_count = 30 * value 
				#else:
				#	days_count = 364 * value

				#print "daystoadd " + str(daystoadd)
				#days_count += daystoadd

			#	print "Days From today " + str(days_count)
			#	print "Days from last app " + str(last_app_days)

			#	if days_count - last_app_days < 45 and last_app_days > 0:
			#		continue
				
			#	last_app_days = days_count	

				download_btn = soup_app.find("a", attrs={"class" : "aptweb-button--app"})
				print download_btn.get("href")	

				path = fileDir + "/" + app + "_"+version+".apk"
				apps_to_download[path] = download_page

				csv += path + "," + download_page + "\n"

				#apk_count += 1

			next_page = soup.find("div", attrs={"class" : "widget-pagination__next"})
			print next_page
			if next_page.a:
				Next = True
				next_page_url =  next_page.a.get("href")
				url_list = next_page_url.split('?')
				content = get_html_content(url_list[0],"/?" + url_list[1])
			else:
				Next = False

		f = open(csv_path,"w+")
		f.write(csv)
		f.close()
	else:
		with open(csv_path) as csv_file:
			print("Csv Found")
			csv_reader = csv.reader(csv_file, delimiter = ",")
			line_count = 0

			for row in csv_reader:
				if t == 0:
					t = 1
				else:
					apps_to_download[row[0]] = row[1]


	if len(apps_to_download) >= 11:

		for key, value in d.iteritems():
			
			print("About to download " + key)
			download_page = requests.get(value)
			d_page = BeautifulSoup(download_page.content, "html.parser")
			dl = d_page.find("a", string="Click here")

			download_page = requests.get(dl.get("href"))
			with open(key,"wb") as f:
				f.write(download_page.content)
	else:
		print("Not enough APKs")

	#time.sleep(10)





