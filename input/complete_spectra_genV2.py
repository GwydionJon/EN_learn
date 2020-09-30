import itertools as it
import numpy as np
import os,sys,re
import argparse
import glob
import time
from sklearn.utils.extmath import cartesian
from itertools import product
import pandas as pd
import shutil




#global variables:
#for submission creation

#bool to check if nSteps and rangeStep has been called:
nSteps_called=False
rangeStep_called=False

#for submissions and managing
start_next_batch=True
#number of total jobs to do: 
number_of_jobs=len(glob.glob('*.sh'))
print("total number of jobs:", number_of_jobs)
keep_running=True #variable for the loop
found_new_output=False

#functions


#this will take inputs from the console to setup the following program
#The differentquestionsin order are:
#which mode
#which parameters 	(if mode =1,2)
#which range 		(if mode =1,2)
#which directory

def get_input_data():
	
	#beginn input for the program
	print("This program is designed to initilize submission files, submit those to to MCDTH and manage the ouput.\n"+
		"pyrmod4.op, pyr4.inp and submit.sh must be in the same directory!")
	
	#first use test_mode, later this will be the normal mode
	mode_string=input('Choose one of the following (#2,3,4,5 can be combined with \",\"): \n'+
					'1: create input, send to server, manage output.\n'+
					'2: create input.\n'+
					'3: send to server\n'+
					'4: manage output\n'+
					'5: analyze spectra\n') 
	
	#transforms input into list of int
	mode_list=[int(mode_str)for mode_str in mode_string.split(",")]
	
	#make dict
	dict_param={}
	
	#this must only be used if mode 1 or 2 are selected
	if(any([mode in [1,2] for mode in mode_list])):
		number_of_files=1 #this is for later
		#transforms input into list of strings 
		print("Chosse which parameters should be modified, choose names and seperate with \',\'. ")
		parameter_string=input("all, k6a1, k6a2, k11, k12, k9a1, k9a2, delta, lambda\n") 
		parameter_list=str(parameter_string).split(',')
		#check if all was used
		if(any([param =="all" for param in parameter_list])):
			parameter_list=["k6a1","k6a2","k11","k12","k9a1","k9a2","delta","lambda"]
	
		
		#set the parameter ranges for all parameters
		if(any([param in ["k6a1","k6a2","k11","k12","k9a1","k9a2"] for param in parameter_list])):
			same_values_bool = input("Do you want to use the same range for all k-parameters? y/n \n")
		else: 
			same_values_bool="n"
		
		#set values for all k values if same_values_bool== y
		if(same_values_bool=="y"):
			same_array_input=input("Choose the input range for all k* values:\n"+
				"Use min,max,step (eg.: 0,5.1,200) as input format\n")
			min_same,max_same,steps_same = [float(inp) for inp in same_array_input.split(',')]
			same_array=np.linspace(min_same,max_same,int(steps_same))
		
		
		#check for every param if it is one of the k values and wether the same value should be used
		# if not use different input for each and collect in dict
		for param in parameter_list:
		
			if(same_values_bool=="y" and param in ["k6a1", "k6a2", "k11", "k12", "k9a1", "k9a2"]):
				dict_param[param]=same_array
			else:
				param_array_input=input("Choose the input range for "+
				param+"\n"+
				"Use min,max,step (eg.: 0,5.1,200) as input format\n")
				param_min,param_max,param_steps = [float(inp) for inp in param_array_input.split(',')]
				dict_param[param]=np.linspace(param_min,param_max,int(param_steps))
			#no of files to be created:
			number_of_files=number_of_files*len(dict_param[param])
			
		if(number_of_files >1e6):
			print("Number of files to be created is over 1000000 and the program will terminate to protect the server. (Files to be created:",number_of_files,")" )
			sys.exit()
		print(number_of_files, " Files will be created, if that is not correct please terminate the program now!")
	#print(dict_param)
	
	bool_directory=input("Do you wish to choose a specific directory? y/n\n")
	if(bool_directory=='y'):
		working_directory=input("Enter working directory\n")
	else:
		working_directory="test"
	
	
	
	
	return mode_list, dict_param, working_directory

###
#this will first create a dataFrame of all possible combinations for the given parameters and save it as a csv
#

def create_submit_files(dict_param, path_dict):

	if(os.path.exists("submit.sh")==False):
		sys.exit("this program can not function if submit.sh is missing")
	inputfile = "submit.sh"
	
	test=product(*dict_param.values())
	df_combi = pd.DataFrame(test, columns=dict_param.keys())
	df_combi.to_csv(path_dict["working_directory"]+"/all_"+str(len(df_combi))+"_combinations.csv")
	
	#print(df_combi.head())
	
	complete_array=df_combi.to_numpy()
	for i,row in enumerate(complete_array):
		outname=path_dict["input_Data"]+"/submit__"
		run_str="run"+str(i)
		parameter_str="-mnd -D run" +str(i)
		for j,nr in enumerate(row):
			outname=outname+df_combi.columns[j]+"_"+str(nr)+"__"
			parameter_str=parameter_str + " -p " +df_combi.columns[j]+" "+str(nr)
							
		outname=outname+".sh"
		print(outname)
		print(parameter_str)
		with open(outname,'w') as new_file:
						with open(inputfile, 'r') as old_file:
							line = old_file.read()
							new_file.write(line.replace("runxxx", run_str).replace("xyz", parameter_str))


