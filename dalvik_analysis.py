import csv
import os
import pickle
from bs4 import BeautifulSoup
import requests
import brotli 
import argparse
import sys


dalvik_opcodes = []
dalvik_opcodes_an = []
dalvik_apps = []
working_dir = ""

csv.field_size_limit(sys.maxsize)



class dalvik_opcode:

	def __init__(self, op_code, op_name, explanation, example):	
		self.op_code = op_code
		self.op_name = op_name
		self.explanation = explanation
		self.example = example
		self.added = 0
		self.removed = 0


def get_dalvik_table():
	global dalvik_opcodes

	url = 'http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html'

	headers = {
	    'cache-control': "no-cache",
	    'postman-token': "1fe87c7d-b0a4-e420-decb-46d857929fc4"
	    }

	response = requests.request("GET", url, headers=headers)

	soup = BeautifulSoup(response.content, "html.parser")

	table = soup.find('table')

	tbody = table.find('tbody')
	rows = tbody.find_all('tr')

	i = 0 
	for row in rows:
		if i > 0:
			cells = row.find_all("td")
			op_code = cells[0].get_text()
			name = cells[1].get_text()
			explanation = cells[2].get_text()
			example = cells[3].get_text()

			dalvik = dalvik_opcode(op_code, name, explanation, example)
			dalvik_opcodes.append(dalvik)

		i = 1

	save_obj(dalvik_opcodes,'dalvik_opcodes')


def save_obj(obj, name ):
    with open('./'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('./' + name, 'rb') as f:
        return pickle.load(f)


def index_of(op):
	global dalvik_opcodes_an

	for i in range(len(dalvik_opcodes_an)):
	#	print("if " + op + " in " + dalvik_opcodes[i].op_name)
		if (op in dalvik_opcodes_an[i].op_name):
			return i

	return -1


def analyze_dalvik():

	categories = sorted([dI for dI in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir,dI))])	

	for cat in categories:

		print("Category : " + cat)

		path = os.path.join(working_dir, cat)

		cat_apps = sorted([dI for dI in os.listdir(path) if os.path.isdir(os.path.join(path,dI))])	

		for app in cat_apps:
			app_path = os.path.join(path,app)

			if cat + '_' + app in dalvik_apps:
				continue;

			summary_path = app_path + "/" + app + "_Summary.csv"
			if os.path.exists(summary_path):
				with open(summary_path) as csv_file:
					print(app + " summary csv Found")
					csv_reader = csv.reader(csv_file, delimiter = ",")
					line_count = 0

					t = 0
					added_index = 0 
					removed_index =0
					for row in csv_reader:
						if len(row) == 0:
							continue
						if t== 0:
							index = 0
							for column in row:
								if column == "addedLines" :
									added_index = index
								if column == 'removedLines':
									removed_index = index

								index += 1
						else:
							#print(added_index	)
							#print(row[added_index])
							if(len(row) > added_index):
								addedlines = row[added_index].split('|')
								for a in addedlines:
									#print("checking " + a)
									#print(a.op_name)
									ind = index_of(a)
									if(ind > -1):
										dalvik_opcodes_an[ind].added += 1

							if(len(row) > added_index):
								removedlines = row[removed_index].split('|')
								for r in removedlines:
									ind = index_of(r)
									if(ind > -1):
										dalvik_opcodes_an[ind].removed += 1
					

						t = 1
			save_obj(dalvik_opcodes_an, 'dalvik_opcodes_an')
			dalvik_apps.append(cat + '_' + app)
			save_obj(dalvik_apps, 'dalvik_apps')



if __name__ == '__main__':

	global	dalvik_opcodes
	global working_dir
	global dalvik_opcodes_an

	parser = argparse.ArgumentParser(description='Process some integers.')
	#parser.add_argument('category', type=str,
     #               help='Category to search')


	parser.add_argument('--analize-dalvik-table', '-a', type=int,
                    help='Analize Dalvik')

	parser.add_argument('--generate-dalvik-table', '-d', type=int,
                    help='Generate Dalvik Table')


	parser.add_argument('--print-dalvik-table', '-p', type=int,
                    help='Print Dalvik Table')

	parser.add_argument('--print-dalvik-table-an', '-pan', type=int,
                    help='Print Dalvik Table')


	working_dir = '.'

	args = parser.parse_args()
	
	if(args.analize_dalvik_table):
		if os.path.exists('./dalvik_opcodes.pkl'):
			dalvik_opcodes = load_obj('dalvik_opcodes.pkl')
		
		if(dalvik_opcodes):
			if(len(dalvik_opcodes) == 0):
				get_dalvik_table()
		else:
			get_dalvik_table()

		#print(dalvik_opcodes)
		dalvik_opcodes_an = []
		if os.path.exists('./dalvik_opcodes_an.pkl'):
			dalvik_opcodes_an = load_obj('dalvik_opcodes_an.pkl')
		else:	
			for d in dalvik_opcodes:
			#	print(d.op_code)
			#	print(d.op_name)
				dalvik_opcodes_an.append(dalvik_opcode(d.op_code, d.op_name, d.explanation, d.example))

		
		if os.path.exists('dalvik_apps.pkl'):
			dalvik_apps = load_obj("dalvik_apps.pkl")


		analyze_dalvik()

	elif(args.generate_dalvik_table):
		get_dalvik_table()
	elif(args.print_dalvik_table):
		dalvik_opcodes = load_obj('dalvik_opcodes.pkl')
		print('dalvik_codes')
		for d in dalvik_opcodes:
			print(d.op_code + '-> ' + d.op_name)
	elif(args.print_dalvik_table_an):
		dalvik_opcodes_an = load_obj('dalvik_opcodes_an.pkl')
		print('dalvik_opcodes_an')
		for d in dalvik_opcodes_an:
			print(d.op_code + '-> ' + d.op_name +', added: '+str(d.added)+', removed: ' + str(d.removed))



