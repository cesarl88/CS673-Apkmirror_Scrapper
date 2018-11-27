
from smalanalysis.smali import SmaliObject, ChangesTypes, SmaliProject, Metrics
from smalanalysis.tools.commands import queryAaptForPackageName
import subprocess
import json
import os
import re
import argparse
import csv		
import xlsxwriter.workbook 
import statistics
import requests
import bs4
from bs4 import BeautifulSoup
from datetime import datetime, date
import pickle
import sys
import shutil

minSDK = { }
targetSDK = {}
Categories = []
regenerate_res = True
verbose = False


pkl_categories = "categories_list"
pkl_dalvik_opcodes = "dalvik_opcodes"
pkl_dalvik_opcodes_an = "dalvik_opcodes_an"

dalvik_opcodes = []
dalvik_opcodes_an = []
dalvik_apps = []	
dalvik_op = {}
dalvik_op_cat = {}

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
		self.res_size_diff = 0
		self.lib_size_diff = 0
		self.dex_size_diff = 0
		self.smali_size_diff = 0
		
		self.apk_size = 0
		self.res_size = 0
		self.lib_size = 0
		self.dex_size = 0
		self.smali_size = 0
		
		self.min_sdk = 0
		self.target_sdk = 0
		self.platform_sdk = 0
		
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


	#def print(self):
		
		#print(" res_layout_addition: " + self.res_layout_addition + ", res_layout_changes: " + self.res_layout_changes + ", res_orientation_support: " + self.res_orientation_support + ", res_direction_support " + self.res_direction_support + ", res_size_support: " + self.res_size_support + ", res_dpi_support: " self.res_dpi_support + ", res_platform_support: " + self.res_platform_support)

		#self.res_layout_removal= 0
		#self.res_rem_orientation_support = 0
		#self.res_rem_direction_support = 0
		#self.res_rem_size_support = 0
		#self.res_rem_dpi_support = 0
		#self.res_rem_platform_support = 0

	def get_apk_path(self):
		return os.path.join(self.application.get_path(), _removeNonAscii(self.version).replace(".", "_").replace(" ","_") + ".apk")

	def get_smali_path(self):
		return os.path.join(self.application.get_path(), _removeNonAscii(self.version).replace(".", "_").replace(" ","_") + ".apk.smali")

	def get_old_apk_dir(self):
		return os.path.join(self.application.get_path(), _removeNonAscii(self.version).replace(".", "_").replace(" ","_"))

	def get_apk_dir(self):
		return os.path.join(self.application.get_path(), _removeNonAscii(self.version).replace(".", "_").replace(" ","_") + "_apktool")

	def get_date(self):
		try:
			return datetime.strptime(self.date, '%Y-%m-%d')
		except ValueError:
			return datetime.strptime(self.date, " %B %d  %Y")

	def reprJSON(self):
		return self.__dict__

	def is_decompiled(self):
		return os.path.exists(self.get_smali_path())

	def get_lib_dir(self):
		return self.get_apk_dir() + '/lib'

	def get_smali_dir(self):
		return self.get_apk_dir() + '/smali'
	
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
			self.res_size = get_dir_size(res_path)
		self.dex_size = get_dir_size(self.get_apk_dir(), '.dex')
		self.smali_size = get_dir_size(self.get_smali_dir())
		

		self.application.category.apk_sizes.append(self.apk_size)
		self.application.category.dex_sizes.append(self.dex_size)
		self.application.category.res_sizes.append(self.res_size)
		self.application.category.lib_sizes.append(self.lib_size)
		self.application.category.smali_sizes.append(self.smali_size)

	def get_SDK_info(self):
		
		manifest_path = os.path.join(self.get_apk_dir(), 'AndroidManifest.xml')

		if os.path.exists(manifest_path):
			print("Manifest found")
			print(manifest_path)
			print(self.version)
			file = open(manifest_path, 'r')
			content = file.read()

			manifest_soup = BeautifulSoup(content, "xml")

			sdk_tag = manifest_soup.find('uses-sdk')
			manifest_tag = manifest_soup.find('manifest')

			if manifest_tag:
				print("manifest_tag")
				#print(manifest_tag.has_attr('platformBuildVersionCode'))
				#print(manifest_tag['platformBuildVersionCode'])
				if manifest_tag.has_attr('platformBuildVersionCode'):
					platform_sdk = manifest_tag['platformBuildVersionCode']
					self.platform_sdk = int(platform_sdk)
					if(platform_sdk in self.application.category.platform_sdk):
						self.application.category.platform_sdk[platform_sdk] += 1
					else:
						self.application.category.platform_sdk[platform_sdk] = 1
					print("platformBuildVersionCode: " + platform_sdk)

			if sdk_tag:
				print("sdk_tag")
				#print('android:targetSdkVersion' in sdk_tag)
				#print('android:minSdkVersion' in sdk_tag)

				if  sdk_tag.has_attr('android:minSdkVersion'):
					min_sdk = sdk_tag['android:minSdkVersion']

					if(min_sdk in self.application.category.min_sdk):
						self.application.category.min_sdk[min_sdk] += 1
					else:
						self.application.category.min_sdk[min_sdk] = 1
					
					self.min_sdk = int(min_sdk)
					print("targetSdkVersion: " + min_sdk)

				

				if  sdk_tag.has_attr('android:targetSdkVersion'):
					target_sdk = sdk_tag['android:targetSdkVersion']

					if(target_sdk in self.application.category.target_sdk):
						self.application.category.target_sdk[target_sdk] += 1
					else: 
						self.application.category.target_sdk[target_sdk] = 1

					self.target_sdk = int(target_sdk)
					print("targetSdkVersion: " + target_sdk)


	def get_smali(self):
		global verbose

		apk_path = self.get_apk_path()
		smali_path = self.get_smali_path()

		if os.path.exists(smali_path):
			if verbose:
				print("Ignoring Found (" +smali_path+")") 

		elif os.path.exists(apk_path):
			Command = "sa-disassemble '" + apk_path +"'"
			if verbose:
				print(Command)
			try:
				p = subprocess.Popen(Command, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
				(output, err) = p.communicate()
				p_status = p.wait()
			except KeyboardInterrupt:
				print("Exiting")
				#sys.exit(0)
			except Exception as e:
				FailList += version0 + '\n'
		elif verbose:
			print("Ignoring not Found (" +apk_path+")") 


	def extract_resources(self):
		#global regenerate_res
		
		res_path = self.get_apk_dir()
		print("exists: "+ res_path)
		if(not os.path.exists(res_path)):
			path = self.get_apk_path()
			print("Checking " + path)
			return run_apktool(path)
		else: 
			# if(regenerate_res):
			# 	os.path.rmdir(res_path)
			# 	return run_apktool(path)
			return True

	def remove_apk_folder(self):
		res_path = self.get_old_apk_dir()
		if os.path.exists(res_path):
			if verbose:
				print("Removing (" + res_path + ")" )
			shutil.rmtree(res_path)


	def compare_res_content(self, prev_version):
		print("compare_res_content")
		
		res0_dir = prev_version.get_res_dir();
		res1_dir = self.get_res_dir();

		if(os.path.exists(res0_dir) and os.path.exists(res1_dir)):

			#print("res0_dir" + res0_dir)
			#print("res1_dir" + res1_dir)


			v0_resoures_folders = [dI for dI in os.listdir(res0_dir) if os.path.isdir(os.path.join(res0_dir,dI)) and dI.startswith('layout')]
			v1_resoures_folders = [dI for dI in os.listdir(res1_dir) if os.path.isdir(os.path.join(res1_dir,dI)) and dI.startswith('layout')]


			#print("v0_resoures_folders" + str(v0_resoures_folders))
			#print("v1_resoures_folders" + str(v1_resoures_folders))

			#comparing changes and deletions from previous to new
			print("comparing changes and deletions from previous to new")

			for l0 in v0_resoures_folders:
				l0_dir  = os.path.join(res0_dir, l0)
				l1_dir  = os.path.join(res1_dir, l0)

				files  = [f for f in os.listdir(l0_dir) if os.path.isfile(os.path.join(l0_dir, f))]

				if(not os.path.exists(l1_dir)):
					self.res_layout_removal = len(files)
					qualifiers = l0.split('-')
					if len(qualifiers) > 0:

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
						#print(f0_path)
						#print(f1_path)
						
						if(os.path.exists(f1_path)):
							#run md5
							output0 = ''
							output1 = ''

							cmd = "md5sum '" + f0_path +"'"
							p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
							(output0, err) = p.communicate()


							cmd = "md5sum '" + f1_path +"'"
							p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE,  stderr=subprocess.PIPE)
							(output1, err) = p.communicate()

							
							out_0 = str(output0).split(' ')
							out_1 = str(output1).split(' ')	
							#print(out_0[0] +" != "+ out_1[0])
							if(out_0[0] != out_1[0]):
								self.res_layout_changes += 1
								#print("self.res_layout_changes " + str(self.res_layout_changes))
						else:
							qualifiers = l0.split('-')
							#print(qualifiers)
							if len(qualifiers) > 0:
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
			print("comparing additions from  new to previous")
			for l1 in v1_resoures_folders:
				l0_dir  = os.path.join(res0_dir, l1)
				l1_dir  = os.path.join(res1_dir, l1)

				files  = [f for f in os.listdir(l1_dir) if os.path.isfile(os.path.join(l1_dir, f))]

				if(not os.path.exists(l0_dir)):
					self.res_layout_addition = len(files)
					qualifiers = l1.split('-')
					#print(qualifiers)
					if len(qualifiers) > 0:

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
							
						#print(f0_path)
						#print(f1_path)


						if(not os.path.exists(f0_path)):
							self.res_layout_addition += 1
							qualifiers = l1.split('-')
							#print(qualifiers)
							if len(qualifiers) > 0:
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
		#print("compare_apk_content")
		self.apk_size_diff = self.apk_size - prev_version.apk_size
		self.res_size_diff = self.res_size - prev_version.res_size
		self.lib_size_diff = self.lib_size - prev_version.lib_size
		self.dex_size_diff = self.dex_size - prev_version.dex_size
		self.smali_size_diff = self.smali_size - prev_version.smali_size

		#print("apk_size_diff: " + str(self.apk_size_diff))
		#print("res_size_diff: " + str(self.res_size_diff))
		#print("lib_size_diff: " + str(self.lib_size_diff))
		#print("dex_size_diff: " + str(self.dex_size_diff))
		#print("smali_size_diff: " + str(self.smali_size_diff))


		
