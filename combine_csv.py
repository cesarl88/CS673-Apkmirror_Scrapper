import os
import argparse
import csv		
import xlsxwriter.workbook 
import re
import zipfile
import shutil
import time
import sys
import statistics
import pickle
import re


# "drawable" :   { "removeOrAdded" : [], "Modified": [] },
# "animation" :  { "removeOrAdded" : [], "Modified": [] },
# "color" :      { "removeOrAdded" : [], "Modified": [] },
# "layout" :     { "removeOrAdded" : [], "Modified": [] },
# "menu" :       { "removeOrAdded" : [], "Modified": [] },
# "string" :     { "removeOrAdded" : [], "Modified": [] },
# "style" :      { "removeOrAdded" : [], "Modified": [] },
# "font" : 	   { "removeOrAdded" : [], "Modified": [] },
# "dimensions" : { "removeOrAdded" : [], "Modified": [] },
# "other" : 	   { "removeOrAdded" : [], "Modified": [] },



pa_anim = re.compile('/anim([.]*)')
pa_color = re.compile('/color([.]*)')
pa_drawable = re.compile('/drawable([.]*)')
pa_layout = re.compile('/layout([.]*)')
pa_menu = re.compile('/menu([.]*)')
pa_values = re.compile('/values([.]*)')
pa_font = re.compile('/font([.]*)')

def get_woorkbook(workbook, csv_path, name):
	worksheet = workbook.add_worksheet(name)

	with open(csv_path) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter = ",")
		line_count = 0
		for r, row in enumerate(csv_reader):
			for c, col in enumerate(row):
				worksheet.write(r, c, col)


def compare_versions(v0_path, v1_path, count):

	print("Comparing")
	print("=> " + v0_path)
	print("=> " + v1_path)
	print("=> " + str(count))
	res0_path = ''
	res1_path = ''

	if os.path.exists(v0_path+"/r"):
		res0_path = v0_path + "/r"
	elif os.path.exists(v0_path+"/res"):
		res0_path = v0_path + "/res"

	if os.path.exists(v1_path+"/r"):
		res1_path = v1_path + "/r"
	elif os.path.exists(v1_path+"/res"):
		res1_path = v1_path + "/res"


	if os.path.isdir(v0_path) and os.path.isdir(v1_path):
		count = count_res(v0_path, v1_path, count)	
	

	print("Now sub")
	print(count)

	if os.path.isdir(res0_path) and os.path.isdir(res1_path):
		return compare_resources(res0_path, res1_path, count)
	else:
		return count

def count_res(v0, v1, count):
	resoures = [fI for fI in os.listdir(v0) if os.path.isfile(os.path.join(v0,fI))]

	#print("v0 = > ")
	#print(v0)
	#print(resoures)
	Modified = 0
	Removed = 0
	for resource in resoures:
		
		v0_file = v0 + "/" + resource
		v1_file = v1 + "/" + resource
		#print(v0_file)
		#print(v1_file)
		
		if (os.path.exists(v1_file)):

			#print("Exists")	
			statinfo0 = os.stat(v0_file)
			statinf1 = os.stat(v1_file)

			if(statinfo0.st_size != statinf1.st_size):

				#print("Modified")
				Modified += 1
		else:
			#print("Removed")
			Removed += 1


	# print(str(count))
	# print(Modified)
	# print(Removed)

	count["Modified"] += Modified
	count["removeOrAdded"]+= Removed

	return count

def compare_resources(v0, v1, count):
	print("=> " + v0)
	print("=> " + v1)
	print("=> " + str(count))
	#time.sleep(2)

	if not os.path.exists(v0):
		return count

	resoures_folders = [dI for dI in os.listdir(v0) if os.path.isdir(os.path.join(v0,dI))]

	Modified = 0
	Removed = 0
	for res in resoures_folders:
		r0 = v0 + "/" + res
		r1 = v1 + "/" + res

		if os.path.exists(r1):
			count = compare_resources(r0,r1, count)
			#print("Here => " + str(count))
		else:
			Removed += sum([len(files) for r, d, files in os.walk(r0)])


	count["Modified"] += Modified
	count["removeOrAdded"]+= Removed
	count = count_res(v0, v1, count)

	return count


