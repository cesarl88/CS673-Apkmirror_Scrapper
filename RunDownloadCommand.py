import os
import subprocess, sys
import json
import time

if __name__ == '__main__':

	IsFromAPKMirror = True #DO NOT CHANGE THIS

    ######################
	#Manualy set Category#
	######################
	Category = 'PRODUCTIVITY'

	if not IsFromAPKMirror:
		print("")
		#python ./aptoide.py 'EDUCATION' 'QuizLet'

		#EDUCATIO
		#Apps = ['QuizLet', 'RosettaStone', 'Lumosity']
		#Urls = ['quizlet','languages','lumosity']

		#PRODUCTIVITY
		#	Apps = [
		#		'adobe-acrobat-reader', 'camscanner', 'dropbox', 
		#		'evernote', 'super-file-manager', 'fleksy-legacy', 
		#		'gboard-the-google-keyboard', 'google-inc-calendar','docs', 
		#		'google-drive', 'keep', 'google-talkback',
		#		'google-sheets','slides','lastpass-authenticator',
		#		'mega','cortana','microsoft-excel',
		#		'outlook','office-mobile','microsoft-powerpoint',
		#		'microsoft-corporation-to-do','microsoft-word','nytimes-latest-news',
		#		'pokemon-tv','samsung-notes','starbucks',
		#		'com-teamviewer-teamviewer','comcast-interactive-media-tv','es-file-explorer',
		#		]
		#	Apps = [
		#		'avast-cleanup','bittorrent','snaptube',
		#		'brave','calculator','ccleaner',
		#		'kika-keyboard','google-inc-clock','google-opinion-rewards',
		#		'google-translate','google-inc-earth','',
		#		'kernel-booster','lookout-security-antivirus','microsoft-bing',
		#		'opera-mini-web-browser','network-signal-guru','network-signal-info',
		#		'peel-remote','remote-control-collection','root-checker-basic',
		#		'shareit','android-deskclock','teamviewer',
		#		'titanium-backup','tv-vodafone','vrem-software-development-wifi-analyzer',
		#		'wifi-analyzer','home','fire-tv',
		#		]
			#Urls = ['adobe-acrobat-reader','camscanner','lumosity']
			
		#	i = 0
		#	for app in Apps:

		#		Command = "python ./aptoide.py '" + Category + "' '" + app + "' 'https://" + app + ".en.aptoide.com/versions'" 
		#		print("Command " + Command)
		#		os.system(Command)

	else:

		####################################
		#        *****IMPORTANT******      #
		#   This Array contains the list   #
		#   of search teerms that will     #
		#   return the best result for     #
		#   the app we are looking for     #
		#   Before setting this values     #
		#   Make sure the term only return #
		#   the app you are looking for,   #
		#   and also make sure that there  #
		#   are enough versions            #
		####################################
		Apps = [
				'Adobe Acrobat','CamScanner','dropbox',
				'ES File Explorer Global','Solid Explorer','Solid Explorer ',
				'Google Calendar','Google Docs','Google Drive',
				'Google Slides','Microsoft Cortana','Microsoft Excel',
				'Microsoft OneDrive','Microsoft OneNote','Microsoft PowerPoint',
				'Microsoft Word','Samsung Notes','SwiftKey',
				'SwiftKey'
				]
		
		#Running Category analysis
		for app in Apps:

			Command = "python ./GetCategoryAppsList.py '" + Category + "' 0 '" + app + "'"
			print("Command " + Command)
			os.system(Command)
		 	time.sleep(150) #delay for 10 seconds
			
 	#Running Summarize
	for app in Apps:
		Command = "python ./SummarizeApks.py '" + Category + "' '" + app +"'"
		print("Command " + Command)
		os.system(Command)