class Application:

	def __init__(self, category, name, versions_url):
		self.category = category
		self.versions = []
		self.name = name
		self.versions_url = versions_url
		self.is_checked = False
		self.res_checked = False
		self.is_apk_mirror = False
		self.is_resources_done = False
		self.is_differencer_done = False

	def get_path(self):
		return "./" + (self.category.name) + "/" + (self.name) + "/"

	
	def analize_dalvik(self):
		global dalvik_op_cat
		for version in self.versions:
			if not version.is_downloaded:
				continue

			if not version.metrics:
				continue

			bases = [""]
			
			
			tt= 0
			for b in bases:
				if not self.category.set_total_metrics or not self.category.metrics:
					for k in filter(lambda x: type(next_version.metrics[x]) != set and x.startswith(b), next_version.metrics.keys()):
						t+=1

			added = ('|'.join(version.metrics["{}addedLines".format(b)]))
			removed = ('|'.join(version.metrics["{}removedLines".format(b)]))

			addedlines = added.split('|')
			removedlines = removed.split('|')
			#print(addedlines)
			#print(removedlines)
			
			for a in addedlines:
				ind = dalvik_opcodes_an_index_of(dalvik_op_cat[self.category], a)
				if(ind > -1):
					dalvik_op_cat[self.category][ind].added += 1

			for r in removedlines:
				ind = dalvik_opcodes_an_index_of(dalvik_op_cat[self.category],r)
				if(ind > -1):
					dalvik_op_cat[self.category][ind].removed += 1



	def analize_differences(self):
		size = len(self.versions) - 1


		for i in range(size, 0, -1):
			
			version = self.versions[i]
			
			if not version.is_downloaded:
				continue

			print("Version 0 :" + version.version)
			nextI = i - 1
			next_version = self.versions[nextI]
			while not next_version.is_downloaded  and nextI >= 0:
				nextI -=1 
				next_version = self.versions[nextI]


			print("Version 1 :" + next_version.version)


			if(version.is_checked):
				continue
			if(next_version.is_checked):
				continue
			version0 = version.get_smali_path()



			try:
				print("Parsing old Version: " + version0)
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

				while not Compared and nextI >= 0:
					try:
						version1 = next_version.get_smali_path()

						print("Parsing New Version: " + version1)
						if(not next_version.is_downloaded and next_version.is_checked and next_version.isObfuscated):
							nextI -=1
							next_version = self.versions[nextI]
							continue
					    #parseProject(new, args.smaliv2, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)


						print("Comparing %s against %s" % (version0, version1))
						new = SmaliProject.SmaliProject()
						new.parseProject(version1, None, exclude_lists, None, True)

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
						#next_version.metrics = metrics
						metrics["#M-"] = mold + moldin
						metrics["#M+"] =  mnew + mnewin
						Metrics.computeMetrics(diff, metrics, "", True, False)
						print("About to print ")
						#print(metrics)
						next_version.metrics = metrics
						print(next_version.metrics)
						Compared = True
					except Metrics.ProjectObfuscatedException:
						print(next_version.version + " is obfuscated. Unable to proceed.")
						nextI -= 1
						next_version = self.versions[nextI]
					except Exception as e:
						print("Error parsing")
						print(e)
						nextI -= 1
						next_version = self.versions[nextI]
				
				i = nextI + 1
			except Metrics.ProjectObfuscatedException:
				print(version.version + " is obfuscated. Unable to proceed.")
				continue
			except Exception as e:
				print("Error parsing")
				print(e)
				continue
				#sys.exit(0)
			bases = [""]
			#headers_printed = False
			#headers= ""
			
			
			for b in bases:
				if not self.category.set_total_metrics or not self.category.metrics:
					for k in filter(lambda x: type(next_version.metrics[x]) != set and x.startswith(b), next_version.metrics.keys()):
						self.category.metrics[k[len(b):]] = []
				self.category.set_total_metrics = bool(self.category.metrics)
				#print(self.category.metrics)
				#self.category.metrics = dict.fromkeys(next_version.metrics.keys(), [])
				

			for k in filter(lambda x: type(next_version.metrics[x]) != set and x.startswith(b), next_version.metrics.keys()):
				#print(k +" : "+ str(next_version.metrics[k]))
				self.category.metrics[k].append(next_version.metrics[k])
				#print(self.category.metrics[k])

			print("Saving categories")
			save_obj(self.category,self.category.name, ext)
			
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
		self.category.print(4)

	def extract_apks(self):
		for i in range(len(self.versions) - 1, 0, -1):
			v = self.versions[i]
			if not v.extract_resources():
				continue
			# Check APK size composition
			v.check_apk_size()
			v.get_SDK_info()
			#save_obj(Categories, pkl_categories, ext)
			#print_categories()
			#sys.exit(0)


	def remove_apk_folder(self):
		for v in self.versions:
			v.remove_apk_folder();

	def process_resources(self):
		
		#if(regenerate_res):
		print("Removing old extraction")
		self.remove_apk_folder()

		# Perform the extraction separate to avoid double extraction work while moving every two version
		print("extracting apk content")
		self.extract_apks()

		for i in range(len(self.versions) - 1, 0, -1):
			

			version = self.versions[i]

			print("version." + version.version)
			if(not version.is_downloaded):
				print("version." + str(version.is_downloaded))
				continue

			if not version.extract_resources():
				print("version skipping")
				continue

			nextI = (i - 1)

			while nextI >= 0:
				next_version = self.versions[nextI]
				print("Next." + next_version.version)
				if not next_version.is_downloaded:
					print("Next." + str(next_version.is_downloaded))
					nextI -= 1

				elif not next_version.extract_resources():
					print("next_version skipping")
					nextI -=1
				else:
					i = nextI + 1

					print("About to compare")
					print("1. " + version.version)
					print("2." + next_version.version)
					next_version.compare_res_content(version)
					#check apk sizes diff 
					next_version.compare_apk_content(version)	
					break
			
			
			#self.is_resources_done = True
			#save_obj(self.category, self.category.name, ext)
		self.category.print(1)
		self .category.print(2)	
		self .category.print(4)


				





	def number_of_versions(self):
		t = [v for v in self.versions if v.is_completed == True]
		return len(t)

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



