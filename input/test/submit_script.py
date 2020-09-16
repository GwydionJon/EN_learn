import itertools as it
import numpy as np
import os,sys,re
import argparse


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

	
print("Starting with submission nr:")
print(start_number)
for i in range(start_number,start_number+5):
	print(str("submit" + str(i)+".sh"))
	print(os.path.exists("submit0.sh"))
	if(os.path.exists(str("submit" + str(i)+".sh"))==True):
		#os.system("sbatch submit"+str(i)+".sh") 
		print("submitting file")
		with open("submitting_iteration.txt",'a') as file:
			file.write(str(i)+"\n")
	else:
		print("no further submitxxx.sh could be found")
		#raise SystemExit
		

		
		
		
		
		
		