import numpy as np
from joblib import Parallel, delayed
from scipy.optimize import minimize
from aegon.libutils import scale_coords
#------------------------------------------------------------------------------------------
def lj_energy(positions, epsilon = 1.0, sigma = 1.0):
    N = len(positions)
    energy = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            rij = positions[i] - positions[j]
            r = np.linalg.norm(rij)
            if r < 15.0:
                sr6 = (sigma / r) ** 6
                energy +=  4.0 * epsilon * sr6 * (sr6 - 1.0)
    return energy
#------------------------------------------------------------------------------------------
def lj_forces(positions, epsilon = 1.0, sigma = 1.0):
    N = len(positions)
    forces = np.zeros_like(positions)
    for i in range(N):
        for j in range(i + 1, N):
            rij = positions[i] - positions[j]
            r = np.linalg.norm(rij)
            if r < 15.0:
                sr6 = (sigma / r) ** 6
                f_scalar = 24.0 * epsilon * sr6 * (2.0 * sr6 - 1.0)/r
                fij = f_scalar * (rij / r)
                forces[i] +=  fij
                forces[j] -=  fij
    return forces
#------------------------------------------------------------------------------------------
def opt_lj(atoms):
    epsilon=1.0
    sigma=3.0/np.power(2,1/6)
    cluster=atoms.copy()
    cluster=scale_coords(cluster,1.0/sigma)
    x0=cluster.positions
    ### SciPy BFGS
    result = minimize(
    fun=lambda x: lj_energy(x.reshape(-1, 3)),
    x0=x0.reshape(-1),
    jac=lambda x: -lj_forces(x.reshape(-1, 3)).reshape(-1),
    method='BFGS',
    options={'disp': False, 'gtol': 1e-6}
    )
    opt_scipy = result.x.reshape(-1, 3)
    energy_scipy = lj_energy(opt_scipy)
    cluster_opt=atoms.copy()
    cluster_opt.set_positions(opt_scipy)
    cluster_opt=scale_coords(cluster_opt,sigma)
    cluster_opt.info['e']=energy_scipy
    #writexyzs([cluster_opt], cluster_opt.info['i']+'.xyz')
    return cluster_opt
#------------------------------------------------------------------------------------------
def parallel_opt_LJ(mol_list, n_jobs = -1):
    results = Parallel(n_jobs = n_jobs)(delayed(opt_lj)(mol) for mol in mol_list)
    return results
#------------------------------------------------------------------------------------------
