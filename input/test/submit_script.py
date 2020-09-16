import itertools as it
import numpy as np
import os,sys,re
import argparse
import glob
import re
import time
#some necissary variables
start_next_batch=True

#number of total jobs to do: 
number_of_jobs=len(glob.glob('*.sh'))
print("total number of jobs:", number_of_jobs)
keep_running=True #variable for the loop
found_new_output=False

def check_completion():
	number_spectra = len(glob.glob('./spectra_data/*'))
	print("number of spectras:", number_spectra)
	if(number_spectra==number_of_jobs):
		return True
	else:
		return False

def commit_job():
	for i in range(start_number,start_number+5):
		print(str("submit" + str(i)+".sh"))
		if(os.path.exists(str("submit" + str(i)+".sh"))==True):
			os.system("sbatch submit"+str(i)+".sh") 
			print("submitting file")
			with open("submitting_iteration.txt",'a') as file:
				file.write(str(i)+"\n")
		else:
			print("no further submitxxx.sh could be found")
	print("start next set to false")
	start_next_batch=False



def manage_output():
	output_name_list=glob.glob('outputs/*.output')
	print("output name list:", output_name_list)
	if(len(output_name_list)!=0):
		for output_dir in output_name_list:
			#gets the current path to return later
			current_path=os.getcwd()
			
			#gets the run number from the dir name
			run_file_name=glob.glob(output_dir+'/run*')[0]
			run_number=int(run_file_name.split("run")[1])
			print("Run file name: "+ run_file_name)
			print("Run number: ",run_number)
			
			#change dir for autospec
			os.chdir(run_file_name)
			os.system("autospec85 0 5 ev 0")
						
			#return to previous dir
			os.chdir(current_path)
			#copys the spectrum into the spectra_data dir and changes its name according to the run number
			os.system("cp "+ run_file_name +"/spectrum.pl " 
				+ "./spectra_data/spectrum"+str(run_number)+".pl") 
				#moves the complete output dir into the finished 
			os.system("mv "+ output_dir + " outputs/finished/submit"+str(run_number)+".output")
			
			print("\n \n")
		start_next_batch=True # new outputs could be managed
		print("after managing start_next_batch ist: ", start_next_batch)
	else:
		start_next_batch=False
		print("nothing to manage: ", start_next_batch)


parser = argparse.ArgumentParser(description='''
        Script to submit all files in chunks of 20.
        ''')
		
epilog = '\nUsage: python test_skript.py'

	 
parser.add_argument('-i', '--iteration',
	 help= 'manual starting iteration' , required =False)

print("This script will submit all pending spectra calculations\n")




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

print("Starting with submission nr:", start_number)
	
	

while(keep_running==True):
	with open("submitting_iteration.txt", "r") as file:
		first_line = file.readline()
		for last_line in file:
			pass
		start_number= int(last_line)+1
	#commit new jobs
	print("\nstart next batch after managing output:", start_next_batch)
	if(start_next_batch==True):
		print("should start new job now")
		commit_job()
	print("beginn sleep phase")
	print("-z--z--z--z--z--z--z--z--z--z--z--z--z--z- \n \n")
	time.sleep(150)

	#manage outputs
	manage_output()
		
		
	if(check_completion==True):
		keep_running=False
	




		
		
		
