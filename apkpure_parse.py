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
import string
import json
import argparse
from collections import namedtuple



Apps = []
max_Date = '2016-12-31'
sleep_time = 10
short_sleep_time = 2
min_apks = 10
max_apks = 12
months = 1
days = 1

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

class AppVersion:

	def __init__(self, version, url, date, size):	
		self.version = version
		self.url = url
		self.date = date
		self.is_downloaded = False
		self.size = size
		self.download_link = ""

	def get_date(self):
		return datetime.strptime(self.date, "%Y-%m-%d")

	def reprJSON(self):
		return self.__dict__
		
class Application:

	def __init__(self, category, name, versions_url):
		self.category = category
		self.versions = []
		self.name = name
		self.versions_url = versions_url
		self.is_checked = False

	def number_of_versions(self):
		return len(self.versions)

	def is_completed(self):
		downloaded = 0
		for v in self.versions:
			if v.is_downloaded:
				downloaded += 1

		return downloaded >= max_apks

	def get_valid_apks(self):

		m_date = datetime.strptime(max_Date, "%Y-%m-%d")
		valid = []
		date = m_date 
		for v in self.versions:
			#print(v.version)
			date_diff = relativedelta(m_date, v.get_date())

			if(date_diff.days > days):
				if(date_diff.months > months):
					valid.append(v)
					date = v.get_date()


		print(" => " + str(len(valid)))
		return valid

	def is_valid(self):
		
		num = self.number_of_versions()
		#print(num)
		if  num < min_apks:
			#print("num < min_apks")
			return False

		return len(self.get_valid_apks()) >= min_apks 


	def download_apks(self):
		valid_apks = self.get_valid_apks()

		print("Valid Apks: " + str(len(valid_apks)))
		

		fileDir = os.path.dirname(os.path.abspath(__file__))
		fileDir = os.path.join(fileDir, self.category)


		for apk in valid_apks:
			
			if(apk.is_downloaded):
				continue


			appDir = os.path.join(fileDir, self.name)

			if not os.path.exists(appDir):
				os.mkdir(appDir)
				print("Directory " , appDir ,  " Created ")
			else:
				print("Directory " , appDir ,  " Exists ")

			
			
			apk_file = requests.get(apk.url)
			
			soup = BeautifulSoup(apk_file.content, "html.parser")
			link = soup.find("a", attrs={"id":"download_link"})
			apk.download_link = link.get("href")

			print("Downloading " + self.name + "_" + apk.version.replace(".", "_"))
			

			apk_file = requests.get(apk.download_link)
			appDir = os.path.join(appDir, self.name + "_" + apk.version.replace(".", "_"))
			print("saving into "+ appDir + ".apk")

			f = open(appDir + ".apk","w+")
			f.write(apk_file.content);
			f.close()

			apk.is_downloaded = True

			if(self.is_completed())
				break

			print("Waiting " + str(sleep_time) + " seconds")
			time.sleep(sleep_time)



def get_versions(url):
	
	url = url

	headers = {
	    'cache-control': "no-cache",
	    'postman-token': "1fe87c7d-b0a4-e420-decb-46d857929fc4"
	    }

	response = requests.request("GET", url, headers=headers)

	return response.content


def getAppCategoryPage(Category, page):


	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	url = "https://apkpure.com/"+Category

	querystring = {"page": str(page), "ajax":"1"}


	headers = {
	    'cache-control': "no-cache",
	    'postman-token': "e6affbba-44c5-764b-be6b-59d3fe17b957"
    }

	dirName = fileDir + "/" + Category
	if not os.path.exists(dirName):
		os.mkdir(dirName)
		print("Directory " , dirName ,  " Created ")

	response = requests.request("GET", url, headers=headers, params=querystring)

	
	htmlFileName = dirName +"/" + Category + str(page)+ ".html"
	f= open(htmlFileName,"w+")
	f.write(response.content);
	f.close()

	return response.content




