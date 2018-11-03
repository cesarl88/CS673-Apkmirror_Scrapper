import os
import argparse
import csv		
import xlsxwriter.workbook 
import re

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

	args = parser.parse_args()
	category = args.category

	fileDir = os.path.dirname(os.path.abspath(__file__)) 
	category_path = fileDir +"/" + category 

	cat_apps = [dI for dI in os.listdir(category_path) if os.path.isdir(os.path.join(category_path,dI))]	

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