class Category:

	def __init__(self, name):
		self.name = name
		self.applications = []
		self.metrics = {}

		self.min_min_sdk = 0
		self.max_min_sdk = 0
		
		self.min_target_sdk = 0
		self.max_target_sdk = 0
		self.platform_sdk = 0

		self.min_release_date = datetime.strptime('1999-01-01', "%Y-%m-%d")
		self.max_release_date = datetime.strptime('1999-01-01', "%Y-%m-%d")
		
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

		self.min_smali_size = 0
		self.max_smali_size = 0
		self.avg_smali_size = 0
		self.median_smali_size = 0

		self.apk_sizes = []
		self.res_sizes = []
		self.dex_sizes = []
		self.smali_sizes = []
		self.lib_sizes = []


		self.res_layout_addition = []
		self.res_layout_changes = []
		self.res_orientation_support = []
		self.res_direction_support = []
		self.res_size_support = []
		self.res_dpi_support = []
		self.res_platform_support = []

		self.res_layout_removal= []
		self.res_rem_orientation_support = []
		self.res_rem_direction_support = []
		self.res_rem_size_support = []
		self.res_rem_dpi_support = []
		self.res_rem_platform_support = []

		self.min_sdk = {}
		self.target_sdk = {}
		self.platform_sdk = {}
		for i in range(29):
			self.min_sdk[str(i)] = 0
			self.target_sdk[str(i)] = 0
			self.platform_sdk[str(i)] = 0


		self.metrics = {}
		self.set_total_metrics = False

		self.dalvik_opcodes = []

	def print(self, option = 1):
		global verbose

		if verbose:

			print("+- " + self.name )
			
			if  option == 1:
				print(" - apk_sizes: ", self.apk_sizes)
				print(" - dex_sizes: ", self.dex_sizes)
				print(" - res_sizes: ", self.res_sizes)
				print(" - lib_sizes: ", self.lib_sizes)
				print(" - smali_sizes: ", self.smali_sizes)
			elif (option == 2):
				print(" - res_layout_addition: ", self.res_layout_addition)
				print(" - res_layout_changes: ", self.res_layout_changes)
				print(" - res_orientation_support: ", self.res_orientation_support)
				print(" - res_direction_support: ", self.res_direction_support)
				print(" - res_size_support: ", self.res_size_support)
				print(" - res_dpi_support: ", self.res_dpi_support)
				print(" - res_platform_support: ", self.res_platform_support)
				print(" - res_layout_removal: ", self.res_layout_removal)
				print(" - res_rem_orientation_support: ", self.res_rem_orientation_support)
				print(" - res_rem_direction_support: ", self.res_rem_direction_support)
				print(" - res_rem_size_support: ", self.res_rem_size_support)
				print(" - res_rem_dpi_support: ", self.res_rem_dpi_support)
				print(" - res_rem_platform_support: ", self.res_rem_platform_support)
			elif option == 3:
				print("min_sdk: " + str(self.min_sdk))
				print("target_sdk: " + str(self.target_sdk))
				print("platform_sdk_sdk: " + str(self.platform_sdk))
			elif option == 4:
				print("metrics: " + str(self.metrics))
			elif option == 5:
				done_apps_r = [a for a in self.applications if a.is_resources_done]
				done_apps_m = [a for a in self.applications if a.is_differencer_done]
				print(" +- Apps resources done(" + str(len(done_apps_r)) + "),  metrics done(" + str(len(done_apps_m)) + ")")

				for app in done_apps_m:
					print("  - " + app.name)
					versions = [v for v in app.versions if v.metrics]
					for v in app.versions:
						print("   - " + v.version)
						print("   - " + str(v.metrics))



	def run_dissasemble(self):

		for app in self.applications:
			for v in app.versions:
				if not v.is_downloaded:
					continue
				v.get_smali();

	def run_differencer(self):
		for app in self.applications:

			print("Application: "+ app.name)
			
			if app.is_differencer_done:	
				continue
			app.analize_differences()
			app.is_differencer_done = True
			save_obj(self, self.name, ext)


	def compare_resources(self):

		for app in self.applications:
			
			if len([v for v in app.versions if v.is_downloaded]) == 0 or app.is_resources_done:
				continue

			app.process_resources()
			app.is_resources_done = True
			save_obj(self, self.name, ext)
			#sys.exit(0)

	def analize_dalvik(self):
		for app in self.applications:
			app.analize_dalvik()

	def find_application(self, app_name):

		for app in self.applications:
			if(app.name == app_name):
				return app

		return None		
