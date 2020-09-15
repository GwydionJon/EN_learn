import itertools as it
import numpy as np
#a=np.arange(-0.5,0.5,0.1)
a=[-0.5,0,0.5]

final=np.asarray(list((it.product(a,a,a,a,a,a))))
inputfile = "submit.sh"
for i in range(len(final)):
    outname="test/submit"+str(i)+".sh"
    with open(outname,'w') as new_file:
        with open(inputfile, 'r') as old_file:
            line = old_file.read()
            new_file.write(line.replace("runxxx", "run"+str(i)).replace("xyz", "-mnd -D {} -p k6a1 {} -p k6a2 {} -p k11 {} -p k12 {} -p k9a1 {} -p k9a2 {}".format("run"+str(i),*final[i])))