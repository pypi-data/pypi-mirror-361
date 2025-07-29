#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 18:09:36 2024

@author: casper
"""
class RandomStructureAndFractionGenerator():
    
    """
    Generator to pair structure generation with random chemical fraction
    generation in order to be able to pre-relax the resulting atoms object
    with the WeightedCalculatorPrior.
    notice: This is only for 3D structures: For hyperspatial structure 
    generation with fractions, use HighDimRandomStructureAndFractionGenerator
    
    Examples
    --------
    >>> sgen=RandomStructureAndFractionGenerator(structure_generator, 
                                                 fraction_generator,
                                                 relaxer=...)
    >>> new_atoms=sgen.get()
    """  
    
    
    def __init__(self, structure_generator, fraction_generator, relaxer=None):

        """
        parameters
        ----------
        structure_generator: structure generator object
            Structure generator outputing an ase atoms object
            Required
            
        fraction_generator: fraction generator object
            A fraction generator taking atoms as an input to make chemical
            fractions for each element for each atom in the atoms object. 
            Required
        
        relaxer: relaxer object, optional 
            An atoms relaxer. Use WeightedCalculatorPrior with 
            WeightedRepulsivePotential to relax atoms based on their chemical
            fractions
            Default is None (no relaxation)
        """
        
        self.sgen=structure_generator
        self.fgen=fraction_generator
        self.relaxer=relaxer
    
    def get(self):
        
        atoms = self.sgen.get()
        
        fractions=self.fgen.get_fractions(atoms)
        atoms.fractions=fractions
        
        # necessary to not get error due to lack of properties in prior
        # better solution would be to have a hyperatomsobject, 
        # where the properties are always present
        atoms.extra_coords=None  
        atoms.dims=3
        
        if self.relaxer is not None:
            atoms=self.relaxer.run(atoms)
            
    
        return  atoms
    
    
    
class HighDimRandomStructureAndFractionGenerator():
    
    '''
    Like RandomStructureAndFractionGenerator but in an arbitrary
    amount of spatial dimensions.
    
    Structure generator must output atoms objects with the attached properties
    "dims" and "extra_coords" as done by all highdim structure generators
    in BEACON
    
    See RandomStructureAndFractionGenerator for more info
    '''
    
    def __init__(self, structure_generator, fraction_generator, relaxer=None):
    
        self.sgen=structure_generator
        self.fgen=fraction_generator
        self.relaxer=relaxer
    
    def get(self):
        
        atoms = self.sgen.get()
        
        fractions=self.fgen.get_fractions(atoms)
        atoms.fractions=fractions
        
        if self.relaxer is not None:
            extra_coords=atoms.extra_coords
            atoms, extra_coords=self.relaxer.run(atoms, 
                                                 self.sgen.world_center, 
                                                 extra_coords)
            atoms.extra_coords=extra_coords

        return  atoms