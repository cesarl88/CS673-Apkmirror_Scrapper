import os
import subprocess, sys
import json

if __name__ == '__main__':

	Categories = [dI for dI in os.listdir('.') if os.path.isdir(os.path.join('.',dI))]#filter(lambda x: os.path.isdir(x), os.listdir('.'))
	if not os.path.exists('./_ValidApps/'):
		os.mkdir('./_ValidApps/')

	Report = ""

	for cat in Categories:
		if cat != ".git":
			folder_app = os.path.join('.',cat)
			Valid_apks_path = './_ValidApps/' + cat + '/' 
			cat_apps = [dI for dI in os.listdir(folder_app) if os.path.isdir(os.path.join(folder_app,dI))]
			
			if not os.path.exists(Valid_apks_path):
				os.mkdir(Valid_apks_path)

			Report += cat + "\n"
			NumberOfApps = 0
			for app in cat_apps:
				apk_path = os.path.join(folder_app,app)
				#print apk_path
				apks = [dI for dI in os.listdir(apk_path) if os.path.isfile(os.path.join(apk_path,dI)) and os.path.join(apk_path,dI).endswith(".apk")]
				
				#validapks = 0
				#for apk in apks:



				if len(apks) >= 12:

					apks_num = 0
					for apk in apks:
						print("about to run apkID")
						cmd = "apkid --json " + apk 
						print(cmd)
						p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
						(output, err) = p.communicate()
 
						## Wait for date to terminate. Get return returncode ##
						p_status = p.wait()
						if output:
							out = json.loads(str(output))
							for x in out:
								xx= out[x]
								for y in xx:
									if y == 'packer':
										Report+= apk + "\n"
										apks_num += 1

					Report+= app + "\n"
					Report+= "Number of APKS("+str(len(apks))+")" + "\n"
					Report+= "Number of APKS Good to go("+str(len(apks) - apks_num)+")" + "\n"
					Report+= "Number of APKS Packed("+str(apks_num)+")\n\n"

					print(Report)
					f = open("./_ValidApps/" + cat + "/" + cat + "(Report).txt","w+")
					f.write(Report)
					f.close()

					if len(apks) - apks_num > 12:
						NumberOfApps+= 1
						
					app = app.replace(" ", "\ ")
					newpath = "./_ValidApps/" + cat + "/" + app + "/"
					Command = "mkdir " + newpath
					print("Creating " + newpath)
					os.system(Command)
					Command = "cp -r ./" + cat + "/" + app +" ./_ValidApps/" + cat + "/"
					print("Copying to " + newpath)
					os.system(Command)
					Command = "cp -r ./" + cat + "/" +cat+".csv" + " ./_ValidApps/" + cat + "/"
					print("Copying to " + newpath)
					os.system(Command)


			print("There are " + str(NumberOfApps) + " Valid apps for this category")
			f = open("./_ValidApps/" + cat + "/" + cat + "(" + str(NumberOfApps) + ").txt","w+")
			f.write("There are " + str(NumberOfApps) + " Valid apps for this category")
			f.close()

