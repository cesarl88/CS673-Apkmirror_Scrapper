import requests
import brotli
import sys
import os
import bs4
from bs4 import BeautifulSoup
import time

def read_search(page, app_name):

    print 'Downloading Page ' + str(page) 
    url = "https://www.apkmirror.com/"

    time.sleep(10) #delay for 10 seconds
    
    querystring = {"post_type":"app_release","searchtype":"apk","s":app_name}
    path = "/?post_type=app_release&searchtype=apk&s=" + app_name
    if page > 1:
       path = "/?post_type=app_release&searchtype=apk&page="+str(page)+"&s=" + app_name
       querystring = {"post_type":"app_release","searchtype":"apk","page":str(page),"s":app_name}

    print path     
    headers = {
        'authority': "www.apkmirror.com",
        'method': "GET",
        'path': path,
        'scheme': "https",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9",
        'cache-control': "no-cache",
        'cookie': "__cfduid=d699853d9c626a37ebd9c0c3cf3dd1aa31537726781; _ga=GA1.2.267269207.1537726795; _gid=GA1.2.524874324.1537726795; bm_monthly_unique=true; __qca=P0-1787143825-1537726800793; bm_daily_unique=true; bm_sample_frequency=100; _gat=1; bm_last_load_status=NOT_BLOCKING",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        'postman-token': "0322ae40-c7ab-50b6-ec7d-59c2bc03a2ab"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    
    content = brotli.decompress(response.content)
    
    print  'Page downloaded' + str(page)

    fileDir = os.path.dirname(os.path.abspath(__file__)) 
    htmlFileName = fileDir + '/Search_Page'+str(page)+'.html'
    f= open(htmlFileName,"w+")
    f.write(content);
    f.close()

    return content

def readNext(page, app_name):

    html_content = read_search(page, app_name)
    soup = BeautifulSoup(html_content, 'html.parser')

    pagination = soup.find('div', attrs={'class': 'pagination desktop'})

    print 'Content: ' + pagination.contents[2].string
    print 'Page: ' + str(page)
    
    if pagination.contents[2].string == 'Next >':
        readNext(page + 1, app_name)
    elif len(pagination.contents) > 4 and pagination.contents[4].string and pagination.contents[4].string == 'Next >':
        readNext(page + 1, app_name)
    else:
        print 'eop'



if __name__ == '__main__':

    app_name = sys.argv[1]  
    print 'Searching for ' + app_name

    readNext(1, app_name)



