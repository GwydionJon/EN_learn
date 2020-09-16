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

if(os.path.exists("submitting_iteration.txt")==False):
	print("Start new run of submissions")
	with open("submitting_iteration.txt",'w') as new_file:
		new_file.write("Start sumbmission counting: \n")
		new_file.write("0")
		
		
		
with open("submitting_iteration.txt", "r") as file:
    first_line = file.readline()
    for last_line in file:
        pass
	
print("Starting with submission nr:")
print(int(last_line))
for i in range(int(last_line),int(last_line)+1):
	print(str("subtmit" + str(i)+".sh"))
	
	if(os.path.exists(str("subtmit" + str(i)+".sh"))==True):
		os.system("sbatch submit"+str(i)+".sh") 
		with open("submitting_iteration.txt",'w') as new_file:
			new_file.write("\n "+ str(i))
	else:
		print("no further submitxxx.sh could be found")
		raise SystemExit
		

		
		
		
		
		
		