###
###  Utilities
###

def dalvik_opcodes_an_index_of(dalvik_op, op):

	for i in range(len(dalvik_op) - 1):
	#	print("if " + op + " in " + dalvik_opcodes[i].op_name)
		if (op in dalvik_op[i].op_name):
			return i

	return -1

def find_category(name):

	for cat in Categories:
		if(cat.name == name):
			return cat

	return None

def parse_csv_apk_mirror(cat):

	print("Loading Categories")
	#load_categories()

	print("Parsing CSVs from apk mirror")

	root = '.' 

	print("Processing category(" + cat.name + ")")


	cat_path = os.path.join(root, cat.name)
	apps = sorted([dI for dI in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, dI))])

	for app in apps:
		print("Processing applicaions for (" + cat.name + ")")
		app_path = os.path.join(cat_path, app)

		csv_description_path = os.path.join(app_path, app + "_Description.csv")

		print("Looking for: " + csv_description_path)
		app_obj = cat.find_application(app)
		if(os.path.exists(csv_description_path) and app_obj == None):

			with open(csv_description_path) as csv_file:
				print("Csv Found")
				csv_reader = csv.reader(csv_file, delimiter = ",")
				line_count = 0

				app_obj = Application(cat, app, 'http://apkmirror.com')
				app_obj.is_apk_mirror = True
				t = 0
				for row in csv_reader:
					if(t == 0):
						t = 1
						continue
					print(row)
					version = AppVersion(app_obj, row[0], row[3], row[1], 0, 'Android')		
					version.is_downloaded = True
					app_obj.versions.append(version)

					print(version.version + " added")

				cat.applications.append(app_obj)	
				save_obj(cat, cat.name, ext)				




def _removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def initialize_SDK_dict():
	global minSDK
	global targetSDK

	for i in range(29):
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

	save_obj(dalvik_opcodes,pkl_dalvik_opcodes, ext)


def load_json_folder(cat,folder, name):
	Apps = []

	#print(analyze_technology)
	json_data = folder +"/apps.json"
	#print(json_data)

	if os.path.exists(json_data):
		with open(json_data) as json_data:
			apps = json.load(json_data)
			for app in apps:
				#print(cat.name)
				a = Application(cat,app['name'],app['versions_url'])
				#a.__dict__ = app
				a.is_checked = app['is_checked']
				a.category = cat
				versions = []
				
				for v in app["versions"]:
					#application, version, url, date, size, android):	
					ver = AppVersion(a, v["version"], v["url"], v["date"], v["size"], v["android"])
					ver.is_downloaded = v["is_downloaded"]
					versions.append(ver)
					
				a.versions = versions
				Apps.append(a)

	return Apps

