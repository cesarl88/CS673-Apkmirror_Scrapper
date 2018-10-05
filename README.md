
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

"PRODUCTIVITY" is the Category that you will look for in Google Play Store
4 is the number of times I will refresh the google play search list. 
   - 1 to get 60 apps
   - 2 to get 120 apps
   - 3 to get 180
   - 4 to get 240
   and so on

This script will create a folder for the category and a folder per app.
   



