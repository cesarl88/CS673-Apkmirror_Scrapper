import sys
import os
import bs4
from bs4 import BeautifulSoup
import requests
import brotli 
import time


#Retrieves html content from apkmirror
def get_html_content(url, path):
	
	time.sleep(5) #delay for 5 seconds
	#url = "https://www.apkmirror.com/apk/samsung-electronics-co-ltd/artcanvas/artcanvas-1-0-41-release/artcanvas-draw-paint-1-0-41-android-apk-download/"
	print 'URL: ' + url
	print 'path: ' + path

	headers = {
        'authority': "www.apkmirror.com,",
        'method': "GET",
        'path': path,
        'scheme': "https",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9",
        'cookie': "__cfduid=d699853d9c626a37ebd9c0c3cf3dd1aa31537726781; _ga=GA1.2.267269207.1537726795; _gid=GA1.2.524874324.1537726795; bm_monthly_unique=true; bm_daily_unique=true; __qca=P0-1787143825-1537726800793; bm_sample_frequency=100; bm_last_load_status=NOT_BLOCKING; _gali=searchButton",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        'cache-control': "no-cache",
        'postman-token': "abc33b57-5b55-176d-1301-aed81d0102s5"
        }

	response = requests.request("GET", url, headers=headers)

	#print response.content
	#print response.status
	return brotli.decompress(response.content)


#It analizes the description of the APK to retrieve useful info about the version
def analize_apk_description(description_html, version_dir):

	#print description_html
	#Parsing HTML
	soup_app = BeautifulSoup(description_html, 'html.parser')
	#Finding details table
	apk_detail = soup_app.find('div', attrs={'class' : 'apk-detail-table'})
	apk_details_str = ' ' 

	#Analyzing Details Table
	for detail in apk_detail.contents:
		if type(detail)  is not bs4.element.NavigableString and detail['class'][0] == 'appspec-row':
			for det in detail.contents:
				#print type(det)
				if type(det)  is not bs4.element.NavigableString and det['class'][0] == 'appspec-value':
						if det.string:
							apk_details_str += det.string + ' '
						elif det.div and det.div.string:
							apk_details_str += det.div.string + ' '
						else:
							for d in det.contents:
								if type(d)  is  bs4.element.NavigableString:
									apk_details_str += d + ' '
								elif d.string:
									apk_details_str += d.string + ' '

	apk_details_str = apk_details_str.replace('\n', ' ')
	#Saving info in a separate file
	f = open(version_dir + ".txt","w+")
	f.write(apk_details_str);
	f.close()	

	return apk_details_str



########
# Main #
########
if __name__ == '__main__':

	#Current Directory
	fileDir = os.path.dirname(os.path.abspath(__file__)) 

	#APK Mirror base URL
	apk_Mirror_url = 'https://www.apkmirror.com/'

	#Expected Parameters
	# 1. '/Art & Design/Canvas/Html/' -->App Base Drectory
	# 2. Canvas  --> App Name
	# 3. 1 --> Number of Start Search Pages 
	# 3. 2 --> Number of Search Pages eg Searh_Page1.html, Search_Page2.html....Search_Pagen.html


	#################################################################################
	#  THe directory is supposed to be as follow									#
	#   + Category eg. Art & Design													#
	#	    - AppName eg. Canvas													#
	#		- Html : Added becuase I had something else in mind, so i just left it  #
	#################################################################################
	Directory = sys.argv[1]
	AppName =  sys.argv[2]
	SearchPages = int(sys.argv[4])
	Start_SearchPages = int(sys.argv[3])

	if Start_SearchPages < 1:
		Start_SearchPages = 1

	if SearchPages <= Start_SearchPages:
		SearchPages = Start_SearchPages + 1
	
	#CSV Headers
	csv_content = 'App Version, Date,  Details URL, Download URl, APK Info\n'

	# Looping in all search pages
	for Start_SearchPages in range(1,SearchPages + 1):
		
		htmlFileName = fileDir + Directory + 'Search_Page'+ str(Start_SearchPages) +'.html'
		HtmlFile = open(htmlFileName, "r")
		HtmlContent = HtmlFile.read()

		print 'Parsing : ' + htmlFileName

		soup = BeautifulSoup(HtmlContent, 'html.parser')
		list_widget = soup.find('div', attrs={'class': 'listWidget'})
		
		#Reading List of app versions
		for widget in list_widget.contents:
			if type(widget)  is not bs4.element.NavigableString and widget['class'][0] == 'appRow':
				
				#Getting Date
				Date =  widget.div.contents[3].span.span.string	
				Date = Date.replace(',', ' ')

				#Getting Variants APK URL
				url_1 = widget.div.contents[7].contents[1].contents[3].a.get('href')
				url_variants = apk_Mirror_url + url_1	

				temp_url =  url_1[ 0 : len(url_1) - 1 ]
				l_index =  temp_url.rfind('/')
				url_download = ' '

				#Getting App Version Name	
				Name = url_1[l_index + 1 : len(temp_url) ]
				
				print '** App Version **'
				print 'App Name : ' + Name
				print 'App url variants : ' + url_variants

				app_dir = fileDir + sys.argv[1] + AppName
				
				# Downloading Variants HTML
				variant_html_page = get_html_content(url_variants, url_1)
				#Temp Reading from File for testing
				#variant_html_file = open(fileDir + '/_Test.html', "r")
				#variant_html_page = variant_html_file.read()

				apk_details_str = ' '


				soup_variants = BeautifulSoup(variant_html_page, 'html.parser')
				v_list_widget = soup_variants.find_all('div', attrs={'class': 'listWidget'})
				for v_widget in v_list_widget:
					if len(v_widget.contents) > 0:
						for it in v_widget.contents:
							if type(it) is not bs4.element.NavigableString and it.string == "Download":
								# Here needs to loop for variants if needed
								# Downloading Variant HTML
								download_url =  v_widget.contents[5].contents[1].contents[3].contents[1].a.get('href').strip()
								download_url = apk_Mirror_url + download_url
								apk_html = get_html_content(download_url, download_url)	
								apk_details_str += ',' + analize_apk_description(apk_html,  app_dir)
								
								#Temp Reading from File for testing
								#tempFile = fileDir + sys.argv[1] + '/Test_release.html'
								#detail_html_file = open(tempFile, "r")
								#apk_html = detail_html_file.read()
								#apk_details_str += ',' + analize_apk_description(apk_html,  app_dir + '_' + Name)

				print download_url
				
				download_url = download_url.replace('//', '/')	

				print 'App url Description : ' + download_url
				
				csv_content += Name + ', ' + Date +',' +  download_url +','+ download_url + 'download,' + apk_details_str + '\n'


	#Saving CSV Content

	f= open(fileDir + sys.argv[1] + AppName  + "_Description.csv","w+")
	f.write(csv_content);
	f.close()


										

								