def create_submit_track_file(path_dict):
	print("This script will submit all pending spectra calculations\n")

	
	
	if(os.path.exists(working_directory+"/submitting_iteration.txt")==True):
		with open(working_directory+"/submitting_iteration.txt", "r") as file:
			first_line = file.readline()
			for last_line in file:
				pass
			start_number= int(last_line)+1
		
	else:
		print("Start new run of submissions")
		with open(working_directory+"/submitting_iteration.txt",'w') as new_file:
			new_file.write("Start sumbmission counting: \n")
			start_number=0
	
	print("Starting with submission nr:", start_number)
	return start_number

def check_completion(path_dict):
	number_spectra = len(glob.glob(working_directory+'/spectra_data/*'))
	print("number of spectras:", number_spectra)
	if(number_spectra==number_of_jobs):
		return True
	else:
		return False

def commit_job(file_name):
	os.system("sbatch "+ file_name) 
	print("submitting file")
			



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
			os.system("autospec85 -e -0.2258 eV  -1.0 1.0 eV 30 1")
						
			#return to previous dir
			os.chdir(current_path)
			#copys the spectrum into the spectra_data dir and changes its name according to the run number
			os.system("cp "+ run_file_name +"/spectrum.pl " 
				+ "./spectra_data/spectrum"+str(run_number)+".pl") 
				#moves the complete output dir into the finished 
			os.system("mv "+ output_dir + " outputs/finished/submit"+str(run_number)+".output")
			
			print("\n \n")
			start_next_batch=True # new outputs could be managed
			



def run_jobs(mode_list,path_dict):
	all_input_data=glob.glob(path_dict["input_Data"]+'/*.sh')


	#later

	#os.system("sbatch "+file_name) 
	print("submitting file")


	# keep_running=True
	# start_next_batch=True
	# while(keep_running==True):
	# 	#commit new jobs
	# 	print("start next batch after managing output:", start_next_batch)
	# 	if(start_next_batch==True and any([mode in [1,3] for mode in mode_list])):
	# 		print("should start new job now")
	# 		commit_job(start_number)
	# 		start_next_batch=False
	# 	print("beginn sleep phase")
	# 	time.sleep(300)
	# 	print("--------------------------")
	# 	#manage outputs
	# 	if(start_next_batch==False and any([mode in [1,4] for mode in mode_list])):
	# 		manage_output()
			
			
	# 	if(check_completion==True):
	# 		keep_running=False






#'1: create input, send to server, manage output.\n'+
#'2: create input.\n'+
#'3: send to server\n'+
#'4: manage output\n'+
#'5: analyze spectra\n') 







##############################
#actual program start
##############################
#print(get_input_data())
#change to current path
current_path=(os.path.dirname(__file__))
os.chdir(current_path)

#get basic setup parameters
mode_list, dict_param, working_directory = get_input_data()


if(os.path.exists(working_directory)==False):
	os.makedirs(working_directory)
if(os.path.exists(working_directory+"/input_Data")==False):
	os.makedirs(working_directory+"/input_Data")
if(os.path.exists(working_directory+"/input_Data/finished_input")==False):
	os.makedirs(working_directory+"/input_Data/finished_input")
if(os.path.exists(working_directory+"/outputs")==False):
	os.makedirs(working_directory+"/outputs")
if(os.path.exists(working_directory+"/outputs/finished_outputs")==False):
	os.makedirs(working_directory+"/outputs/finished_outputs")
if(os.path.exists(working_directory+"/spectra_data")==False):
	os.makedirs(working_directory+"/spectra_data")

#setup dict for all paths
path_dict={	"working_directory":working_directory,
			"input_Data": working_directory+"/input_Data",
			"finished_outputs": working_directory+"/finished_outputs",
			"finished_input":working_directory+"/finished_input",
			"output": working_directory+"/output",
			"spectra_data": working_directory+"/spectra_data"}



#all and file generation
if(any([mode in [1,2] for mode in mode_list])):
	create_submit_files(dict_param, path_dict)
	
	
#all and send to server

if(any([mode in [1,3,4] for mode in mode_list])):

	#check if needed files for calculations are present in the same dir as this file. if not throw exepction
	if(os.path.exists("pyr4.inp")==False):
		sys.exit("this program can not function if pyr4.inp is missing")
	if(os.path.exists("pyrmod4.op")==False):
		sys.exit("this program can not function if pyrmod4.op is missing")

	#copy pyr4.inp and pyrmod4.op into the input_Data dir
	shutil.copy2("./pyr4.inp",path_dict["input_Data"] )
	shutil.copy2("./pyrmod4.op",path_dict["input_Data"] )



	run_jobs(mode_list,path_dict)

#####potentially redo everything in sending to server