def is_in_categories(cat):
	global Categories
	#print(Categories)
	for c in Categories:
		if(c.name == cat.name):
			return True

	return False

def load_categories():
	
	global verbose

	#if(os.path.exists(pkl_categories)):	
	#	Categories = load_obj(pkl_categories, ext)

	#print(len(Categories))
	total = 0
	i = 0
	lst = []

	exclusion_folders = ['Summary','exclusionlist', 
	#'FINANCE', 'PRODUCTIVITY', 'EDUCATION', 'BUSINESS', 'COMMUNICATION', 
	'Summaries_bkp']
	cat_folders = [dI for dI in os.listdir("./") if os.path.isdir(os.path.join("./",dI)) and not dI in exclusion_folders]

	for cat in cat_folders:
		if verbose:
			print("Analizing " + cat)

		if(os.path.exists("./" + cat + ext)):
			if verbose:
				print("skipping: " + cat)
			continue

		cat_f = os.path.join("./",cat)

		category = Category(cat)
		
		category.applications = load_json_folder(category,cat_f, cat)

		#print(len(category.applications))

		#Categories.append(category)

		save_obj(category, category.name, ext)

	#print(len(Categories))

def get_dir_size(start_path = '.', ext = '*'):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			if(ext == '*' or f.endswith(ext)):
				fp = os.path.join(dirpath, f)
				if os.path.exists(fp):
					total_size += os.path.getsize(fp)
	return total_size

def run_apktool(path):
	global verbose

	fileDir = os.path.dirname(os.path.abspath(__file__))
	path = os.path.join(fileDir, path.replace('./', ''))
	outpath = os.path.join(fileDir, path.replace('.apk', '_apktool'))
	if not os.path.exists(path):
		print(path + " not found")
		return False

	if os.path.exists(outpath):
		return True
	try:
		Command = "apktool d '" + path + "' -o '" + outpath + "'"
		if verbose:
			print(Command)
		os.system(Command)

		return os.path.exists(outpath)
	except Exception as e:
		print(e)
		print("Error on apktool d " + path)
		return False
		

def save_obj(obj, name, ext):
    with open('./'+ name + ext, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name, ext):
	global verbose
	if verbose:
		print('Loading ./' + name + ext)
	with open('./' + name + ext, 'rb') as f:
		return pickle.load(f)

def sdk_info_worksheet(workbook):
	print("Generating SDK Summary")
	worksheet = workbook.add_worksheet("SDK Summary")

	worksheet.write(0, 0, 'Min SDK Version')
	worksheet.write(1, 0, 'Category')

	for i in range(1,29):
		worksheet.write(1, i, str(i))

	cat_size = len(Categories) - 1
	for i in range(cat_size):
		cat = Categories[i]
		worksheet.write(i + 2, 0, cat.name)

		for j in range(1,29):
			if str(j) in cat.min_sdk:
				worksheet.write(i + 2, j, cat.min_sdk[str(j)])
			else:
				worksheet.write(i + 2, j, 0)
			
		i+=1

	shift = cat_size + 4
	worksheet.write(shift, 0, 'Target SDK Version')
	worksheet.write(shift + 1, 0, 'Category')

	for i in range(1,29):
		worksheet.write(shift + 1,  i, str(i))

	for i in range(cat_size):
		cat = Categories[i]
		index = i + shift
		worksheet.write(index + 2, 0, cat.name)

		for j in range(1,29):
			if str(j) in cat.target_sdk:
				worksheet.write(index + 2, j, cat.target_sdk[str(j)])
			else:
				worksheet.write(index + 2, j, 0)


	shift = shift +  cat_size + 4
	worksheet.write(shift, 0, 'Platform Build SDK Version')
	worksheet.write(shift + 1, 0, 'Category')

	for i in range(1,29):
		worksheet.write(shift + 1,  i, str(i))

	for i in range(cat_size):
		cat = Categories[i]
		index = i + shift
		worksheet.write(index + 2, 0, cat.name)

		for j in range(1,29):

			if str(j) in cat.platform_sdk:
				worksheet.write(index + 2, j, cat.platform_sdk[str(j)])
			else:
				worksheet.write(index + 2, j, 0)
			

	return worksheet

def op_code_worksheet(workbook):
	global dalvik_opcodes
	global dalvik_op_cat
	print("Op Codes Summary")
	worksheet = workbook.add_worksheet("Op codes Summary")

	if os.path.exists('./' + pkl_dalvik_opcodes):
		dalvik_opcodes = load_obj(pkl_dalvik_opcodes, ext)
		
	if(dalvik_opcodes):
		if(len(dalvik_opcodes) == 0):
			get_dalvik_table()
	else:
		get_dalvik_table()

	start_col = 0

	for cat in Categories:

		op_codes = []
		for d in dalvik_opcodes:
			op_codes.append(dalvik_opcode(d.op_code, d.op_name, d.explanation, d.example))

		dalvik_op_cat[cat] = op_codes
		cat.analize_dalvik()

		worksheet.write(0, start_col + 0, 'Category')
		worksheet.write(0, start_col + 1, 'Op code')
		worksheet.write(0, start_col + 2, 'Op Name')
		worksheet.write(0, start_col + 3, 'Added')
		worksheet.write(0, start_col + 4, 'Removed')
		#worksheet.write(0, start_col + 5, 'Explanation')
		#worksheet.write(0, start_col + 6, 'Example')

		i = 1
		worksheet.write(i, start_col + 0, cat.name)
		for op in dalvik_op_cat[cat]:

			worksheet.write(i, start_col + 1, op.op_code)
			worksheet.write(i, start_col + 2, op.op_name )
			worksheet.write(i, start_col + 3, op.added)
			worksheet.write(i, start_col + 4, op.removed)
			#worksheet.write(i, start_col + 5, op.explanation)
			#worksheet.write(i, start_col + 6, op.example)

			i+=1

		start_col += 6



	return worksheet