# def does_file_exist_in_dir(path, file):
#     folders = [dI for dI in os.listdir(path) if os.path.isdir(os.path.join(path,dI))]

#     for folder in folders:
#     	if (does_file_exist_in_dir(path + "/folder", file)):
#     		return True


# 	files = [fI for fI in os.listdir(path) if os.path.isfile(os.path.join(path,fi))]

# 	files


def save_obj(obj, name ):
    with open('./'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('./' + name, 'rb') as f:
        return pickle.load(f)


def count_resources():
	
	i = 0
	count = {"Removed" : [], "Added" : [], "Modified": []}
	processed = []
	if(os.path.exists("./res_processed.pkl")):
		processed = load_obj("res_processed.pkl")
		count = load_obj("resources_count.pkl")
		
	cat_folders = [dI for dI in os.listdir("./") if os.path.isdir(os.path.join("./",dI))]

	for cat in cat_folders:

		category_path = fileDir + "/" + cat
		print("Category => " + cat)

		cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]

		#print(sorted(cat_apps))
		cat_apps = sorted(cat_apps)
		toRemove = []
		for app in cat_apps:

			if app in processed:
				print(app + " already processed")
				continue

			app_path = os.path.join(category_path,app)
			print("App => " + app)
			apks = sorted([dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith(".apk")])
			
			
			i += 1
			j = 1

			apks = sorted(apks)

			total_app = []

			apk_count = len(apks)

			for index in range(apk_count - 1):

				next_index = (index + 1) % apk_count
				apk = apks[index]
				apk_next = apks[next_index]

				n_folder = app_path + "/" +  apk.replace(".apk","") 
				n_folder_next = app_path + "/" + apk_next.replace(".apk","")

				print("Comparing")
				print("=> " + n_folder)
				print("=> " + n_folder_next)

				try:

					if not os.path.exists(n_folder):
						zip_ref = zipfile.ZipFile(n_folder + ".apk", 'r')
						zip_ref.extractall(n_folder)
						zip_ref.close()
					#time.sleep(3)

					if (not os.path.exists(n_folder)):
						continue
					done = False

					while not done and next_index < apk_count - 1:
						try:	
							if not os.path.exists(n_folder_next):
								zip_ref = zipfile.ZipFile(n_folder_next + ".apk", 'r')
								zip_ref.extractall(n_folder_next )
								zip_ref.close()
							
							#time.sleep(3)

							done = True
						except Exception as e:
							next_index += 1
							apk_next = apks[next_index]
							n_folder_next = app_path + "/" + apk_next.replace(".apk","")
							print("skipping")
							print(e)
							continue

					if (not os.path.exists(n_folder_next)):
								continue

				except Exception as e:
					print(e)
					continue
				


				old_new = compare_versions(n_folder, n_folder_next, {"removeOrAdded" : 0, "Modified" : 0})

				new_old = compare_versions(n_folder_next, n_folder,  {"removeOrAdded" : 0, "Modified" : 0})

				#print("Result")
				print("Old to New => " + str(old_new))
				print("New to Old => " + str(new_old))

				count["Removed"].append(old_new["removeOrAdded"])
				count["Added"].append(new_old["removeOrAdded"])
				count["Modified"].append(old_new["Modified"])

				#lib_count = sum([len(files) for r, d, files in os.walk(n_folder+"/lib")])
				#r_count = sum([len(files) for r, d, files in os.walk(n_folder+"/r")])
				#r_count += sum([len(files) for r, d, files in os.walk(n_folder+"/res")])

				toRemove.append(n_folder)
				toRemove.append(n_folder_next)
				# print("Removing " + n_folder)
				# shutil.rmtree(n_folder)
				# print("Removing " + n_folder_next)
				# shutil.rmtree(n_folder_next)
				j += 1

			#time.sleep(2)	
			
			processed.append(app)

			save_obj(processed, "res_processed")
			save_obj(count, "resources_count")
			if i == 30:
				break
			# print("Removing")
			# for r in toRemove:
			# 	if os.path.exists(r):
			# 		print(r)
			# 		shutil.rmtree(r)

			toRemove = []


	#print(count)
	
	save_obj(count, "resources_count")


