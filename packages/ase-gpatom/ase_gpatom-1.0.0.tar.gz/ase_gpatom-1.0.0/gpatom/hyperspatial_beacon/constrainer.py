#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 22:44:34 2024

@author: casper
"""

import numpy as np
from gpatom.beacon.str_gen import get_fixed_index


class HSConstrainer:
    
    '''
    static class with methods to handle fixation of 
    atomic coordinates in in arbitrary amount of spatial dimensions. 
    '''
    
    @staticmethod
    def setup_bounds(n_atoms, dims):
        lb = [-np.inf for i in range(dims)]*n_atoms
        ub = [np.inf for i in range(dims)]*n_atoms
        return lb, ub
    
    @staticmethod
    def setup_bounds_unitcell(n_atoms, dims):
        lb = [-np.inf for i in range(dims)]*n_atoms +[-np.inf]*9
        ub = [np.inf for i in range(dims)]*n_atoms +[np.inf]*9
        return lb, ub

    @staticmethod
    def hs_constrain_atoms(atoms, dims, world_center, lb, ub):
            
        cindex=cindex=get_fixed_index(atoms)
            
        if len(cindex)>0:
            for atom in atoms:
                if atom.index in cindex:
                    idx=atom.index*dims
                    for i in range( dims ):
                       
                        if i<3:
                            lb[idx+i]=np.array( atom.position[i] )
                            ub[idx+i]=lb[idx+i]
                        else:
                            lb[idx+i]=world_center[i]
                            ub[idx+i]=lb[idx+i]
                            
        return lb ,ub