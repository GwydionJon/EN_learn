#!/usr/bin/env python3
#this script generates the input and submits to the queue;
#processes the output
#IU 09/2020
#
import os,sys,re
import argparse
parser = argparse.ArgumentParser(description='''
        Input generater and output processing for ENlearn spectra analysis.
        ''')

epilog = '\nUsage: python gen_data.py -r input -c k6a1 -ds 0.1 -n 10'
parser.add_argument('-r', '--runtype', help='input: generate input and submit to queue; output: \
        process through the output files; default=none', required=True)
parser.add_argument('-c', '--coordinate', help='the coupling constant to be scanned; default=k6a1', required=False)
parser.add_argument('-ds', '--dstep', help='stepsize of the scan, default=0.1', required=False)
parser.add_argument('-n', '--number', help='number of steps to be generated, default=10', 
        required=False)

args = vars(parser.parse_args())

#now these are slightly specific to pyrazine
if args['coordinate']:
    c1 = str(args['coordinate'])
else:
    c1='k6a1'

if args['dstep']:
    dx = float(args['dstep'])
else:
    dx = 0.1

if args['number']:
    n = int(args['number'])
else:
    n = 10

#add more arguments if required
#if args['']:
#else:
#
#here is some hard-coded specifics that need to be adapted later
#files
inputfile = 'pyr4.inp'
opfile = 'pyrmod4.op'
submitfile = 'submit.sh'
#
#molecular constants
#
#

# generating the operator file
print("data will be read from file {:s}".format(opfile))

outname = 'run{:03}.op'.format(n)
outstring = '{} = {}, ev'.format(c1,dx)

with open(outname,'w') as new_file:
    with open(opfile, 'r') as old_file:
        line = old_file.read()
        new_file.write(line.replace(c1 +' =', outstring))


# generating the input file
print("data will be read from file {:s}".format(inputfile))

outname = 'run{:03}.inp'.format(n)
outstring = 'opname = run{:03}'.format(n)

with open(outname,'w') as new_file:
    with open(inputfile, 'r') as old_file:
        line = old_file.read()
        new_file.write(line.replace('opname = pyrmod4', outstring))
