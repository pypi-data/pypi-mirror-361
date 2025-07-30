import time
import torchani
import requests
import h5py
import torch
from ase.optimize import BFGS
#from aiqm.calculator import AIMNETCalculator
#------------------------------------------------------------------------------------------
eVtokcalpermol=float(23.060548012069496)
preclist=get_float_list('prec',[1E-03, 1E-04, 1E-05])
#------------------------------------------------------------------------------------------
def calculator_anix_all(moleculelist,opt='ani1ccx'):
    moleculeout=[]
    n=len(moleculelist)
    for i,imol in enumerate(moleculelist):
        timein=time.strftime("%c")
        print('%3d from %d at %s' %(i+1,n,timein))
        id=imol.info['i']
        for prec in preclist:
            calculator= {
                'ani1x'  : torchani.models.ANI1x().ase(),
                'ani1ccx': torchani.models.ANI1ccx().ase(),
                'ani2x'  : torchani.models.ANI2x().ase()
            }[opt]
            imol.calc=calculator
            dyn = BFGS(imol, logfile=None)
            dyn.run(fmax=prec, steps=200)
        energy=imol.get_potential_energy()
        imol.info['e']=energy*eVtokcalpermol
        imol.info['c']=1
        moleculeout.extend([imol])
    return moleculeout
#------------------------------------------------------------------------------------------
