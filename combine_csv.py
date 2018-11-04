import os
import argparse
import csv		
import xlsxwriter.workbook 
import re
import zipfile
import shutil
import time

def get_woorkbook(workbook, csv_path, name):
	worksheet = workbook.add_worksheet(name)

	with open(csv_path) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter = ",")
		line_count = 0
		for r, row in enumerate(csv_reader):
			for c, col in enumerate(row):
				worksheet.write(r, c, col)

if __name__ == '__main__':

	pattern = re.compile('[\W_]+')

	parser = argparse.ArgumentParser(description='Process csv.')
	parser.add_argument('category', type=str,
                    help='Category to search')
	parser.add_argument('--count', '-c', type=int,
                    help='Minimum number of apks to be a valid app')

	count = 0
	args = parser.parse_args()
	category = args.category

	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	category_path = fileDir +"/" + category 

	cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]

	if args.count:
		count = args.count
		

	if count > 0:
		workbook = xlsxwriter.Workbook(category + '_lib_resources_count.xlsx')

		i = 0
		for app in cat_apps:
			app_path = os.path.join(category_path,app)
			apks = [dI for dI in os.listdir(app_path) if os.path.isfile(os.path.join(app_path,dI)) and os.path.join(app_path,dI).endswith(".apk")]

			name = pattern.sub('', app)
			name = name[:25] + "_" + str(i)	
			worksheet = workbook.add_worksheet(name)
			i += 1
			j = 1


			worksheet.write(0, 0, 'APK')
			worksheet.write(0, 1, 'Libraries')
			worksheet.write(0, 2, 'Diff Libraries')
			worksheet.write(0, 3, 'Resources')
			worksheet.write(0, 4, 'Diff Resources')

			prev_lib = -999
			prev_res = -999
			apks = sorted(apks)
			for apk in apks:

				worksheet.write(j, 0, apk)
				n_folder = app_path + "/" +  apk.replace(".apk","")

				print(app_path + "/" + apk)
				try:
					zip_ref = zipfile.ZipFile(app_path + "/" + apk, 'r')
					zip_ref.extractall(n_folder)
					zip_ref.close()
				except Exception as e:
					continue
				

				lib_count = sum([len(files) for r, d, files in os.walk(n_folder+"/lib")])
				r_count = sum([len(files) for r, d, files in os.walk(n_folder+"/r")])
				r_count += sum([len(files) for r, d, files in os.walk(n_folder+"/res")])

				if(prev_res != -999):
					worksheet.write(j, 2, str(lib_count - prev_lib))
					worksheet.write(j, 4, str(r_count - prev_res))


				worksheet.write(j, 1, str(lib_count))
				worksheet.write(j, 3, str(r_count))

				prev_res = r_count
				prev_lib = lib_count

				print("Removing " + n_folder)
				shutil.rmtree(n_folder)
				j += 1

				
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




	

			                
