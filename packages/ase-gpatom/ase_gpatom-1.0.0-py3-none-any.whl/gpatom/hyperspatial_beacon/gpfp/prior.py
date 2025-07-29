#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 13:24:03 2023

@author: casper
"""

import numpy as np
from gpatom.gpfp.prior import ConstantPrior, CalculatorPrior, RepulsivePotential

from ase.calculators.calculator import Calculator, all_changes
from ase.data import covalent_radii
from ase.neighborlist import NeighborList

class HighDimConstantPrior(ConstantPrior):
    
    '''
    Constant prior working in any amount of dimensions.  
    Fingerprint object must carry an attribute 
    "dims" describing the total number of dimensions

    See ConstantPrior for further info
    '''

    def potential(self, x):
        d = len(x.atoms) * x.dims  
        output = np.zeros(d + 1)
        output[0] = self.constant
        return output


class HighDimCalculatorPrior(CalculatorPrior):    

    '''
    Calculator prior working in any amount of dimesnions.  
    Fingerprint object must carry an attribute "dims" describing the total 
    number of dimensions as well as the attribute "extra_coords" describing
    the hyperspatial coordinates.

    See CalculatorPrior for more info
    '''    
        
    def get_atoms(self,x):    
        """ 
        Method to setup atoms for high dim repulsive protential. 
        Takes the attribute "extra_coords" and "dims" on the fingerprint 
        object and atttaches it to the atoms object
        """
        atoms=x.atoms.copy()
    
        extra_coords=x.extra_coords
        atoms.extra_coords=extra_coords
        
        dims=x.dims
        atoms.dims=dims
        
        return atoms

    def get_output_size(self, atoms):
        return 1 + len(atoms) * atoms.dims


def get_highdim_distance_info(atoms, atom_idx, neighbor_list):
    
    """
    Method to find vectors between atoms in an arbitrary
    amount of dimensions.  Atoms must carry the property
    "extra_coords" for the method to work. 
    """
    
    positions = atoms.positions
    
    cell = atoms.cell

    neighbors, offsets = neighbor_list.get_neighbors(atom_idx)
         
    cells = np.dot(offsets, cell)

    d = positions[neighbors] + cells - positions[atom_idx]
                
    if atoms.extra_coords is not None:
        extra_coords=atoms.extra_coords
        d_ext=extra_coords[neighbors]-extra_coords[atom_idx]
        d=np.hstack((d,d_ext))
    
    return neighbors, d
        
        
    
class HighDimRepulsivePotential(RepulsivePotential):
    """
    RepulsulvePotential, working in any amount of spatial dimensions 
    Fingerprint object must carry an attribute "dims" describing the total 
    number of dimensions as an attribute "extra_coords" describing the
    hyperspatial coordinates.

    See RepulsivePotential for more info
    """

    implemented_properties = ['energy', 'forces', 'stress']

    default_parameters = {'prefactor': 1,'rc': 0.9, 
                          'potential_type': 'LJ', 'exponent': 2,
                          'extrapotentials': None}    
    
    nolabel = True
  
    def setup_energy_forces(self, atoms):
        energy = 0.0
        forces = np.zeros((len(atoms),   max(atoms.dims, 3)))
        return energy, forces    

    def get_distance_info(self, atoms, atom_idx, neighbor_list):
        """
        Find interatomic vectors and neighbors in arbitrary many dimensions
        """
        neighbors, d = get_highdim_distance_info(atoms, atom_idx, neighbor_list)
        return neighbors, d

    def update_stress(self, stress, derivative, d):
        stress -= np.dot(derivative[:,:3].T, d[:,:3])  
        return stress    

    def get_extra_potential(self, atoms):
        
        for potential in self.parameters.extrapotentials:
            ep_energy=potential.potential(atoms)
            ep_forces=potential.forces(atoms)
            ep_stress=potential.stress(atoms)
        
            self.results['energy']  +=  ep_energy
            
            n_force_coords=np.shape(ep_forces)[1]
            
            self.results['forces'][:,:n_force_coords] += ep_forces
            
            self.results['stress']  += ep_stress
            


class ExtraDimTallStructurePunisher:
    
    """
    Extra potental to punish atoms in a hyperspatial dimension
    with coordinate ec being below eclow or above echigh
    
    E += strength * (ec - eclow)**2 if ec < eclow
    E += strength * (ec - chigh)**2 if ec > echigh
    E = 0                          else

    
    Examples
    --------
    >>> extrapotential=ExtraDimTallStructurePunisher(eclow=..., echigh=...)
    >>> energy=extrapotential.potential(atoms)
    >>> forces=extrapotential.forces(atoms)
    >>> stress=extrapotential.stress(atoms)
    """

    def __init__(self, eclow=0.0, echigh=5.0, strength=10):
        """
        Parameters
    
        eclow : float, optional
            Height under which the potential starts
            Default is 0
        echigh : float, optional            
            Height over which the potential starts
            Default is  5
        strength : float, optional
            Strength constant of the potential
            Default is 10
        """
        
        self.eclow = eclow
        self.echigh = echigh
        self.strength = strength
        
    def potential(self, atoms):
        """ Get the energy """
        
        result = 0.0
        
        if atoms.extra_coords is None:
            return result
        
        extra_coords=atoms.extra_coords
        for i in range(len(atoms)):
            ec = extra_coords[i,:]
            
            for j in range(len(ec)):
                if ec[j] >= self.echigh:
                    result += self.strength * (ec[j] - self.echigh)**2
                elif ec[j] <= self.eclow:
                    result += self.strength * (ec[j] - self.eclow)**2
        return result
        
    def forces(self, atoms):
        """ Get the forces """

        if atoms.extra_coords is None:        
            return np.zeros((len(atoms),3))
        
        extra_coords=atoms.extra_coords
        
        n_dims = 3 + len(extra_coords[0,:])
        
        result = np.zeros((len(atoms), n_dims ))
        
        for i in range(len(atoms)):
            ec = extra_coords[i, :]
            
            for j in range(len(ec)):
                if ec[j] >= self.echigh:
                    result[i, 3+j] += self.strength * 2 * (ec[j] - self.echigh)
                elif ec[j] <= self.eclow:
                    result[i, 3+j] += self.strength * 2 * (ec[j] - self.eclow)
                    
        return -result

    def stress(self, atoms):
        """ Get the stresses """
        return np.zeros(6)
