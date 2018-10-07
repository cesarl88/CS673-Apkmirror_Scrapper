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
import _brotli


def getCategoryAppList(Category, pages):


	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	url = "https://play.google.com/store/apps/category/"+Category+"/collection/topselling_free"

	querystring = {"authuser":"0"}

	#payload = "start=0&num=60&numChildren=0&ipf=1&xhr=1&token=jC4VzuQT8jtyxDQt43bhtnsIkZw%3A1538679259608"
	headers = {
		"accept": "*/*",
		"accept-encoding": "gzip, deflate, br",
		"accept-language": "en-US,en;q=0.9",
		"content-length": "92",
		"content-type": "application/x-www-form-urlencoded;charset=UTF-8",
		"cookie": "ANID=AHWqTUnlUBROwEbZWe2fmATcAWosu4AhGto40Bzd5zghT3nZkOLS2H2lVQpwj53_; _ga=GA1.3.312782823.1537726972; OTZ=4590383_72_76_104100_72_446760; OGPC=19005936-2:19006913-1:19006965-1:19007018-1:19007661-2:19008076-2:422038528-9:; SID=hAaJw-Jwy5_4nJ8UXg0QXox_R0-CxfQKPtRR-HVtNe1kEfRuhBD98_6oNmiFatXTpq2QkQ.; HSID=AcuzO_mwckH3zqYmH; SSID=A9oOqtbDOHU_ug_LR; APISID=VgBJvUOCUUMsLS5k/AUMR2z4bcdAPgvvYz; SAPISID=qTpxiqe_TS8tqeFP/AlgbNrc5_b5KGG_5I; PLAY_ACTIVE_ACCOUNT=ICrt_XL61NBE_S0rhk8RpG0k65e0XwQVdDlvB6kxiQ8=cls33@njit.edu; _gid=GA1.3.997865890.1538474562; PLAY_PREFS=CuoMCImHm6zIERLgDAoCVVMQ0oO5g-QsGqEMERITFBUWGNQB1QGnAsQE4wXlBegF1wbYBt4G3waQlYEGkZWBBpKVgQaVlYEGl5WBBqSVgQa3lYEGuJWBBsCVgQbBlYEGxJWBBsWVgQbIlYEGzpWBBs-VgQbQlYEG1JWBBtmVgQbylYEGhpaBBoeWgQaMloEGj5aBBpKWgQadloEGnpaBBp-WgQagloEGpZaBBqaWgQanloEGqJaBBu6XgQbvl4EGhZiBBomYgQaKmIEGi5iBBqubgQatm4EGypuBBsubgQbVm4EGvJ2BBt2dgQbnnYEGkJ6BBqGigQbiooEG86KBBvyigQaLo4EGmqSBBr-lgQbqpYEGxqaBBtSmgQbVpoEG1qaBBv6mgQaAp4EGgqeBBoSngQaGp4EGiKeBBoqngQbOqIEG8qiBBvSogQa8rIEG566BBtavgQbBsIEGpLGBBqWxgQaHsoEGibKBBtaygQbJs4EGsbSBBr-5gQbWuYEGjsCBBqLAgQbAwIEGwcCBBvLAgQbBwYEG1sKBBozFgQaPxYEGtMaBBsrGgQbLxoEGsMeBBvjHgQaqyoEG2MyBBtzMgQbdzYEGhs6BBqHPgQbE0oEGldWBBtrYgQbi2IEG8tuBBtjkgQaX5YEGuOiBBs_rgQaw7IEG1_WBBrr7gQa7_4EGyf-BBtWDggbIhIIGuYaCBqaHgganh4IGs4eCBuyHggbth4IG642CBvuNggaJjoIGy5GCBpWYggaPmoIGmZqCBsGaggb3moIGnZ6CBvaiggbipIIGkqWCBp6ogga0qIIG0bWCBq22ggb8uYIG_rmCBv-5ggbCu4IGj7-CBrzBggaQy4IGkcuCBtHLggbczIIG2NCCBvPRggaL0oIG29OCBoHYggaF2oIGjtqCBpzaggaj2oIGxduCBrHcggb43YIG79-CBqbhggbR4YIG5eGCBpbpggaj7YIGhe6CBrPuggax8IIG6_aCBq34ggaz-IIG9vqCBuP7ggbb_IIGgICDBvKBgwbqhIMGkIWDBteFgwbrhYMG14eDBpuIgwa5iIMG8IiDBoWPgwaQj4MG2ZGDBv2Rgwb8koMGrJWDBriVgwbAloMG5ZaDBtyXgwaZm4MG0JyDBvGegwb0noMGlZ-DBsafgwaYoIMGm6CDBv2ggwaproMG7K-DBpW0gwantIMGrbSDBri2gwbgvIMG9LyDBva8gwawvoMGzb6DBp7Dgwa4xoMG5MaDBq3IgwaeyYMGm8qDBvXLgwbKzYMG_s2DBqLQgwa60IMG-dODBuvUgwbP1oMG49eDBunXgwbR2YMGsN-DBojggwaZ4YMG7-ODBqblgwaR5oMGpuyDBursgwaV7oMGwO-DBuPvgwal8oMGnfSDBtX0gwaN-IMGrfuDBoz-gwak_oMGh_-DBqeBhAbdgYQG34GEBvKChAb6g4QGj4SEBteEhAbJiIQGyoiEBr6JhAani4QGmoyEBvaMhAaAjoQGrI6EBoaQhAbbk4QGipiEBoeZhAaWmYQG_ZqEBvmchAaKnYQG4Z-EBpWghAbNo4QGz6OEBtCjhAbTo4QGjqSEBqGkhAaopYQG_6eEBtuohAaSqYQGk6mEBsuphAbBr4QG2rOEBsq0hAaltYQGoLaEBqG2hAbVtoQGrbiEBuG4hAbyuIQGoLmEBsC5hAbIu4QG0ruEBv27hAaYvYQGs72EBoe_hAasv4QGt7-EBqPBhAbkwoQG8sKEBozDhAaaw4QG6MWEBtnHhAamyIQGtsiEBuLJhAaFyoQGk8uEBsvLhAbPy4QGssyEBtzMhAbpzoQG-86EBvjQhAb-0IQGqdGEBtTRhAaB04QGhdOEBobUhAbM14QGr9iEBsfYhAbd2YQG39mEBo_chAak3YQGsd2EBsrdhAbf3YQG6t6EBuHfhAbE4YQG3-GEBuHhhAbk4YQG5eGEBorihAbG5oQGx-aEBuvmhAb_5oQGheeEBobnhAaV54QGwueEBpfohAaZ6IQGm-iEBpzohAbF6YQG8emEBvLphAbU6oQG0uuEBubrhAbK7YQG2--EBrPyhAau9IQGsPSEBo72hAa_9oQG2PaEBoX4hAaH-IQG5fiEBoD5hAbB-YQGKO2NifTjLDokMWRkMWNiYzUtODMyYS00Njc4LWJhNTktMjE2Nzc4NDhlODFlQAFIAA:S:ANO1ljIejNcjltlpGQ; NID=140=nfQYBPDoYJHP680E10jH4l9n-4qUeAociM4dop0JsNhzjSUMrVx5UqaHgSzMwQyJn_W0e1IiEBW9hd6EQhuCKOr1XN8kYfhNDeswX2Njh1m46COdjTsDzLt-7NvlEOysHLdfRjis1BB2hhvt6lnVD9g8skKpz5PImE5fQXdINc6U8xWwHRrBVM8cIXWVVevN1HFMoJ1lGmiFcMlioOCOIg1Amj1RUL2x7IZ8I-LMdo2gJWb9LDUAr6xlDMCQUqepExBHoOeg65QFCwWkEwHAZptswe592JQI-323fNkWKWaoNIfDNg; 1P_JAR=2018-10-4-18; S=billing-ui-v3=ujshduSFC-LbkykLmg_D8brXA4BHHVVS:billing-ui-v3-efe=ujshduSFC-LbkykLmg_D8brXA4BHHVVS; _gat=1; SIDCC=AGIhQKTsH-GHeKSaoxtSXtUXYP61iADZuJDE-X1oL-iPlVcV0ormJGB3YMoTFw0dMdOw6lF8wAE",
		"origin": "https://play.google.com",
		"referer": "https://play.google.com/store/apps/category/"+ Category +"/collection/topselling_free",
		"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
		"x-client-data": "CIu2yQEIpbbJAQjBtskBCKmdygEI2J3KAQjancoBCKijygEY+aXKAQ==",
		"cache-control": "no-cache",
		"postman-token": "43d9911d-720d-4d81-3337-c4fea9cfab5c"
    }

	#response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
	dirName = fileDir + "/" + Category
	if not os.path.exists(dirName):
		os.mkdir(dirName)
		print("Directory " , dirName ,  " Created ")

	for page in range(0,pages):

		start = page * 60
		print("Google Play Category("+Category+") Search : Start Index " + str(start))

		payload = "start="+str(start)+"&num=60&numChildren=0&ipf=1&xhr=1&token=jC4VzuQT8jtyxDQt43bhtnsIkZw%3A1538679259608"
		response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
		
		htmlFileName = dirName +"/" + Category + str(page)+ ".html"
		f= open(htmlFileName,"w+")
		f.write(response.content);
		f.close()
		


