#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 13:27:25 2023

@author: casper
"""

from gpatom.gpfp.kernel import FPKernel, FPStressKernel

class HighDimKernel(FPKernel):
    
    """
    Kernel class used when training on energies and forces for atoms with an 
    arbitrarty amount of dimensions with training on forces.
        
    See FPKernel for more info
    """
        
    def get_size(self, x):
        """
        Return the correct size of a kernel matrix when gradients are
        trained.
        
        Fingerprint, x, must carry an attribute "dims", describing the number of
        spatial dimensions
        """
        return len(x.atoms) * x.dims + 1
        
    
class HighDimStressKernel(FPStressKernel):
    
    '''
    Kernel class used when trained on for atoms with an arbitrarty amount of 
    dimensions wth trainiing on forces and stresses
    
    Fingerprint must carry an attribute "dims", describing the number of
    spatial dimensions
    
    See FPStressKernel for more info
    '''
    
    def get_size(self, x):
        """
        Return the correct size of a kernel matrix when gradients are
        trained.
        
        Fingerprint, x, must carry an attribute "dims", describing the number of
        spatial dimensions
        """
        return len(x.atoms) * x.dims + 1