def compare_versions_ver_2(v0_path, v1_path, count):

	print("Comparing")
	print("=> " + v0_path)
	print("=> " + v1_path)
	print("=> " + str(count))
	res0_path = ''
	res1_path = ''

	if os.path.exists(v0_path+"/r"):
		res0_path = v0_path + "/r"
	elif os.path.exists(v0_path+"/res"):
		res0_path = v0_path + "/res"

	if os.path.exists(v1_path+"/r"):
		res1_path = v1_path + "/r"
	elif os.path.exists(v1_path+"/res"):
		res1_path = v1_path + "/res"


	if os.path.isdir(v0_path) and os.path.isdir(v1_path):
		count = count_res_ver_2(v0_path, v1_path, count)	
	

	print("Now sub")
	print(count)

	if os.path.isdir(res0_path) and os.path.isdir(res1_path):
		return compare_resources_ver_2(res0_path, res1_path, count)
	else:
		return count

def count_res_ver_2(v0, v1, count):
	resoures = [fI for fI in os.listdir(v0) if os.path.isfile(os.path.join(v0,fI))]

	#print("v0 = > ")
	#print(v0)
	#print(resoures)
	Modified = 0
	Removed = 0
	for resource in resoures:
		
		v0_file = v0 + "/" + resource
		v1_file = v1 + "/" + resource
		#print(v0_file)
		#print(v1_file)
		
		if (os.path.exists(v1_file)):

			#print("Exists")	
			statinfo0 = os.stat(v0_file)
			statinf1 = os.stat(v1_file)

			if(statinfo0.st_size != statinf1.st_size):
				print(v1_file)
				print(count)
				if(pa_drawable.search(v1_file)):
					count["drawable"]["Modified"] += 1
				if(pa_color.search(v1_file)):
					count["color"]["Modified"] += 1
				elif(pa_anim.search(v1_file)):
					count["animation"]["Modified"] += 1
				elif(pa_layout.search(v1_file)):
					count["layout"]["Modified"] += 1
				elif(pa_menu.search(v1_file)):
					count["menu"]["Modified"] += 1
				elif(pa_values.search(v1_file)):
					if("string" in resource):
						count["string"]["Modified"] += 1
					else:
						count["style"]["Modified"] += 1
				elif(pa_font.search(v1_file)):
					count["font"]["Modified"] += 1
				else:
					
					count["others"]["Modified"] += 1
		else:
			#print("Removed")
			if(pa_drawable.search(v1_file)):
					count["drawable"]["removeOrAdded"] += 1
			elif(pa_anim.search(v1_file)):
					count["animation"]["removeOrAdded"] += 1
			elif(pa_color.search(v1_file)):
					count["color"]["removeOrAdded"] += 1
			elif(pa_layout.search(v1_file)):
				count["layout"]["removeOrAdded"] += 1
			elif(pa_menu.search(v1_file)):
				count["menu"]["removeOrAdded"] += 1
			elif(pa_values.search(v1_file)):
				if("string" in resource):
					count["string"]["removeOrAdded"] += 1
				else:
					count["style"]["removeOrAdded"] += 1
			elif(pa_font.search(v1_file)):
				count["font"]["removeOrAdded"] += 1
			else:
				count["others"]["removeOrAdded"] += 1
			#Removed += 1


	# print(str(count))
	# print(Modified)
	# print(Removed)

	#count["Modified"] += Modified
	#count["removeOrAdded"]+= Removed

	return count

