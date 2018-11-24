
import subprocess
from smalanalysis.smali import SmaliObject, ChangesTypes, SmaliProject, Metrics
from smalanalysis.tools.commands import queryAaptForPackageName
import os
import re
import argparse
import csv		
import xlsxwriter.workbook 


minSDK = { }
targetSDK = {}
Categories = []
regenerate_res = True

pkl_categories = "categories_list"
pkl_dalvik_opcodes = "dalvik_opcodes.pkl"
pkl_dalvik_opcodes_an = "dalvik_opcodes_an.pkl"

ext = ".pkl"
exclude_lists = ['./exclusionlist/exclusionlist.txt', './exclusionlist/Merge.txt']

pa_platform = re.compile('v[1-9]+')
pa_width = re.compile('w[0-9]+dp')
pa_height = re.compile('h[0-9]+dp')
pa_swidth = re.compile('sw[0-9]+dp')

###
###  Class definitions
###

class dalvik_opcode:

	def __init__(self, op_code, op_name, explanation, example):	
		self.op_code = op_code
		self.op_name = op_name
		self.explanation = explanation
		self.example = example
		self.added = 0
		self.removed = 0


class Category:

	def __init__(self, name):
		self.name = name
		self.applications = []
		self.metrics = {}

		self.min_min_sdk = 0
		self.max_min_sdk = 0
		
		self.min_target_sdk = 0
		self.max_target_sdk = 0
		
		self.min_release_date = '1999-01-01'
		self.max_release_date = '1999-01-01'
		
		self.min_apk_size = 0
		self.max_apk_size = 0
		self.avg_apk_size = 0
		self.median_apk_size = 0
		
		self.min_lib_size = 0
		self.max_lib_size = 0
		self.avg_lib_size = 0
		self.median_lib_size = 0
		
		self.min_res_size = 0
		self.max_res_size = 0
		self.avg_res_size = 0
		self.median_res_size = 0
		
		self.min_dex_size = 0
		self.max_dex_size = 0
		self.avg_dex_size = 0
		self.median_dex_size = 0

		self.min_sdk = {}
		self.target_sdk = {}
		for i in range(28):
			min_sdk[str(i)] = 0
			target_sdk[str(i)] = 0




	def run_dissasemble(self):

		for app in applications:
			for v in app.versions:
				v.get_smali();

	def run_differencer(self):

		for app in applications:
			app.analize_differences()


	def compare_resources(self):

		for app in applications:
			if app.res_checked:
				continue

			app.process_resources()

	def analize_dalvik(self):
		for app in applications:
			app.analize_dalvik()

	def find_application(self, app_name):

		for app in self.applications:
			if(app.name == app_name):
				return app

		return None			