def category_app_summary(woorkbook):
	print("Category App Summary")
	worksheet = woorkbook.add_worksheet("Category App Summary")
	worksheet.write(0, 0, 'Category')
	worksheet.write(0, 1, 'Number of Applications')
	worksheet.write(0, 2, 'Max Number of Versions')
	worksheet.write(0, 3, 'Min Number of Versions')
	worksheet.write(0, 4, 'Average Number of Versions')
	worksheet.write(0, 5, 'Min Release Date')
	worksheet.write(0, 6, 'Max Release Date')

	for cat in Categories:
		cat.min_release_date = datetime.strptime('1999-01-01', "%Y-%m-%d")
		cat.max_release_date = datetime.strptime('1999-01-01', "%Y-%m-%d")

	row = 1
	for cat in Categories:
		total_versions = []

		apps = []
		for app in cat.applications:

			versions = [v for v in app.versions if v.is_downloaded == True ]
			total_versions.append(len(versions))

			if(len(versions) > 0):
				apps.append(app)

			for v in versions:
				v_date = v.get_date()
				if  v_date < cat.min_release_date:
					cat.min_release_date = v_date
				if  v_date > cat.max_release_date:
					cat.max_release_date = v_date


		worksheet.write(row, 0, cat.name)
		worksheet.write(row, 1, len(apps))
		worksheet.write(row, 2, max(total_versions))
		worksheet.write(row, 3, min(total_versions))
		worksheet.write(row, 4, round(sum(total_versions) / max(len(total_versions),1),2))
		worksheet.write(row, 5, cat.min_release_date)
		worksheet.write(row, 6, cat.max_release_date)
		row += 1

	return worksheet
	

def caregory_summary_worksheet(workbook):
	print("Category Summary")
	worksheet = workbook.add_worksheet("Category Summary")
	worksheet.write(0, 0, 'Category')

	bases = [""]
	cat = Categories[0]
	for b in bases:
		if not cat.set_total_metrics or not cat.metrics:
			for k in filter(lambda x: type(next_version.metrics[x]) != set and x.startswith(b), next_version.metrics.keys()):
					print(k + " ")


	i = 1
	for k in filter(lambda x: type(cat.metrics[x]) != set and x.startswith(b), cat.metrics.keys()):
		worksheet.write(0, i, str(k) + ' Total')
		worksheet.write(0, i + 1, str(k) + ' Min')
		worksheet.write(0, i + 2, str(k) + ' Max')
		worksheet.write(0, i + 3, str(k) + ' Average')
		worksheet.write(0, i + 4, str(k) + ' Median')
		i += 5

	i = 1
	rows = 1
	for cat in Categories:
		worksheet.write(rows, 0, cat.name)
		i = 1
		for k in filter(lambda x: type(cat.metrics[x]) != set and x.startswith(b), cat.metrics.keys()):
			worksheet.write(rows, i, sum(cat.metrics[k])) #TOTAL
			worksheet.write(rows, i + 1, min(cat.metrics[k])) #MIN
			worksheet.write(rows, i + 2, max(cat.metrics[k])) #MAX
			worksheet.write(rows, i + 3, round(sum(cat.metrics[k]) / max(len(cat.metrics[k]),1),2)) #AVG
			worksheet.write(rows, i + 4, statistics.median(cat.metrics[k])) #MEDIAN
			i += 5
		rows += 1

	
	return worksheet	


def apk_worksheet(workbook):
	print("APK Summary")
	worksheet = workbook.add_worksheet("APK Summary")
	worksheet.write(0, 0, 'Category')
	worksheet.write(0, 1, 'Max Apk Size')
	worksheet.write(0, 2, 'Min Apk Size')
	worksheet.write(0, 3, 'Avg Apk Size')
	worksheet.write(0, 4, 'Median Apk Size')
	worksheet.write(0, 5, 'Max Resource Size')
	worksheet.write(0, 6, 'Min Resource Size')
	worksheet.write(0, 7, 'Avg Resource Size')
	worksheet.write(0, 8, 'Median Resource Size')
	worksheet.write(0, 9, 'Max Lib Size')
	worksheet.write(0, 10, 'Min Lib Size')
	worksheet.write(0, 11, 'Avg Lib Size')
	worksheet.write(0, 12, 'Median Lib Size')
	worksheet.write(0, 13, 'Max Dex Size')
	worksheet.write(0, 14, 'Min Dex Size')
	worksheet.write(0, 15, 'Avg Dex Size')
	worksheet.write(0, 16, 'Median Dex Size')
	worksheet.write(0, 17, 'Max Smali Size')
	worksheet.write(0, 18, 'Min Smali Size')
	worksheet.write(0, 19, 'Avg Smali Size')
	worksheet.write(0, 20, 'Median Smali Size')
	rows = 1
	for cat in Categories:
		worksheet.write(rows, 0, cat.name)
		worksheet.write(rows, 1, max(cat.apk_sizes))
		worksheet.write(rows, 2, min(cat.apk_sizes))
		worksheet.write(rows, 3, round(sum(cat.apk_sizes) / max(len(cat.apk_sizes),1),2))
		worksheet.write(rows, 4, statistics.median(cat.apk_sizes))
		worksheet.write(rows, 5, max(cat.res_sizes))
		worksheet.write(rows, 6, min(cat.res_sizes))
		worksheet.write(rows, 7, round(sum(cat.res_sizes) / max(len(cat.res_sizes),1),2))
		worksheet.write(rows, 8, statistics.median(cat.res_sizes))
		worksheet.write(rows, 9, max(cat.lib_sizes))
		worksheet.write(rows, 10, min(cat.lib_sizes))
		worksheet.write(rows, 11, round(sum(cat.lib_sizes) / max(len(cat.lib_sizes),1),2))
		worksheet.write(rows, 12, statistics.median(cat.lib_sizes))
		worksheet.write(rows, 13, max(cat.dex_sizes))
		worksheet.write(rows, 14, min(cat.dex_sizes))
		worksheet.write(rows, 15, round(sum(cat.dex_sizes) / max(len(cat.dex_sizes),1),2))
		worksheet.write(rows, 16, statistics.median(cat.dex_sizes))
		worksheet.write(rows, 17, max(cat.smali_sizes))
		worksheet.write(rows, 18, min(cat.smali_sizes))
		worksheet.write(rows, 19, round(sum(cat.smali_sizes) / max(len(cat.smali_sizes),1),2))
		worksheet.write(rows, 20, statistics.median(cat.smali_sizes))
		rows += 1

	return worksheet

