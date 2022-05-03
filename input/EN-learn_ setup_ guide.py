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
from scipy.signal import find_peaks


#functions


#this will take inputs from the console to setup the following program
#The differentquestionsin order are:
#which mode
#which parameters 	(if mode =1,2)
#which range 		(if mode =1,2)
#which directory

def load_prebuild_structure():
	list_main_dir=[]
	for main_dir in os.listdir('.'):
		if(os.path.isdir(main_dir)):
			list_needed_dir=["finished_input","finished_outputs","input_Data",
				"output","spectra_data","spectra_data_finished"]
			if(set(list_needed_dir).issubset(os.listdir(main_dir))  ):
				list_main_dir.append(main_dir)


	choice_use_existing=input("Do you want to use one of the "+ 
	str(len(list_main_dir))+
	" existing directories? y/n \n" )
	if(choice_use_existing=="y"):
		for i in range(len(list_main_dir)):
			print("Use ",i, "to choose ", list_main_dir[i])
				
		choice_nr=int(input("Please enter the desired number.\n"))
		working_directory=list_main_dir[choice_nr]

	else: #choice use existing =!y
		bool_directory=input("Do you wish to choose a specific directory? (if not \"test\" will be used) y/n\n")

		if(bool_directory=='y'):
			working_directory=input("Enter working directory\n")
		else:
			working_directory="test"
	
	return working_directory
	
			

			

def find_operator_files(main_dir=0):
#operator list= [.inp,.op,.sh]
	
	#get .inp  and .op from preexisting dir, if available

	mol_inp=glob.glob(main_dir+"/output/*.inp")
	mol_op=glob.glob(main_dir+"/output/*.op")
	
	if(len(mol_inp)!=1 or len(mol_op)!=1 ):
		print("Not the correct number of .inp, .op and .sh files found. Number of files should be 1 bis is",
		len(mol_inp), len(mol_op), "respectivly")
		mol_inp=0
		mol_op=0
		print("Enter desired .inp and .op files when asked.")
	else:
		file_inp=mol_inp[0].split("/")[-1]
		print("Found .inp file:", file_inp)
		file_op=mol_op[0].split("/")[-1]
		print("Found .op file:", file_op)
			
	if(mol_inp==0 or mol_op==0): # if no dir is given, search for available .inp and .op files
		mol_inp=glob.glob("*.inp")
		mol_op=glob.glob("*.op")
		if(len(mol_inp)>0):
			print("Choose one of the ", len(mol_inp), " .inp files.")
			for i,inp in enumerate(mol_inp):
				print(i, "for ", inp)

			choice_inp =int(input("Please enter the desired number.\n"))
			file_inp=mol_inp[choice_inp]
		else:
			exit("No .inp files found")
		if(len(mol_op)>0):
			print("Choose one of the ", len(mol_op), " .op files.")
			for i,op in enumerate(mol_op):
				print(i, "for ", op)
			choice_op =int(input("Please enter the desired number.\n"))
			file_op=mol_op[choice_op]
		else:
			exit("No .op files found")

	#search for avaiable .sh files to use as template
	input_sh=glob.glob("*.sh")
	if(len(input_sh)>0):
		print("Choose one of the ", len(input_sh), " .sh files.")
		for i,sh in enumerate(input_sh):
			print(i, "for ", sh)
		choice_sh =int(input("Please enter the desired number.\n"))
		file_sh=input_sh[choice_sh]
	else:
		exit("No .sh files found")

	return file_inp,file_op,file_sh




