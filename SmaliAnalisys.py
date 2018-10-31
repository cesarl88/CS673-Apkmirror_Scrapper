from smalanalysis.smali import SmaliObject, ChangesTypes, SmaliProject, Metrics
from smalanalysis.tools.commands import queryAaptForPackageName

import sys, time, csv
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

	

def main(LocalPath, Category, option):


	print("Working on " + LocalPath)

	if not os.path.exists(LocalPath):
		print("LocalPath does not exists " + LocalPath)
		return 0

	AppStartDownloadTime = time.time()

	cat_apps = [dI for dI in os.listdir(LocalPath) if os.path.isdir(os.path.join(LocalPath,dI))]	

	cat_apps = sorted(cat_apps)
	ObfuscatedApps = ""
	Report = ""
	CorruptedApps = ""
	AppsAnlazed = ""

	apks_num = 0

	total = len(cat_apps)
	progress = 1
	prog = 0

	#exclude list

	exclude_lists = ['./exclusionlist/exclusionlist.txt', './exclusionlist/Merge.txt']


	set_total_metrics = False	
	total_metrics = {}
	headers = ""

	FailList = ""


	headers_printed = False	
	for app in cat_apps:
		try:
			FailList += app + "-------\n" 

			app_path = os.path.join(LocalPath,app)
			print("Analizing " + app, 2)
			print("")
			AppsAnlazed += app + "\n"

			pr = 0
			smali_count = 0
			csv_file = ""

			if option == 0:
				apks = [dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith(".apk")]
				#print(apks)
				size = len(apks)
				for i in range(size - 1):
					if smali_count == 12:
						break

					t = (pr / float((size))) * 100 *  (1 / float(total)) + prog

					print_same_line("Completed: " + str(t) + "%")

					version0 = os.path.join(app_path,apks[i])
					smali = version0 + ".smali"
					if os.path.exists(smali): 
						smali_count+=1
						continue

					Command = "sa-disassemble '" + version0 +"'"
					#print("Command " + Command)
					
					try:
						p = subprocess.Popen(Command, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
						(output, err) = p.communicate()
						p_status = p.wait()
						smali_count+=1
					except KeyboardInterrupt:
						print("Exiting")
						sys.exit(0)
					except Exception as e:
						FailList += version0 + '\n'
						#print(FailList)

				if smali_count < 12:
					FailList+= "app has " + str(smali_count) +" smali files, Missing "+str(12 - smali_count)+"\n"

				smali_count = 0
					
			elif option == 1:

				#if os.path.exists(app_path +"/Obfuscated.txt"): 
				#	print("Not enough Apps majority are obfuscated")
				#	continue

				summary_path = app_path + "/" + app + "_Summary.csv"
				print("Checking for " + summary_path)
				if os.path.exists(summary_path):
					with open(summary_path) as csv_file:
						print(app + " summary csv Found")
						csv_reader = csv.reader(csv_file, delimiter = ",")
						line_count = 0

						t = 0
						for row in csv_reader:
							if len(row) == 0:
								continue
							if t== 0:
								if not set_total_metrics:
									for column in row:
										#print(column)
										if column != "addedLines" and column != 'removedLines':
											total_metrics[column] = 0
									set_total_metrics = True
								t = 1
								print(total_metrics)
							else:
								print("Here")
								p = 0
								for key, value in total_metrics.items():
									print(key)
									print(row[p])
									if key != "addedLines" and key != 'removedLines':
										total_metrics[key] += int(row[p])
										p += 1
								
									#print(column)
									

						print(total_metrics)
					continue


				apks = [dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith(".smali")]
				#print(apks)
				apks = sorted(apks)
				print(apks)
				size = len(apks)
				print("Size " + str(size))
				pkg = ""
				if size > 0:
					pkg = queryAaptForPackageName(os.path.join(app_path,apks[0]).replace(".smali",""))

				print("Package: " + str(pkg))

				for i in range(size - 1):
					nextI = i + 1
					version0 = os.path.join(app_path,apks[i])
					version1 = os.path.join(app_path,apks[nextI])
					print("Comparing %s against %s : Package: %s" % (version0, version1,pkg))


					try:
						print("Parsing old Version")
						old = SmaliProject.SmaliProject()
						old.parseProject(version0, None, exclude_lists, None, True)

						print("Checking old version obfuscated")
						if old.isProjectObfuscated():
							raise Metrics.ProjectObfuscatedException()

						mold, moldin = Metrics.countMethodsInProject(old)

						Compared = False
						metrics = {}

						while not Compared and nextI < size - 1:
							try:
								print("Parsing New Version")
								new = SmaliProject.SmaliProject()
								new.parseProject(version1, None, exclude_lists, None, True)
								
							    #parseProject(new, args.smaliv2, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)

								print("Getting Metrics")
								mnew, mnewin = Metrics.countMethodsInProject(new)
								print("Checking New version obfuscated")
								if new.isProjectObfuscated():
									raise Metrics.ProjectObfuscatedException()


								print("Comparing differences")	
								diff = old.differences(new, [])
								#print(diff)
								


								print("Extracting differences")	
								Metrics.initMetricsDict("", metrics)
								metrics["#M-"] = mold + moldin
								metrics["#M+"] =  mnew + mnewin
								Metrics.computeMetrics(diff, metrics, "", True, False)

								Compared = True
							except Exception as e:
								nextI += 1
								version1 = os.path.join(app_path,apks[nextI])
						

						

					except Metrics.ProjectObfuscatedException:
						print("This project is obfuscated. Unable to proceed.", file=sys.stderr)
						continue
					except Exception as e:
						print("Error parsing")
						print(e)
						continue
						#sys.exit(0)
					
					if not metrics:
						continue
					print("Parsing differences")

					bases = [""]

					if not set_total_metrics:
						total_metrics = dict.fromkeys(metrics.keys(), 0)
						set_total_metrics = True
					
					for b in bases:
						if not headers_printed:
							for k in filter(lambda x: type(metrics[x]) != set and x.startswith(b), metrics.keys()):
								headers += k[len(b):] + ','
							
							headers += "addedLines"  +  ','
							headers += "removedLines"
							headers += '\n'
							headers_printed = True

					#print(b, end=',')


					for k in filter(lambda x: type(metrics[x]) != set and x.startswith(b), metrics.keys()):
						csv_file += str(metrics[k]) +  ','
						total_metrics[k] += metrics[k] 



					csv_file += '|'.join(metrics["{}addedLines".format(b)]) +  ','
					csv_file += '|'.join(metrics["{}removedLines".format(b)]) +  ','	

					csv_file += '\n'
				
				File = open(LocalPath + "/" + app + "/"+app+"_Summary.csv", "+w")
				File.write(headers + '\n' + csv_file)
				File.close()

		except Exception as e:
			print(e)
			print("Skiping " + app)
			#sys.exit(0)


		

	if option == 0:
		File = open(LocalPath + "/Category_Failed.txt", "+w")
		File.write(FailList)
		File.close()
	else:
		total_csv = ""
		total_avg = ""
		for key, value in total_metrics.items():
			total_csv += str(value) + ','
			total_avg += str(value / total) + ','
		

		File = open(LocalPath + "/Category_Summary.csv", "+w")
		File.write(headers + '\n' + total_csv + '\n' + total_avg)
		File.close()

		prog = (progress / float(total)) * 100.00
		progress += 1

				#Command = 'sa-metrics ' + version0 + ' '+ version1 +' -e ../../exclusionlist/exclusionlist/exclusionlist.txt ../../exclusionlist/exclusionlist/Merge.txt > version' + str(i) + '_version' + str(nextI) + '.csv' 

				##print_same_line(Command)
				#os.system(Command)

	Elapsed_time = time.time() - AppStartDownloadTime

	print('Elapsed Time: ' + str(Elapsed_time / 60) + " min")
	return 0


if __name__ == '__main__':

	try:
		if len(sys.argv) < 3:
			print("Usage")
			print("python SmaliAnalysis.py 'Category' 'option'")
		else:

			Category = sys.argv[1]
			option = int(sys.argv[2])
			LocalPath = os.path.join('.',Category) 
			main(LocalPath, Category, option)


	except Exception as e:
		raise
	
	
	

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

