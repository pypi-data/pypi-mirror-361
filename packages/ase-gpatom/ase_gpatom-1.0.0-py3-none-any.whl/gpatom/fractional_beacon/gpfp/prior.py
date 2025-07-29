#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 13:29:24 2023

@author: casper
"""

import numpy as np
from ase.data import covalent_radii, atomic_numbers
from gpatom.gpfp.prior import ConstantPrior
from gpatom.hyperspatial_beacon.gpfp.prior import (HighDimCalculatorPrior, 
                                                   CalculatorPrior, 
                                                   RepulsivePotential)
from gpatom.hyperspatial_beacon.gpfp.prior import (HighDimConstantPrior, 
                                                   HighDimRepulsivePotential) 
from gpatom.fractional_beacon.icebeacon import ICEInfo
from ase.neighborlist import NeighborList


  
class WeightedConstantPrior(HighDimConstantPrior):
    """
    Constant prior for atoms with fractional chemical coordinates and 
    hyperspatial dimensions. Fingerprnt must carry the attributes
    "fractions" describing the elemental coordinates, "dims" describing
    the total amount of spatial dimensions and "extra_coords" describing
    the hyperspatial coordinates
    
    See ConstantPrior for more info
    """
    def get_frac_grads(self, x):
        """ Output prior derivatives of energy w.r.t fractions."""
        frac_grads=np.zeros(np.shape(x.fractions))
        return frac_grads
    
    
class WeightedCalculatorPrior(HighDimCalculatorPrior):
    
    """
    Calculator prior for atoms with fractional chemical coordinates and 
    hyperspatial dimensions. Fingerprnt must carry the attributes
    "fractions" describing the elemental coordinates, "dims" describing
    the total amount of spatial dimensions and "extra_coords" describing
    the hyperspatial coordinates. 
    
    see CalculatorPrior fore more info
    """
    
    def get_atoms(self,x):    
        """ 
        Method to setup atoms for weighted repulsive potential. 
        Takes the attributes "fractions", "extra_coords" and "dims" on the
        fingerprint and attached them to the atoms
        """
        atoms=x.atoms.copy()
    
        extra_coords=x.extra_coords
        atoms.extra_coords=extra_coords
        
        dims=x.dims
        atoms.dims=dims
        
        atoms.fractions=x.fractions.copy()
        
        return atoms
    
    def get_frac_grads(self,x):
        """ Output prior derivatives of energy w.r.t fractions."""
        frac_grads=self.calculator.results['frac_grads']
        return frac_grads
    
    
        
class WeightedRepulsivePotential(HighDimRepulsivePotential):
    
    """
    Repulsive potential for atoms with fractional chemical coordinates and 
    hyperspatial dimensions. Fingerprnt must carry the attributes
    "fractions" describing the elemental coordinates, "dims" describing
    the total amount of spatial dimensions and "extra_coords" describing
    the hyperspatial coordinates. 
    
    See RepulsivePotential for more info
    """
    
    implemented_properties = ['energy', 'forces', 'frac_grads', 'stress']

    default_parameters = {'prefactor': 1,'rc_factor': 0.9, 
                          'potential_type': 'LJ', 'exponent': 2,
                          'extrapotentials': None,
                          'elements': None, 'min_radius': False}    
    
    nolabel = True   
    
    
    def get_covrads(self, elements):
        """
        Get the scaled covalent radius of all elements in the system.
        Also get the minimal radius
        """
        covrads = np.array([covalent_radii[atomic_numbers[e]] 
                            for e in elements])
                
        covrads*=self.parameters.rc_factor
        
        if self.parameters.min_radius is None:
            min_rad=min(covrads)
        else:
            min_rad=self.parameters.min_radius
             
        return covrads, min_rad
    
    
    def get_existence(self, fracs):
        """ Calculate atomic existence """
        existence = np.sum(fracs, axis=1)
        return existence  
    
    
    def get_weighted_covrad(self, elements, fracs, covrads, min_rad):  
        """
        Get the atomic radii as the weighted average of their element
        compositions according to the fractional elemental coordinates
        """
        covrads=covrads.reshape(len(elements))

        weighted_rad=np.sum(fracs*np.array(covrads), axis=1)
        
        existence=self.get_existence(fracs)
    
        rc=weighted_rad  + (1-existence)*min_rad
        
        return rc
        
    
    def get_radii(self, atoms):
        """ 
        Get the atomic radii weighted by their element composition
        """
        weights=atoms.fractions.copy()
            
        elements=ICEInfo.get_sorted_elements(atoms)
        
        covrads, min_rad=self.get_covrads(elements)

        rc=self.get_weighted_covrad(elements, weights, covrads, min_rad)
        
        return rc
        
    
    def get_energy_and_derivatives(self, atoms, rc, neighbor_list):
        """
        Get the total energy, forces, stress and derivatve of energy w.r.t
        elemental coordinates for the atomic system
        """
        energy, forces = self.setup_energy_forces(atoms)  
        
        elements=ICEInfo.get_sorted_elements(atoms)
        
        existence=self.get_existence(atoms.fractions.copy())
        
        frac_grads=np.zeros(  (len(atoms), len(elements))  )
        
        stress = np.zeros((3, 3))

        for a1 in range(len(atoms)):
            
            neighbors, d = self.get_distance_info(atoms, a1, neighbor_list)
            
            if len(neighbors)>0:     
                
                u, potential, dudr, dudq = self.get_potential(a1, rc, d, 
                                                              neighbors, 
                                                              existence, 
                                                              elements)   

                energy = self.update_energy(energy, potential)
                
                forces = self.update_forces(forces, dudr, a1, neighbors)      # its gradienst not forces
                
                frac_grads=self.update_frac_grads(frac_grads, u, dudq, 
                                                  existence, a1, neighbors) 
                
                stress = self.update_stress(stress, dudr, d)
            
        self.results['frac_grads']=frac_grads
        return energy, forces, stress

    
    
    def get_potential(self, atom_index, rc, d, 
                      neighbors, existence, elements):   
        """
        Get the contribution to the energy, forces, stress and 
        derivatve of energy w.r.t  elemental coordinates for a single 
        atom and its neighbors
        """        
        r, crs = self.radial_info(d, rc, atom_index, neighbors)  

        U, dUdx = self.get_x_potential(r, crs)
        
        ex_nbs=np.array( [   existence[n] for n in neighbors   ]  )
        
        ex_combined=existence[atom_index]*ex_nbs
        
        dUdq=np.zeros(  (len(neighbors), len(elements))  )
        
        covrads, min_rad = self.get_covrads(elements)
        
        for e in range(len(elements)):
            
            dUdq[:,e]=ex_nbs*U-ex_combined*dUdx*r/(crs**2)*(covrads[e]-min_rad)
            
    
        dUdr = ex_combined * dUdx * 1/crs
    
        cartesian_dUdr = self.cartesian_conversion(dUdr, d, r)  
    
        potential=U*ex_combined
        
        return U, potential, -cartesian_dUdr , dUdq
    


    def update_frac_grads(self, frac_grads, u, dudq, existence, atom_index, neighbors):
        """
        Update the total derivatives of the energy w.r.t elemental coordinates
        """
    
        frac_grads[atom_index] += dudq.sum(axis=0)

        for a2, g2, u2 in zip(neighbors, dudq, u):            
            frac_grads[a2] += g2 + u2*(existence[atom_index]-existence[a2])
            
        return frac_grads
        
      