def get_input_data():
	
	#beginn input for the program
	print("This program is designed to initilize submission files, submit those to to MCDTH and manage the ouput.\n"+
		"pyrmod4.op, pyr4.inp and submit.sh must be in the same directory!\n"+
		"Only one data set should be in a working directory at a time to avoid confusion.\n The program will not allow a second set of data to be generated if there is already a csv file with variables present.")
	
	#first use test_mode, later this will be the normal mode
	mode_string=input('Choose one of the following (#2,3,4,5 can be combined with \",\"): \n'+
					'1: create input, send to server, manage output, anaylse spectra.\n'+
					'2: create input.\n'+
					'3: send to server\n'+
					'4: manage output\n'+
					'5: analyze spectra\n'+
					'6: check for all submissions\n'+
					'666: cleanup (clean tmpa) !This cleanup is not included in mode 1 and has to be done seperate or added (1,666)! \n') 
	
	#transforms input into list of int
	mode_list=[int(mode_str)for mode_str in mode_string.split(",")]
	
	#make dict
	dict_param={}
	submit_template=[0,0,0]
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


	#setup directory and operator files or import from existing directory
	if(any([mode in [1,2,3,4,5,6] for mode in mode_list])):
		working_directory =load_prebuild_structure()

		submit_template=find_operator_files(working_directory)



		

	if(any([mode in [1,3] for mode in mode_list])):
		no_of_submits=int(input("Enter number of submits in each run:\n"))
	else:
		no_of_submits=0

	if(any([mode in [1,5] for mode in mode_list])):
		peak_height_for_spectra=float(input("Enter the percentage number (20 = 20%)of peak height that should be added to the csv output:\n"))
		peak_height_for_spectra=peak_height_for_spectra/100
	else:
		peak_height_for_spectra=1
	
	if(any([mode in [6] for mode in mode_list])):
		print("Mode 6 will compare the content of finished_submits"+
		"with the spectral_Data to check if some submissions need to be rerun")

	print("Finished setup\n")
	return mode_list, dict_param, working_directory, no_of_submits, peak_height_for_spectra, submit_template

###
#this will first create a dataFrame of all possible combinations for the given parameters and save it as a csv



def create_submit_files(dict_param, path_dict):

	print("Begin creation of submit files")
	if(os.path.exists(path_dict["submit_template"])==False):
		sys.exit("this program can not function if submit.sh is missing")
	inputfile = path_dict["submit_template"]
	
	all_combination_values=product(*dict_param.values())
	df_combi = pd.DataFrame(all_combination_values, columns=dict_param.keys())
	df_combi=df_combi.round(4)
	if(len(glob.glob(path_dict["working_directory"]+"/*.csv"  ))!=0):
		print("There is already a csv file with parameters present! No new data will be generated!")
		print("Instead the previous submissions will be continued if mode 1 or 3 were chosen.")
	else:
		df_combi.to_csv(path_dict["working_directory"]+"/all_"+str(len(df_combi))+"_combinations.csv")
		
		#print(df_combi.head())
		
		complete_array=df_combi.to_numpy()
		for i,row in enumerate(complete_array):
			outname=path_dict["input_Data"]+"/submit"
			run_str="run"+str(i)
			output_name="output__"   
			parameter_str="-mnd -D run" +str(i)
			for j,nr in enumerate(row):
				outname=outname+"__"+df_combi.columns[j]+"_"+str(nr)
				parameter_str=parameter_str + " -p " +df_combi.columns[j]+" "+str(nr/27.211)  #divide by 27.211 to convert from ev to au
				output_name=output_name+"++"+df_combi.columns[j]+"%"+str(nr).replace(".","_")			
			outname=outname+".sh"
			
			#print(outname)
			#print(parameter_str)
			with open(outname,'w') as new_file:
							with open(inputfile, 'r') as old_file:
								line = old_file.read()
								new_file.write(line.replace("runxxx", run_str).replace("xyz", parameter_str).replace("whatever",output_name)  )
								#new_file.write(line.replace("runxxx", run_str).replace("xyz", parameter_str))#.replace("whatever",output_dir)   )
		print("Finished creation of submit files")




def commit_jobs(path_dict, no_of_submits):
	all_input_data=glob.glob(path_dict["input_Data"]+'/*.sh')
	all_input_data_long_path=[os.path.abspath(input) for input in all_input_data]
	#print("all data:",all_input_data[0])
	#print("all input long",all_input_data_long_path[0])


	current_path=os.getcwd()

	#change directory to have output in the right place

	#print("current",current_path)
	if(len(all_input_data)!=0):
		os.chdir(path_dict["output"])

		print("Total of ", len(all_input_data), " jobs remaining.")
		if(len(all_input_data)<=no_of_submits):
			no_of_submits=len(all_input_data)

		for i in range(no_of_submits):
			print(str(all_input_data_long_path[i]))
			os.system("sbatch "+ all_input_data_long_path[i]) 
		print("submitting file")
		os.chdir(current_path)
		for i in range(no_of_submits):
			shutil.move(all_input_data_long_path[i],path_dict["finished_input"] )



		return True,no_of_submits
	else:
		print("No jobs remaining.")
		return False,0