def compare_resources_ver_2(v0, v1, count):
	print("=> " + v0)
	print("=> " + v1)
	print("=> " + str(count))
	#time.sleep(2)

	if not os.path.exists(v0):
		return count

	resoures_folders = [dI for dI in os.listdir(v0) if os.path.isdir(os.path.join(v0,dI))]

	Modified = 0
	Removed = 0
	for res in resoures_folders:
		r0 = v0 + "/" + res
		r1 = v1 + "/" + res

		if os.path.exists(r1):
			count = compare_resources_ver_2(r0,r1, count)
			#print("Here => " + str(count))
		else:
			Removed += sum([len(files) for r, d, files in os.walk(r0)])
			if(pa_drawable.search(r0)):
				count["drawable"]["removeOrAdded"] += Removed
			elif(pa_color.search(r0)):
				count["color"]["removeOrAdded"] += Removed
			elif(pa_layout.search(r0)):
				count["layout"]["removeOrAdded"] += Removed
			elif(pa_menu.search(r0)):
				count["menu"]["removeOrAdded"] += Removed
			elif(pa_values.search(r0)):
				if("string" in res):
					count["string"]["removeOrAdded"] += Removed
				else:
					count["style"]["removeOrAdded"] += Removed
			elif(pa_font.search(r0)):
				count["font"]["removeOrAdded"] += Removed
			else:
				count["others"]["removeOrAdded"] += Removed
			


	#count["Modified"] += Modified
	#count["removeOrAdded"]+= Removed
	count = count_res_ver_2(v0, v1, count)

	return count


