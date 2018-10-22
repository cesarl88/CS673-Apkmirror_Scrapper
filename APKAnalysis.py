from smalanalysis.smali.SmaliProject import SmaliProject
from smalanalysis.tools.commands import queryAaptForPackageName

import sys, time 
import os
import subprocess
import json


CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


def delete_last_lines(n=1):
    for _ in range(n):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


def print_same_line(str, n = 1):
	delete_last_lines(n)
	print(str)

	


def main(LocalPath, Category):


	print("Working on " + LocalPath)

	if not os.path.exists(LocalPath):
		print("LocalPath does not exists " + LocalPath)
		return 0

	AppStartDownloadTime = time.time()

	cat_apps = [dI for dI in os.listdir(LocalPath) if os.path.isdir(os.path.join(LocalPath,dI))]	

	ObfuscatedApps = ""
	Report = ""
	CorruptedApps = ""
	AppsAnlazed = ""

	apks_obf = 0
	apks_corr = 0
	#cat_apps = ['My Verizon VZ', 'aida']

	total = len(cat_apps)
	progress = 1
	prog = 0

	#exclude list

	#exclude_lists = ['../../exclusionlist/exclusionlist/exclusionlist.txt' '../../exclusionlist/exclusionlist/Merge.txt']
	
	for app in cat_apps:
		
		app_path = os.path.join(LocalPath,app)
		print_same_line("Analizing " + app, 2)
		print("")
		AppsAnlazed += app + "\n"

		
		apks = [dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith(".apk")]
		
		size = len(apks)

		pr = 0

		for apk in apks:

			cmd = "apkid --json '" + os.path.join(app_path,apk) +"'"
			p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
			(output, err) = p.communicate()

			t = (pr / float((size))) * 100 *  (1 / float(total)) + prog

			print_same_line("Completed: " + str(t) + "%")
			pr += 1

			p_status = p.wait()

			if len(str(output)) > 3:
				try:
					out = json.loads(str(output))
					for x in out:
						xx= out[x]
						for y in xx:
							if y == 'packer' or y == 'obfuscator' or y == 'anti_disassembly':
								ObfuscatedApps+= apk + "\n"
								apks_obf += 1

				except Exception as e:
					print("Exception")
					CorruptedApps +=  cmd + " => "+ str(output)+" \n"
					apks_corr += 1

				
			else:
				print(str(len(output)))
				CorruptedApps +=  cmd + " => "+ str(output)+" \n------\n"
				apks_corr += 1

			


		Report+= app + "\n"
		Report+= "Number of APKS("+str(len(apks))+")" + "\n"
		Report+= "Number of APKS Good to go("+str(len(apks) - apks_obf - apks_corr)+")" + "\n"
		Report+= "Number of APKS Packed("+str(apks_obf)+")\n\n"
		Report+= "Number of APKS Corrupted("+str(apks_corr)+")\n\n"

		prog = (progress / float(total)) * 100.00
		progress += 1
		


		
	Elapsed_time = time.time() - AppStartDownloadTime
	Report += "Analized Apps:\n" + AppsAnlazed 
	Report += "Elapsed Time secs: " + str(Elapsed_time) + " s "
	Report += "Elapsed Time minutes: " + str(Elapsed_time / 60) + " s "

	File = open(LocalPath + "/Report.txt", "w")
	File.write(Report)
	File.close()

	File = open(LocalPath + "/Obfuscated.txt", "w")
	File.write(ObfuscatedApps)
	File.close()


	File = open(LocalPath + "/CorruptedApps.txt", "w")
	File.write(CorruptedApps)
	File.close()

	return 0


if __name__ == '__main__':

	if len(sys.argv) < 2:
		print("Usage")
		print("python APKAnalysis.py 'Category'")
	else:

		Category = sys.argv[1]
		LocalPath = os.path.join('.',Category) 
		main(LocalPath, Category,)

	

	#APK = "/Users/cesarsalazar/Documents/NJIT/Fall 2018/CS 673/Final Project/APKMirrorScrapper/COMMUNICATION/Plus Messenger/plus-messenger-3-13-1-9-release.apk"

	#package = queryAaptForPackageName(APK)
	#print(package);

	#proj_A = SmaliProject()
	#proj_A.parseProject('/Users/cesarsalazar/Documents/NJIT/Fall 2018/CS 673/Final Project/APKMirrorScrapper/COMMUNICATION/Plus Messenger/plus-messenger-3-13-1-9-release.apk.smali')
	#print(proj_A.isProjectObfuscated())
	
	#proj_B = SmaliProject()
	#proj_B.parseProject('/Users/cesarsalazar/Documents/NJIT/Fall 2018/CS 673/Final Project/APKMirrorScrapper/COMMUNICATION/Plus Messenger/plus-messenger-4-2-1-1-release.apk.smali')
	#print(proj_B.isProjectObfuscated())
#'com.bsb.hike'
	#print(proj_A.differences(proj_B,[]))


  

 #python3 sa-metrics '/Users/cesarsalazar/Documents/NJIT/Fall 2018/CS 673/Final Project/APKMirrorScrapper/COMMUNICATION/Plus Messenger/plus-messenger-3-13-1-9-release.apk.smali' '/Users/cesarsalazar/Documents/NJIT/Fall 2018/CS 673/Final Project/APKMirrorScrapper/COMMUNICATION/Plus Messenger/plus-messenger-4-2-1-1-release.apk.smali' 'org.telegram.plus'
 #python3 sa-metrics '/Users/cesarsalazar/Documents/NJIT/Fall 2018/CS 673/Final Project/APKMirrorScrapper/COMMUNICATION/Hike Messenger/hike-4-12-2-release.apk.smali' '/Users/cesarsalazar/Documents/NJIT/Fall 2018/CS 673/Final Project/APKMirrorScrapper/COMMUNICATION/Hike Messenger/hike-4-9-1-release.apk.smali' 'com.bsb.hike'