def manage_output(path_dict,output_name_list):
	print("output name list:", output_name_list)
	#gets the current path to return later

	current_path=os.getcwd()
	print("current",current_path)

	
	for output_dir in output_name_list:
		
		#gets the run number from the dir name
		if(len(glob.glob(output_dir+'/run*'))>0):
			run_file_name=glob.glob(output_dir+'/run*')[0]
			print("run name:",run_file_name)
			print("output_name:",output_dir )
			run_parameters=(run_file_name.split("__")[1].split(".")[0])

			print("Run file name: "+ run_file_name)
			print("Run parameter: ",run_parameters)
			
			#change dir for autospec
			os.chdir(run_file_name)
			os.system("autospec85 -e -0.2258 eV  -1.0 1.0 eV 30 1")
						
			#return to previous dir
			os.chdir(current_path)
			#copys the spectrum into the spectra_data dir and changes its name according to the run number
			shutil.copy(run_file_name +"/spectrum.pl",path_dict["spectra_data"]+"/"+run_parameters+".pl" )
			#moves the complete output dir into the finished 
			shutil.move(output_dir,path_dict["finished_outputs"]+"/submits_"+run_parameters+".output" )

			print("\n \n")
		else:
			print("len von output dir ==0")
def run_jobs_ordered(mode_list,path_dict,no_of_submits,peak_height_for_spectra):
	start_next_batch=True
	completed_all_tasks=False
	while(completed_all_tasks==False):
		
		#beginn with submitting spectra 
		if(start_next_batch==True and any([mode in [1,3] for mode in mode_list])):
			jobs_available,actual_submits = commit_jobs(path_dict,no_of_submits)
			start_next_batch=False
			print("nap 60s")
			time.sleep(60)	

		#check how much output is available and compare that with the
		#number of submitted files.
		output_name_list=glob.glob(path_dict["output"]+'/*.output')
		#exeption if mode 3 not included:
		if(mode_list==[4,5] or mode_list==[4] or mode_list==[5]):
			print("Warning: mode 3 not included. The program has no knowledge about how many submissions are expected")
			actual_submits=len(output_name_list)
		print("This many outputs are prensent:",len(output_name_list))
		print("This many outputs are expected:",actual_submits)

		if(len(output_name_list)>=actual_submits and len(output_name_list)>0):
			start_next_batch=True #start new batch when all previos files are finished
			if(any([mode in [1,4] for mode in mode_list])):
				manage_output(path_dict,output_name_list)


		#wait for more outputs		
		elif(actual_submits==0):
			print("Warning: No submissions expected and no output found, "+
				 "this program can not manage any output.\n"+
				 "Check manually if there are more Submits on the server and rerun the program afterwards")
		else:
			print("Not enough output yet:", len(output_name_list), "found but",
				actual_submits, "needed.\n waiting for 30 seconds")
			time.sleep(30)	

		if(any([mode in [1,5] for mode in mode_list])):
			spectra_analysis(path_dict,peak_height_for_spectra)
		
		completed_all_tasks=check_completion(path_dict,mode_list)

	print("Main Loop finished!\n"+
			"All Tasks were done")


def check_completion(path_dict,mode_list):
		#get all the file counts:
		num_input_data=len(glob.glob(path_dict["input_Data"]+'/*.sh'))
		num_finished_inputs=len(glob.glob(path_dict["finished_input"]+'/*.sh'))
		num_output=len(glob.glob(path_dict["output"]+'/*.output'))
		num_finished_output=len(glob.glob(path_dict["finished_outputs"]+'/*.output'))
		num_spectra_data=len(glob.glob(path_dict["spectra_data"]+'/*.pl'))
		num_finished_spectra=len(glob.glob(path_dict["spectra_data_finished"]+'/*.pl'))


		if(any([mode in [1] for mode in mode_list]) or mode_list==[3,4,5] or mode_list==[2,3,4,5]):
			print("case 1",num_finished_inputs, num_finished_spectra,num_input_data)

			if(num_finished_inputs==num_finished_spectra and num_input_data==0):
				print("exit 1")
				return True
			else: return False
		if(mode_list==[3] or mode_list==[2,3]):
			if(num_input_data==0):
				return True
			else: return False
		if(mode_list==[3,4] or mode_list==[4]or mode_list==[2,3,4]):
			if(num_finished_inputs==num_spectra_data):
				return True
			else: return False
		if(mode_list==[5] or mode_list==[4,5] ):
			if(num_finished_inputs==num_finished_spectra):
				return True
			else: return False

