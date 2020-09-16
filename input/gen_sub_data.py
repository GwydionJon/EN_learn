import itertools as it
import numpy as np
#a=np.arange(-0.5,0.5,0.1)



import os,sys,re
import argparse
parser = argparse.ArgumentParser(description='''
        Input generater and output processing for ENlearn spectra analysis.
        ''')


epilog = '\nUsage: python gen_sub_data.py (-r 0.5 -dr 0.5 -n 3 -s test')# these are optional


parser.add_argument('-r', '--range', help='input range from -r to +r; dafault = -0.5 to 0.5' , required =False)

parser.add_argument('-dr', '--rangeStep', help='size of the steps, that the values are changed by for each run, alternativly number of steps can be used, this will be ignored if both are given; default = 0.5', required =False)


parser.add_argument('-n','--nSteps',help='Tells the program how many steps it should do, will take priority if not consistend with rangeStep; default =3', required =False)

parser.add_argument('-s','--save',help='tells the program where to store the data, the directory needs to exist beforehand; default =test', required =False)

#bool to chekc if nSteps and rangeStep has been called:

nSteps_called=False
rangeStep_called=False

args = vars(parser.parse_args())

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
	save_location = "test"
	
	
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
	


final=np.asarray(list((it.product(var_array,var_array,var_array,var_array,var_array,var_array))))

print('The number of generated inputfiles will be:', len(final))


inputfile = "submit.sh"
if(os.path.exists(save_location)==False)
	os.system("mkdir "+ save_location)


for i in range(len(final)):
    outname=save_location+"/submit"+str(i)+".sh"
    with open(outname,'w') as new_file:
        with open(inputfile, 'r') as old_file:
            line = old_file.read()
            new_file.write(line.replace("runxxx", "run"+str(i)).replace("xyz", "-mnd -D {} -p k6a1 {} -p k6a2 {} -p k11 {} -p k12 {} -p k9a1 {} -p k9a2 {}".format("run"+str(i),*final[i])))