def count_resources_ver_2():
	
	i = 0
	count = {
				"drawable" :   { "Removed" : [], "Added" : [], "Modified": [] },
				"animation" :  { "Removed" : [], "Added" : [], "Modified": [] },
				"color" :      { "Removed" : [], "Added" : [], "Modified": [] },
				"layout" :     { "Removed" : [], "Added" : [], "Modified": [] },
				"menu" :       { "Removed" : [], "Added" : [], "Modified": [] },
				"string" :     { "Removed" : [], "Added" : [], "Modified": [] },
				"style" :      { "Removed" : [], "Added" : [], "Modified": [] },
				"font" : 	   { "Removed" : [], "Added" : [], "Modified": [] },
				"dimensions" : { "Removed" : [], "Added" : [], "Modified": [] },
				"others" :     { "Removed" : [], "Added" : [], "Modified": [] }
			}

	processed = []

	if(os.path.exists("./res_processed_ver_2.pkl")):
		processed = load_obj("res_processed_ver_2.pkl")
		count = load_obj("resources_count_ver_2.pkl")
		
	cat_folders = [dI for dI in os.listdir("./") if os.path.isdir(os.path.join("./",dI))]

	for cat in cat_folders:

		category_path = fileDir + "/" + cat
		print("Category => " + cat)

		cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]

		#print(sorted(cat_apps))
		cat_apps = sorted(cat_apps)
		toRemove = []
		for app in cat_apps:

			if app in processed:
				print(app + " already processed")
				continue

			app_path = os.path.join(category_path,app)
			print("App => " + app)
			apks = sorted([dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith(".apk")])
			
			
			i += 1
			j = 1

			apks = sorted(apks)

			total_app = []

			apk_count = len(apks)

			for index in range(apk_count - 1):

				next_index = (index + 1) % apk_count
				apk = apks[index]
				apk_next = apks[next_index]

				n_folder = app_path + "/" +  apk.replace(".apk","") 
				n_folder_next = app_path + "/" + apk_next.replace(".apk","")

				print("Comparing")
				print("=> " + n_folder)
				print("=> " + n_folder_next)

				try:

					if not os.path.exists(n_folder):
						zip_ref = zipfile.ZipFile(n_folder + ".apk", 'r')
						zip_ref.extractall(n_folder)
						zip_ref.close()
					#time.sleep(3)

					if (not os.path.exists(n_folder)):
						continue
					done = False

					while not done and next_index < apk_count - 1:
						try:	
							if not os.path.exists(n_folder_next):
								zip_ref = zipfile.ZipFile(n_folder_next + ".apk", 'r')
								zip_ref.extractall(n_folder_next )
								zip_ref.close()
							
							#time.sleep(3)

							done = True
						except Exception as e:
							next_index += 1
							apk_next = apks[next_index]
							n_folder_next = app_path + "/" + apk_next.replace(".apk","")
							print("skipping")
							print(e)
							continue

					if (not os.path.exists(n_folder_next)):
								continue

				except Exception as e:
					print(e)
					continue
				

				temp = {
					"drawable" :   { "removeOrAdded" : 0, "Modified": 0 },
					"animation" :  { "removeOrAdded" : 0, "Modified": 0 },
					"color" :      { "removeOrAdded" : 0, "Modified": 0 },
					"layout" :     { "removeOrAdded" : 0, "Modified": 0 },
					"menu" :       { "removeOrAdded" : 0, "Modified": 0 },
					"string" :     { "removeOrAdded" : 0, "Modified": 0 },
					"style" :      { "removeOrAdded" : 0, "Modified": 0 },
					"font" : 	   { "removeOrAdded" : 0, "Modified": 0 },
					"dimensions" : { "removeOrAdded" : 0, "Modified": 0 },
					"others" : 	   { "removeOrAdded" : 0, "Modified": 0 },
				}

				old_new = compare_versions_ver_2(n_folder, n_folder_next, temp)
				temp = {
					"drawable" :   { "removeOrAdded" : 0, "Modified": 0 },
					"animation" :  { "removeOrAdded" : 0, "Modified": 0 },
					"color" :      { "removeOrAdded" : 0, "Modified": 0 },
					"layout" :     { "removeOrAdded" : 0, "Modified": 0 },
					"menu" :       { "removeOrAdded" : 0, "Modified": 0 },
					"string" :     { "removeOrAdded" : 0, "Modified": 0 },
					"style" :      { "removeOrAdded" : 0, "Modified": 0 },
					"font" : 	   { "removeOrAdded" : 0, "Modified": 0 },
					"dimensions" : { "removeOrAdded" : 0, "Modified": 0 },
					"others" : 	   { "removeOrAdded" : 0, "Modified": 0 },
				}
				new_old = compare_versions_ver_2(n_folder_next, n_folder,  temp)

				#print("Result")
				print("Old to New => " + str(old_new))
				print("New to Old => " + str(new_old))

				#drawable
				count["drawable"]["Removed"].append(old_new["drawable"]["removeOrAdded"])
				count["drawable"]["Added"].append(new_old["drawable"]["removeOrAdded"])
				count["drawable"]["Modified"].append(old_new["drawable"]["Modified"])


				#"animation" 
				count["animation"]["Removed"].append(old_new["animation"]["removeOrAdded"])
				count["animation"]["Added"].append(new_old["animation"]["removeOrAdded"])
				count["animation"]["Modified"].append(old_new["animation"]["Modified"])

				#"color" :
				count["color"]["Removed"].append(old_new["color"]["removeOrAdded"])
				count["color"]["Added"].append(new_old["color"]["removeOrAdded"])
				count["color"]["Modified"].append(old_new["color"]["Modified"])

				#"layout" 
				count["layout"]["Removed"].append(old_new["layout"]["removeOrAdded"])
				count["layout"]["Added"].append(new_old["layout"]["removeOrAdded"])
				count["layout"]["Modified"].append(old_new["layout"]["Modified"])
				
				#"menu" 
				count["menu"]["Removed"].append(old_new["menu"]["removeOrAdded"])
				count["menu"]["Added"].append(new_old["menu"]["removeOrAdded"])
				count["menu"]["Modified"].append(old_new["menu"]["Modified"])

				#"string"
				count["string"]["Removed"].append(old_new["string"]["removeOrAdded"])
				count["string"]["Added"].append(new_old["string"]["removeOrAdded"])
				count["string"]["Modified"].append(old_new["string"]["Modified"])

				#"style"
				count["style"]["Removed"].append(old_new["style"]["removeOrAdded"])
				count["style"]["Added"].append(new_old["style"]["removeOrAdded"])
				count["style"]["Modified"].append(old_new["style"]["Modified"])


				#"font" 
				count["font"]["Removed"].append(old_new["font"]["removeOrAdded"])
				count["font"]["Added"].append(new_old["font"]["removeOrAdded"])
				count["font"]["Modified"].append(old_new["font"]["Modified"])

				#"dimensions"
				count["dimensions"]["Removed"].append(old_new["dimensions"]["removeOrAdded"])
				count["dimensions"]["Added"].append(new_old["dimensions"]["removeOrAdded"])
				count["dimensions"]["Modified"].append(old_new["dimensions"]["Modified"])

				#"others"
				count["others"]["Removed"].append(old_new["others"]["removeOrAdded"])
				count["others"]["Added"].append(new_old["others"]["removeOrAdded"])
				count["others"]["Modified"].append(old_new["others"]["Modified"])

				#lib_count = sum([len(files) for r, d, files in os.walk(n_folder+"/lib")])
				#r_count = sum([len(files) for r, d, files in os.walk(n_folder+"/r")])
				#r_count += sum([len(files) for r, d, files in os.walk(n_folder+"/res")])

				toRemove.append(n_folder)
				toRemove.append(n_folder_next)
				# print("Removing " + n_folder)
				# shutil.rmtree(n_folder)
				# print("Removing " + n_folder_next)
				# shutil.rmtree(n_folder_next)
				j += 1

			#time.sleep(2)	
			
			processed.append(app)

			save_obj(processed, "res_processed_ver_2")
			save_obj(count, "resources_count_ver_2")
			if i == 30:
				break
			# print("Removing")
			# for r in toRemove:
			# 	if os.path.exists(r):
			# 		print(r)
			# 		shutil.rmtree(r)

			toRemove = []


	#print(count)
	
	save_obj(count, "resources_count_ver_2")