def resources_worksheet(workbook):
	print("Resources Summary")
	worksheet = workbook.add_worksheet("Resources Summary")
	worksheet.write(0, 0, 'Category')
	worksheet.write(0, 1, 'Layout Addition')
	worksheet.write(0, 2, 'Layout Removal')
	worksheet.write(0, 3, 'Layout Changes')
	worksheet.write(0, 4, 'Orientation added')
	worksheet.write(0, 5, 'Direction Added')
	worksheet.write(0, 6, 'Size Support Added')
	worksheet.write(0, 7, 'Dpi Support Added')
	worksheet.write(0, 8, 'Platform Support Added')
	worksheet.write(0, 9, 'Orientation Removed')
	worksheet.write(0, 10, 'Direction Removed')
	worksheet.write(0, 11, 'Size Support Removed')
	worksheet.write(0, 12, 'Dpi support Removed')
	worksheet.write(0, 13, 'Platform Support Removed')


	row = 1
	for cat in Categories:

		for app in cat.applications:

			for v in app.versions:

				if(not v.is_downloaded):
					continue
				cat.res_layout_addition.append(v.res_layout_addition)
				cat.res_layout_changes.append(v.res_layout_changes)
				cat.res_orientation_support.append(v.res_orientation_support)
				cat.res_direction_support.append(v.res_direction_support)
				cat.res_size_support.append(v.res_size_support)
				cat.res_dpi_support.append(v.res_dpi_support)
				cat.res_platform_support.append(v.res_platform_support)

				cat.res_layout_removal.append(v.res_layout_removal)
				cat.res_rem_orientation_support.append(v.res_rem_orientation_support)
				cat.res_rem_direction_support.append(v.res_rem_direction_support)
				cat.res_rem_size_support.append(v.res_rem_size_support)
				cat.res_rem_dpi_support.append(v.res_rem_dpi_support)
				cat.res_rem_platform_support.append(v.res_rem_platform_support)


		worksheet.write(row, 0, cat.name)
		worksheet.write(row, 1, sum(cat.res_layout_addition))
		worksheet.write(row, 2, sum(cat.res_layout_removal))
		worksheet.write(row, 3, sum(cat.res_layout_changes))
		worksheet.write(row, 4, sum(cat.res_orientation_support))
		worksheet.write(row, 5, sum(cat.res_direction_support))
		worksheet.write(row, 6, sum(cat.res_size_support))
		worksheet.write(row, 7, sum(cat.res_dpi_support))
		worksheet.write(row, 8, sum(cat.res_platform_support))
		worksheet.write(row, 9, sum(cat.res_rem_orientation_support))
		worksheet.write(row, 10, sum(cat.res_rem_direction_support))
		worksheet.write(row, 12, sum(cat.res_rem_size_support))
		worksheet.write(row, 13, sum(cat.res_rem_dpi_support))
		worksheet.write(row, 14, sum(cat.res_rem_platform_support))

		row += 1 

	return worksheet

def export_to_excel():
	print("Export to excel")

	global verbose
	global Categories

	exclusion_folders = ['Summary','exclusionlist'
	#,'PRODUCTIVITY', 'EDUCATION', 'COMMUNICATION', 
	'Summaries_bkp']

	cat_folders = [dI for dI in os.listdir("./") if os.path.isdir(os.path.join("./",dI)) and not dI in exclusion_folders]

	for cat in cat_folders:
		if verbose:
			print("Analizing " + cat)

		if(os.path.exists("./" + cat + ext)):
			print("Loading " + cat)
			category = load_obj("./" + cat,ext)
			Categories.append(category)
			

	workbook = xlsxwriter.Workbook(os.path.join('.', 'final_report.xlsx'))
	sdk_info_worksheet(workbook)
	op_code_worksheet(workbook)
	caregory_summary_worksheet(workbook)
	apk_worksheet(workbook)
	resources_worksheet(workbook)
	category_app_summary(workbook)

	workbook.close()

def backup():
	print("Backup")

	exclusion_folders = ['Summary','exclusionlist'
	#,'PRODUCTIVITY', 'EDUCATION', 'COMMUNICATION', 'BUSINESS','TOOLS','FINANCE' 
	'Summaries_bkp']

	cat_folders = [dI for dI in os.listdir("./") if os.path.isdir(os.path.join("./",dI)) and not dI in exclusion_folders]

	for cat in cat_folders:
		print("Analizing " + cat)
		cat_path = os.path.join(".", cat)
		apps_folders = [dI for dI in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path,dI)) ]

		for app in apps_folders:

			app_path = os.path.join(cat_path, app)
			res_folders = [dI for dI in os.listdir(app_path) if os.path.isdir(os.path.join(app_path,dI)) and dI.endswith("_apktool")]

			for res in res_folders:
				res_path = os.path.join(app_path, res)
				bkp = "'/Volumes/LACIE SHARE/Personal/Documents/NJIT/Fall 2018/CS 673" + res_path.replace('./','/') + "'"
				command = "cp - '" + res_path + "' " + bkp
				print(command)
				#os.system(command)