def get_different_rows(source_df, new_df):
    """Returns just the rows from the new dataframe that differ from the source dataframe"""
    merged_df = source_df.merge(new_df, indicator=True, how='outer')
    changed_rows_df = merged_df[merged_df['_merge'] == 'right_only']
    return changed_rows_df.drop('_merge', axis=1)

def compare_submits_to_otput(path_dict):
	current_path=os.getcwd()
	print("current",current_path)
	print(type(path_dict["working_directory"]))
	combination_csv=glob.glob( path_dict["working_directory"]+'/*combinations.csv')[0]
	output_csv=glob.glob( path_dict["working_directory"]+'/*list.csv')[0]

	#df_combinations=pd.read_csv(combination_csv)[["k6a1","k6a2","k11","k12","k9a1","k9a2","delta", "lambda"]]
	df_combinations=pd.read_csv(combination_csv)
	column_names=df_combinations.columns.values[1:]
	df_combinations=df_combinations[column_names]
	df_output=pd.read_csv(output_csv)[column_names]

	df_missing = get_different_rows(df_output,df_combinations)
	print(df_missing.head())
	list_missing_submit_files=[]
	for row in df_missing.values:
		list_missing_submit_files.append("/submit")
		for i, comlumname in enumerate(column_names):
			list_missing_submit_files[-1]=str(list_missing_submit_files[-1] +
				"__"+comlumname+"_"+str(row[i]))
			
		list_missing_submit_files[-1]=str(list_missing_submit_files[-1] + ".sh")
	print(list_missing_submit_files)

	#move all missing files back to input_Data

	for file_str in list_missing_submit_files:
		shutil.move(path_dict["finished_input"]+file_str, path_dict["input_Data"]     )

def run_jobs(mode_list,path_dict,no_of_submits,peak_height_for_spectra):
	jobs_available=True
	start_next_batch=True
	while(jobs_available==True and any([mode in [1,3,4] for mode in mode_list])):
		#only start new batch when last is finished and mode 1 or 3 was chosen
		if(start_next_batch==True and any([mode in [1,3] for mode in mode_list])):
			jobs_available = commit_jobs(path_dict,no_of_submits)
			start_next_batch=False
		#only wait if batches should be commited (mode 1,3)
			print("nap 60s")
			time.sleep(60)	
		output_name_list=glob.glob(path_dict["output"]+'/*.output')
		if(len(output_name_list)>=1 and any([mode in [1,4] for mode in mode_list])):
			manage_output(path_dict,output_name_list)
			if(any([mode in [1,5] for mode in mode_list])):

				spectra_analysis(path_dict,peak_height_for_spectra)

			start_next_batch=True

		#this shoudl ensure that the program can finish if only mode 3 and 4 are selected
		elif((len(glob.glob(path_dict["spectra_data"]+'/*.pl'))==
			len(glob.glob(path_dict["finished_input"]+'/*.sh') ))
			 or
			(len(glob.glob(path_dict["spectra_data_finished"]+'/*.pl'))==
			len(glob.glob(path_dict["finished_input"]+'/*.sh')))
			):
			print("No of spectra = number of inputs -> finished")
			jobs_available=False

		else:
			print("No output found, but still waiting")
			print("nap 30s")
			time.sleep(30)

	#aditional control depending on the chosen mode and
	if(any([mode in [4] for mode in mode_list]) and any([mode in [5] for mode in mode_list])==False     ):
		while(len(glob.glob(path_dict["spectra_data"]+'/*.pl'))!=
			len(glob.glob(path_dict["finished_input"]+'/*.sh'))
			):
			
			if(len(output_name_list)>=1):
				manage_output(path_dict,output_name_list)
			
			print("nap for mode 4")
			time.sleep(45)

	elif(any([mode in [1] for mode in mode_list])):
		while(len(glob.glob(path_dict["spectra_data_finished"]+'/*.pl'))!=
			len(glob.glob(path_dict["finished_input"]+'/*.sh'))
			):
			
			if(len(output_name_list)>=1):
				manage_output(path_dict,output_name_list)
				spectra_analysis(path_dict,peak_height_for_spectra)

			print("nap for mode 1")
			time.sleep(45)	
			
			
	print("All input files were converted into spectra.")



