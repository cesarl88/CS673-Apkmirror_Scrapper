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

	cat_folders = [dI for dI in os.listdir("./") if os.path.isdir(os.path.join("./",dI))]

	print(cat_folders)
	#sys.exit(0)
	for cat in cat_folders:

		category_path = fileDir + "/" + cat
		print("Category => " + cat)

		cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]

		#print(sorted(cat_apps))
		cat_apps = sorted(cat_apps)
		toRemove = []
		for app in cat_apps:
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

					if not os.path.exists(n_folder)
						zip_ref = zipfile.ZipFile(n_folder + ".apk", 'r')
						zip_ref.extractall(n_folder)
						zip_ref.close()
					#time.sleep(3)

					if (not os.path.exists(n_folder)):
						continue
					done = False

					while not done and next_index < apk_count - 1:
						try:	
							if not os.path.exists(n_folder_next)
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

			# print("Removing")
			# for r in toRemove:
			# 	if os.path.exists(r):
			# 		print(r)
			# 		shutil.rmtree(r)

			toRemove = []


	#print(count)
	
	save_obj(count, "resources_count")


def unzip_apks(category):
	
	
	category_path = "./" + category
	cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]

		#print(sorted(cat_apps))
	cat_apps = sorted(cat_apps)
	for app in cat_apps:
		app_path = os.path.join(category_path,app)
		print("App => " + app)
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
				zip_ref = zipfile.ZipFile(n_folder + ".apk", 'r')
				zip_ref.extractall(n_folder)
				zip_ref.close()
			

			except Exception as e:
				print(e)
				continue
			



	


def combine_resources_count():
	print("Count Resources")
	workbook = xlsxwriter.Workbook('combined_resources.xlsx')
	
	worksheet = workbook.add_worksheet("Resources Summary")
	worksheet.write(0, 0, 'Type')
	worksheet.write(0, 1, 'Added')
	worksheet.write(0, 2, 'Removed')
	worksheet.write(0, 3, 'Modified')


	pkls = sorted([dI for dI in os.listdir("./") if os.path.isfile(os.path.join("./",dI)) and os.path.join("./",dI).endswith(".pkl")])

	#print(pkls)
	count = {"Removed" : [], "Added" : [], "Modified": []}

	for pkl in pkls:
		c = load_obj(pkl)

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
		count_resources();
	elif count_ == 2:
		combine_resources_count()
	elif count_ == 3:
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




	

			                
