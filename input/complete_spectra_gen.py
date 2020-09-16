import itertools as it
import numpy as np
import os,sys,re
import argparse
import glob
import re
import time

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
			




parser = argparse.ArgumentParser(description='''
        Input generater and output processing for ENlearn spectra analysis.
        ''')

epilog = '\nUsage: python gen_sub_data.py (-r 0.5 -dr 0.5 -n 3 -s test)'# these are optional

parser.add_argument('-m', '--mode', help='Decides the task this script should perform. 1.[all] Generate new submission files, submit and process the spectra. 2. [gen] generate only the files. 3.[subProc] only submit and process spectra. 4.[sub] only submit. 5.[proc] only process ', required =True, choices= [1,2,3,4,5,"all", "gen","subProc","sub","proc")

parser.add_argument('-r', '--range', help='input range from -r to +r; dafault = -0.5 to 0.5; only relevant in mode 1 and 2' , required =False)

parser.add_argument('-dr', '--rangeStep', help='size of the steps, that the values are changed by for each run, alternativly number of steps can be used, this will be ignored if both are given; default = 0.5; only relevant in mode 1 and 2', required =False)


parser.add_argument('-n','--nSteps',help='Tells the program how many steps it should do, will take priority if not consistend with rangeStep; default =3; only relevant in mode 1 and 2', required =False)

parser.add_argument('-s','--save',help='tells the program where to store the data, the directory needs to exist beforehand; default =submits', required =False)

parser.add_argument('-i', '--iteration',
	 help= 'manual starting iteration' , required =False)
	 
	 


args = vars(parser.parse_args())

if(args['mode']:
	mode=args['mode']

#now these are slightly specific to pyrazine
if args['range']:
	r = float(args['range'])
else:
	r= 0.5

print('The given range will be from',-1*r, 'to', r) 
if args['rangeStep']:
	dr = float(args['rangeStep'])
	rangeStep_called=True
else:
	dr = 0.5
if args['nSteps']:
	n = int(args['nSteps'])
	nSteps_called=True
else:
	n = 3
if args['save']:
	save_location = str(args['save'])
else:
	save_location = "submits"


1,2,3,4,5,"all", "gen","subProc","sub","proc"
#manage the different modes:
if(mode=="all"):
	mode=1
elif(mode=="gen"):
	mode=2
elif(mode=="subProc"):
	mode=3
elif(mode=="sub"):
	mode=4
elif(mode=="proc"):
	mode=5
else:
	mode=int(mode)



if(mode in [1,2]:
	# decide which steps to take:
	#first case both or none are given
	if(rangeStep_called==nSteps_called):
		if(rangeStep_called==True and nSteps_called==True ):
			print('Both nSteps and rangeStep have been given. rangeStep will be ignored.')
		else:
			print('no additional arguments were made.')
		var_array=  np.linspace(-r,r,n, endpoint=True)
		print('The used range will thus be: ', var_array)
	
	#second case: only range step
	elif(rangeStep_called==True):
		print('rangeStep was given')
		var_array= np.arange(-r,r+dr,dr) # r+dr is nesicassry to ensure that some value around the desired endpoint is present
		print('The used range will thus be:', var_array)
	
	#third case only nStep
	elif(nSteps_called==True):
		print('nSteps was given')
		var_array= np.linspace(-r,r,n, endpoint=True)
		print('The used range will thus be:', var_array)	
		
	
	#producing the final input array for the submission files
	final=np.asarray(list((it.product(var_array,var_array,var_array,var_array,var_array,var_array))))
	print('The number of generated inputfiles will be:', len(final))
	
	
	inputfile = "submit.sh"
	if(os.path.exists(save_location)==False):
		os.system("mkdir "+ save_location)
		
	if(os.path.exists(save_location+"/outputs")==False):
		os.system("mkdir "+ save_location+"/outputs")
	if(os.path.exists(save_location+"/outputs/finished")==False):
		os.system("mkdir "+ save_location+"/outputs/finished")
	if(os.path.exists(save_location+"/spectra_data")==False):
		os.system("mkdir "+ save_location+"/spectra_data")
	
	
	
	for i in range(len(final)):
		outname=save_location+"/submit"+str(i)+".sh"
		with open(outname,'w') as new_file:
			with open(inputfile, 'r') as old_file:
				line = old_file.read()
				new_file.write(line.replace("runxxx", "run"+str(i)).replace("xyz", "-mnd -D {} -p k6a1 {} -p k6a2 {} -p k11 {} -p k12 {} -p k9a1 {} -p k9a2 {}".format("run"+str(i),*final[i])))
				
				
#second part: submitting and managing:

if(mode in[1,3,4,5]):
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
		#commit new jobs
		print("start next batch after managing output:", start_next_batch)
		if(start_next_batch==True and mode in [1,3,4]):
			print("should start new job now")
			commit_job()
			start_next_batch=False
		print("beginn sleep phase")
		time.sleep(300)
		print("--------------------------")
		#manage outputs
		if(start_next_batch==Falseand mode in [1,3,5]):
			manage_output()
			
			
		if(check_completion==True):
			keep_running=False
						
