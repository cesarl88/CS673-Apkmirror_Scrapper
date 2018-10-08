import os

if __name__ == '__main__':

	Categories = [dI for dI in os.listdir('.') if os.path.isdir(os.path.join('.',dI))]#filter(lambda x: os.path.isdir(x), os.listdir('.'))
	if not os.path.exists('./_ValidApps/'):
		os.mkdir('./_ValidApps/')

	for cat in Categories:
		if cat != ".git":
			folder_app = os.path.join('.',cat)
			Valid_apks_path = './_ValidApps/' + cat + '/' 
			cat_apps = [dI for dI in os.listdir(folder_app) if os.path.isdir(os.path.join(folder_app,dI))]
			
			if not os.path.exists(Valid_apks_path):
				os.mkdir(Valid_apks_path)

			NumberOfApps = 0
			for app in cat_apps:
				apk_path = os.path.join(folder_app,app)
				#print apk_path
				apks = [dI for dI in os.listdir(apk_path) if os.path.isfile(os.path.join(apk_path,dI)) and os.path.join(apk_path,dI).endswith(".apk")]
				
				#validapks = 0
				#for apk in apks:



				if len(apks) >= 12:

					for apk in apks:
						print("about to run apkID")
						os.system("apkid " + apk)

					NumberOfApps+= 1
					app = app.replace(" ", "\ ")
					newpath = "./_ValidApps/" + cat + "/" + app + "/"
					Command = "mkdir " + newpath
					print("Creating " + newpath)
					os.system(Command)
					Command = "cp -r ./" + cat + "/" + app +" ./_ValidApps/" + cat + "/"
					print("Copying to " + newpath)
					os.system(Command)

			print("There are " + str(NumberOfApps) + " Valid apps for this category")
			f = open("./_ValidApps/" + cat + "/" + cat + "(" + str(NumberOfApps) + ").txt","w+")
			f.write("There are " + str(NumberOfApps) + " Valid apps for this category")
			f.close()