def unzip_apks(category):
	
	i = 0
	
	category_path = "./" + category
	cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]

	force_stop = False
		#print(sorted(cat_apps)) 
	cat_apps = sorted(cat_apps)
	for app in cat_apps:
		app_path = os.path.join(category_path,app)
		print("App("+str(i)+") => " + app)
		apks = sorted([dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith(".apk")])
		
		
		i += 1
		j = 1

		apks = sorted(apks)

		total_app = []

		apk_count = len(apks)

		for index in range(apk_count - 1):

			apk = apks[index]
			
			n_folder = app_path + "/" +  apk.replace(".apk","") 
			
			
			try:
				if not os.path.exists(n_folder):
					zip_ref = zipfile.ZipFile(n_folder + ".apk", 'r')
					zip_ref.extractall(n_folder)
					zip_ref.close()
			

			except Exception as e:
				print(e)
				continue
			

		if i == 30:
			break


	


def combine_resources_count():
	print("Count Resources")
	path = './Summary/Resources Count'
	workbook = xlsxwriter.Workbook(os.path.join(path,'combined_resources.xlsx'))
	
	worksheet = workbook.add_worksheet("Resources Summary")
	worksheet.write(0, 0, 'Type')
	worksheet.write(0, 1, 'Added')
	worksheet.write(0, 2, 'Removed')
	worksheet.write(0, 3, 'Modified')


	pkls = sorted([dI for dI in os.listdir(path) if os.path.isfile(os.path.join(path,dI)) and os.path.join(path,dI).endswith(".pkl")])

	#print(pkls)
	count = {"Removed" : [], "Added" : [], "Modified": []}

	for pkl in pkls:
		c = load_obj(os.path.join(path,pkl))
		#print(c)
		#print(pkl)

		for r in c["Removed"]:
			count["Removed"].append(r)

		for r in c["Added"]:
			count["Added"].append(r)

		for r in c["Modified"]:
			count["Modified"].append(r)


	worksheet.write(1, 0, 'Total')
	worksheet.write(1, 1, sum(count["Added"]))
	worksheet.write(1, 2, sum(count['Removed']))
	worksheet.write(1, 3, sum(count['Modified']))

	worksheet.write(2, 0, 'Average')
	worksheet.write(2, 1,  round(sum(count["Added"]) / max(len(count["Added"]),1),2))
	worksheet.write(2, 2,  round(sum(count["Removed"]) / max(len(count["Removed"]),1),2))
	worksheet.write(2, 3,  round(sum(count["Modified"]) / max(len(count["Modified"]),1),2))

	worksheet.write(3, 0, 'Median')
	worksheet.write(3, 1, statistics.median(count["Added"]))
	worksheet.write(3, 2, statistics.median(count["Removed"]))
	worksheet.write(3, 3, statistics.median(count["Modified"]))

	worksheet.write(4, 0, 'Min')
	worksheet.write(4, 1, min(count["Added"]))
	worksheet.write(4, 2, min(count["Removed"]))
	worksheet.write(4, 3, min(count["Modified"]))

	worksheet.write(5, 0, 'Max')
	worksheet.write(5, 1, max(count["Added"]))
	worksheet.write(5, 2, max(count["Removed"]))
	worksheet.write(5, 3, max(count["Modified"]))

	workbook.close()	