class AppVersion:

	def __init__(self, application, version, url, date, size, android):	
		self.application = application
		self.version = version
		self.url = url
		self.date = date
		self.is_downloaded = False
		self.size = size
		self.download_link = ""
		self.android = android
		
		self.apk_size_diff = 0
		self.resources_size_diff = 0
		self.lib_size_diff = 0
		self.dex_size_diff = 0
		
		self.apk_size = 0
		self.resources_size = 0
		self.lib_size = 0
		self.dex_size = 0
		
		self.min_sdk = 0
		self.target_sdk = 0
		
		self.is_checked = False
		self.isObfuscated = False
		self.compare_against = None
		
		self.metrics = {}

		self.res_layout_addition = 0
		self.res_layout_changes = 0
		self.res_orientation_support = 0
		self.res_direction_support = 0
		self.res_size_support = 0
		self.res_dpi_support = 0
		self.res_platform_support = 0

		self.res_layout_removal= 0
		self.res_rem_orientation_support = 0
		self.res_rem_direction_support = 0
		self.res_rem_size_support = 0
		self.res_rem_dpi_support = 0
		self.res_rem_platform_support = 0

		
	def get_apk_path(self):
		return os.path.join(self.application.get_path(), _removeNonAscii(self.version).replace(".", "_").replace(" ","_") + ".apk")

	def get_smali_path(self):
		return os.path.join(self.application.get_path(), _removeNonAscii(self.version).replace(".", "_").replace(" ","_") + ".smali")

	def get_apk_dir(self):
		return os.path.join(self.application.get_path(), _removeNonAscii(self.version).replace(".", "_").replace(" ","_"))

	def get_date(self):
		return datetime.strptime(self.date, "%Y-%m-%d")

	def reprJSON(self):
		return self.__dict__

	def is_decompiled(self):
		return os.path.exists(self.get_smali_path())

	def get_lib_dir(self):
		return self.get_apk_dir() + '/lib'
	
	def get_res_dir(self):
		res_path = self.get_apk_dir() + '/res'
		r_path = self.get_apk_dir() + '/r'
		
		if(os.path.exists(res_path)):
			return res_path;
		if(os.path.exists(r_path)):
			return r_path;

		return ''

	def check_apk_size(self):
		self.apk_size = get_dir_size(self.get_apk_dir())
		lib_path = self.get_lib_dir()
		res_path = self.get_res_dir()

		if(os.path.exists(lib_path)):
			self.lib_size = get_dir_size(lib_path)
		if(os.path.exists(res_path)):

		self.dex_size = get_dir_size(self.get_apk_dir(), '.dex')

	def get_SDK_info(self):
		
		manifest_path = os.path.join(self.get_apk_dir(), 'AndroidManifest.xml'

		manifest_soup = BeautifulSoup(response.content, "xml")

		sdk_tag = soup.find_all('uses-sdk')

		min_sdk = sdk_tag['android:minSdkVersion']
		target_sdk = sdk_tag['android:targetSdkVersion']
		
		self.application.category.min_sdk[min_sdk] += 1
		self.application.category.target_sdk[target_sdk] += 1

		self.min_sdk = int(min_sdk)
		self.target_sdk = int(target_sdk)

	def get_smali(self):

		apk_path = get_apk_path()
		smali_path = get_smali_path()

		if not os.path.exists(smali_path) and os.path.exists(apk_path):
			Command = "sa-disassemble '" + apk_path +"'"
			try:
				p = subprocess.Popen(Command, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
				(output, err) = p.communicate()
				p_status = p.wait()
			except KeyboardInterrupt:
				print("Exiting")
				sys.exit(0)
			except Exception as e:
				FailList += version0 + '\n'

	def extract_resources(self):
		#global regenerate_res
		
		res_path = self.get_apk_dir()
		if(not os.path.exists(res_path)):
			path = self.get_apk_path()
			print("Checking " + path)
			return run_apktool(path)
  		else: 
			# if(regenerate_res):
			# 	os.path.rmdir(res_path)
			# 	return run_apktool(path)
			return True

	def remove_apk_folder(self)
		res_path = self.get_apk_dir()
			if os.path.exists(res_path):
				print("Removing (" + res_path + ")" )
				#os.path.rmdir(res_path)


	def compare_res_content(self, prev_version):
		res0_dir = prev_version.get_res_dir();
 		res1_dir = self.get_res_dir();

		v0_resoures_folders = [dI for dI in os.listdir(res0_dir) if os.path.isdir(os.path.join(res0_dir,dI)) and os.path.join(res0_dir,dI).startswith('layout')]
		v1_resoures_folders = [dI for dI in os.listdir(res1_dir) if os.path.isdir(os.path.join(res1_dir,dI)) and os.path.join(res1_dir,dI).startswith('layout')]

		#comparing changes and deletions from previous to new

		for l0 in v0_resoures_folders:
			l0_dir  = os.path.join(res0_dir, l0)
			l1_dir  = os.path.join(res1_dir, l0)

			files  = [f for f in os.listdir(l0_dir) if os.path.isfile(os.path.join(l0_dir, f))]

			if(not os.path.exists(l1_dir)):
				self.res_layout_removal = len(files)
				qualifiers = l0.split('-')
				if len(qualifiers > 0):

					for qual in qualifiers:
						if(qual == 'ldrtl' or qual == 'ldltr'):
							self.res_rem_direction_support += 1
						elif(qual == 'small' or qual == 'normal' or qual == 'large' or qual == 'xlarge'):
							self.res_rem_size_support += 1
						elif(qual == 'port' or qual == 'land'):
							self.res_rem_size_support += 1
						elif(qual.endswith('dpi')):
							self.res_rem_dpi_support += 1
						elif(pa_swidth.search(qual)):
							self.res_rem_size_support += 1
						elif(pa_width.search(qual)):
							self.res_rem_size_support += 1
						elif(pa_height.search(qual)):
							self.res_rem_size_support += 1
						elif(pa_platform.search(qual)):
							self.res_rem_platform_support += 1
			else:

				for f in files:
					f0_path = os.path.join(l0_dir, f)
					f1_path = os.path.join(l1_dir, f) 
					
					if(os.path.exists(f1_path))
						#run md5
						output0 = ''
						output1 = ''

						cmd = "md5sum '" + f0_path +"'"
						p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
						(output0, err) = p.communicate()


						cmd = "md5sum '" + f1_path +"'"
						p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
						(output1, err) = p.communicate()

						out_0 = output0.split(' ')
						out_1 = output1.split(' ')	
						if(out0[0] != out[1])
							self.res_layout_changes += 1
					else:
						qualifiers = l0.split('-')
						if len(qualifiers > 0):
							for qual in qualifiers:
								if(qual == 'ldrtl' or qual == 'ldltr'):
									self.res_rem_direction_support += 1
								elif(qual == 'small' or qual == 'normal' or qual == 'large' or qual == 'xlarge'):
									self.res_rem_size_support += 1
								elif(qual == 'port' or qual == 'land'):
									self.res_rem_size_support += 1
								elif(qual.endswith('dpi')):
									self.res_rem_dpi_support += 1
								elif(pa_swidth.search(qual)):
									self.res_rem_size_support += 1
								elif(pa_width.search(qual)):
									self.res_rem_size_support += 1
								elif(pa_height.search(qual)):
									self.res_rem_size_support += 1
								elif(pa_platform.search(qual)):
									self.res_rem_platform_support += 1

		#comparing additions from  new to previous
		for l1 in v1_resoures_folders:
			l0_dir  = os.path.join(res0_dir, l0)
			l1_dir  = os.path.join(res1_dir, l0)

			files  = [f for f in os.listdir(l1_dir) if os.path.isfile(os.path.join(l1_dir, f))]

			if(not os.path.exists(l0_dir)):
				self.res_layout_addition = len(files)
				qualifiers = l1.split('-')
				if len(qualifiers > 0):

					for qual in qualifiers:
						if(qual == 'ldrtl' or qual == 'ldltr'):
							self.res_direction_support += 1
						elif(qual == 'small' or qual == 'normal' or qual == 'large' or qual == 'xlarge'):
							self.res_size_support += 1
						elif(qual == 'port' or qual == 'land'):
							self.res_size_support += 1
						elif(qual.endswith('dpi')):
							self.res_dpi_support += 1
						elif(pa_swidth.search(qual)):
							self.res_size_support += 1
						elif(pa_width.search(qual)):
							self.res_size_support += 1
						elif(pa_height.search(qual)):
							self.res_size_support += 1
						elif(pa_platform.search(qual)):
							self.res_platform_support += 1
			else:
				for f in files:
					f0_path = os.path.join(l0_dir, f)
					f1_path = os.path.join(l1_dir, f) 
					
					if(not os.path.exists(f0_path))
						self.res_layout_addtiion += 1
						qualifiers = l0.split('-')
						if len(qualifiers > 0):
							for qual in qualifiers:
								if(qual == 'ldrtl' or qual == 'ldltr'):
									self.res_rem_direction_support += 1
								elif(qual == 'small' or qual == 'normal' or qual == 'large' or qual == 'xlarge'):
									self.res_rem_size_support += 1
								elif(qual == 'port' or qual == 'land'):
									self.res_rem_size_support += 1
								elif(qual.endswith('dpi')):
									self.res_rem_dpi_support += 1
								elif(pa_swidth.search(qual)):
									self.res_rem_size_support += 1
								elif(pa_width.search(qual)):
									self.res_rem_size_support += 1
								elif(pa_height.search(qual)):
									self.res_rem_size_support += 1
								elif(pa_platform.search(qual)):
									self.res_rem_platform_support += 1
				




	def compare_apk_content(self, prev_version):
 		
 		self.apk_size_diff = self.apk_size - prev_version.apk_size
 		self.resources_size_diff = self.resources_size - prev_version.resources_size
 		self.lib_size_diff = self.lib_size - prev_version.lib_size
 		self.dex_size_diff = self.dex_size - prev_version.dex_size


		
class Application:

	def __init__(self, category, name, versions_url):
		self.category = category
		self.versions = []
		self.name = name
		self.versions_url = versions_url
		self.is_checked = False
		self.res_checked = False
		self.is_apk_mirror = False

	def get_path(self):
		return "./" + self.category.name "/" + self.name + "/"

	
	def analize_dalvik(self):
		for version in self.versions:
			added = ('|'.join(version.metrics["{}addedLines".format(b)]))
			removed = ('|'.join(version.metrics["{}removedLines".format(b)]))

			addedlines = row[added_index].split('|')
			removedlines = row[removed_index].split('|')
			
			for a in addedlines:
				ind = dalvik_opcodes_an_index_of(a)
				if(ind > -1):
					dalvik_opcodes_an[ind].added += 1

			for r in removedlines:
				ind = dalvik_opcodes_an_index_of(r)
				if(ind > -1):
					dalvik_opcodes_an[ind].removed += 1



	def analize_differences(self):
		for i in range(len(app.versions) - 1):
			nextI = i + 1

			version = app.versions[i]
			next_version = app.versions[nextI]


			if(version.is_checked):
				continue
			if(next_version.is_checked):
				continue
			version0 = version.get_apk_path()
			version1 = next_version.get_apk_path()

			print("Comparing %s against %s" % (version0, version1))


			try:
				print("Parsing old Version")
				old = SmaliProject.SmaliProject()
				old.parseProject(version0, None, exclude_lists, None, True)

				print("Checking old version obfuscated")
				if old.isProjectObfuscated():
					version.is_checked = True
					version.isObfuscated = True
					raise Metrics.ProjectObfuscatedException()

				mold, moldin = Metrics.countMethodsInProject(old)

				Compared = False
				#metrics = {}

				while not Compared and nextI < size - 1:
					try:
						print("Parsing New Version")
						new = SmaliProject.SmaliProject()
						new.parseProject(version1, None, exclude_lists, None, True)
						

						if(next_version.is_checked and next_version.isObfuscated):
							continue
					    #parseProject(new, args.smaliv2, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)

						print("Getting Metrics")
						mnew, mnewin = Metrics.countMethodsInProject(new)
						print("Checking New version obfuscated")
						if new.isProjectObfuscated():
							next_version.is_checked = True
							next_version.isObfuscated = True
							raise Metrics.ProjectObfuscatedException()


						print("Comparing differences")	
						diff = old.differences(new, [])
						#print(diff)
						


						print("Extracting differences")	
						metrics = {}
						Metrics.initMetricsDict("", metrics)
						next_version.metrics = metrics
						next_version.metrics["#M-"] = mold + moldin
						next_version.metrics["#M+"] =  mnew + mnewin
						Metrics.computeMetrics(diff, metrics, "", True, False)

						Compared = True
					except Exception as e:
						nextI += 1
						version1 = app.versions[nextI].get_apk_path()
				

			except Metrics.ProjectObfuscatedException:
				print("This project is obfuscated. Unable to proceed.", file=sys.stderr)
				continue
			except Exception as e:
				print("Error parsing")
				print(e)
				continue
				#sys.exit(0)
			

			save_obj(Categories,pkl_categories)
			
			# if not metrics:
			# 	continue
			# print("Parsing differences")

			# bases = [""]

			# if not set_total_metrics:
			# 	total_metrics = dict.fromkeys(metrics.keys(), 0)
			# 	complete_metrics = dict.fromkeys(metrics.keys(), [])
			# 	set_total_metrics = True
			
			# for b in bases:
			# 	if not headers_printed:
			# 		for k in filter(lambda x: type(metrics[x]) != set and x.startswith(b), metrics.keys()):
			# 			headers += k[len(b):] + ','
					
			# 		headers += "addedLines"  +  ','
			# 		headers += "removedLines"
			# 		headers += '\n'
			# 		headers_printed = True

			# #print(b, end=',')


			# for k in filter(lambda x: type(metrics[x]) != set and x.startswith(b), metrics.keys()):
			# 	csv_file += str(metrics[k]) +  ','
			# 	total_metrics[k] += metrics[k] 
			# 	complete_metrics[k].append(metrics[k])


			# added = ('|'.join(metrics["{}addedLines".format(b)]))
			# removed = ('|'.join(metrics["{}removedLines".format(b)]))

			# added = (added.replace(',',";"))
			# removed = (removed.replace(',',";"))


			# csv_file += added + ','#'|'.join(metrics["{}addedLines".format(b)]).replace(',',";") +  ','
			# csv_file += removed + ','#'|'.join(metrics["{}removedLines".format(b)]).replace(',',";") +  ','	

			# csv_file += '\n'

	def extract_apks(self):
		for v in self.versions:
			if not v.extract_resources():
				continue
			# Check APK size composition
			version.check_apk_size()
			version.get_SDK_info()


	def remove_apk_folder():
		for v in self.versions:
			v.remove_apk_folder();

	def process_resources(self):
		
		if(regenerate_res):
			remove_apk_folder()

		# Perform the extraction separate to avoid double extraction work while moving every two version
		self.extract_apks()

		for i in range(len(app.versions) - 1):
			
			version = app.versions[i]
			if not version.extract_resources():
				continue

			nextI = (i + 1) % len(app.versions)
			while nextI < len(app.versions) - 1:
				next_version = app.versions[nextI]
				if not next_version.extract_resources()
					continue
				next_version.compare_res_content(version)
				#check apk sizes diff 
				next_version.compare_apk_content(version)

				

				





	def number_of_versions(self):
		return len(self.versions)

	def is_completed(self, is_minOrmax):
		downloaded = 0
		fileDir = os.path.dirname(os.path.abspath(__file__))
		fileDir = os.path.join(fileDir, self.category)
		appDir = os.path.join(fileDir, self.name)

		for v in self.versions:
			print("Checking " + appDir + "/" + _removeNonAscii(v.version).replace(".", "_").replace(" ","_") + ".apk")
			if v.is_downloaded and os.path.exists(appDir + "/" + _removeNonAscii(v.version).replace(".", "_").replace(" ","_") + ".apk"):
				downloaded += 1


		#print downloaded
		return (downloaded >= min_apks and is_minOrmax) or downloaded >= max_apks
		#return downloaded >= max_apks

	def get_valid_apks(self):

		m_date = datetime.strptime(max_Date, "%Y-%m-%d")
		valid = []
		date = m_date 
		# print("Stating Date " + str(date))
		# time.sleep(3)
		for v in self.versions:
			date_diff = relativedelta(date, v.get_date())


			# print("date " + str(date))
			# print("v date " + str(v.date))
			# print("Years difference " + str(date_diff.years))
			# print("Years difference " + str(date_diff.years))
			# print("Months difference " + str(date_diff.months))
			# print("Days difference " + str(date_diff.days))

			if(date_diff.days > days):
				if(date_diff.months > months and date_diff.years >= 0):
					valid.append(v)
					date = v.get_date()
					#print("adding")


		print("Number of Valid APKS => " + str(len(valid)))
		return valid

	def is_valid(self):
		
		num = self.number_of_versions()
		#print(num)
		if  num < min_apks:
			#print("num < min_apks")
			return False

		return len(self.get_valid_apks()) >= min_apks 


	def download_apks(self):
		valid_apks = self.get_valid_apks()

		print("Valid Apks: " + str(len(valid_apks)))
		

		fileDir = os.path.dirname(os.path.abspath(__file__))
		fileDir = os.path.join(fileDir, self.category)


		for apk in valid_apks:
			appDir = os.path.join(fileDir, self.name)

			print("Checking " + appDir + "/" + _removeNonAscii(apk.version).replace(".", "_").replace(" ","_") + ".apk")
			
			if(apk.is_downloaded and os.path.exists(appDir + "/" + _removeNonAscii(apk.version).replace(".", "_").replace(" ","_") + ".apk")):
				print(apk.version + " is being ignored becuase it is already downloaded")
				#time.sleep(2)
				continue



			if not os.path.exists(appDir):
				os.mkdir(appDir)
				print("Directory " , appDir ,  " Created ")
			else:
				print("Directory " , appDir ,  " Exists ")

			
			
			apk_file = requests.get(apk.url)
			
			soup = BeautifulSoup(apk_file.content, "html.parser")
			link = soup.find("a", attrs={"id":"download_link"})
			apk.download_link = link.get("href")

			print(apk.version)
			print(self.name)
			print("Downloading " + _removeNonAscii(self.name) + " => " + _removeNonAscii(apk.version).replace(".", "_").replace(" ","_"))
			

			apk_file = requests.get(apk.download_link)
			appDir = os.path.join(appDir, _removeNonAscii(apk.version).replace(".", "_").replace(" ","_"))
			print("saving into "+ appDir + ".apk")

			f = open(appDir + ".apk","w+")
			f.write(apk_file.content);
			f.close()

			apk.is_downloaded = True

			if(self.is_completed(False)):
				print(str(max_apks) + " downloaded")
				break

			print("Waiting " + str(sleep_time) + " seconds")
			time.sleep(sleep_time)

	def analyze_android_version(self):
		
		androidVersions = []


		for i in range(len(self.versions) - 1):
			next_i = (i + 1) % len(self.versions)

			v0 = self.versions[i]
			#v1 = self.versions[next_i] 

			if v0.android not in androidVersions:
				androidVersions.append(v0.android)
			#if v0.android != v1.android:
				

		return androidVersions


###
###  Utilities
###

def dalvik_opcodes_an_index_of(op):
	global dalvik_opcodes_an

	for i in range(len(dalvik_opcodes_an)):
	#	print("if " + op + " in " + dalvik_opcodes[i].op_name)
		if (op in dalvik_opcodes_an[i].op_name):
			return i

	return -1

def find_category(name):

	for cat in Categories:
		if(cat.name == name):
			return cat

	return None

def parse_csv_apk_mirror():

	print("Loading Categories")
	load_categories()

	print("Parsing CSVs from apk mirror")

	root = '.'

	categories = sorted([dI for dI in os.path.listdir(root) if os.path.isdir(os.path.join(root, dI))])


	for cat in categories:
		print("Processing category(" + cat + ")")

		category_obj = find_category(cat)

		cat_path = os.path.join(root, cat)
		apps = sorted([dI for dI in os.path.listdir(root) if os.path.isdir(os.path.join(root, dI))])

		for app in apps:
			print("Processing applicaion(" + cat + ")")
			app_path = os.path.join(cat_path, app)

			csv_description_path = os.path.join(app_path, app + "_Description.csv")

			app_obj = category_obj.find_application(app)
			if(os.path.exists(csv_description_path) and app_obj == None):

				with open(csv_description_path) as csv_file:
					print("Csv Found")
					csv_reader = csv.reader(csv_file, delimiter = ",")
					line_count = 0

					app_obj = Application(category_obj, app, 'http://apkmirror.com')
					app_obj.is_apk_mirror = True
					t = 0
					for row in csv_reader:
						if(t == 0):
							t = 1
							continue;
						version = AppVersion(app_obj, row(0), row(3), row(1), 0, 'Android')		
						app_obj.versions.append(version)

					category_obj.applications.append(app_obj)	
					save_obj(Categories, pkl_categories)				




def _removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def initialize_SDK_dict():
	global minSDK
	global targetSDK

	for i in range(28):
		minSDK[str(i)] = 0
		targetSDK[str(i)] = 0


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


def load_json_folder(folder, name):
	Apps = []

	#print(analyze_technology)
	json_data = folder +"/apps.json"

	if os.path.exists(json_data):
		with open(json_data) as json_data:
			apps = json.load(json_data)
			for app in apps:
				a = Application('','','')
				a.__dict__ = app

				versions = []
				
				for v in app["versions"]:
					ver = AppVersion(v["version"], v["url"], v["date"], v["size"], v["android"])
					ver.is_downloaded = v["is_downloaded"]
					versions.append(ver)
					
				a.versions = versions
				Apps.append(a)

	return Apps


def load_categories():
	
	global Categories

	if(os.path.exists(pkl_categories))
		Categories = load_obj(pkl_categories)

	total = 0
	i = 0
	lst = []

	cat_folders = [dI for dI in os.listdir("./") if os.path.isdir(os.path.join("./",dI))]
	for cat in cat_folders:
		print("Analizing " + cat)

		if( cat in Categories):
			continue

		cat_f = os.path.join("./",cat)

		category = Category(cat)
		
		category.apps = load_json_folder(cat_f, cat)

		Categories.append(category)

		save_obj(Categories, pkl_categories)


def get_dir_size(start_path = '.', ext = '*'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
        	if(ext != '*' or f.endswith(ext))
            	fp = os.path.join(dirpath, f)
            	total_size += os.path.getsize(fp)
    return total_size

def run_apktool(path):

	if not os.path.exists(path):
		return False
	try:
		sys.Command("apktool d " + path)
		return True
	except Exception as e:
		return False
		

def save_obj(obj, name, ext):
    with open('./'+ name + ext, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name, ext):
    with open('./' + name + ext, 'rb') as f:
        return pickle.load(f)



if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Milestone 1 analisys.')

	#Dalvik Analisys
	parser.add_argument('--analize-dalvik-table', '-analize_dalvik', type=int,
                    help='Analize Dalvik')
	parser.add_argument('--generate-dalvik-table', '-get_dalvik_table', type=int,
                    help='Generate Dalvik Table from web')
	parser.add_argument('--print-dalvik-table', '-print_dalvik', type=int,
                    help='Print Dalvik Table')
	parser.add_argument('--print-dalvik-table-an', '-print_a_dalvik', type=int,
                    help='Print Analized Dalvik Table')

	#Categories Loading
	parser.add_argument('--load-categories', '-load_categories', type=int,
                    help='Load Categories from Json apps')
	parser.add_argument('--parse-csv-apk_-mirror', '-parse_csv_apk_mirror', type=int,
                    help='Add apps from apk mirror to apk pure Json format')

	#Differencer
	parser.add_argument('--run-dissasemble', '-run_dissasemble', type=int,
                    help='Get Smali from apks')
	parser.add_argument('--run-differenceer', '-run_differencer', type=int,
                    help='Run differencer')


	#Resources
	parser.add_argument('--compare-resources', '-compare_resources', type=int,
                    help='Compare resources')

	args = parser.parse_args()

	#Categories Loading
	if args.load_categories:
		load_categories()
	elif args.parse_csv_apk_mirror:
		parse_csv_apk_mirror()
	#Differencer
	elif args.run_dissasemble:
		for cat in Categories:
			cat.run_dissasemble()
	elif args.run_differencer:
		for cat in Categories:
			cat.run_differencer()
	#resources
	elif args.compare_resources:
		for cat in Categories:
			cat.compare_resources()
	#Dalvik Analisys
	elif args.get_dalvik_table:
		get_dalvik_table()
	elif(args.analize_dalvik_table):
		if os.path.exists('./' + pkl_dalvik_opcodes):
			dalvik_opcodes = load_obj(pkl_dalvik_opcodes)
		
		if(dalvik_opcodes):
			if(len(dalvik_opcodes) == 0):
				get_dalvik_table()
		else:
			get_dalvik_table()

		#print(dalvik_opcodes)
		dalvik_opcodes_an = []
		if os.path.exists('./' + pkl_dalvik_opcodes_an):
			dalvik_opcodes_an = load_obj(pkl_dalvik_opcodes_an)
		else:	
			for d in dalvik_opcodes:
			#	print(d.op_code)
			#	print(d.op_name)
				dalvik_opcodes_an.append(dalvik_opcode(d.op_code, d.op_name, d.explanation, d.example))

		
		if os.path.exists(pkl_dalvik_opcodes):
			dalvik_apps = load_obj(pkl_dalvik_opcodes)


		for cat in Categories:
			cat.analize_dalvik()


	






	