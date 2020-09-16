import itertools as it
import numpy as np
import os,sys,re
import argparse
import glob
import re
parser = argparse.ArgumentParser(description='''
        Script to submit all files in chunks of 20.
        ''')
		
epilog = '\nUsage: python test_skript.py'

	 
parser.add_argument('-i', '--iteration',
	 help= 'manual starting iteration' , required =False)

print("This script will submit all pending spectra calculations\n")

testing=False

if(testing==False):
	if(os.path.exists("submitting_iteration.txt")==True):
		with open("submitting_iteration.txt", "r") as file:
			first_line = file.readline()
			for last_line in file:
				pass
			start_number= int(last_line)+1
		
	else:
		print("Start new run of submissions")
		with open("submitting_iteration.txt",'w') as new_file:
			new_file.write("Start sumbmission counting: \n")
			start_number=0

	print("Starting with submission nr:")
	print(start_number)
	
start_next_batch=True


if(start_next_batch==True):
	for i in range(start_number,start_number+5):
		print(str("submit" + str(i)+".sh"))
		print(os.path.exists("submit0.sh"))
		if(os.path.exists(str("submit" + str(i)+".sh"))==True):
			os.system("sbatch submit"+str(i)+".sh") 
			print("submitting file")
			with open("submitting_iteration.txt",'a') as file:
				file.write(str(i)+"\n")
			start_next_batch=False
		else:
			print("no further submitxxx.sh could be found")
			raise SystemExit
		
if(start_next_batch==False):
	
	output_name_list=glob.glob('outputs/*.output')
	if(len(output_name_list)!=0):
		for output_dir in output_name_list:
			#gets the current path to return later
			current_path=os.getcwd()
			run_file_name=glob.glob(output_dir+'/run*')[0]
			run_number=int(run_file_name.split("run")[1])
			print("Run file name: "+ run_file_name)
			print("Run number: ",run_number)
			#change dir for autospec
			os.chdir(run_file_name)
			os.system("autospec85 0 5 ev 0")
			
			
			
			#return to previous dir
			os.chdir(current_path)
			
			
			
			print("\n \n")
		
		
		
		
