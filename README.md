
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



<b>python ./DownloadSearchHtmlContent.py '/Art & Design/Canvas/Html/' Canvas 3</b>

'/Art & Design/Canvas/Html/' is where the SearchPages are stored and where the final output will be saved.
Canvas is the name of the app
3 is the number of search pages

It will analyse all the search pages and create a csv with the apk download link, date and release name


<h1>RetrieveSearchPages.py Usage</h1>

<b>python ./RetrieveSearchPages.py  Canvas</b>

It will download the html content of all the search pages for Canvas which will be the word used to do the search in APK Mirrir
