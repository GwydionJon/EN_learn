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
		"pyrmod4.op, pyr4.inp and submit.sh must be in the same directory!\n"+
		"Only one data set should be in a working directory at a time to avoid confusion.\n The program will not allow a second set of data to be generated if there is already a csv file with variables present.")
	
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
	if(any([mode in [1,3] for mode in mode_list])):
		no_of_submits=int(input("Enter number of submits in each run:\n"))
	else:
		no_of_submits=0
	
	return mode_list, dict_param, working_directory, no_of_submits

###
#this will first create a dataFrame of all possible combinations for the given parameters and save it as a csv

def create_submit_files(dict_param, path_dict):

	if(os.path.exists("submit.sh")==False):
		sys.exit("this program can not function if submit.sh is missing")
	inputfile = "submit.sh"
	
	test=product(*dict_param.values())
	df_combi = pd.DataFrame(test, columns=dict_param.keys())
	
	if(len(glob.glob(path_dict["working_directory"]+"/*.csv"  ))!=0):
		print("There is already a csv file with parameters present! No new data will be generated!")
	else:
		df_combi.to_csv(path_dict["working_directory"]+"/all_"+str(len(df_combi))+"_combinations.csv")
		
		#print(df_combi.head())
		
		complete_array=df_combi.to_numpy()
		for i,row in enumerate(complete_array):
			outname=path_dict["input_Data"]+"/submit__"
			run_str="run"+str(i)
			output_dir="output"
			parameter_str="-mnd -D run" +str(i)
			for j,nr in enumerate(row):
				outname=outname+df_combi.columns[j]+"_"+str(nr)+"__"
				parameter_str=parameter_str + " -p " +df_combi.columns[j]+" "+str(nr)
				output_dir=output_dir+"__"+df_combi.columns[j]+"_"+str(nr)			
			outname=outname+".sh"
			#print(outname)
			#print(parameter_str)
			with open(outname,'w') as new_file:
							with open(inputfile, 'r') as old_file:
								line = old_file.read()
								new_file.write(line.replace("runxxx", run_str).replace("xyz", parameter_str).replace("whatever",output_dir)   )




def commit_jobs(path_dict, no_of_submits):
	all_input_data=glob.glob(path_dict["input_Data"]+'/*.sh')
	if(len(all_input_data)!=0):
		print("Total of ", len(all_input_data), " jobs remaining.")
		if(len(all_input_data)<=no_of_submits):
			no_of_submits=len(all_input_data)
		for i in range(no_of_submits):
			os.system("sbatch "+ all_input_data[i]) 
			shutil.move(all_input_data[i], path_dict["finished_input"])
		print("submitting file")
		return True
	else:
		print("No jobs remaining.")
		return False



def manage_output(path_dict,output_name_list):
	print("output name list:", output_name_list)
	#gets the current path to return later

	current_path=os.getcwd()
	print(current_path)

	
	if(len(output_name_list)!=0):
		for output_dir in output_name_list:
			
			#gets the run number from the dir name
			run_file_name=glob.glob(output_dir+'/run*')[0]
			run_parameters=(run_file_name.split("run")[1])

			print("Run file name: "+ run_file_name)
			print("Run parameter: ",run_parameters)
			
			#change dir for autospec
			os.chdir(run_file_name)
			os.system("autospec85 -e -0.2258 eV  -1.0 1.0 eV 30 1")
						
			#return to previous dir
			os.chdir(current_path)
			#copys the spectrum into the spectra_data dir and changes its name according to the run number
			shutil.copy(run_file_name +"/spectrum.pl ",path_dict["spectra_data"]+"/"+run_parameters+".pl" )
			#moves the complete output dir into the finished 
			shutil.move(output_dir,path_dict["finished_outputs"]+"/submits_"+run_parameters+".output" )

			print("\n \n")
	
			



def run_jobs(mode_list,path_dict,no_of_submits):
	jobs_available=True
	start_next_batch=True
	while(jobs_available==True):
		#only start new batch when last is finished and mode 1 or 3 was chosen
		if(start_next_batch==True and any([mode in [1,3] for mode in mode_list])):
			jobs_available = commit_jobs(path_dict,no_of_submits)
			start_next_batch=False
		time.sleep(60)	
		output_name_list=glob.glob(path_dict["output"]+'/*.output')
		if(len(output_name_list)>=no_of_submits and any([mode in [1,4] for mode in mode_list])):
			manage_output(path_dict)
			start_next_batch=True






def setup_dir_structure(path_dict):
		
	if(os.path.exists(path_dict["working_directory"])==False):
		os.makedirs(path_dict["working_directory"])
	if(os.path.exists(path_dict["input_Data"])==False):
		os.makedirs(path_dict["input_Data"])
	if(os.path.exists(path_dict["finished_input"])==False):
		os.makedirs(path_dict["finished_input"])
	if(os.path.exists(path_dict["output"])==False):
		os.makedirs(path_dict["output"])
	if(os.path.exists(path_dict["finished_outputs"])==False):
		os.makedirs(path_dict["finished_outputs"])
	if(os.path.exists(path_dict["spectra_data"])==False):
		os.makedirs(path_dict["spectra_data"])

	if(any([mode in [1,3,4] for mode in mode_list])):

	#check if needed files for calculations are present in the same dir as this file. if not throw exepction
		if(os.path.exists("pyr4.inp")==False):
			sys.exit("this program can not function if pyr4.inp is missing")
		if(os.path.exists("pyrmod4.op")==False):
			sys.exit("this program can not function if pyrmod4.op is missing")

		#copy pyr4.inp and pyrmod4.op into the input_Data dir
		shutil.copy2("./pyr4.inp",path_dict["input_Data"] )
		shutil.copy2("./pyrmod4.op",path_dict["input_Data"] )	



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
#print(current_path)
filename = sys.argv[0]

os.chdir(os.path.abspath(filename))

#get basic setup parameters
mode_list, dict_param, working_directory, no_of_submits= get_input_data()



#setup dict for all paths
path_dict={	"working_directory":working_directory,
			"input_Data": working_directory+"/input_Data",
			"finished_outputs": working_directory+"/finished_outputs",
			"finished_input":working_directory+"/finished_input",
			"output": working_directory+"/output",
			"spectra_data": working_directory+"/spectra_data"}

setup_dir_structure(path_dict)

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



	run_jobs(mode_list,path_dict,no_of_submits)

#####potentially redo everything in sending to server




