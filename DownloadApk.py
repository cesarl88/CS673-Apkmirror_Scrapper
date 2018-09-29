
import csv
import sys
import requests
import brotli
import bs4
from bs4 import BeautifulSoup
import time


def download_apk(app_name, url):
	print 'Downloading APK ' + url 
	read_page = 0

	if 'download.php' not in url:
		read_page = 1


	if read_page:
		if 'https:/www' in url:
			url = url.replace('https:/', 'https://')
		
		download_page = requests.get(url)
		download_html = download_page.content
		#print download_html	

		soup_app = BeautifulSoup(download_html, 'html.parser')
		#Finding details table
		apk_detail = soup_app.find_all('p', attrs={'class' : 'notes'})

		f = open('htmlFileName.html''',"w+")
		f.write(download_html);
		f.close()

		#print apk_detail
		for p in apk_detail:
			print p
			if p.span.a:
				url = 'http://www.apkmirror.com/' +  p.span.a.get('href')

		print 'downloading ' + url
		download_page = requests.get(url)


	else:
		download_page = requests.get(url)
		
	with open(app_name + '.apk','wb') as f:
		f.write(download_page.content)


	time.sleep(10) #delay for 5 seconds


if __name__ == '__main__':

	FilePath = sys.argv[1] 
	with open(FilePath) as csv_file:
		print 'Csv Found'
		csv_reader = csv.reader(csv_file, delimiter = ',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count = 1
			else:
				download_apk(row[0], row[3])




