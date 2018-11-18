
<h1>DownloadSearchHtmlContent.py Usage</h1>

Folder Structure
- DownloadSearchHtmlContent.py
+ /Art & Design
  + Canvas
     + Html
     	- Search_page1.html
     	- Search_page2.html
     	- Search_page3.html
     	- . . .



<b>python ./DownloadSearchHtmlContent.py '/Art & Design/Canvas/Html/' Canvas 1 3</b>

'/Art & Design/Canvas/Html/' is where the SearchPages are stored and where the final output will be saved.
Canvas is the name of the app
1 is the starting page
3 is the number of search pages

It will analyse all the search pages and create a csv with the apk download link, date and release name


<h1>RetrieveSearchPages.py Usage</h1>

<b>python ./RetrieveSearchPages.py  Canvas</b>

It will download the html content of all the search pages for Canvas which will be the word used to do the search in APK Mirror

<h1>DownlaodApk.py Usage</h1>

<b>python ./DownlaodApk.py  Canvas_Description.csv</b>

It receives the csv file to analyze and starts downloading each APK. It uses the name from the CSV. All the APK will be downloaded on your current directory.

There is a gap of 10 seconds between each download.


<h1>GetCategoryAppsList.py Usage</h1>
<b>python ./GetCategoryAppsList.py  "PRODUCTIVITY" 4</b>

<b>python ./GetCategoryAppsList.py  "PRODUCTIVITY" 4 "Adobe Scan"</b>

"PRODUCTIVITY" is the Category that you will look for in Google Play Store
4 is the number of times I will refresh the google play search list. 
   - 1 to get 60 apps
   - 2 to get 120 apps
   - 3 to get 180
   - 4 to get 240
   and so on

This script will create a folder for the category and a folder per app. 
if the app name is added to the command, the Google search will be ignored and the script will look for and download all the app apks given in the command. This last parameter will be the search term in APKMirror. 
Make sure to type the category in capitals
   
   
<h1>SummarizeApks.py Usage</h1>
<b>python ./SummarizeApks.py</b>

It wil move all the apps that contain more than 12 apk version to a folder call _ValidApps and it will separate them by category.

The script will run <b>apkid</b> in each apk and create a final report as follows:

TOOLS
Find My
Number of APKS(15)
Number of APKS Good to go(15)
Number of APKS Packed(0)

AppLock
Number of APKS(19)
Number of APKS Good to go(19)
Number of APKS Packed(0)

Call Recorder
Number of APKS(24)
Number of APKS Good to go(24)
Number of APKS Packed(0)

In case it finds any apk packed, It will add the list of apks. The name of this report will be as follows:

TOOLS(19).txt

where TOOLs is the category and 19 the number of apps that have the 12 apks versions.


<h>apkpure_parse.py</h>

usage: apkpure_parse.py [-h] [--start-page START_PAGE] [--end-page END_PAGE]
                        [--max-date MAX_DATE] [--min-apks MIN_APKS]
                        [--max-apks MAX_APKS] [--months MONTHS] [--days DAYS]
                        [--sleep-time SLEEP_TIME]
                        category

Process some integers.

positional arguments:
  category              Category to search

optional arguments:
  -h, --help            show this help message and exit
  --start-page START_PAGE, -s START_PAGE
                        Start Search Page
  --end-page END_PAGE, -e END_PAGE
                        End Search Page
  --max-date MAX_DATE, -d MAX_DATE
                        Maximum valid date to start downloading apks. Default
                        2016-12-31
  --min-apks MIN_APKS, -min MIN_APKS
                        Minimum number of apks to be a valid app
  --max-apks MAX_APKS, -max MAX_APKS
                        Maximum number of apks to be a valid app
  --months MONTHS, -months MONTHS
                        Months between each download
  --days DAYS, -days DAYS
                        Days between each download
  --sleep-time SLEEP_TIME, -sleep SLEEP_TIME
                        Sleep time between each download



Sample:
python apkpure_parse.py tools -s 1 -e 2 -d '2016-12-31' -min 12 -max 12 -months 1 -days 1 -sleep 30

<h>dalvik_analysis.py</h>

usage: dalvik_analysis.py [-h] [--analize-dalvik-table ANALIZE_DALVIK_TABLE]
                          [--generate-dalvik-table GENERATE_DALVIK_TABLE]
                          [--print-dalvik-table PRINT_DALVIK_TABLE]
                          [--print-dalvik-table-an PRINT_DALVIK_TABLE_AN]

Process some integers.

optional arguments:
  -h, --help            show this help message and exit
  --analize-dalvik-table ANALIZE_DALVIK_TABLE, -a ANALIZE_DALVIK_TABLE
                        Analize Dalvik
  --generate-dalvik-table GENERATE_DALVIK_TABLE, -d GENERATE_DALVIK_TABLE
                        Generate Dalvik Table
  --print-dalvik-table PRINT_DALVIK_TABLE, -p PRINT_DALVIK_TABLE
                        Print Dalvik Table
  --print-dalvik-table-an PRINT_DALVIK_TABLE_AN, -pan PRINT_DALVIK_TABLE_AN
                        Print Dalvik Table Analized


this script will analye the dalvik lines added and removed so we can later analyze.





