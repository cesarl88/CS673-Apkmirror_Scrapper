import os
import subprocess, sys
import json
import time

if __name__ == '__main__':

	IsFromAPKMirror = True #DO NOT CHANGE THIS

    ######################
	#Manualy set Category#
	######################
	Category = 'FINANCE'



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
		'Paypal Here','Simple - Better','Robinhood',
		'square cash','blockchain Cash Wallet','Coinbase',
		'Mobile Recharge DTH','Phonepe','Barclay'
	]

	username = "cl33"
	server = 1
	repoDirectory = "./CS673/Tools/CS673-Apkmirror_Scrapper/"

	
	#Running Category analysis
	for app in Apps:

		print("########")
		print(app)

		Command = "mkdir "+Category+"/"
		print(Command)

		Command = "mkdir "+Category+"/"+app.replace(" ", "\ ")+"/"
		print(Command)

		Command = "rm "+Category+"/"+app.replace(" ", "\ ")+"/SearchProcessDone"
		print(Command)


		Command = "scp ./"+Category+"/" + app.replace(" ", "\ ") + "/* "+username+"@afs"+str(server)+".njit.edu:" + repoDirectory + Category + "/" + app.replace(" ", "\ ")+"'"
		print(Command)

		Command = "python ./GetCategoryAppsList.py '" + Category + "' 0 '" + app + "'"
		print(Command)


		Command = "scp "+username+"@afs"+str(server)+".njit.edu:" + repoDirectory + Category+"/"+app.replace(" ", "\ ")+"/*' ./"+Category+"/" + app.replace(" ", "\ ") + "/"
		print(Command)

		Command = "rm -r "+Category+"/"+app.replace(" ", "\ ") +"/"
		print(Command)
			