def spectra_analysis(path_dict,peak_height_for_spectra):
	print("Begin spectra analysis")
	data_file_list=glob.glob(path_dict["spectra_data"]+"/*.pl")
	#print(data_file_list)
	if(len(data_file_list)>=1):
		if os.path.exists(path_dict["working_directory"]+"/RENAME_THIS_AFTERWARDS_New_Peak_list.csv"):
			complete_df=pd.read_csv(path_dict["working_directory"]+"/RENAME_THIS_AFTERWARDS_New_Peak_list.csv")
		else:
			complete_df=pd.DataFrame()
		for data_file_str in data_file_list:
			#extract the variables names and their values from the name
			varialbes_names_value=data_file_str.split(".")[0].split("++")[1:]
			#print(varialbes_names_value)
			label_dict={}
			for variable in varialbes_names_value:
				label_dict[variable.split("%")[0]]=variable.split("%")[1].replace("_",".")
				#this holds all names and values for the different label
			#print(label_dict)

			#get peaks from spectrum
			print(data_file_str)
			df_spectrum = pd.read_csv(data_file_str,sep="   ",header =2,engine='python')
			df_spectrum=df_spectrum.dropna(1) #remove all na entrys
			df_spectrum.rename(columns={'#': 'Energy',' Energy':'g1','Unnamed: 2':'g2','Unnamed: 3':'g3'}, 
					inplace=True) 
			print("peak minimum:",df_spectrum.g1.max()*peak_height_for_spectra)
			df_maxima=df_spectrum.iloc[find_peaks(df_spectrum.g1.values,height=df_spectrum.g1.max()*peak_height_for_spectra)[0]   ].dropna().drop(columns=['g2','g3'])
			print(df_maxima)
			if(len(df_maxima["Energy"].values) >=20):
				#print("more than 20 maxima detected (", len(df_maxima["Energy"].values),")")
				new_threshold=peak_height_for_spectra
				
				while(len(df_maxima["Energy"].values) >=20):
					new_threshold=new_threshold+0.2
					print(len(df_maxima["Energy"].values), 
					"Maxima were found. Setting limit to ",
					new_threshold," of the current maximal value" )

					df_maxima=df_spectrum.iloc[find_peaks(df_spectrum.g1.values,height=df_spectrum.g1.max()*new_threshold)[0]   ].dropna().drop(columns=['g2','g3'])




			#this should filter out any spectra with small peaks
			if(len(df_maxima.nlargest(1,'g1')["Energy"].values)>0):
				main_max=df_maxima.nlargest(1,'g1')["Energy"].values[0]
				#print("\n",main_max)
				label_dict["main_maximum"]=main_max
				label_dict["all_maxima"]=(df_maxima["Energy"].values)
				label_dict["no_of_max"]=(len(df_maxima["Energy"].values))
				label_dict["Intensity"]=(df_maxima["g1"].values)

				if(complete_df.empty==True):

					complete_df=pd.DataFrame(columns=label_dict.keys())

				complete_df=complete_df.append(label_dict,ignore_index=True)
			shutil.move(data_file_str,path_dict["spectra_data_finished"] )

		print(complete_df.head())
		print(len(complete_df))
		complete_df.to_csv(path_dict["working_directory"]+"/RENAME_THIS_AFTERWARDS_New_Peak_list.csv",index= False)
		print("Saved CSV to "+path_dict["working_directory"]+"/RENAME_THIS_AFTERWARDS_New_Peak_list.csv")
		#move finished spectra