def combine_pkl(res_type, c, count):	
	for r in c[res_type]["Removed"]:
		count[res_type]["Removed"].append(r)

	for r in c["Added"]:
		count[res_type]["Added"].append(r)

	for r in c[res_type]["Modified"]:
		count["Modified"].append(r)

def add_res_type(column, row, key, count, worksheet):
	
	worksheet.write(column, row, key)
	row += 1
	
	worksheet.write(column, row, 'Type')
	worksheet.write(column, row + 1, 'Added')
	worksheet.write(column, row + 2, 'Removed')
	worksheet.write(column, row + 3, 'Modified')
	
	column += 1
	worksheet.write(column, row + 0, 'Total')
	worksheet.write(column, row + 1, sum(count[key]["Added"]))
	worksheet.write(column, row + 2, sum(count[key]['Removed']))
	worksheet.write(column, row + 3, sum(count[key]['Modified']))

	column += 1
	worksheet.write(column, row + 0, 'Average')
	worksheet.write(column, row + 1,  round(sum(count[key]["Added"]) / max(len(count[key]["Added"]),1),2))
	worksheet.write(column, row + 2,  round(sum(count[key]["Removed"]) / max(len(count[key]["Removed"]),1),2))
	worksheet.write(column, row + 3,  round(sum(count[key]["Modified"]) / max(len(count[key]["Modified"]),1),2))

	column += 1
	worksheet.write(column, row +  0, 'Median')
	worksheet.write(column, row + 1, statistics.median(count[key]["Added"]))
	worksheet.write(column, row + 2, statistics.median(count[key]["Removed"]))
	worksheet.write(column, row + 3, statistics.median(count[key]["Modified"]))

	column += 1
	worksheet.write(column, row + 0, 'Min')
	worksheet.write(column, row + 1, min(count[key]["Added"]))
	worksheet.write(column, row + 2, min(count[key]["Removed"]))
	worksheet.write(column, row + 3, min(count[key]["Modified"]))

	worksheet.write(column, row + 0, 'Max')
	worksheet.write(column, row + 1, max(count[key]["Added"]))
	worksheet.write(column, row + 2, max(count[key]["Removed"]))
	worksheet.write(column, row + 3, max(count[key]["Modified"]))