def scrap_version(app):
	global Apps
	
	version_content = get_versions(app.versions_url)
	soup = BeautifulSoup(version_content, "html.parser")
	
	title = soup.find("div", attrs={"class": "ver-title"})

	has_prev = type(title) is bs4.element.Tag	

	if has_prev:

		versions = soup.find("ul", attrs={"class": "ver-wrap"})

		#
		list_versions = versions.find_all("li")

		
		for version in list_versions:

			#print(version)	
			url = "https://apkpure.com" +  version.a.get("href")
			v_item = version.find("div", attrs={"class" : "ver-item"})
			v_name = v_item.find("span", attrs={"class" : "ver-item-n"})
			v_size = v_item.find("span", attrs={"class" : "ver-item-s"})
			v_a = v_item.find("div", attrs={"class" : "ver-item-a"})
			v_date = v_a.find("p", attrs={"update-on"})

			v_app = AppVersion(v_name.string, url, v_date.string, v_size.string)

			app.versions.append(v_app)


	app.is_checked = True



def download_category_page(category, page, max_page):
	global Apps

	print("Category: " + category + ", page: " + str(page) + ", max page: " + str(max_page))

	categoryContent = getAppCategoryPage(category, page)


	soup = BeautifulSoup(categoryContent, "html.parser")
	list_app = soup.findAll("li")

	if(len(list_app) > 0 and page <= max_page):


		for app in list_app:

			name_div = app.find("a").get("title")
			
			if is_app_info_downloaded(name_div):
				print("(" + name_div + ") is being skipped because all the information has been already stored")
				#time.sleep(short_sleep_time)
				continue

			url_div = "https://apkpure.com" + app.find("a").get("href") + "/versions"
			
			App = Application(category, name_div, url_div)

			print("scrapping app: " + App.name)
			scrap_version(App)

			Apps.append(App)
		
		
		download_category_page(category, page + 1, max_page)




def is_app_info_downloaded(app):
	global Apps
	for a in Apps:
		#print(a.name + " == " + app)
		if app == a.name:
			return True

	return False


def load_json(category):
	global Apps

	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	json_data = fileDir +"/" + category +"/apps.json"

	if os.path.exists(json_data):
		with open(json_data) as json_data:
			apps = json.load(json_data)
			for app in apps:
			 	a = Application('','','')
			 	a.__dict__ = app

			 	versions = []
				
				for v in app["versions"]:
					ver = AppVersion(v["version"], v["url"], v["date"], v["size"])
					versions.append(ver)
					
				a.versions = versions
				Apps.append(a)



def dump_json(category):
	fileDir = os.path.dirname(os.path.abspath(__file__)) 

	s = json.dumps([ob.__dict__ for ob in Apps], cls=ComplexEncoder)# s set to: {"x":1, "y":2}

	json_data = fileDir +"/" + category +"/apps.json"
	f= open(json_data,"w+")
	f.write(s);
	f.close()

if __name__ == '__main__':

	global max_Date
	global min_apks
	global max_apks
	global months
	global days

	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('category', type=str,
                    help='Category to search')

	parser.add_argument('--start-page', '-s', type=int,
                    help='Start Search Page')


	parser.add_argument('--end-page', '-e', type=int,
                    help='End Search Page')


	parser.add_argument('--max-date', '-d', type=str,
                    help='Maximum valid date to start downloading apks. Default 2016-12-31')



	parser.add_argument('--min-apks', '-min', type=int,
                    help='Minimum number of apks to be a valid app')


	parser.add_argument('--max-apks', '-max', type=int,
                    help='Maximum number of apks to be a valid app')

	parser.add_argument('--months', '-months', type=int,
                    help='Months between each download')


	parser.add_argument('--days', '-days', type=int,
                    help='Days between each download')





	args = parser.parse_args()

	#Configuration to download

	print("Arguments configurations")

	if args.max_date:
		max_Date = args.max_date
		print("Max Date: " + max_Date)

	if args.min_apks:
		min_apks = args.min_apks
		print("Min APks: " + str(min_apks))

	if args.max_apks:
		max_apks = args.max_apks
		print("Max Apks: " + str(max_apks))

	if args.months:
		months = args.months
		print("months: " + str(months))

	if args.days:
		days = args.days
		print("days: " + str(days))


	print("Loading Json")
	load_json(args.category)
	print("Downloading apps versions information")
	download_category_page(args.category,args.start_page,args.end_page)
	print("Saving info into json")
	dump_json(args.category)

	print("About to download apks")
	for app in Apps:
		print("Checking: " + app.name)
		if(app.is_valid()):
			app.download_apks()


		dump_json(args.category)


	

		



			