def setup_dir_structure(path_dict):
	all_dir_keys=path_dict.keys()
	for key in all_dir_keys:
		if(os.path.exists(path_dict[key])==False):
			os.makedirs(path_dict[key])


	# if(os.path.exists(path_dict["working_directory"])==False):
	# 	os.makedirs(path_dict["working_directory"])
	# if(os.path.exists(path_dict["input_Data"])==False):
	# 	os.makedirs(path_dict["input_Data"])
	# if(os.path.exists(path_dict["finished_input"])==False):
	# 	os.makedirs(path_dict["finished_input"])
	# if(os.path.exists(path_dict["output"])==False):
	# 	os.makedirs(path_dict["output"])
	# if(os.path.exists(path_dict["finished_outputs"])==False):
	# 	os.makedirs(path_dict["finished_outputs"])
	# if(os.path.exists(path_dict["spectra_data"])==False):
	# 	os.makedirs(path_dict["spectra_data"])

	if(any([mode in [1,3] for mode in mode_list])):

	#check if needed files for calculations are present in the same dir as this file. if not throw exepction
		if(os.path.exists(path_dict["pyr4_template"])==False):
			sys.exit("this program can not function if pyr4.inp is missing")
		if(os.path.exists(path_dict["pyrmod4_template"])==False):
			sys.exit("this program can not function if pyrmod4.op is missing")

		#copy pyr4.inp and pyrmod4.op into the input_Data and outputdir
		shutil.copy2(path_dict["pyr4_template"],path_dict["input_Data"] )
		shutil.copy2(path_dict["pyrmod4_template"],path_dict["input_Data"] )	
		shutil.copy2(path_dict["pyr4_template"],path_dict["output"] )
		shutil.copy2(path_dict["pyrmod4_template"],path_dict["output"] )	



#possible modes
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
#current_path=(os.path.dirname(__file__))
filename = sys.argv[0]
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
os.chdir(dir_path)

#get basic setup parameters
mode_list, dict_param, working_directory, no_of_submits,peak_height_for_spectra,submit_templates= get_input_data()

 #["submit.sh","pyr4.inp","pyrmod4.op"]

#setup dict for all paths
path_dict={	"working_directory":working_directory,
			"pyr4_template": submit_templates[0],
			"pyrmod4_template": submit_templates[1],
			"submit_template": submit_templates[2],

			"input_Data": working_directory+"/input_Data",
			"finished_outputs": working_directory+"/finished_outputs",
			"finished_input":working_directory+"/finished_input",
			"output": working_directory+"/output",
			"spectra_data": working_directory+"/spectra_data",
			"spectra_data_finished": working_directory+"/spectra_data_finished"}

setup_dir_structure(path_dict)

#all and file generation
if(any([mode in [1,2] for mode in mode_list])):
	create_submit_files(dict_param, path_dict)
	
	
#all and send to server

if(any([mode in [1,3,4,5] for mode in mode_list])):

	#check if needed files for calculations are present in the same dir as this file. if not throw exepction
	if(os.path.exists(path_dict["pyr4_template"])==False):
		sys.exit("this program can not function if pyr4.inp is missing")
	if(os.path.exists(path_dict["pyrmod4_template"])==False):
		sys.exit("this program can not function if pyrmod4.op is missing")

	#copy pyr4.inp and pyrmod4.op into the input_Data dir
	shutil.copy2(path_dict["pyr4_template"],path_dict["input_Data"] )
	shutil.copy2(path_dict["pyrmod4_template"],path_dict["input_Data"] )

	#run_jobs(mode_list,path_dict,no_of_submits,peak_height_for_spectra)
	run_jobs_ordered(mode_list,path_dict,no_of_submits,peak_height_for_spectra)

	#maybe add this to the workflow

#and one standalone spectra analysis 
#this should be very quick if all spectras have already been analyzed
#if(any([mode in [1,5] for mode in mode_list])):
#	spectra_analysis(path_dict,peak_height_for_spectra)
if(any([mode in [6] for mode in mode_list])):
	compare_submits_to_otput(path_dict)


if(any([mode in [666] for mode in mode_list])):
	print("This cleanup will only work on the hitchcock server and is otherwise unneccesary!")
	answer_sure=input("Are you sure you want to run the clean up program for the tmpe directory? yes/no\n")
	if(answer_sure=="yes"):
		get_current_user=os.path.dirname(os.path.realpath(__file__))
		current_user=get_current_user.split("home/")[1].split("/")[0]
		user_correct=input("Is " + current_user +" the current user? yes/no\n")
		if(user_correct=="yes"):
			os.chdir("/tmpa/"+current_user)
			all_files_to_clean=glob.glob("*.output")
			print("The following files are going to be deleted:\n")
			print(all_files_to_clean)
			is_that_correct=input("Is that correct? yes/no\n")
			if(is_that_correct=="yes"):
				for remove_file in all_files_to_clean:
					shutil.rmtree(remove_file)