def print_categories():

	Categories = load_obj(pkl_categories, ext)
	for cat in Categories:
		print("+- " + cat.name )
		print(" - apk_sizes: ", cat.apk_sizes)
		print(" - dex_sizes: ", cat.dex_sizes)
		print(" - res_sizes: ", cat.res_sizes)
		print(" - lib_sizes: ", cat.lib_sizes)

		print(" - res_layout_addition: ", cat.res_layout_addition)
		print(" - res_layout_changes: ", cat.res_layout_changes)
		print(" - res_orientation_support: ", cat.res_orientation_support)
		print(" - res_direction_support: ", cat.res_direction_support)
		print(" - res_size_support: ", cat.res_size_support)
		print(" - res_dpi_support: ", cat.res_dpi_support)
		print(" - res_platform_support: ", cat.res_platform_support)
		print(" - res_layout_removal: ", cat.res_layout_removal)
		print(" - res_rem_orientation_support: ", cat.res_rem_orientation_support)
		print(" - res_rem_direction_support: ", cat.res_rem_direction_support)
		print(" - res_rem_size_support: ", cat.res_rem_size_support)
		print(" - res_rem_dpi_support: ", cat.res_rem_dpi_support)
		print(" - res_rem_platform_support: ", cat.res_rem_platform_support)


		# i = 1
		# for app in cat.applications:
			
		# 	versions = [v for v in app.versions if v.is_downloaded]

		# 	if(len(versions) > 0):
		# 		print("  +- " + str(i) + '. ' + app.name)	
		# 		i += 1

		# 	for v in versions:
		# 		print("    -- " + v.version)	
		# 		print("      -- " + str(v.metrics))										

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Milestone 1 analisys.')

	parser.add_argument('category', type=str,
                    help='Category to process')

	#General
	parser.add_argument('--print-categories', '-print_categories', action='store_true',
                    help='Print Categories')
	parser.add_argument('--verbose', '-verbose', action='store_true',
                    help='Print Progress')

	#Dalvik Analisys
	parser.add_argument('--analize-dalvik-table', '-analize_dalvik', action='store_true',
                    help='Analize Dalvik')
	parser.add_argument('--get-dalvik-table', '-get_dalvik_table', action='store_true',
                    help='Generate Dalvik Table from web')
	parser.add_argument('--print-dalvik-table', '-print_dalvik', action='store_true',
                    help='Print Dalvik Table')
	parser.add_argument('--print-dalvik-table-an', '-print_a_dalvik', action='store_true',
                    help='Print Analized Dalvik Table')

	#Categories Loading
	parser.add_argument('--load-categories', '-load_categories', action='store_true',
                    help='Load Categories from Json apps')
	parser.add_argument('--parse-csv-apk-mirror', '-parse_csv_apk_mirror', action='store_true',
                    help='Add apps from apk mirror to apk pure Json format')

	#Differencer
	parser.add_argument('--run-dissasemble', '-run_dissasemble', action='store_true',
                    help='Get Smali from apks')
	parser.add_argument('--run-differencer', '-run_differencer', action='store_true',
                    help='Run differencer')


	#Resources
	parser.add_argument('--compare-resources', '-compare_resources', action='store_true',
                    help='Compare resources')

	#Report
	parser.add_argument('--generate-report', '-generate_report', action='store_true',
                    help='Generate excel report')

	#backup

	parser.add_argument('--backup', '-backup', action='store_true',
                    help='Generate excel report')

	args = parser.parse_args()

	#global verbose
	
	if args.verbose:
		verbose = True


	category_pkl = args.category
	if not os.path.exists("./" + args.category + ext):
		load_categories()

	if args.load_categories:
		print("Loading categories_list")
	elif args.parse_csv_apk_mirror:
		cat = load_obj(category_pkl,ext)
		parse_csv_apk_mirror(cat)
	elif args.print_categories:
		cat = load_obj(category_pkl,ext)
		cat.print(1)
		cat.print(5)
		cat.print(2)
		cat.print(3)
		cat.print(4)
		#print_categories()
	#Differencer
	elif args.run_dissasemble:

		cat = load_obj(category_pkl,ext)
		#for cat in Categories:
		cat.run_dissasemble()
	elif args.run_differencer:
		cat = load_obj(category_pkl,ext)
		#for cat in Categories:
		cat.run_differencer()
	#resources
	elif args.compare_resources:
		cat = load_obj(category_pkl,ext)
		#for cat in Categories:
		cat.compare_resources()
	#excel report
	elif args.generate_report:
		export_to_excel()
	#Dalvik Analisys
	elif(args.print_dalvik_table):
		dalvik_opcodes = load_obj(pkl_dalvik_opcodes, ext)
		print('dalvik_codes')
		for d in dalvik_opcodes:
			print(d.op_code + '-> ' + d.op_name)
	elif(args.print_dalvik_table_an):
		dalvik_opcodes_an = load_obj(pkl_dalvik_opcodes_an, ext)
		print('dalvik_opcodes_an')
		for d in dalvik_opcodes_an:
			print(d.op_code + '-> ' + d.op_name +', added: '+str(d.added)+', removed: ' + str(d.removed))
	elif args.get_dalvik_table:
		get_dalvik_table()
	elif(args.analize_dalvik_table):
		if os.path.exists('./' + pkl_dalvik_opcodes):
			dalvik_opcodes = load_obj(pkl_dalvik_opcodes, ext)
		
		if(dalvik_opcodes):
			if(len(dalvik_opcodes) == 0):
				get_dalvik_table()
		else:
			get_dalvik_table()

		#print(dalvik_opcodes)
		dalvik_opcodes_an = []
		if os.path.exists('./' + pkl_dalvik_opcodes_an):
			dalvik_opcodes_an = load_obj(pkl_dalvik_opcodes_an, ext)
		else:	
			for d in dalvik_opcodes:
			#	print(d.op_code)
			#	print(d.op_name)
				dalvik_opcodes_an.append(dalvik_opcode(d.op_code, d.op_name, d.explanation, d.example))

		
		if os.path.exists(pkl_dalvik_opcodes):
			dalvik_apps = load_obj(pkl_dalvik_opcodes, ext)


		for cat in Categories:
			cat.analize_dalvik()

	elif args.backup:
		backup()



	






	