#Retrieve Search pages
def read_search(page, app_name):

    print("Downloading Page " + str(page))
    url = "https://www.apkmirror.com/"

    time.sleep(8) #delay for 10 seconds

    querystring = {"post_type":"app_release","searchtype":"apk","s":app_name}
    path = "/?post_type=app_release&searchtype=apk&s=" + app_name
    if page > 1:
       path = "/?post_type=app_release&searchtype=apk&page="+str(page)+"&s=" + app_name
       querystring = {"post_type":"app_release","searchtype":"apk","page":str(page),"s":app_name}

    #print path     
    headers = {
        "authority": "www.apkmirror.com",
        "method": "GET",
        "path": path,
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "cookie": "__cfduid=d699853d9c626a37ebd9c0c3cf3dd1aa31537726781; _ga=GA1.2.267269207.1537726795; _gid=GA1.2.524874324.1537726795; bm_monthly_unique=true; __qca=P0-1787143825-1537726800793; bm_daily_unique=true; bm_sample_frequency=100; _gat=1; bm_last_load_status=NOT_BLOCKING",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "postman-token": "0322ae40-c7ab-50b6-ec7d-59c2bc03a2ab"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    
    content = brotli.decompress(response.content)
    
    
    return content

def readNext(page, app_name, category):

	html_content = read_search(page, app_name)
	soup = BeautifulSoup(html_content, "html.parser")

	#print(html_content)
    
	list_widget = soup.find("div", attrs={"class": "listWidget"})
	#print list_widget
	padding = list_widget.find("div", attrs={"class": "addpadding"})
	if padding or page >= 20:
		print("eop")
	else:
		pagination = soup.find("div", attrs={"class": "pagination desktop"})
		app = app_name.replace(":","").replace("'", "").replace(",", "").replace(".", "")
				

		fileDir = os.path.dirname(os.path.abspath(__file__)) 
		dirName = fileDir + "/" + category + "/" + app  + "/"
		
		
		htmlFileName = dirName + "/Search_Page"+str(page)+"_ " + app  +".html"
		f= open(htmlFileName,"w+")
		f.write(html_content);
		f.close()

		print (htmlFileName + " Saved")

		if pagination:
			print("Content: " + pagination.contents[2].string)
			print ("Page: " + str(page))
        
			if pagination.contents[2].string == "Next >":
				return readNext(page + 1, app_name, category)
			elif len(pagination.contents) > 4 and pagination.contents[4].string and pagination.contents[4].string == "Next >":
				return readNext(page + 1, app_name, category)
			else:
				print("eop")
		else:
			print("eop")
		

	return page    


#Analize Seach Pages

#Retrieves html content from apkmirror
def get_html_content(url, path):
	
	time.sleep(8) #delay for 5 seconds
	#url = "https://www.apkmirror.com/apk/samsung-electronics-co-ltd/artcanvas/artcanvas-1-0-41-release/artcanvas-draw-paint-1-0-41-android-apk-download/"
	print("URL: " + url)
	print("path: " + path)

	headers = {
        "authority": "www.apkmirror.com,",
        "method": "GET",
        "path": path,
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "__cfduid=d699853d9c626a37ebd9c0c3cf3dd1aa31537726781; _ga=GA1.2.267269207.1537726795; _gid=GA1.2.524874324.1537726795; bm_monthly_unique=true; bm_daily_unique=true; __qca=P0-1787143825-1537726800793; bm_sample_frequency=100; bm_last_load_status=NOT_BLOCKING; _gali=searchButton",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "cache-control": "no-cache",
        "postman-token": "abc33b57-5b55-176d-1301-aed81d0102s5"
        }

	response = requests.request("GET", url, headers=headers)

	#print response.content
	#print response.status
	return brotli.decompress(response.content)


#It analizes the description of the APK to retrieve useful info about the version
def analize_apk_description(description_html, version_dir):

	#print description_html
	#Parsing HTML
	soup_app = BeautifulSoup(description_html, "html.parser")
	#Finding details table
	apk_detail = soup_app.find("div", attrs={"class" : "apk-detail-table"})
	apk_details_str = " " 

	#Analyzing Details Table
	for detail in apk_detail.contents:
		if type(detail)  is not bs4.element.NavigableString and detail["class"][0] == "appspec-row":
			for det in detail.contents:
				#print type(det)
				if type(det)  is not bs4.element.NavigableString and det["class"][0] == "appspec-value":
						if det.string:
							apk_details_str += det.string + " "
						elif det.div and det.div.string:
							apk_details_str += det.div.string + " "
						else:
							for d in det.contents:
								if type(d)  is  bs4.element.NavigableString:
									apk_details_str += d + " "
								elif d.string:
									apk_details_str += d.string + " "

	apk_details_str = apk_details_str.replace("\n", " ").encode("utf-8")
	#Saving info in a separate file
	f = open(version_dir + ".txt","w+")
	f.write(apk_details_str);
	f.close()	

	return apk_details_str


def ProcessSearchPages(AppName, category,Start_SearchPages, SearchPages):

	#Current Directory
	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	dirName = fileDir + "/" + category

	#APK Mirror base URL
	apk_Mirror_url = "https://www.apkmirror.com/"

	#Expected Parameters
	# 1. "/Art & Design/Canvas/Html/" -->App Base Drectory
	# 2. Canvas  --> App Name
	# 3. 1 --> Number of Start Search Pages 
	# 3. 2 --> Number of Search Pages eg Searh_Page1.html, Search_Page2.html....Search_Pagen.html


	#################################################################################
	#  THe directory is supposed to be as follow									#
	#   + Category eg. Art & Design													#
	#	    - AppName eg. Canvas													#
	#		- Html : Added becuase I had something else in mind, so i just left it  #
	#################################################################################
	Directory = "/" + AppName.replace(":","").replace(",","").replace("'","").replace("'","").replace(".","") 

	#SearchPages = int(sys.argv[4])
	#Start_SearchPages = int(sys.argv[3])

	#if Start_SearchPages < 1:
	#	Start_SearchPages = 1

	#if SearchPages <= Start_SearchPages:
#		SearchPages = Start_SearchPages + 1
	
	#CSV Headers
	csv_content = "App Version, Date,  Details URL, Download URl, APK Info\n"

	urls = []
	today = datetime.now()
	#OldDate = today + relativedelta(months= +2)
	AppNumbers = {}
	Dates = {}
	difference_in_months = 2

	# Looping in all search pages
	for Start_SearchPages in range(1,SearchPages + 1):
		
		htmlFileName = dirName + Directory + "/Search_Page"+str(Start_SearchPages) +"_ " + AppName.replace(",","").replace("'","").replace(".","") +".html"

		if not os.path.exists(htmlFileName):
			print("Search not found")
			continue

		HtmlFile = open(htmlFileName, "r")
		HtmlContent = HtmlFile.read()

		print("Parsing : " + htmlFileName)

		soup = BeautifulSoup(HtmlContent, "html.parser")
		list_widget = soup.find("div", attrs={"class": "listWidget"})
		
		#Reading List of app versions
		for widget in list_widget.contents:
			if type(widget)  is not bs4.element.NavigableString and widget["class"][0] == "appRow":
				
				#Getting Dev
				byDev = widget.find("a", attrs={"class": "byDeveloper"}).string

				if not byDev in AppNumbers:
					AppNumbers[byDev] = 0
				
					



				#Getting Date
				Date =  widget.div.contents[3].span.span.string	
				print("################")
				print("Date: " + Date)

				appDate = datetime.strptime(Date, "%B %d, %Y")
				Date = Date.replace(",", " ")
				date_diff = relativedelta(today, appDate)

				print("Dates Difference: Years(" + str(date_diff.years) + "), Months(" +str(date_diff.months)+")")

				if date_diff.years >= 2 and date_diff.months >= 6:
					isdone = False
					for key, value in AppNumbers.items():
						isdone = value >= 15

					if isdone:
						print("Information collected for 2 years stopping process")
						break

				if byDev in Dates:
					difference_in_months = relativedelta(Dates[byDev], appDate).months
					print("Months Difference: " + str(difference_in_months))

				if(difference_in_months < 2):
					print("Less than 2 months ignoring")
					continue

				Dates[byDev] = appDate
#				OldDate = appDate
				#Getting Variants APK URL
				url_1 = widget.div.contents[7].contents[1].contents[3].a.get("href")
				url_variants = apk_Mirror_url + url_1	

				temp_url =  url_1[ 0 : len(url_1) - 1 ]
				l_index =  temp_url.rfind("/")
				url_download = " "

				#Getting App Version Name	
				Name = url_1[l_index + 1 : len(temp_url) ]
				
				print("** App Version **")
				print("App Name : " + Name)
				print("App url variants : " + url_variants)

				app_dir = dirName + Directory + "/" + AppName.replace(":","")
				
				# Downloading Variants HTML
				variant_html_page = get_html_content(url_variants, url_1)
				#Temp Reading from File for testing
				#variant_html_file = open(fileDir + "/_Test.html", "r")
				#variant_html_page = variant_html_file.read()

				apk_details_str = " "
				download_url = ""

				soup_variants = BeautifulSoup(variant_html_page, "html.parser")
				v_list_widget = soup_variants.find_all("div", attrs={"class": "listWidget"})
				for v_widget in v_list_widget:
					if len(v_widget.contents) > 0:
						for it in v_widget.contents:
							if type(it) is not bs4.element.NavigableString and it.string == "Download":
								# Here needs to loop for variants if needed
								# Downloading Variant HTML
								
								if len(v_widget.contents[5].contents[1].contents) < 4:
									#print("Got u")
									#print(v_widget.contents[9]#.contents[1].contents[3].contents[1].a.get("href").strip()
									download_url =  v_widget.contents[9].contents[1].contents[3].contents[1].a.get("href").strip()

								else:
									download_url =  v_widget.contents[5].contents[1].contents[3].contents[1].a.get("href").strip()
								
								download_url = apk_Mirror_url + download_url
								apk_html = get_html_content(download_url, download_url)	
								apk_details_str += "," + analize_apk_description(apk_html,  app_dir)
								
								
								#Temp Reading from File for testing
								#tempFile = fileDir + sys.argv[1] + "/Test_release.html"
								#detail_html_file = open(tempFile, "r")
								#apk_html = detail_html_file.read()
								#apk_details_str += "," + analize_apk_description(apk_html,  app_dir + "_" + Name)

				download = ""
				if download_url == "":
					print("Not Variants")
					download_url = url_variants
					download = url_variants
					apk_details_str += "," + analize_apk_description(variant_html_page,  app_dir)
				else:
					download = download_url + "download"

				download_url = download_url.replace("//", "/")	
				download = download.replace("//", "/")	

				csv_content += Name + ", " + Date +"," +  download_url +","+ download + "," + apk_details_str.decode("utf-8") + '\n'
				urls.append(download_url + "download")
				AppNumbers[byDev] += 1
				print("Number of versions "+ byDev + " so far: " + str(AppNumbers[byDev]))

	#Saving CSV Content

	f = open(dirName + Directory + "/" + AppName.replace(":","").replace(",", "")  + "_Description.csv","w+")
	f.write(csv_content.encode("utf-8"))
	f.close()

	#for link in urls:
	#	print(download_url)
	#	download_apk(app_name, download_url)

#Download APK

def download_apk(Path, app_name, url):
	print("Downloading APK " + url)
	read_page = 0

	if "download.php" not in url:
		read_page = 1


	if read_page:
		if "https:/www" in url:
			url = url.replace("https:/", "https://")
		
		download_page = requests.get(url)
		download_html = download_page.content
		#print download_html	

		soup_app = BeautifulSoup(download_html, "html.parser")
		#Finding details table
		apk_detail = soup_app.find_all("p", attrs={"class" : "notes"})

		#f = open("htmlFileName.html","w+")
		#f.write(download_html);
		#f.close()

		#print apk_detail
		for p in apk_detail:
			#print p
			if p.span.a:
				url = "http://www.apkmirror.com/" +  p.span.a.get("href")

		print("downloading " + url)
		download_page = requests.get(url)


	else:
		download_page = requests.get(url)
		
	with open(Path + "/" + app_name + ".apk","wb") as f:
		f.write(download_page.content)


	time.sleep(8) #delay for 10 seconds

#main

if __name__ == "__main__":

	#print(bs4.__file__)
	print(_brotli.__file__)
	#print(bs4.__file__)
	#from .builder import builder_registry, ParserRejectedMarkup


	#Current Directory
	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	AppName =  sys.argv[1]
	End = int(sys.argv[2])
	#Category = int(sys.argv[3])

	getCategoryAppList(AppName, 4)

	dirName = fileDir + "/" + AppName
	
	Content = "Index, Name\n"
	Apps = []

	for i in range(0, End ):

		print ("Parsing Category Html: " + AppName + ", Index: " + str(i))

		htmlFileName = dirName + "/" +AppName + str(i) + ".html"
		HtmlFile = open(htmlFileName, "r")
		HtmlContent = HtmlFile.read()

		soup = BeautifulSoup(HtmlContent, "html.parser")
		list_app = soup.findAll("div", attrs={"class": "card-content"})

		print(len(list_app))
		for app in list_app:
			div = app.find("a", attrs={"class": "details"})
			#print(div)
			if type(div)  is not bs4.element.NavigableString:
				title = app.find("a", attrs={"class": "title"})
				if title.contents and len(title.contents):
					temp = title.contents[0].split(".")
					Content += u" ".join((temp[0] + ",", temp[1].strip())).encode("utf-8").strip() + "\n"
					splitted = temp[1].strip().encode("utf-8").split()
					size = len(splitted)
					size = min(2, size)
					name = " ".join(splitted[0:size])
					#print Content
					Apps.append(name)


	print("Looping in the Apps")
	#print(Apps)
	search_pages = 1
	for app in Apps:

		Directory = "/" + app.replace(":","").replace(",", "").replace("'","").replace(".","")
		print("Checking if exist " + dirName + Directory)
		if not os.path.exists(dirName + Directory):
			os.mkdir(dirName + Directory )
			print("Directory " , dirName + Directory  ,  " Created ")
		
		print("App Search: " + app)

		if not os.path.exists(dirName + Directory + "/SearchDone"):
			search_pages = readNext(1, app, AppName)
			print("Search Pages: " + str(search_pages))
			f = open(dirName + Directory + "/SearchDone","w+")
			f.write(str(search_pages));
			f.close()
		else:
			File = open(dirName + Directory + "/SearchDone", "r")
			search_pages = int(File.read())
			print("Search pages " + str(search_pages))	

		app = app.replace(":", "")
		app = app.replace(",", "").replace("'","").replace(".","")


		if not os.path.exists(dirName + Directory + "/SearchProcessDone"):
			ProcessSearchPages(app,AppName, 1, search_pages)
			f = open(dirName + Directory + "/SearchProcessDone","w+")
			f.write("Done")
			f.close()
		else:
			print("Search Analysis Done. Skiping")

		if not os.path.exists(dirName + Directory + "/DownloadProcessDone"):
			FilePath = dirName + Directory + "/" + app.replace(",","").replace("'","").replace(".","")  + "_Description.csv"
			with open(FilePath) as csv_file:
					print("Csv Found")
					csv_reader = csv.reader(csv_file, delimiter = ",")
					line_count = 0
					for row in csv_reader:
						if line_count == 0:
							line_count = 1
						else:
							download_apk(dirName + Directory, row[0], row[3])

			f = open(dirName + Directory + "/DownloadProcessDone","w+")
			f.write("Done")
			f.close()
		else:
			print("Download Process Done. Skiping")


		print("#################################")

	