def combine_resources_count_ver_2():
	print("Count Resources")
	path = './Summary/Resources Count 2'
	workbook = xlsxwriter.Workbook(os.path.join(path,'combined_resources_ver_2.xlsx'))
	
	worksheet = workbook.add_worksheet("Resources Summary")
	


	pkls = sorted([dI for dI in os.listdir(path) if os.path.isfile(os.path.join(path,dI)) and os.path.join(path,dI).endswith(".pkl")])

	#print(pkls)
	count = {"Removed" : [], "Added" : [], "Modified": []}

	column = 0
	row = 0
	for pkl in pkls:
		c = load_obj(os.path.join(path,pkl))
		#print(c)
		#print(pkl)
		# "drawable" :   { "removeOrAdded" : [], "Modified": [] },
		# "animation" :  { "removeOrAdded" : [], "Modified": [] },
		# "color" :      { "removeOrAdded" : [], "Modified": [] },
		# "layout" :     { "removeOrAdded" : [], "Modified": [] },
		# "menu" :       { "removeOrAdded" : [], "Modified": [] },
		# "string" :     { "removeOrAdded" : [], "Modified": [] },
		# "style" :      { "removeOrAdded" : [], "Modified": [] },
		# "font" : 	   { "removeOrAdded" : [], "Modified": [] },
		# "dimensions" : { "removeOrAdded" : [], "Modified": [] },
		# "other" : 	   { "removeOrAdded" : [], "Modified": [] },
		combine_pkl("drawable", c, count)
		combine_pkl("animation", c, count)
		combine_pkl("color", c, count)
		combine_pkl("layout", c, count)
		combine_pkl("menu", c, count)
		combine_pkl("string", c, count)
		combine_pkl("style", c, count)
		combine_pkl("font", c, count)
		combine_pkl("dimensions", c, count)
		combine_pkl("other", c, count)

		

	add_res_type(column, row, "drawable", count, worksheet)
	row+=5
	add_res_type(column, "animation", count, worksheet)
	row+=5
	add_res_type(column, "color", count, worksheet)
	row+=5
	add_res_type(column, "layout", count, worksheet)
	row+=5
	add_res_type(column, "menu", count, worksheet)
	row+=5
	add_res_type(column, "string", count, worksheet)
	row+=5
	add_res_type(column, "style", count, worksheet)
	row+=5
	add_res_type(column, "font", count, worksheet)
	row+=5
	add_res_type(column, "dimensions", count, worksheet)
	row+=5
	add_res_type(column, "other", count, worksheet)
	row+=5
	# worksheet.write(1, 0, 'Total')
	# worksheet.write(1, 1, sum(count["Added"]))
	# worksheet.write(1, 2, sum(count['Removed']))
	# worksheet.write(1, 3, sum(count['Modified']))

	# worksheet.write(2, 0, 'Average')
	# worksheet.write(2, 1,  round(sum(count["Added"]) / max(len(count["Added"]),1),2))
	# worksheet.write(2, 2,  round(sum(count["Removed"]) / max(len(count["Removed"]),1),2))
	# worksheet.write(2, 3,  round(sum(count["Modified"]) / max(len(count["Modified"]),1),2))

	# worksheet.write(3, 0, 'Median')
	# worksheet.write(3, 1, statistics.median(count["Added"]))
	# worksheet.write(3, 2, statistics.median(count["Removed"]))
	# worksheet.write(3, 3, statistics.median(count["Modified"]))

	# worksheet.write(4, 0, 'Min')
	# worksheet.write(4, 1, min(count["Added"]))
	# worksheet.write(4, 2, min(count["Removed"]))
	# worksheet.write(4, 3, min(count["Modified"]))

	# worksheet.write(5, 0, 'Max')
	# worksheet.write(5, 1, max(count["Added"]))
	# worksheet.write(5, 2, max(count["Removed"]))
	# worksheet.write(5, 3, max(count["Modified"]))

	workbook.close()	

if __name__ == '__main__':

	pattern = re.compile('[\W_]+')

	parser = argparse.ArgumentParser(description='Process csv.')
	parser.add_argument('category', type=str,
                    help='Category to search')
	parser.add_argument('--count', '-c', type=int,
                    help='Minimum number of apks to be a valid app')

	count_ = 0
	args = parser.parse_args()
	category = args.category

	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	category_path = fileDir +"/" + category 

	cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]

	if args.count:
		count_ = args.count

	total = []
		

	if count_ == 1:
		count_resources_ver_2();
	elif count_ == 2:
		combine_resources_count_ver_2()
	elif count_ == 3:
		# cat = ['BUSINESS', 'FINANCE', 'EDUCATION', 'TOOLS', 'COMMUNICATION']
		# for c in cat:
		unzip_apks(category)
	else:
		content_csv = []


		workbook = xlsxwriter.Workbook(category + '.xlsx')
		#print(category_path + "Category_Summary.csv")
		get_woorkbook(workbook, category_path + "/Category_Summary.csv", category + " Summary")

		i = 0

		for app in cat_apps:
			app_path = os.path.join(category_path,app)
			name = pattern.sub('', app)
			name = name[:25] + "_" + str(i)
			i += 1
			#print(name)
			#worksheet = workbook.add_worksheet(name)
			csvs = [dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith("_Summary.csv")]

			csv_f = csvs[0]
			csv_path = os.path.join(app_path,csv_f)
			get_woorkbook(workbook, csv_path, name)
			
		
		workbook.close()	




	

			                
